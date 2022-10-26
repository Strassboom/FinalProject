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
    #print(proc.stdout)
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

    return [d['deviceid'] for d in devices if drive_types[d['drivetype']] == "Removable Disk"]

def listLinuxDrives() -> List:
    """
    Get a list of drives using ls on the media mount
    :return: list of drive names
    """
    proc = subprocess.run(
        args=[
            'ls',
            f'/media/{os.getlogin()}'
        ],
        text=True,
        stdout=subprocess.PIPE
    )
    return proc.stdout.split('\n')

def windowsDriveEject(driveName):
    os.system(f'powershell (New-Object -comObject Shell.Application).Namespace(17).ParseName("""{driveName}""").InvokeVerb("""Eject""")')

def linuxDriveEject(driveName):
    os.system(f'umount /media/{os.getlogin()}/{driveName}')


def driveCheckerSetup(dbName):
    cur_dir = os.path.abspath(".")
    conn = dbOperations.initDB(dbName)
    if platform == 'win32':
        driveEject = windowsDriveEject
        listDrives = listWindowsDrives
    elif platform == 'linux':
        driveEject = linuxDriveEject
        listDrives = listLinuxDrives
    driveCheckerLoop(conn,cur_dir,listDrives,driveEject)
        
def driveCheckerLoop(conn,cur_dir,listDrives,driveEject):
    drives = listDrives()
    print(drives)
    oldDriveCount = len(drives)
    newDriveCount = oldDriveCount
    while(True):
        while newDriveCount <= oldDriveCount:
            drives = listDrives()
            oldDriveCount = newDriveCount
            newDriveCount = len(drives)
        driveCheckerHalt(conn,drives,cur_dir,driveEject)
        oldDriveCount = newDriveCount


def driveCheckerHalt(conn,drives,cur_dir,driveEject):

    for drive in drives:
        #if drive.drive_type == 'Removable Disk':
        print(drive)
        if dbOperations.findDrive(conn,drive):
            if os.path.exists(f"{drive}\\driveAuth.txt") is False:
                if dbOperations.adminAuth(conn,input("Auth File does not exist. Please enter the password to create your auth: ")):
                    with open(f"{drive}\\driveAuth.txt","w+") as driveAuth:
                        driveAuth.write(dbOperations.getAuthKey(conn,drive))
                    print("Password correct! Auth Created! Re-insert flash drive to run again")
                else:
                    print("Password invalid. Re-insert flash drive and try again")
            else:
                with open(f"{drive}\\driveAuth.txt","r") as driveAuth:
                    if dbOperations.authenticateDrive(conn,drive,driveAuth.readlines()[0]):
                        print("Drive authenticated! Beginning drive processes:")
                        os.chdir(f"{drive}\\")
                        with open(f"{drive}\\processes.txt","r") as executor:
                            for line in executor.readlines():
                                os.system(line)
                        print("All processes successfully run!")
                        os.chdir(f"{cur_dir}")
                    elif dbOperations.adminAuth(conn,input("Auth is invalid. Please enter the password to recover your auth: ")):
                        with open(f"{drive}\\driveAuth.txt","w+") as driveAuth:
                            driveAuth.write(dbOperations.getAuthKey(conn,drive))
                        print("Password correct! Re-insert flash drive to run again")
                    else:
                        print("Password invalid. Re-insert flash drive and try again")
        else:
            if dbOperations.adminAuth(conn,input("Drive not found. Please enter the password to create your auth: ")):
                dbOperations.insertDrive(conn,drive)
                print("Password correct! Drive and auth added to database!")
                with open(f"{drive}\\driveAuth.txt","w+") as driveAuth:
                    driveAuth.write(dbOperations.createAuthKey(drive))
                print("Auth added to Drive! Re-insert flash drive to run again")
            else:
                print("Password invalid. Re-insert flash drive and try again")
        driveEject(drive)
        print(f"Drive {drive} successfully ejected!")
    conn.commit()

if __name__ == '__main__':
    disk = "D:"
    dbName = "sql.db"
    driveCheckerSetup(dbName)
