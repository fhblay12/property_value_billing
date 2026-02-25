from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, UploadFile, File
from typing import Optional



class Property_service:

        def __init__(self, db):
            self.db = db
            self.BILLING_MULTIPlIER = 0.001

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
            monthly_bill=property_value*self.BILLING_MULTIPlIER
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

        async def add_property_files(self, property_id, image1, image2, image3, image4, document1, document2, document3, document4):
            files_to_insert = []
            created_time = datetime.now()

            # ---- Images (filetype_id = 1) ----
            for img in [image1, image2, image3, image4]:
                if img.filename:
                    file_bytes = await img.read()
                    files_to_insert.append(
                        (property_id, file_bytes, img.filename, 1, created_time)
                    )

            # ---- Documents (filetype_id = 2) ----
            for doc in [document1, document2, document3, document4]:
                if doc.filename:
                    file_bytes = await doc.read()
                    files_to_insert.append(
                        (property_id, file_bytes, doc.filename, 2, created_time)
                    )

            sql = """
                INSERT INTO files
                (property_id, file_data, filename, filetype_id, created_datetime)
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db.executemany(sql, files_to_insert)