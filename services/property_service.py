from datetime import datetime
from dateutil.relativedelta import relativedelta

from main import BILLING_MULTIPlIER


class Property_service:
        BILLING_MULTIPlIER=0.001
        def __init__(self, db):
            self.db = db

        def create_contact(self, first_name, last_name, phone_number, email, password):
            created_time = datetime.now()
            sql = """
                   INSERT INTO contacts
                   (first_name, last_name, phone_number, email, created_datetime, updated_datetime, password)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   """

            values = (
                first_name,
                last_name,
                phone_number,
                email,
                created_time,
                created_time,
                password
            )
            owner_id = self.db.execute(sql, values)
            return owner_id
        def create_property(self, owner_id, category, value, longitude, latitude, city, property_value, digital_address, description):
                created_time = datetime.now()

                sql = """
                   INSERT INTO properties
                   (owner_id, category_id, property_value, longitude, latitude, city, digital_address, description, created_datetime)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   """
                values = (
                    owner_id,
                    category,
                    property_value,
                    longitude,
                    latitude,
                    city,
                    digital_address,
                    description,
                    created_time
                )
                owner_id = self.db.execute(sql, values)
                self.create_monthly_bill(owner_id, value, created_time)
                return owner_id

        def create_monthly_bill(self, property_id, property_value, created_time):
            monthly_bill=property_value*BILLING_MULTIPlIER
            one_month_later = created_time + relativedelta(months=1)
            sql = """
                    INSERT INTO billing
                    (property_id, monthly_bill, created_datetime, billing_date)

                    VALUES (%s, %s, %s, %s)
            """

            values = (
                property_id,
                monthly_bill,
                created_time,
                one_month_later
            )
            self.db.execute(sql, values)