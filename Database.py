import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )

    def execute(self, query, params=None, fetchone=False, fetchall=False):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute(query, params or ())

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid

        self.conn.commit()
        cursor.close()
        return result

    def executemany(self, query, params_list):
        cursor = self.conn.cursor(buffered=True)
        cursor.executemany(query, params_list)
        self.conn.commit()
        cursor.close()
        return cursor.rowcount
