import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime
import logging
import os

# Setup logging
logging.basicConfig(
    filename='storage_notification.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Email credentials (⚠️ move to environment variables for security)
EMAIL_ADDRESS = '223110730@gehealthcare.com'
EMAIL_PASSWORD = 'emeralds@2156E'

# Load Excel file
excel_file = r'C:\Users\223110730\Box\AME Lab Management System\AME Lab Management System.xlsm'

print("Checking if file exists...")
print("File exists:", os.path.exists(excel_file))
print("Absolute path:", os.path.abspath(excel_file))

if not os.path.exists(excel_file):
    logging.error(f"Excel file '{excel_file}' not found.")
    raise FileNotFoundError(f"Excel file '{excel_file}' not found.")

print("Reading Excel file...")
try:
    df = pd.read_excel(excel_file, engine='openpyxl')
    print("Excel file loaded successfully.")
except Exception as e:
    logging.error(f"Failed to read Excel file: {e}")
    raise

# Ensure required columns exist
required_columns = {'Storage-Date Out', 'Email ID'}
print("Checking required columns...")
if not required_columns.issubset(df.columns):
    logging.error(f"Missing required columns in Excel file. Required: {required_columns}")
    raise ValueError("Excel file missing required columns.")
print("Required columns found.")

# Remove rows where required columns are empty
print("Removing empty rows...")
df = df.dropna(subset=['Storage-Date Out', 'Email ID'], how='any')
print(f"Rows after removing empty: {len(df)}")

# Get today's date
today = datetime.today().date()
print("Today's date:", today)

# Filter rows where 'Storage-Date Out' matches today
print("Filtering rows with today's storage date...")
df['Storage-Date Out'] = pd.to_datetime(df['Storage-Date Out'], errors='coerce').dt.date
due_rows = df[df['Storage-Date Out'] == today]
print(f"Rows due today: {len(due_rows)}")

# Send emails
for index, row in due_rows.iterrows():
    recipient = row.get('Email ID')
    print(f"Processing row {index} for recipient: {recipient}")

    if pd.isna(recipient) or not isinstance(recipient, str):
        logging.warning(f"Skipping row {index} due to invalid email address.")
        print(f"Skipped row {index} due to invalid email.")
        continue

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Storage Date Reached'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg.set_content(f"""
Hello,

This is a reminder that the storage date for your item has been reached today ({today}).

Please take necessary action.

Regards,
Automated Notification System
""")

        print(f"Connecting to SMTP server for {recipient}...")
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logging.info(f"Email sent to {recipient} for row {index}.")
        print(f"Email sent to {recipient}.")

    except Exception as e:
        logging.error(f"Failed to send email to {recipient} for row {index}: {e}")
        print(f"Failed to send email to {recipient}: {e}")