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
    return [drive for drive in proc.stdout.split('\n') if len(drive) > 0]

def windowsDriveEject(driveName,linuxPassword):
    os.system(f'powershell (New-Object -comObject Shell.Application).Namespace(17).ParseName("""{driveName}""").InvokeVerb("""Eject""")')

def linuxDriveEject(driveName,linuxPassword):
    os.system(f'echo {linuxPassword} | sudo -S eject /media/{os.getlogin()}/{driveName}')

def windowsWriteToFile(fileAddr,text):
    with open(fileAddr,"w+") as driveAuth:
        driveAuth.write(text)

def linuxWriteToFile(fileAddr,text):
    os.system(f'echo "{text}" > {fileAddr}')

def windowsAuthFileExists(driveAddr,linuxPassword):
    return os.path.exists(f"{driveAddr}driveAuth.txt")

def linuxAuthFileExists(driveAddr,linuxPassword):
    command = f'echo {linuxPassword} | sudo -S ls {driveAddr[:-1]}'
    proc = subprocess.check_output(command, text=True, shell=True)
    if 'driveAuth.txt' in proc.split("\n"):
        return True
    return False

def windowsReadAuth(driveAddr,linuxPassword):
    with open(f"{driveAddr}driveAuth.txt","r") as driveAuth:
        return driveAuth.readlines()[0]

def linuxReadAuth(driveAddr,linuxPassword):
    command = f'echo {linuxPassword} | sudo -S cat {driveAddr}driveAuth.txt'
    proc = subprocess.check_output(command, text=True, shell=True)
    return proc.strip('\n')
    
def windowsGetProcessList(driveAddr,linuxPassword):
    with open(f"{driveAddr}processes.txt","r") as executor:
        return [e for e in executor.readlines() if len(e) > 0]

def linuxGetProcessList(driveAddr, linuxPassword):
    command = f'echo {linuxPassword} | sudo -S cat {driveAddr}processes.txt'
    proc = subprocess.check_output(command, text=True, shell=True)
    return [p for p in proc.split('\n') if len(p) > 0]

def windowsChangeDir(driveAddr,linuxPassword):
    os.chdir(f"{driveAddr}")

def linuxChangeDir(driveAddr,linuxPassword):
    command = f'cd {driveAddr}'
    subprocess.run(command, shell=True)

def windowsRunProcess(process,driveAddr,linuxPassword):
    os.system(process)

def linuxRunProcess(process,driveAddr,linuxPassword):
    commandSplit = process.split(" ")
    if "sudo" not in process:
        command = f'echo {linuxPassword} | sudo -S {" ".join(commandSplit[0:-1])} {driveAddr+commandSplit[-1]}'
        subprocess.run(command, shell=True)

def driveCheckerSetup(dbName):
    cur_dir = os.path.abspath(".")
    conn = dbOperations.initDB(dbName)
    linuxPassword = None
    if platform == 'win32':
        authFileExists = windowsAuthFileExists
        readAuth = windowsReadAuth
        writeToFile = windowsWriteToFile
        changeDir = windowsChangeDir
        getProcessList = windowsGetProcessList
        runProcess = windowsRunProcess
        driveEject = windowsDriveEject
        listDrives = listWindowsDrives
        slash = "\\"
    elif platform == 'linux':
        authFileExists = linuxAuthFileExists
        readAuth = linuxReadAuth
        writeToFile = linuxWriteToFile
        changeDir = linuxChangeDir
        getProcessList = linuxGetProcessList
        runProcess = linuxRunProcess
        driveEject = linuxDriveEject
        listDrives = listLinuxDrives
        slash = "/"
        linuxPassword = input("Enter sudo password for Linux Ejection: ")
    driveCheckerLoop(conn,cur_dir,listDrives,slash,authFileExists,readAuth,writeToFile,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
        
def driveCheckerLoop(conn,cur_dir,listDrives,slash,authFileExists,readAuth,writeToFile,changeDir,getProcessList,runProcess,driveEject,linuxPassword):
    drives = listDrives()
    oldDriveCount = len(drives)
    newDriveCount = oldDriveCount
    while(True):
        while newDriveCount <= oldDriveCount:
            drives = listDrives()
            oldDriveCount = newDriveCount
            newDriveCount = len(drives)
        print("New Drive Detected!")
        driveCheckerHalt(conn,drives,cur_dir,slash,authFileExists,readAuth,writeToFile,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
        oldDriveCount = newDriveCount

def driveCheckerHalt(conn,drives,cur_dir,slash,authFileExists,readAuth,writeToFile,changeDir,getProcessList,runProcess,driveEject,linuxPassword):
    for drive in drives:
        if slash == "\\":
            driveAddr = drive+slash
        elif slash == "/":
            drive = f'"{drive}"'
            driveAddr = f'/media/{os.getlogin()}/{drive}{slash}'
        if dbOperations.findDrive(conn,drive):
            if authFileExists(driveAddr,linuxPassword) is False:
                if dbOperations.adminAuth(conn,input("Auth File does not exist. Please enter the password to create your auth: ")):
                    writeToFile(driveAddr+"driveAuth.txt",dbOperations.getAuthKey(conn,drive))
                    print("Password correct! Auth Created! Re-insert flash drive to run again")
                else:
                    print("Password invalid. Re-insert flash drive and try again")
            else:
                driveAuth = readAuth(driveAddr,linuxPassword)
                if dbOperations.authenticateDrive(conn,drive,driveAuth):
                    print("Drive authenticated! Beginning drive processes:")
                    changeDir(driveAddr,linuxPassword)
                    processes = getProcessList(driveAddr,linuxPassword)
                    for process in processes:
                        print(process)
                        runProcess(process,driveAddr,linuxPassword)
                    print("All processes successfully run!")
                    changeDir(cur_dir,linuxPassword)
                elif dbOperations.adminAuth(conn,input("Auth is invalid. Please enter the password to recover your auth: ")):
                    writeToFile(driveAddr+"driveAuth.txt",dbOperations.getAuthKey(conn,drive))
                    print("Password correct! Re-insert flash drive to run again")
                else:
                    print("Password invalid. Re-insert flash drive and try again")
        else:
            if dbOperations.adminAuth(conn,input("Drive not found. Please enter the password to create your auth: ")):
                dbOperations.insertDrive(conn,drive)
                print("Password correct! Drive and auth added to database!")
                writeToFile(driveAddr+"driveAuth.txt",dbOperations.getAuthKey(conn,drive))
                print("Auth added to Drive! Re-insert flash drive to run again")
            else:
                print("Password invalid. Re-insert flash drive and try again")
        driveEject(drive,linuxPassword)
        print(f"Drive {drive} successfully ejected!")
    conn.commit()

if __name__ == '__main__':
    dbName = "sql.db"
    driveCheckerSetup(dbName)
