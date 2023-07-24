from aifc import Error
import sqlite3

class db_config():

    def connect_db(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def disconnect_db(conn:sqlite3.Connection):
        try:
            conn.close
            return conn
        except Error as e:
            print(e)
        return conn


    def create_table(conn, table):
        try:
            c = conn.cursor()
            c.execute(table)
        except Error as e:
            print(e)


    def main():
        database = r"C:\sqlite\db\lpp-database.db"

        actions_table = """ 
        CREATE TABLE IF NOT EXISTS actions (
            [correlationId] INTEGER PRIMARY KEY, 
            [deviceType] TEXT,
            [deviceId] TEXT,
            [checkTime] TIMESTAMP,
            [checkDuration] TIMESTAMP,
            [actionTime] TIMESTAMP,
            [light] TEXT,
            [volume] INT,
            [reason] TEXT
            ); """

        actions_epc_table = """
        CREATE TABLE IF NOT EXISTS tasks (
            FOREIGN KEY (epc_id) REFERENCES actions (correlationId)
            [epc] TEXT
            );"""

        conn = db_config.connect_db(database)

        if conn is not None:
            db_config.create_table(conn, actions_table)
            db_config.create_table(conn, actions_epc_table)
        else:
            print("Error! cannot create the database connection.")

        db_config.disconnect_db

    if __name__ == '__main__':
        main()

