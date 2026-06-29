class Admin_home_repository:

        def __init__(self, db):
            self.db = db

        def get_category_counts(self):
            category_ids=self.db.execute("SELECT category_id, COUNT(*) FROM properties GROUP BY category_id", fetchall=True)
            return category_ids
        
        def get_city_counts(self):
            city_counts=self.db.execute("SELECT city, COUNT(*) FROM properties GROUP BY city", fetchall=True)
            return city_counts
        

        def property_count_today(self):
             return self.db.execute(
                """SELECT COUNT(*)
                FROM
                properties
                WHERE
                created_datetime = CURDATE()""", fetchall=True
                )[0][0]
        
        def contact_count_today(self):
             return self.db.execute(
                """SELECT COUNT(*)
                FROM
                contacts
                WHERE
                created_datetime = CURDATE()""", fetchall=True
                )[0][0]
        
        def property_count(self):
             return self.db.execute(
            """SELECT COUNT(*)
            FROM
            properties
            """, fetchall=True
            )[0][0]
        
        def expected_monthly_revenue(self):
             return self.db.execute(
        """SELECT SUM(monthly_bill) AS total
            FROM billing
        """, fetchall=True
        )[0][0]

        def total_revenue_collected(self):
            return self.db.execute(
            """SELECT SUM(monthly_bill) AS total
                FROM billing
                WHERE has_been_paid = 1
            """, fetchall=True
        )[0][0]


        def revenue_by_payment_date(self):
           return self.db.execute("""
            SELECT payment_date, SUM(monthly_bill) AS total_revenue
            FROM billing
            WHERE has_been_paid = 1
            GROUP BY payment_date
            ORDER BY payment_date
        """, fetchall=True)