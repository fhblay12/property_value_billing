
class Admin_contact_list_repository:

        def __init__(self, db):
            self.db = db

        def get_contact_query(self, search: str | None,):
              return self.db.execute("""
                SELECT * FROM contacts WHERE  (
                      first_name LIKE %s
                      OR last_name LIKE %s
                      OR phone_number LIKE %s

                    ) 
        """, (search, search, search), fetchall=True
                       )
              
        def get_contacts(self):
            return self.db.execute("""
                SELECT * FROM contacts 
        """, fetchall=True
                       )