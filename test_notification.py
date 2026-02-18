
import smtplib
import mysql.connector
from email.message import EmailMessage
from datetime import datetime

# SQL DATABASE CONNECTION
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="6172BBbb!",
    database="property_value_billing"
)
cursor = conn.cursor()

# Get today's billing
billing_date = datetime.now().date()
query = "SELECT * FROM billing WHERE billing_date = %s"
cursor.execute(query, (billing_date,))

row = cursor.fetchone()

if row:
    bill_id = row[0]        # optional, if needed
    bill = row[1]
    property_id = row[2]

    # Get property info
    query = "SELECT owner_id, digital_address FROM properties WHERE property_id = %s"
    cursor.execute(query, (property_id,))
    row = cursor.fetchone()
    if row:
        owner_id, address = row

        # Get owner contact
        query = "SELECT email, first_name, last_name FROM contacts WHERE owner_id = %s"
        cursor.execute(query, (owner_id,))
        row = cursor.fetchone()
        if row:
            email, first_name, last_name = row

            # Email details
            sender_email = "fhblay12@gmail.com"
            receiver_email = email
            app_password = "gtku qbcz mdgg brqh"
            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = "Property Billing Notification"
            msg.set_content(
                f"Dear {first_name} {last_name},\n\n"
                f"You have a bill of ${bill} for one of your properties at the address {address}.\n"
                "Pay at our website using the link below."
            )

            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)

            print("Email sent successfully!")
else:
    print("No billing found for today.")

cursor.close()
conn.close()