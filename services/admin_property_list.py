from repository.admin_property_list import Admin_property_list_repository
class Admin_property_list_service:

        def __init__(self, db, Admin_property_list_repository):
            self.db = db
            self.base_query = Admin_property_list_repository.base_query

        def apply_conditions(self, q: str | None, city: str | None, category: int | None, has_been_paid: int | None):
            conditions, params = Admin_property_list_repository.build_property_filters(q, city, category, has_been_paid)
            base_query = self.base_query
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            return self.db.execute(base_query, tuple(params), fetchall=True)
                