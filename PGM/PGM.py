# PGM
# Python Gmail Module
# https://github.com/Y4hL/Python-Gmail-Module/

import os
import email
import base64
import imaplib
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class MailReader():

    def __init__(self, user, password, imaplib_url="imap.gmail.com", inbox="INBOX"):
        self.user = user
        self.password = password
        self.imap_url = imaplib_url
        self.inbox = inbox

        if type(self.user) == bytes: # Decodes email if needed
            self.user = self.user.decode()
        if type(self.password) == bytes: # Decodes password if needed
            self.password = self.password.decode()
   
        self.con = imaplib.IMAP4_SSL(self.imap_url) # Initiate connection to server
        self.con.login(self.user, self.password) # Log in
        self.con.select(self.inbox) # Selects mailbox


    def change_inbox(self, INBOX):
        # Allows changing of the mailbox

        self.con.select(INBOX)
        return


    def get_mail_ids(self):
        # Gets a list of all mail ids in a inbox
        _, LATEST_DATA = self.con.search(None, "ALL")

        MAIL_ID_STR = LATEST_DATA[0] # LATEST DATA is a list
        if MAIL_ID_STR == b'': # checks if there are no mails
            return [] # returns empty list
        return MAIL_ID_STR.split(b' ') # returns list of mail ids


    def mail_check(self, MAIL_ID):
        # Check if a mail_id is valid

        if type(MAIL_ID) != bytes:
            raise TypeError("MAIL_ID should be a bytes object")

        MAIL_IDS = self.get_mail_ids()
        if not MAIL_ID in MAIL_IDS:
            raise ValueError("Invalid MAIL_ID")
        return


    def get_mail_author(self, MAIL_ID):
        # Return the author of a specific email
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['From'] # Returns Email Author


    def get_mail_subject(self, MAIL_ID):
        # Return the subject of a specific email

        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['Subject'] # Returns Email Subject


    def get_mail_date(self, MAIL_ID):
        # Return the date of a specific email
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['Date'] # Returns Email Date


    def get_mail_body(self, MAIL_ID):
        # Gets the body of a given MAIL_ID

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches a mail by its id
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1]) # Exracts mail from raw format
        for PART in RAW.walk():
            if PART.get_content_type() == 'text/plain':
                BODY = PART.get_payload()
                try:
                    BODY = base64.b64decode(BODY).decode()
                except Exception:
                    pass
                return BODY


    def get_mail_body_from_raw(self, MAIL_MESSAGE):
        # Gets the mail body from the get_raw function
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1]) # Exracts mail from raw format
        for PART in RAW.walk():
            if PART.get_content_type() == 'text/plain':
                BODY = PART.get_payload()
                try:
                    BODY = base64.b64decode(BODY).decode()
                except Exception:
                    pass
                return BODY


    def get_raw(self, MAIL_ID):
        # Gets the raw email

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches a mail by its id
        return MAIL_MESSAGE


    def get_mail(self, MAIL_ID):
        # Same as list_mails function, but only returns it for one given mail

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid
        
        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)

        BODY = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets Email Body

        return dict(zip(["Id", "Subject", "From", "Date", "To", "Body"], [MAIL_ID, EMAIL_MESSAGE['Subject'], EMAIL_MESSAGE['From'], EMAIL_MESSAGE['Date'], EMAIL_MESSAGE['To'], BODY])) # Combines values into dict


    def list_mails(self):
        # returns a list of dictionaries ( each dictionary is a mail )

        MAIL_ID_LIST = self.get_mail_ids() # Gets all mail_ids

        messages = []

        for MAIL_ID in MAIL_ID_LIST: # Loops through all mail ids
            _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches mail by its id
            STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
            EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE) # Extracts the email message

            BODY = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets the Email Body

            messages.append(dict(zip(["Id", "Subject", "From", "Date", "To", "Body"], [MAIL_ID, EMAIL_MESSAGE['Subject'], EMAIL_MESSAGE['From'], EMAIL_MESSAGE['Date'], EMAIL_MESSAGE['To'], BODY])))
        
        return messages # Returns dictionary of all mails


    def attachment_state(self, MAIL_ID):
        # Returns False if no attachment is found
        # or the file name if one is found

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches mail by its id
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # Extracts raw email
        FILE_NAMES = []
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAMES.append(PART.get_filename()) # Adds filename to list
        if len(FILE_NAMES) == 0:
            return False
        return FILE_NAMES


    def attachment_state_from_raw(self, MAIL_MESSAGE):
        # Returns False if no attachment is found
        # or the file name if one is found
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        FILE_NAMES = []
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAMES.append(PART.get_filename()) # Adds filename to list
        if len(FILE_NAMES) == 0:
            return False
        return FILE_NAMES


    def get_attachment(self, MAIL_ID, ATTACHMENT_NAME, SAVE_PATH):
        # Returns True or False, depending if a attachment was downloaded
        # Attchement_name should be given from the list that you receive
        # from the attachment_state and attachment_state_from_raw functions
        
        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches a mail by its id
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # Exracts raw email
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            if ATTACHMENT_NAME != PART.get_filename():
                continue

            with open(os.path.join(SAVE_PATH, PART.get_filename()), 'wb') as f:
                f.write(PART.get_payload(decode=True))
        
        return False




    def get_attachment_from_raw(self, MAIL_MESSAGE, ATTACHMENT_NAME, SAVE_PATH):
        # Returns True or False, depending if a attachment was downloaded
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # Exracts raw email
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            if ATTACHMENT_NAME != PART.get_filename(): 
                continue

            with open(os.path.join(SAVE_PATH, PART.get_filename()), "wb") as f:
                f.write(PART.get_payload(decode=True))
            
        return False


    def delete_mail(self, MAIL_ID):
        # Delete a specific mail by mail_id
        
        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        if self.imap_url.lower() == "imap.gmail.com": # Checks if imap url is from google
            self.con.store(MAIL_ID, '+X-GM-LABELS', '\\Trash') # Moves mail to trash
        else:
           self.con.store(MAIL_ID, '+FLAGS', '\\Deleted')
        self.con.expunge() # Expunge
        return


    def disconnect(self):
        # Disconnect the client ( Not Nessecary )

        self.con.close() # Closes client
        self.con.logout() # Logs out
        return


def send_gmail(USER_EMAIL, PASSWORD, RECIPIANT, SUBJECT, MESSAGE, FILE_LOCATION=False):
    # Returns True if email was sent successfully

    # Without 2FA:
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps

    # With 2FA:
    # create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords

    for parameter in [USER_EMAIL, PASSWORD, RECIPIANT, SUBJECT, MESSAGE]: # Checks that parameters are strings
        if type(parameter) != str:
            raise TypeError("All parameters should be strings.")

    msg = MIMEMultipart()
    msg['From'] = USER_EMAIL
    msg['To'] = RECIPIANT
    msg['Subject'] = SUBJECT

    msg.attach(MIMEText(MESSAGE, 'plain'))

    if not FILE_LOCATION == False: # Checks for files to append
        file_locations = []
        if type(FILE_LOCATION) == str:
            file_locations.append(FILE_LOCATION)
        elif type(FILE_LOCATION) == list:
            file_locations = FILE_LOCATION
        else:
            raise TypeError("FILE_LOCATION parameters should be a string or list")
        
        for files in file_locations: # Searches for files and appends them to the email
            files = str(files)
            if not os.path.isfile(files): # Check if file exists
                raise FileNotFoundError("'{files}' does not exist") # Error if FileNotFound
            filename = os.path.basename(FILE_LOCATION) # Gets file location
            attachment = open(FILE_LOCATION, "rb") # Opens attachment
            part = MIMEBase('application', 'octet-stream') # Creates PART
            part.set_payload((attachment).read()) # Attaches payload to PART
            encoders.encode_base64(part) # base64 encodes the PART
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename) # Adds Header to PART

            msg.attach(part) # Attaches PART to mail

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp: # Creates connection
        smtp.starttls() # Starts TLS connection protocol
        smtp.login(USER_EMAIL, PASSWORD) # Logs in
        text = msg.as_string() # Stores mail as string
        smtp.sendmail(USER_EMAIL, RECIPIANT, text) # Sends email
        smtp.quit() # Closes connection
    return

