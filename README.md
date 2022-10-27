# FinalProject
This is my final project for CIS-573

## Steps to Run:
#### (Platform)

### Development (Devs Only)
#### (Windows)
1. Install Python=>3.10.4
2. Install pyinstaller with pip
    python -m pip install pyinstaller
3. Run pyInstaller command to build your current directory, making an executable from argument [1]
    {::comment}For Windows if the file you want to run is main.py{:/comment}
    pyInstaller main.py
#### (Linux)
1. Install Python=>3.10.4
2. Install pip
    sudo apt install python3-pip
3. Install pyinstaller
    pip3 install pyinstaller
4. Install bin-utils
    sudo apt install binutils
5. Install libc-bin
    sudo apt install libc-bin
6. Run PyInstaller command to build your current directory, making an executable from argument [1]
    {::comment}For Linux if the file you want to run is main.py{:/comment}
    python3 -m PyInstaller main.py

### Execution
#### (Windows)
1. Go to the directory where your executable program was created (usually somwhere in the directory of your project, if you are a dev i.e. /dist/main/ if your python file was called main.py)
2. Enter the command below in the terminal, allowing for new db admin password if one wishes to change it
    {::comment}For Windows if the file you want to run is called main.exe and one wishes to change the admin password to blueberry{:/comment}
    main.exe blueberry
#### (Linux)
1. Go to the directory where your executable program was created (usually somewhere in the directory of your project, if you are a dev i.e. ./dist/main/ if your python file was called main.py)
2. Enter the command below in the terminal, allowing for new db admin password if one wishes to change it
    {::comment}For Linux if the file you want to run is called main and one wishes to change the admin password to blueberry{:/comment}
    ./main blueberry