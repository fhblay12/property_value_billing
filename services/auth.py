class Login:
    def __init__(self, db):
        self.db = db
    def login(self, last_name, password):

        row = self.db.execute(
            """
            SELECT owner_id
            FROM contacts
            WHERE email = %s AND password = %s
            """,
            (last_name, password), True
        )
        type="owner"
        print(row)
        if row == None:
        # Try admin login
            row = self.db.execute(
                """
                SELECT admin_login_id
                FROM admin_login
                WHERE admin_username = %s AND admin_password = %s
                """,
                (last_name, password), True
            )
            type="admin"
        # Try admin login
            if row== None:
                row= self.db.execute(
                """
                SELECT collector_id_code
                FROM collectors
                WHERE collector_id_code = %s AND collector_password = %s AND at_work = 1
                """,
                (last_name, password), True
            )
                type="collector"
        return row, type