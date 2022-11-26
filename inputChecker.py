import os
import subprocess
import json
from sys import platform, argv, exit
from getpass import getpass
import dbOperations

def listWindowsDrives():
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
    if not isinstance(devices,list):
        devices = [devices]
    return [d['deviceid'] for d in devices if drive_types[d['drivetype']] == "Removable Disk"]

def listLinuxDrives():
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
    os.system(f'echo {linuxPassword} | sudo -S 2>/dev/null eject /media/{os.getlogin()}/{driveName}')

def getSize(filePath):
    return os.path.getsize(filePath)

def createHashInput(rootDir):
    sizeString = ""
    for subdir, dirs, files in os.walk(rootDir):
        for file in files:
            sizeString += str(getSize(os.path.join(subdir,file)))
    return sizeString
    
def windowsGetProcessList(driveAddr,linuxPassword):
    with open(f"{driveAddr}processes.txt","r") as executor:
        return [e for e in executor.readlines() if len(e) > 0]

def linuxGetProcessList(driveAddr, linuxPassword):
    command = f'echo {linuxPassword} | sudo -S 2>/dev/null cat {driveAddr}processes.txt'
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
        command = f'echo {linuxPassword} | sudo -S 2>/dev/null {" ".join(commandSplit[0:-1])} {driveAddr+commandSplit[-1]}'
        subprocess.run(command, shell=True)

def driveCheckerSetup(dbName,cur_dir,authPassword=''):
    print(cur_dir)
    conn = dbOperations.initDB(os.path.join(cur_dir,dbName),authPassword)
    linuxPassword = authPassword
    if platform == 'win32':
        changeDir = windowsChangeDir
        getProcessList = windowsGetProcessList
        runProcess = windowsRunProcess
        driveEject = windowsDriveEject
        listDrives = listWindowsDrives
        slash = "\\"
        drives = listDrives()
        driveCheckerHalt(conn,drives,cur_dir,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
    elif platform == 'linux':
        changeDir = linuxChangeDir
        getProcessList = linuxGetProcessList
        runProcess = linuxRunProcess
        driveEject = linuxDriveEject
        listDrives = listLinuxDrives
        slash = "/"
        drives = listDrives()
        linuxPassword = authPassword
        #linuxPassword = getpass("Enter sudo password for Linux Ejection: ")
        #while linuxPassword == '' or linuxPassword.isspace():
            #linuxPassword = getpass("Enter sudo password for Linux Ejection: ")
        # driveCheckerLoop(conn,cur_dir,listDrives,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
        driveCheckerHalt(conn,drives,cur_dir,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
        
def driveCheckerLoop(conn,cur_dir,listDrives,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword):
    drives = listDrives()
    oldDriveCount = len(drives)
    newDriveCount = oldDriveCount
    while(True):
        while newDriveCount <= oldDriveCount:
            drives = listDrives()
            oldDriveCount = newDriveCount
            newDriveCount = len(drives)
        print("New Drive Detected!")
        driveCheckerHalt(conn,drives,cur_dir,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword)
        oldDriveCount = newDriveCount

# When a new drive is detected (whetehr event based or in a while loop with driveCheckerLoop)
# This method is called to operate on said Removable Disks
def driveCheckerHalt(conn,drives,cur_dir,slash,createHashInput,changeDir,getProcessList,runProcess,driveEject,linuxPassword):
    for drive in drives:
        if slash == "\\":
            driveAddr = drive+slash
        elif slash == "/":
            drive = f'"{drive}"'
            driveAddr = f'/media/{os.getlogin()}/{drive}{slash}'
        hashInput = createHashInput(driveAddr)
        # If the Drive is found in the database
        if dbOperations.findDrive(conn,drive):
            # If the Drive is authenticated, run all of the processes
            if dbOperations.authenticateDrive(conn,drive,hashInput):
                print("Drive authenticated! Beginning drive processes:")
                changeDir(driveAddr,linuxPassword)
                processes = getProcessList(driveAddr,linuxPassword)
                for process in processes:
                    print(process)
                    runProcess(process,driveAddr,linuxPassword)
                print("All processes successfully run!")
                changeDir(cur_dir,linuxPassword)
            else:
                if dbOperations.adminAuth(conn,getpass("Drive not authenticated. Please enter the password to create your Auth: ")):
                    dbOperations.updateDrive(conn,drive,hashInput)
                    print("Password correct! Auth Updated! Re-insert flash drive to run again")
                else:
                    print("Password invalid. Re-insert flash drive and try again")
        else:
            if dbOperations.adminAuth(conn,getpass("Drive not found. Please enter the password to create your Auth: ")):
                dbOperations.insertDrive(conn,drive,hashInput)
                print("Password correct! Drive and Auth updated! Re-insert flash drive to run again!")
            else:
                print("Password invalid. Re-insert flash drive and try again")
        driveEject(drive,linuxPassword)
        print(f"Drive {drive} successfully ejected!")
    conn.commit()
    if (slash == "/"):
        os.remove(os.path.join(cur_dir,"holdFile"))
    exit("Goodbye!")
    

if __name__ == '__main__':
    dbName = "sql.db"
    if len(argv) > 2:
        driveCheckerSetup(dbName,argv[1],argv[2])
    print("You must submit the path to the executable and the db password (your sudo pw if linux) to the executable file")
