#!/usr/bin/env python
# coding: utf-8

# In[32]:


import requests as r
import pyodbc as p
import schedule
import time
import logging as l


# In[33]:


# NOTE: ensure the server/database names are correct on your machine
conn = p.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-HGTC7MT;'           # e.g. DESKTOP-XYZ\\SQLEXPRESS if you use an instance
    'DATABASE=QUOTESUBSCRIBERS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()
print("Connected to SQL Server")


# In[34]:


def get_users(): 
    cursor.execute("SELECT Name, EmailAddress FROM users WHERE SubscriberStatus = 1")
    return cursor.fetchall()
print(f"{len(get_users())} users found") 


# In[35]:


def send_daily_quotes():
    users = get_users()
    print(f"Sending Quotes to {len(users)} users ....\n")

    for user in users:
        name = user[0]
        email = user[1]
        quote = get_random_quotes()   # one random quote per user
    
        if quote:
            email_body = f"Hello {name},\n\nHere’s your Daily Quote:\n{quote}\n\nHave a great day!\n\n– Daily Quotes Bot"
            send_email(email, "Your Daily Quote", email_body)
        else:
            print(f"Could not fetch quote for {name}.")
    print("All quotes sent for today!\n")


# In[36]:


l.basicConfig(
    filename="logs/quotelogs.log",
    level=l.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
console_handler=l.StreamHandler()
console_handler.setLevel(l.INFO)
formatter=l.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
l.getLogger().addHandler(console_handler)

logger = l.getLogger(__name__)
logger.info("Run Started")


# In[37]:


def get_random_quotes(): 
    try: 
        l.info("Fetching random quote from API...")
        url = "https://zenquotes.io/api/random"
        response = r.get(url, timeout=10)

        # Check for bad response
        if response.status_code != 200:
            l.warning(f"Error {response.status_code}")
            return None  

        data = response.json()

        # Validate JSON structure
        if not isinstance(data, list) or len(data) == 0:
            l.warning("Response malfunction: not a list or empty response.")
            return None

        Quote = data[0].get("q")
        Author = data[0].get("a")

        # Validate quote content
        if Quote:
            return f'"{Quote}" - {Author}'
        else:
            l.warning("API returned incomplete quote data.")
            return None

    except r.exceptions.Timeout:
        l.error("Request timed out.")
        return None
    except r.exceptions.HTTPError as errh:
        l.error(f"HTTP error: {errh}")
        return None
    except Exception as e:
        l.error(f"Unexpected error fetching quote: {e}")
        return None


# In[38]:


# email_utils.py
import os, smtplib as s, logging as l
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")


# In[31]:


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with s.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        l.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        l.error(f"Error sending email: {e}")
        return False

