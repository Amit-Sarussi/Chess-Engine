import sqlite3

class SQL:
    """A simple wrapper for SQLite database operations."""

    def __init__(self, db_path):
        """Initializes the SQLite wrapper with the database path."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_db()
    
    def __del__(self):
        self.disconnect()
    
    def init_db(self, db_path="scoreboard.db"):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scoreboard (
                board TEXT PRIMARY KEY,
                avg_score REAL,
                count INTEGER
            )
        """)
        self.conn.commit()

    def connect(self):
        """Connects to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None

    def disconnect(self):
        """Disconnects from the SQLite database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute(self, query, params=None):
        """Executes an SQL query."""
        if self.cursor:
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return self.cursor
            except sqlite3.Error as e:
                print(f"Error executing query: {e}")
                return None
        else:
            print("Database connection is not established.")
            return None

    def fetchone(self):
        """Fetches a single row from the result set."""
        if self.cursor:
            return self.cursor.fetchone()
        else:
            return None

    def fetchall(self):
        """Fetches all rows from the result set."""
        if self.cursor:
            return self.cursor.fetchall()
        else:
            return None

    def commit(self):
        """Commits the current transaction."""
        if self.conn:
            try:
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error committing transaction: {e}")

    def rollback(self):
        """Rolls back the current transaction."""
        if self.conn:
            try:
                self.conn.rollback()
            except sqlite3.Error as e:
                print(f"Error rolling back transaction: {e}")