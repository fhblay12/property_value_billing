import mysql.connector
from email.message import EmailMessage
from datetime import datetime
from dateutil.relativedelta import relativedelta

# SQL DATABASE CONNECTION
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="6172BBbb!",
    database="property_value_billing"
)
cursor = conn.cursor()
property_id=3
monthly_bill=500
created_time=datetime.now()
five_minutes_later = created_time + relativedelta(minutes=2)
sql3 = """
            INSERT INTO test_billing
            (property_id, monthly_bill, billing_date)

            VALUES (%s, %s, %s)
    """

values3 = (
    property_id,
    monthly_bill,
    five_minutes_later
)
cursor.execute(sql3, values3)
conn.commit()
print("success")