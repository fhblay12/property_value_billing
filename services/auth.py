from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


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

        login_details = (row, type)
        if login_details[1]=="owner":
            owner_id = login_details[0][0]
            return RedirectResponse(
                url=f"/propertylist/{owner_id}",
                status_code=303
            )
        if login_details[1]=="admin":
            admin_id = login_details[0][0]
            return RedirectResponse(
                url=f"/admin/{admin_id}",
                status_code=303
            )

        if login_details[1]=="collector":
            collector_id = login_details[0][0]
            return RedirectResponse(
                url=f"/collector-home/{collector_id}",
                status_code=303
            )

        # If neither matched
        return RedirectResponse(
            url="/login?error=Invalid credentials",
            status_code=303
        )


     