import os
import mysql.connector
from dotenv import load_dotenv
import time

load_dotenv()


class Database:
    def __init__(self):
        retries = 5
        for i in range(retries):
            try:
                self.conn = mysql.connector.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    database=os.getenv("MYSQL_DATABASE")
                )
                break
            except mysql.connector.errors.DatabaseError as e:
                if i < retries - 1:
                    print(f"Database not ready, retrying in 5 seconds... ({i+1}/{retries})")
                    time.sleep(5)
                else:
                    raise e
                
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
