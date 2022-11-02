# FinalProject
This is my final project for CIS-573

## Steps to Run:
#### (Platform)

### Development (Devs Only)
#### Both Listed Platforms
1. Make sure your flash
#### (Windows)
1. Install Python=>3.10.4
2. Install pyinstaller with pip  
    `python -m pip install pyinstaller`  
3. Run pyInstaller command to build your current directory, making an executable from argument [1]  
    For Windows if the file you want to run is inputChecker.py (it is):  
    `pyInstaller inputChecker.py`
4. Go to Control Panel, and search AutoPlay in the top-right searchbar.
5. Select AutoPlay, navigate to "Removable Drives" and select "Take no action".
6. Click Save in the bottom-right and close the window.
7. Change the "C:\YourPath\TotheExecutable\executable.exe" in the tag
    ```xml
    <Arguments>/c "C:\YourPath\TotheExecutable\executable.exe" adminPassword</Arguments>
    ```
    to the path to your executable (including the filename and extension), and change "adminPassword" to your preferred adminPassword.
    Additionally, change the C:\YourPath\TotheExecutable in the tag
    ```xml
    <WorkingDirectory>C:\YourPath\TotheExecutable</WorkingDirectory>
    ```
    to point towards the directory of the executable you wish to run.
##### Option 1 (Task Scheduler GUI)
8. Import the Task Scheduler Task "runInputChecker.xml" into Task Scheduler.
##### Option 2 (Powershell)
8. Change the name of "runInputChecker.xml" to whatever you want (optional).
9. Run the command:  
    `schtasks.exe /Create /XML C:\runInputChecker.xml /tn "Event Viewer Tasks\taskname"`  
    in Powershell, where "runInputChecker.xml" is used to detect the usb flash drive insert event, and where taskname is the name you wish to have for the task. After which, your task should be viewable in the Task Scheduler folder "Event Viewer Tasks".

#### (Linux) UNFINISHED
1. Install Python=>3.10.4
2. Install pip  
    `sudo apt install python3-pip`
3. Install pyinstaller  
    `pip3 install pyinstaller`
4. Install bin-utils  
    `sudo apt install binutils`
5. Install libc-bin  
    `sudo apt install libc-bin`
6. Run PyInstaller command to build your current directory, making an executable from argument [1]   
    For Linux if the file you want to run is inputChecker.py (it is):  
    `python3 -m PyInstaller main.py`  

### Flash Drive Setup
#### (Windows and Linux)
1. Ensure a file exists on the flash drive in the root named processes.txt (i.e. D:\\processes.txt)