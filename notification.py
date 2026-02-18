



import smtplib
import mysql.connector
import time
from email.message import EmailMessage
from datetime import datetime

CHECK_INTERVAL = 5  # seconds (REALISTIC)
processed_bills = set()


def send_email(email, first_name, last_name, bill, address):
    sender_email = "fhblay12@gmail.com"
    app_password = "gtku qbcz mdgg brqh"

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = "Property Billing Notification"
    msg.set_content(
        f"Dear {first_name} {last_name},\n\n"
        f"You have a bill of ${bill} for your property at {address}.\n\n"
        "Please pay via our website.\n\n"
        "Thank you."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)


def main():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="6172BBbb!",
        database="property_value_billing",
        autocommit = True

    )


    print("Billing service started...")

    while True:
        cursor = conn.cursor()
        try:
            now = datetime.now()

            cursor.execute(
                "SELECT * FROM billing WHERE billing_date <= %s",
                (now,)
            )
            bills = cursor.fetchall()
            print(bills)
            for row in bills:
                bill_id = row[0]
                bill = row[1]
                property_id = row[2]

                if bill_id in processed_bills:
                    continue

                cursor.execute(
                    "SELECT owner_id, digital_address FROM properties WHERE property_id = %s",
                    (property_id,)
                )
                prop = cursor.fetchone()
                if not prop:
                    continue

                owner_id, address = prop

                cursor.execute(
                    "SELECT email, first_name, last_name FROM contacts WHERE owner_id = %s",
                    (owner_id,)
                )
                contact = cursor.fetchone()
                if not contact:
                    continue

                email, first_name, last_name = contact

                send_email(email, first_name, last_name, bill, address)

                processed_bills.add(bill_id)
                print(f"Email sent to {email}")

        except Exception as e:
            print("Error:", e)
        finally:
            cursor.close()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
