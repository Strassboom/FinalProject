import subprocess
import json
from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Drive:
    letter: str
    label: str
    drive_type: str

    @property
    def is_removable(self) -> bool:
        return self.drive_type == 'Removable Disk'

def list_drives() -> List[Drive]:
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

if __name__ == '__main__':
    print(list_drives())