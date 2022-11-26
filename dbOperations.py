import sqlite3
from datetime import datetime
import hashlib

# Initializes connection and tables of db, or creates db if it doesn't exist
def initDB(dbName,authPassword=''):
    conn = createConnection(dbName)
    print("DB Created")
    initTables(conn)
    if findDrive(conn,'ADMIN') is False:
        if authPassword == '':
            authPassword = 'adminPassword'
        dtnow = datetime.now().strftime("%Y-%m-%d %I:%M:%S")
        conn.execute(f""" INSERT INTO Authkeys (Name,key,registeredDateTime) VALUES ('ADMIN','{authPassword}','{dtnow}');""")
    elif authPassword != '' and getAdminPassword(conn) != authPassword:
        dtnow = datetime.now().strftime("%Y-%m-%d %I:%M:%S")
        conn.execute(f""" UPDATE Authkeys SET key = '{authPassword}', registeredDateTime = '{dtnow}' WHERE Name = 'ADMIN';""")
    return conn

# Creates connection to sql database of name dbName
def createConnection(dbName):
    return sqlite3.connect(f"{dbName}")

# Creates tables if they do not exist
def initTables(conn):
    tables = [["Events",""" CREATE TABLE IF NOT EXISTS Events (
            Name VARCHAR(255) NOT NULL,
            Type VARCHAR(255) NOT NULL,
            eventDateTime DATETIME NOT NULL
        ); """],
            ["Authkeys",""" CREATE TABLE IF NOT EXISTS Authkeys (
                Name VARCHAR(255) UNIQUE NOT NULL,
                key VARCHAR(255) NOT NULL,
                registeredDateTime DATETIME NOT NULL
            ); """]]
    for i in tables:
        try:
            conn.execute(i[1])
            print(f"{i[0]} table created!")
        except:
            continue
    print("All Tables created!")

# Searches Authkeys database for currently plugged in drive of name name
def findDrive(conn, name):
    drive = conn.execute(f""" SELECT * from Authkeys WHERE Name = '{name}';""").fetchone()
    if drive:
        return True
    return False

# Authenticate Drive of name name and with key key
def authenticateDrive(conn, name, hashInput):
    key = createAuthKey(name, hashInput)
    auth = conn.execute(f""" SELECT * from Authkeys WHERE Name = '{name}' and key = '{key}'""").fetchone()
    if auth:
        return True
    else:
        return False

# Create Auth Key for drive of name name
def createAuthKey(name, hashInput):
    unencodedKey = name + hashInput
    encodedKey = hashlib.md5(unencodedKey.encode()).hexdigest()
    return encodedKey

# Updates Existing Drive in AuthKeys table if password correct
def updateDrive(conn, name, hashInput):
    keyDT = datetime.now().strftime("%Y-%m-%d %I:%M:%S")
    key = createAuthKey(name, hashInput)
    conn.execute(f""" UPDATE Authkeys SET key = '{key}', registeredDateTime = '{keyDT}' WHERE name = '{name}';""")

# Adds Drive to AuthKeys table if password correct
def insertDrive(conn, name, hashInput):
    keyDT = datetime.now().strftime("%Y-%m-%d %I:%M:%S")
    key = createAuthKey(name, hashInput)
    conn.execute(f""" INSERT INTO Authkeys (Name,key,registeredDateTime) VALUES ('{name}','{key}','{keyDT}');""")

# Retrieve Admin Password
def getAdminPassword(conn):
    authPassword = conn.execute(f""" SELECT key from Authkeys WHERE Name = 'ADMIN'""").fetchone()[0]
    return authPassword

# Check input against Admin Password
def adminAuth(conn,password):
    findDrive(conn,'ADMIN')
    return getAdminPassword(conn) == password
