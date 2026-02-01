import sqlite3

class Database_connection:
    def __init__(self, db_path=None):
        from Globals import Globals
        self.connection = None
        self.db_path = db_path if db_path is not None else Globals.DB_PATH
    def connect(self):
        """Establish a connection to the SQLite database."""
        self.db_path = self.db_path
        try:
            self.connection = sqlite3.connect(self.db_path)
            print("Connected to database")
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
    def disconnect(self):
        """Close the connection to the SQLite database."""
        if self.connection:
            try:
                self.connection.close()
                print("Disconnected from database")
            except sqlite3.Error as e:
                print(f"An error occurred while disconnecting from the database: {e}")
        else:
            print("No active database connection to disconnect")
    def query(self, query, params=None):
        self.connect()
        """Execute a query on the SQLite database."""
        if not self.connection:
            print("No active database connection")
            return None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        except sqlite3.Error as e:
            print(f"An error occurred while executing the query: {e}")
            return None
        result = None
        first_word = query.strip().split()[0].upper()
        if first_word == "SELECT":
            result = cursor.fetchall()
        elif first_word == "INSERT":
            try:
                self.connection.commit()
                result = cursor.lastrowid
            except sqlite3.Error as e:
                print(f"An error occurred while committing the transaction: {e}")
                result = None
        else:
            try:
                self.connection.commit()
                result = cursor.rowcount
            except sqlite3.Error as e:
                print(f"An error occurred while committing the transaction: {e}")
                result = None
        self.disconnect()
        return result
    
    def get_last_inserted_id(self):
        """Get the ID of the last inserted row."""
        self.connect()
        if not self.connection:
            print("No active database connection")
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            last_id = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving the last inserted ID: {e}")
            last_id = None
        self.disconnect()
        return last_id
    


