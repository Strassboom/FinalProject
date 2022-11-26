# FinalProject
This is my final project for CIS-573

## Steps to Run:
#### (Platform)

### Development (Devs Only)
#### Both Listed Platforms
1. Ensure a file exists on your flash drive in the root named processes.txt (i.e. D:\\processes.txt)  
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
7. Change the "C:\YourPath\TotheExecutable\executable.exe" and "C:\YourPath\TotheExecutable" in the tag
    ```xml
    <Arguments>/c "C:\YourPath\TotheExecutable\executable.exe" "C:\YourPath\TotheExecutable" adminPassword</Arguments>
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

#### (Linux)
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
7. Run the command:



location="/path/to/FinalProject"; nohup watch -n seconds $location/linuxFindDrives.sh $location executable sudoPassword >/dev/null 2>/dev/null & echo $! > "$location/file_to_save_pid_to.txt" ; line=$(head -n 1 "$location/file_to_save_pid_to.txt") ; disown -h $line

where /path/to/FinalProject is the path to the FinalProject directory (INCLUDING FinalProject), seconds is the number of seconds after which you would like to repeatedly check again for flash drives, executable is the name of the executable (usually inputChecker), sudoPassword is your sudo Password, and file_to_save_pid_to.txt is the filename you want the program's process id saved to.
EXAMPLE: 

location="/home/strassboom/Documents/FinalProject"; nohup watch -n 10 $location/linuxFindDrives.sh $location inputChecker Honda#1954 >/dev/null 2>/dev/null & echo $! > "$location/kill_me.txt" ; line=$(head -n 1 "$location/kill_me.txt") ; disown -h $line

8. Memorize where file_to_save_pid_to.txt is, or the integer printed to the terminal after the command is finished running.
9. Close the terminal window with the x button.
10. You are Done.

### Stopping the Program
#### (Windows)
1. Go to task Scheduler, and right click the task, and click disable task. To delete the program you may simply delete the folder where FinalProject is saved, and the task in Task Scheduler you created.

#### (Linux)
1. I you would like to just kill the entire program, open a terminal window, and type the command "kill x" where x is the process id you saved earlier that was printed in the earlier terminal window.
2. To delete the program you may simply delete the folder where FinalProject is saved, and perform step 1 if you have not already.
3. If you are unsure if there are more instances of the watch command running, display all process in the terminal with the command "ps -ef".