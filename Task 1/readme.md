## CREATE DATABASE FOR SUBSCRIBERS
	
	CREATE DATABASE QUOTESUBSCRIBERS

	USE QUOTESUBSCRIBERS
	
	CREATE TABLE users (
	UserID INT identity(1,1) PRIMARY KEY, 
	EmailAddress NVARCHAR(50) NOT NULL, 
	[Name] NVARCHAR(50) NOT NULL, 
	SubscriberStatus BIT DEFAULT 1,
	EmailFrequency NVARCHAR(50) CHECK(EmailFrequency IN ('Weekly', 'Daily'))
	)

	INSERT INTO users (EmailAddress, [Name], SubscriberStatus, EmailFrequency)
	VALUES
	('katechisom072@gmail.com', 'Kate Chisom', 1, 'Daily'),
	('sligoemy@gmail.com', 'Emmanuel Anamelechi', 1, 'Daily'),
	('adeboladesoyin@gmail.com', 'Adebola Adesoyin', 1, 'Daily'),
	('faruksedik@yahoo.com', 'Faruk Sedik', 1, 'Daily'),
	('kabirolawalemohammed@gmail.com', 'Kabir Olawale Mohammed', 1, 'Daily'),
	('iakinyele3@gmail.com', 'Ibrahim Akinyele', 1, 'Daily');

		


## CREATE DATABASE FOR QUOTES SENT
	
	CREATE TABLE quotes (
	ID INTEGER IDENTITY(1,1) PRIMARY KEY, 
	Quote NVARCHAR(MAX) NOT NULL, 
	Author NVARCHAR(70), 
	[DATETIME] DATETIME
	)

Subscribers database holds the data for subscribers while the quotes table holds quotes as sent to the subscribers.

### Importing Libraries

	import requests as r
	import pyodbc as p
	import schedule
	import time
	import logging as l
	import os, smtplib as s, 
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	from dotenv import load_dotenv

"Requests" will help us pull quotes from the Zenquotes
"pyodbc" will help us connect to users from the subscribers database whose status are marked 1 = Active
"schedule" will help us schedule time when  the entire  task of pulling users and sending personalized quotes will be perform 
"logging" helps to create logged where error/success messages are recorded.
"os" helps the interaction of operating systems like accessing system infrmation, managing files and directory and handling environment variables. 
"smtplib" Stands for Simple Mail Transfer Protocol. This library would be send quotes as email to users. 
"MIMeText" helps with formatting emails to plain text. This also allows the use of attachments and multimedia with emails.
"dotenv" this helps to store email credentials securely and as well keep them out of the main codes/scripts.



	conn = p.connect(
	    'DRIVER={SQL Server};'
	    'SERVER=DESKTOP-HGTC7MT;'           
	    'DATABASE=QUOTESUBSCRIBERS;'
	    'Trusted_Connection=yes;'
	)
	cursor = conn.cursor()
	print("Connected to SQL Server")

### Fetching Users into Python Environment

	def get_users(): 
    		cursor.execute("SELECT Name, EmailAddress FROM users WHERE SubscriberStatus = 1")
    		return cursor.fetchall()
	print(f"{len(get_users())} users found") 			

This function will fetch Subcribers from the users table whose status are currently "Active"

### Sending email on the mail list.

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

This function automates the process of sending quotes to each users on the users table


        def send_daily_quotes():
    		users = get_users()
    		print(f"Sending Quotes to {len(users)} users ....\n")
 		
This part returns the list of users. 

    for user in users:
        name = user[0]
        email = user[1]
        quote = get_random_quotes()   # one random quote per user

This parts loop through the users extracting the name and email address

        if quote:
            email_body = f"Hello {name},\n\nHere’s your Daily Quote:\n{quote}\n\nHave a great day!\n\n– Daily Quotes Bot"
            send_email(email, "Your Daily Quote", email_body)
        else:
            print(f"Could not fetch quote for {name}.")

if a quote is successfully retrived, a personalized qupte is sent containing the users name and random quote.

### Logging Success Messages and Errors	
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

This adds a logging systems that records success and error message.
	l.basicConfig(
    		filename="logs/quotelogs.log",
    		level=l.INFO, 
    		format="%(asctime)s - %(levelname)s - %(message)s",
		filemode="a"
	)

This basically log errors which could be WARNING, ERROR, CRITICAL into logs/quotelogs.log. It records the datetime and error messages.



### Fetching Quotes from API

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


The function retrieves random motivational quotes from Zenquotes API.
If the retrieval is successful is returns quote if not, it logs in errors and stop the function early. 

	data = response.json()

	if not isinstance(data, list) or len(data) == 0:
    	l.warning("Response malfunction: not a list or empty response.")
    	return None

This part converts API response to JSON format. this also ensures the data is a list and not empty. 

	Quote = data[0].get("q")
	Author = data[0].get("a")

if successful quote(q) and author(a) is retrieved.

	if Quote:
		return f'"{Quote}" - {Author}'
	else:
    		l.warning("API returned incomplete quote data.")
    		return None

This ensures that the quote text exists beforeing returning it as a formatted string. 

	except r.exceptions.Timeout:
    		l.error("Request timed out.")
    		return None
	except r.exceptions.HTTPError as errh:
    		l.error(f"HTTP error: {errh}")
    		return None
	except Exception as e:
    		l.error(f"Unexpected error fetching quote: {e}")
    		return None	

This part catches and logs different errors including Timeout, HTTPError and Generic Errors. 


## EMAIL CONFIGURATION

	load_dotenv()
	
	SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
	SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
	SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
	SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")	


### Sending Email

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

The send email function is responsible for composing and sending samil securely through an SMTP server. it takes the recipients email address, subject line and the message body as input and sends an email using the secnders ceredntials and sending details as retrieved earlier. 

	msg = MIMEMultipart()
	msg['From'] = SENDER_EMAIL
	msg['To'] = to_email
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))

This creates a felixble email object that can hold text and adds the body of the email as plain text.

		with s.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
    			server.login(SENDER_EMAIL, SENDER_PASSWORD)
    			server.send_message(msg)


This established a secure connection to SMTP server and uses the details from the environment to log in. It also sends teh prepared email using 
		server.send_message(msg)


	l.info(f"Email sent successfully to {to_email}")

logs in confirmation messages to the screen and log file


## LOGGING IN QUOTES AND AUTHOR IN DATABASE

	SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
	SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
	SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
	SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")


	l.basicConfig(
    		filename='Logs/emaillog.log',
		level=l.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
	if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD]):
    		l.error("Faulty Configuration in file.env file")
	else: 
    		l.info("Email Configuration loaded successfully")

This creates an appends logs to logs/emailing.log.

	from datetime import datetime 

	def log_quote(Quote, Author, DATETIME):
    	    try:
              conn = p.connect(
            	'DRIVER={SQL Server};'
            	'SERVER=DESKTOP-HGTC7MT;'           
            	'DATABASE=QUOTESUBSCRIBERS;'
            	'Trusted_Connection=yes;'
               )
               cursor = conn.cursor()

        sql = "INSERT INTO QuotesLog (Quote, Author, DATETIME) VALUES (?, ?, ?)"
        values = (Quote, Author, datetime.now())

        cursor.execute(sql, values)
        conn.commit()
        print("Quote logged successfully")
        l.info("Successful today")
    except Exception as e:
        l.error(f"failed db connection, {e}")
        connection = None
    finally:
        cursor.close()
        conn.close()

THE LOG_QUOTE() function records each quptes sent to a user in a SQL Server ensuring all quotes send along with the authors and timestams are stored.

This is particularly useful for keeping track of daily quotes sent, avoiding duplicate quotes and building a quote history log for users and administrators.

		conn = p.connect(
	    'DRIVER={SQL Server};'
	    'SERVER=DESKTOP-HGTC7MT;'           
	    'DATABASE=QUOTESUBSCRIBERS;'
	    'Trusted_Connection=yes;'
		)
		cursor = conn.cursor)

This connects to the MS SQL Server (Quotesubscribers)


	sql = "INSERT INTO QuotesLog (Quote, Author, DATETIME) VALUES (?, ?, ?)"
	values = (Quote, Author, datetime.now())

	cursor.execute(sql, values)
	conn.commit()

This safely inserts data.

	print("Quote logged successfully")
	l.info("Successful today")

This confirms the insertion was successful both in screen and log file.

	except Exception as e:
    l.error(f"failed db connection, {e}")

This handles possible errors

	finally:
	    cursor.close()
	    conn.close()
		
This ensures that both the cursor and connection are properly closed.

