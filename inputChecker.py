import os
import subprocess
import json
from sys import platform
from dataclasses import dataclass
from typing import Callable, List
from time import sleep
import dbOperations

@dataclass
class Drive:
    letter: str
    label: str
    drive_type: str

    @property
    def is_removable(self):
        return self.drive_type == 'Removable Disk'

def listWindowsDrives() -> List[Drive]:
    """
    Get a list of drives using WMI
    :return: list of drives
    """
    proc = subprocess.run(
        args=[
            'powershell',
            '-noprofile',
            '-command',
            'Get-WmiObject -Class Win32_LogicalDisk | Select-Object deviceid,volumename,drivetype | ConvertTo-Json'
        ],
        text=True,
        stdout=subprocess.PIPE
    )
    print(proc.stdout)
    if proc.returncode != 0 or not proc.stdout.strip():
        print('Failed to enumerate drives')
        return []
    devices = json.loads(proc.stdout)

    drive_types = {
        0: 'Unknown',
        1: 'No Root Directory',
        2: 'Removable Disk',
        3: 'Local Disk',
        4: 'Network Drive',
        5: 'Compact Disc',
        6: 'RAM Disk',
    }

    return [Drive(
        letter=d['deviceid'],
        label=d['volumename'],
        drive_type=drive_types[d['drivetype']]
    ) for d in devices]

def windowsDriveEject(driveName):
    os.system(f'powershell (New-Object -comObject Shell.Application).Namespace(17).ParseName("""{driveName}""").InvokeVerb("""Eject""")')

def driveCheckerSetup(dbName):
    cursor = dbOperations.initDB(dbName)
    if platform == 'win32':
        driveEject = windowsDriveEject
        listDrives = listWindowsDrives
        drives = listDrives()
        for drive in drives:
            if drive.drive_type == 'Removable Disk':
                if dbOperations.findDrive(drive.letter):
                    if dbOperations.authenticateDrive(cursor,drive.letter):
                        continue
                driveEject(drive.letter)
        return drives
        

if __name__ == '__main__':
    disk = "D:"
    dbName = "sql.db"
    print(driveCheckerSetup(dbName))