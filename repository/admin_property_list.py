class Admin_property_list_repository:

        def __init__(self, db):
            self.db = db
            self.base_query = """SELECT p.*, b.has_been_paid
            FROM properties p
            JOIN billing b ON p.property_id = b.property_id
            """

        def base_query(self, query):
            return self.db.execute(query, fetchall=True)
            

        def build_property_filters(q: str | None, city: str | None, category: int | None, has_been_paid: int | None):
            """
            Returns:
                conditions: list of SQL WHERE clauses
                params: list of parameter values
            """
            conditions = []
            params = []

            if q:
                conditions.append("(p.property_id LIKE %s OR p.city LIKE %s OR p.digital_address LIKE %s OR p.description LIKE %s)")
                search = f"%{q}%"
                params.extend([search, search, search, search])

            if city:
                conditions.append("p.city LIKE %s")
                params.append(f"%{city}%")

            if category:
                conditions.append("p.category_id = %s")
                params.append(category)

            if has_been_paid in ("0", "1"):
                conditions.append("b.has_been_paid = %s")
                params.append(has_been_paid)

            return conditions, params