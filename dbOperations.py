import sqlite3
from datetime import datetime
import base64

# Initializes connection and tables of db, or creates db if it doesn't exist
def initDB(dbName):
    sqliteConnection = createConnection(dbName)
    cursor = sqliteConnection.cursor()
    print("DB Created")
    initTables(cursor)
    return cursor

# Creates connection to sql database of name dbName
def createConnection(dbName):
    return sqlite3.connect(f"{dbName}")
    print("Connection Created")

# Creates tables if they do not exist
def initTables(cursor):
    tables = [["Events",""" CREATE TABLE Events (
            Name VARCHAR(255) NOT NULL,
            Type VARCHAR(255) NOT NULL,
            eventDateTime DATETIME NOT NULL
        ); """],
            ["Authkeys",""" CREATE TABLE Authkeys (
                Name VARCHAR(255) NOT NULL,
                key VARCHAR(255) NOT NULL,
                registeredDateTime DATETIME NOT NULL
            ); """]]
    for i in tables:
        try:
            cursor.execute(i[1])
            print(f"{i[0]} table created!")
        except:
            continue
    print("All Tables created!")

# Searches Authkeys database for currently plugged in drive
def findDrive(cursor, name):
    drive = cursor.execute(f""" SELECT * from Authkeys WHERE Name = '{name}';""").fetchone()
    print(drive)
    if drive:
        return True
    return False

# Authenticate Drive
def authenticateDrive(cursor, name, key):
    auth = cursor.execute(f""" SELECT * from Authkeys WHERE Name = '{name}' and key = '{key}'""").fetchone()
    if auth:
        return True
    else:
        return False

# Adds Drive to AuthKeys table if password correct
def insertDrive(cursor, name, keyDT = datetime.now().strftime("%Y-%m-%d %I:%M:%S")):
    keyUnEncoded = name + "_" + keyDT
    encodedKey = keyUnEncoded.encode("ascii")
    base64KeyBytes = base64.b64encode(encodedKey)
    base64KeyString = base64KeyBytes.decode("ascii")
    key = base64KeyString
    cursor.execute(f""" INSERT INTO Authkeys (Name,key,registeredDateTime) VALUES ('{name}','{key}','{keyDT}');""")
    return key

dbName = "sql.db"
initDB(dbName)