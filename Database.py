import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="6172BBbb!",
            database="property_value_billing"
        )
    def execute(self, query, params=None, fetchone=False, fetchall=False):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute(query, params or())

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        self.conn.commit()
        cursor.close()
        return result
