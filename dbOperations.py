import sqlite3
def createDB():
    sqliteConnection = sqlite3.connect('sql.db')
    cursor = sqliteConnection.cursor()
    print('DB Init')

def createConnection(dbName):
    sqliteConnection = sqlite3.connect(f"{dbName}")

createDB()