# PGM
# Python Gmail Module

# GitHub:
# https://github.com/Y4hL/Python-Gmail-Module/

# PyPI:
# https://pypi.org/project/Python-Gmail-Module/


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

    def __init__(self, user : str, password : str, imaplib_url="imap.gmail.com", inbox="INBOX"):
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


    def change_inbox(self, INBOX : str):
        # Allows changing of the mailbox

        self.con.select(INBOX)
        return


    def filter_by_author(self, AUTHOR : str) -> list:
        # Filters email ids by their authors

        if type(AUTHOR) != str:
            raise TypeError("AUTHOR should be a string.")

        FILTERED_MAILS = []

        for MAIL_ID in self.get_mail_ids(): # Loops through mail_id list

            if AUTHOR in self.get_mail_author(MAIL_ID): # Check if the given author is in the author

                FILTERED_MAILS.append(MAIL_ID) # Appends filtered mail_id to list

        return FILTERED_MAILS


    def get_mail_ids(self) -> list:
        # Gets a list of all mail ids in a inbox
        _, LATEST_DATA = self.con.search(None, "ALL")

        MAIL_ID_STR = LATEST_DATA[0] # LATEST DATA is a list
        if MAIL_ID_STR == b'': # checks if there are no mails
            return [] # returns empty list
        return MAIL_ID_STR.split(b' ') # returns list of mail ids


    def mail_check(self, MAIL_ID : bytes):
        # Check if a mail_id is valid

        if not isinstance(MAIL_ID, bytes):
            raise TypeError("MAIL_ID should be a bytes object")

        MAIL_IDS = self.get_mail_ids()
        if not MAIL_ID in MAIL_IDS:
            raise ValueError("Invalid MAIL_ID")
        return


    def get_mail_author(self, MAIL_ID : bytes) -> str:
        # Return the author of a specific email
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['From'] # Returns Email Author


    def get_mail_subject(self, MAIL_ID : bytes) -> str:
        # Return the subject of a specific email

        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['Subject'] # Returns Email Subject


    def get_mail_date(self, MAIL_ID : bytes) -> str:
        # Return the date of a specific email
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID) # Gets the raw email by its id
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)
        return EMAIL_MESSAGE['Date'] # Returns Email Date


    def get_mail_body(self, MAIL_ID : bytes) -> str:
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


    def get_mail_body_from_raw(self, MAIL_MESSAGE) -> str:
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


    def get_raw(self, MAIL_ID : bytes):
        # Gets the raw email

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)") # Fetches a mail by its id
        return MAIL_MESSAGE


    def get_mail(self, MAIL_ID: bytes) -> dict:
        # Same as list_mails function, but only returns it for one given mail

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid
        
        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)

        BODY = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets Email Body

        return dict(zip(["Id", "Subject", "From", "Date", "To", "Body"], [MAIL_ID, EMAIL_MESSAGE['Subject'], EMAIL_MESSAGE['From'], EMAIL_MESSAGE['Date'], EMAIL_MESSAGE['To'], BODY])) # Combines values into dict


    def list_mails(self) -> list:
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


    def attachment_state(self, MAIL_ID: bytes) -> list:
        # Returns empty list if no attachment is found
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
        return FILE_NAMES


    def attachment_state_from_raw(self, MAIL_MESSAGE) -> list:
        # Returns empty list if no attachment is found
        # or the file name if one is found
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        FILE_NAMES = []
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAMES.append(PART.get_filename()) # Adds filename to list
        return FILE_NAMES


    def get_attachment(self, MAIL_ID : bytes, ATTACHMENT_NAME: str, SAVE_PATH : str) -> bool:
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
            
            return True
        
        return False


    def get_attachment_from_raw(self, MAIL_MESSAGE, ATTACHMENT_NAME : str, SAVE_PATH : str) -> bool:
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
            
            return True
            
        return False

    
    def delete_mails(self, MAIL_IDS : list):
        # This should be used to delete multiple mails at once,
        # since deleting a mail can change the mail ID of other mails

        # Check that MAIL_IDS is a list
        if not isinstance(MAIL_IDS, list):
            raise TypeError

        # Sorts Mail IDs to be in order
        MAIL_IDS.sort()

        # Reverse list, so older mails get deleted first
        # Therefore mail ids of yet to be deleted mails do not change
        MAIL_IDS = MAIL_IDS[:-1]

        # Loops through mail IDs
        for MAIL_ID in MAIL_IDS:

            # Check that the mail ID is valid
            self.mail_check(MAIL_ID)

            # Deleted mail
            self.delete_mail(MAIL_ID)
        return


    def delete_mail(self, MAIL_ID : bytes):
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


def send_gmail(USER_EMAIL : str, PASSWORD : str, RECIPIANT : str, SUBJECT, MESSAGE : str, FILE_LOCATION=False):
    # Sends Gmail with or without attachemnts

    # Without 2FA:
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps

    # With 2FA:
    # create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords

    for parameter in [USER_EMAIL, PASSWORD, RECIPIANT, SUBJECT, MESSAGE]: # Checks that parameters are strings
        if not isinstance(parameter, str):
            raise TypeError

    msg = MIMEMultipart()
    msg['From'] = USER_EMAIL
    msg['To'] = RECIPIANT
    msg['Subject'] = SUBJECT

    msg.attach(MIMEText(MESSAGE, 'plain'))

    if not FILE_LOCATION == False: # Checks for files to append
        if type(FILE_LOCATION) == str:
            FILES = [FILE_LOCATION]
        elif type(FILE_LOCATION) == list:
            FILES = FILE_LOCATION
        else:
            raise TypeError("FILE_LOCATION parameter should be a string or list")
        
        for FILE in FILES: # Searches for files and appends them to the email
            FILE = str(FILE)
            if not os.path.isfile(FILE): # Check if file exists
                raise FileNotFoundError("'{FILE}' does not exist") # Error if FileNotFound
            filename = os.path.basename(FILE) # Gets file location
            attachment = open(FILE, "rb") # Opens attachment
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

