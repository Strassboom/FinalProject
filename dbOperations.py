from getpass import getpass
import sqlite3
from datetime import datetime
import base64

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

# Searches Authkeys database for currently plugged in drive
def findDrive(conn, name):
    drive = conn.execute(f""" SELECT * from Authkeys WHERE Name = '{name}';""").fetchone()
    if drive:
        return True
    return False

# Authenticate Drive
def authenticateDrive(conn, name, key):
    auth = conn.execute(f""" SELECT * from Authkeys WHERE Name = '{name}' and key = '{key}'""").fetchone()
    if auth:
        return True
    else:
        return False

def createAuthKey(name, keyDT = datetime.now().strftime("%Y-%m-%d %I:%M:%S")):
    keyUnEncoded = name + "_" + keyDT
    encodedKey = keyUnEncoded.encode("ascii")
    base64KeyBytes = base64.b64encode(encodedKey)
    return base64KeyBytes.decode("ascii")

def getAuthKey(conn, name):
    return conn.execute(f""" SELECT key FROM Authkeys WHERE Name = '{name}';""").fetchone()[0]

# Adds Drive to AuthKeys table if password correct
def insertDrive(conn, name, keyDT = datetime.now().strftime("%Y-%m-%d %I:%M:%S")):
    key = createAuthKey(name, keyDT)
    conn.execute(f""" INSERT INTO Authkeys (Name,key,registeredDateTime) VALUES ('{name}','{key}','{keyDT}');""")
    return key

def getAdminPassword(conn):
    authPassword = conn.execute(f""" SELECT key from Authkeys WHERE Name = 'ADMIN'""").fetchone()[0]
    return authPassword

def adminAuth(conn,password):
    findDrive(conn,'ADMIN')
    return getAdminPassword(conn) == password

def getAllAuthKeys(conn):
    return conn.execute(f""" SELECT * FROM Authkeys;""").fetchall()

# dbName = "sql.db"
# conn = initDB(dbName)
# print(conn.execute(f""" SELECT * FROM Authkeys;""").fetchall())
#print(findDrive(conn,"D:"))
#adminAuth(initDB(dbName),"bubblegum")