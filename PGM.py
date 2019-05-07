# PGM
# Python Gmail Module
# https://github.com/Y4hL/Python-Gmail-Module/

import base64
import imaplib
import email
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class MailReader():

    def __init__(self, user, password, imaplib_url="imap.gmail.com", inbox="INBOX"):
        self.user = user
        self.password = password
        self.imap_url = imaplib_url
        self.inbox = inbox

        if type(self.user) == bytes:
            self.user = self.user.decode()
        if type(self.password) == bytes:
            self.password = self.password.decode()
        
        self.con = imaplib.IMAP4_SSL(self.imap_url)
        self.con.login(self.user, self.password)
        self.con.select(self.inbox)


    def change_inbox(self, INBOX):
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

        if type(MAIL_ID) != bytes:
            raise TypeError("MAIL_ID should be a bytes object")

        MAIL_IDS = self.get_mail_ids()
        if not MAIL_ID in MAIL_IDS:
            raise ValueError("Invalid MAIL_ID")
        return


    def get_mail_date(self, MAIL_ID):
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID)
        return MAIL_MESSAGE['Date'] # Returns Email Date


    def get_mail_subject(self, MAIL_ID):

        MAIL_MESSAGE = self.get_raw(MAIL_ID)
        return MAIL_MESSAGE['Subject'] # Returns Email Subject


    def get_mail_author(self, MAIL_ID):
        
        MAIL_MESSAGE = self.get_raw(MAIL_ID)
        return MAIL_MESSAGE['From'] # Returns Email Author


    def get_mail_body_from_raw(self, MAIL_MESSAGE):
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])
        for PART in RAW.walk():
            if PART.get_content_type() == 'text/plain':
                BODY = PART.get_payload()
                try:
                    BODY = base64.b64decode(BODY).decode()
                except Exception:
                    pass
                return BODY


    def get_mail_body(self, MAIL_ID):
        # Gets the body of a given MAIL_ID

        self.mail_check(MAIL_ID)

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])
        for PART in RAW.walk():
            if PART.get_content_type() == 'text/plain':
                BODY = PART.get_payload()
                try:
                    BODY = base64.b64decode(BODY).decode()
                except Exception:
                    pass
                return BODY


    def get_raw(self, MAIL_ID):
        # Gets raw email

        self.mail_check(MAIL_ID)

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        return MAIL_MESSAGE


    def get_mail(self, MAIL_ID):
        # Same as list_mails function, but only returns it for one given mail

        self.mail_check(MAIL_ID)
        
        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
        EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)

        BODY = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets Email Body

        return dict(zip(["Id", "Subject", "From", "Date", "To", "Body"], [MAIL_ID, EMAIL_MESSAGE['Subject'], EMAIL_MESSAGE['From'], EMAIL_MESSAGE['Date'], EMAIL_MESSAGE['To'], BODY])) # Combines values into dict


    def list_mails(self):
        # returns a list of dictionaries ( each dictionary is a mail )

        MAIL_ID_LIST = self.get_mail_ids()

        messages = []

        for MAIL_ID in MAIL_ID_LIST:
            _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
            STR_MESSAGE = MAIL_MESSAGE[0][1].decode("utf-8")
            EMAIL_MESSAGE = email.message_from_string(STR_MESSAGE)

            BODY = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets Email Body

            messages.append(dict(zip(["Id", "Subject", "From", "Date", "To", "Body"], [MAIL_ID, EMAIL_MESSAGE['Subject'], EMAIL_MESSAGE['From'], EMAIL_MESSAGE['Date'], EMAIL_MESSAGE['To'], BODY])))
        
        return messages


    def attachment_state(self, MAIL_ID):
        # Returns False if no attachment is found
        # or the file name if one is found

        self.mail_check(MAIL_ID)

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAME = PART.get_filename() # Gets download file name
            return FILE_NAME
        return False


    def attachment_state_from_raw(self, MAIL_MESSAGE):
        # Returns False if no attachment is found
        # or the file name if one is found
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAME = PART.get_filename() # Gets download file name
            return FILE_NAME
        return False


    def get_attachment(self, MAIL_ID, SAVE_PATH):
        # Returns True or False, depending if a attachment was downloaded
        
        self.mail_check(MAIL_ID)

        _, MAIL_MESSAGE = self.con.fetch(MAIL_ID, "(RFC822)")
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAME = PART.get_filename() # Gets download file name

            if bool(FILE_NAME):
                FILE_PATH = os.path.join(SAVE_PATH, FILE_NAME)
                with open(FILE_PATH, "wb") as f:
                    f.write(PART.get_payload(decode=True))
                return FILE_PATH
            return False


    def get_attachment_from_raw(self, MAIL_MESSAGE, SAVE_PATH):
        # Returns True or False, depending if a attachment was downloaded
        
        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # gets email from list
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            FILE_NAME = PART.get_filename() # Gets download file name

            if bool(FILE_NAME):
                FILE_PATH = os.path.join(SAVE_PATH, FILE_NAME)
                with open(FILE_PATH, "wb") as f:
                    f.write(PART.get_payload(decode=True))
                return FILE_PATH
            return False


    def delete_mail(self, MAIL_ID):
        
        self.mail_check(MAIL_ID)

        if self.imap_url.lower() == "imap.gmail.com":
            self.con.store(MAIL_ID, '+X-GM-LABELS', '\\Trash') # Moved email to trash
        else:
           self.con.store(MAIL_ID, '+FLAGS', '\\Deleted')
        self.con.expunge()
        return


    def disconnect(self):
        self.con.close()
        self.con.logout()
        return


def send_gmail(USER_EMAIL, PASSWORD, RECIPIANT, SUBJECT, MESSAGE, FILE_LOCATION=False):
    # Returns True if email was sent successfully
    
    # Without 2FA:
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps

    # With 2FA:
    # create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords
    
    if type(USER_EMAIL) != str:
        raise TypeError("USER_EMAIL should be a string")
    if type(PASSWORD) != str:
        raise TypeError("PASSWORD should be a string")
    if type(RECIPIANT) != str:
        raise TypeError("RECIPIANT should be a string")
    if type(SUBJECT) != str:
        raise TypeError("SUBJECT should be a string")
    if type(MESSAGE) != str:
        raise TypeError("MESSAGE should be a string")

    msg = MIMEMultipart()
    msg['From'] = USER_EMAIL
    msg['To'] = RECIPIANT
    msg['Subject'] = SUBJECT

    msg.attach(MIMEText(MESSAGE, 'plain'))

    if not FILE_LOCATION == False:
        file_locations = []
        if type(FILE_LOCATION) == str:
            file_locations.append(FILE_LOCATION)
        if type(FILE_LOCATION) == list:
            file_locations = FILE_LOCATION
        for files in file_locations:
            files = str(files)
            if not os.path.isfile(files):
                raise ValueError("File '{files}' does not exist, remember to enter the path")
            filename = os.path.basename(FILE_LOCATION)
            attachment = open(FILE_LOCATION, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(USER_EMAIL, PASSWORD)
        text = msg.as_string()
        smtp.sendmail(USER_EMAIL, RECIPIANT, text)
        smtp.quit()
    return

