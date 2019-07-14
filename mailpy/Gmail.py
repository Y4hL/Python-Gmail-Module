# mailpy
#
# Copyright (C) Rasmus Kinnunen <rasmus.kinnunen1@gmail.com>
#
# Released under the terms of the GNU GPL 3.0
#

# GitHub:
# https://github.com/Y4hL/mailpy/

# PyPI:
# https://pypi.org/project/mailpy/


import os
import email
import base64
import imaplib
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


# Exceptions
class GmailException(RuntimeError):
    """There was an ambiguous exception that occurred while handling your
    request."""

class AuthenticationError(GmailException):
    """Gmail Authentication failed."""

class MailboxExists(GmailException):
    """Mailbox already exists"""


class Gmail():

    # With 2FA:
    # create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords

    # Without 2FA:
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps

    # Gmail IMAP defaults
    GMAIL_IMAP_HOST = 'imap.gmail.com'
    GMAIL_IMAP_PORT = 993

    # Gmail SMTP defaults
    GMAIL_SMTP_HOST = 'smtp.gmail.com'
    GMAIL_SMTP_PORT = 465
    
    def __init__(self) -> None:
        self.username = None
        self.password = None

        self.imap = None
        self.mailbox = None
        self.mailboxes = None
        self.logged_in = False
        self.MAIL_IDS = None

        # Options
        self.LOW_NETWORK_USAGE = False


    def _connect_imap(self) -> None:

        self.imap = imaplib.IMAP4_SSL(
            self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)
        return


    def _login_imap(self, username : str, password : str) -> bool:

        if not self.imap:
            self._connect_imap()
        imap_login = self.imap.login(self.username, self.password)
        self.logged_in = (imap_login and imap_login[0] == 'OK')
        if self.logged_in:
            self.fetch_mailboxes()
        return self.logged_in


    def login(self, username : str, password : str) -> bool:

        self.username = username
        self.password = password

        try:
            self._login_imap(self.username, self.password)
        except imaplib.IMAP4.error:
            raise AuthenticationError
        # Use 'INBOX' mailbox by default
        self.use_mailbox('INBOX')
        if self.LOW_NETWORK_USAGE:
            self.get_mail_ids()
        return self.logged_in


    def fetch_mailboxes(self) -> list:
        response, mailbox_list = self.imap.list()
        if response == 'OK':
            self.mailboxes = []
            for mailbox in mailbox_list:
                mailbox_name = mailbox.split(
                    b'"/"')[-1].replace(b'"', b'').strip()
                self.mailboxes.append(mailbox_name)
            return self.mailboxes


    def use_mailbox(self, MAILBOX : str) -> None:
        # Allows changing of the mailbox

        self.imap.select(MAILBOX)
        self.mailbox = MAILBOX
        return


    def create_mailbox(self, mailbox_name : str) -> None:

        if not mailbox_name in self.mailboxes:
            self.imap.create(mailbox_name)
            self.mailboxes.append(mailbox_name)
        else:
            raise MailboxExists
        return

    def delete_mailbox(self, mailbox_name : str) -> None:
        
        if mailbox_name in self.mailboxes:
            self.imap.delete(mailbox_name)
            self.mailboxes.remove(mailbox_name)
        return


    def filter_with_string(self, STRING : str, SEARCH_ATTACHMENTS : bool = False) -> list:
        # Filtered email ids by a string
        # Also has the option to search through attachments
        # This is disabled by default though

        # CAUTION: Searching through attachments is a security risk

        if not isinstance(STRING, str):
            raise TypeError

        FILTERED_MAILS = []

        for MAIL_ID in self._MAIL_IDS():

            MAIL_MESSAGE = self.get_raw(MAIL_ID)
            STR_MESSAGE = MAIL_MESSAGE[0][1].decode()
            MAIL = email.message_from_string(STR_MESSAGE)

            if STRING in MAIL['Author'] or STRING in MAIL['Subject'] or STRING in self.imap.get_mail_body_from_raw(MAIL_MESSAGE):

                FILTERED_MAILS.append(MAIL_ID)
                continue
            
            if SEARCH_ATTACHMENTS:

                STATE =  self.imap.attachment_state_from_raw(MAIL_MESSAGE)
                
                for ATTACHMENT in STATE:

                        if STRING in self.get_attachment_text_from_raw(MAIL_MESSAGE, ATTACHMENT):

                            FILTERED_MAILS.append(MAIL_ID)
                            break

        return FILTERED_MAILS


    def filter_by_author(self, AUTHOR : str) -> list:
        # Filters email ids by their authors

        if not isinstance(AUTHOR, str):
            raise TypeError

        FILTERED_MAILS = []

        for MAIL_ID in self._MAIL_IDS(): # Loops through mail_id list

            if AUTHOR in self.get_mail_author(MAIL_ID): # Check if the given author is in the author

                FILTERED_MAILS.append(MAIL_ID) # Appends filtered mail_id to list

        return FILTERED_MAILS


    def _MAIL_IDS(self):
        # MAIL_IDS Cache Fetcher

        if LOW_NETWORK_USAGE and self.MAIL_IDS != None:
            return self.MAIL_IDS
        return self.get_mail_ids()


    def get_mail_ids(self) -> list:
        # Gets a list of all mail ids
        _, LATEST_DATA = self.imap.search(None, "ALL")

        MAIL_ID_STR = LATEST_DATA[0] # LATEST DATA is a list
        if MAIL_ID_STR == b'': # checks if there are no mails
            self.MAIL_IDS = []
        else:
            self.MAIL_IDS = MAIL_ID_STR.split(b' ')
        return self.MAIL_IDS # returns list of mail ids


    def mail_check(self, MAIL_ID : bytes) -> None:
        # Check if a mail_id is valid

        if not isinstance(MAIL_ID, bytes):
            raise TypeError("MAIL_ID should be a bytes object")

        if not MAIL_ID in self._MAIL_IDS():
            raise ValueError("Invalid MAIL_ID")
        return


    def get_mail_from_raw(self, MAIL_MESSAGE) -> str:
        # Get MAIL

        STR_MESSAGE = MAIL_MESSAGE[0][1].decode()
        MAIL = email.message_from_string(STR_MESSAGE)
        MAIL['Body'] = self.get_mail_body_from_raw(MAIL_MESSAGE)
        return MAIL


    def get_mail_author(self, MAIL_ID : bytes) -> str:
        # Return the author of a specific email
        
        return self.get_mail_from_raw(self.get_raw(MAIL_ID))['From'] # Returns Email Author


    def get_mail_subject(self, MAIL_ID : bytes) -> str:
        # Return the subject of a specific email

        return self.get_mail_from_raw(self.get_raw(MAIL_ID))['Subject'] # Returns Email Subject


    def get_mail_date(self, MAIL_ID : bytes) -> str:
        # Return the date of a specific email
        
        return self.get_mail_from_raw(self.get_raw(MAIL_ID))['Date'] # Returns Email Date


    def get_mail_body(self, MAIL_ID : bytes) -> str:
        # Gets the body of a given MAIL_ID

        return self.get_mail_body_from_raw(self.get_raw(MAIL_ID))


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

        _, MAIL_MESSAGE = self.imap.fetch(MAIL_ID, "(RFC822)") # Fetches a mail by its id
        return MAIL_MESSAGE


    def get_mail(self, MAIL_ID : bytes) -> dict:
        # Returns dictionary with info about a mail

        self.mail_check(MAIL_ID) # Verifies that the mail id is valid
        
        _, MAIL_MESSAGE = self.imap.fetch(MAIL_ID, "(RFC822)")
        STR_MESSAGE = MAIL_MESSAGE[0][1].decode()
        MAIL = email.message_from_string(STR_MESSAGE)

        MAIL['ID'] = MAIL_ID
        MAIL['Body'] = self.get_mail_body_from_raw(MAIL_MESSAGE) # Gets Email Body

        return MAIL


    def list_mails(self) -> list:
        # returns a list of dictionaries ( each dictionary is a mail )

        messages = []

        for MAIL_ID in self._MAIL_IDS(): # Loops through all mail ids

            messages.append(self.get_mail(MAIL_ID))
        
        return messages # Returns dictionary of all mails


    def attachment_state(self, MAIL_ID : bytes) -> list:
        # Returns empty list if no attachment is found
        # or the file name if one is found

        return self.attachment_state_from_raw(self.get_raw(MAIL_ID))


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


    def get_attachment_text(self, MAIL_ID : bytes, ATTACHMENT_NAME : str) -> bytes:
        # Returns attachment content as a string

        return self.get_attachment_text_from_raw(self.get_raw(MAIL_ID), ATTACHMENT_NAME)
    

    def get_attachment_text_from_raw(self, MAIL_MESSAGE : bytes, ATTACHMENT_NAME : str) -> bytes:

        RAW = email.message_from_bytes(MAIL_MESSAGE[0][1])  # Exracts raw email
        for PART in RAW.walk():
            if PART.get_content_maintype() == "multipype":
                continue
            if PART.get("Content-Disposition") is None:
                continue
            if ATTACHMENT_NAME != PART.get_filename():
                continue

            return PART.get_payload(decode=True)

        return False


    def get_attachment(self, MAIL_ID : bytes, ATTACHMENT_NAME : str, SAVE_PATH : str) -> bool:
        # Returns True or False, depending if a attachment was downloaded
        # Attchement_name should be given from the list that you receive
        # from the attachment_state and attachment_state_from_raw functions
        
        return self.get_attachment_from_raw(self.get_raw(MAIL_ID), ATTACHMENT_NAME, SAVE_PATH)


    def get_attachment_from_raw(self, MAIL_MESSAGE, ATTACHMENT_NAME : str, SAVE_PATH : str) -> bool:
        # Returns True or False, depending if a attachment was downloaded
        
        CONTENT = self.get_attachment_text_from_raw(MAIL_MESSAGE, ATTACHMENT_NAME)

        if CONTENT:

            with open(os.path.join(SAVE_PATH, ATTACHMENT_NAME), 'wb') as f:
                f.write(CONTENT)
            
            return True
        
        return False

    
    def delete_mails(self, MAIL_IDS : list) -> None:
        # This should be used to delete multiple mails at once,
        # since deleting a mail can change the mail ID of other mails

        # Check that MAIL_IDS is a list
        if not isinstance(MAIL_IDS, list):
            raise TypeError

        # Sorts Mail IDs to be in order
        MAIL_IDS.sort()

        # Reverse list
        # Therefore mail ids of yet to be deleted mails do not change
        MAIL_IDS.reverse()

        # Loops through mail IDs
        for MAIL_ID in MAIL_IDS:

            # Delete mail
            self.delete_mail(MAIL_ID)
        return


    def delete_mail(self, MAIL_ID : bytes) -> None:
        # Delete a specific mail by mail_id
        
        self.mail_check(MAIL_ID) # Verifies that the mail id is valid

        self.imap.store(MAIL_ID, '+X-GM-LABELS', '\\Trash') # Moves mail to trash
        
        self.imap.expunge() # Expunge

        # Refresh MAIL_IDS in LOW_NETWORK_USAGE
        if self.LOW_NETWORK_USAGE:
            self.get_mail_ids()
        
        return


    def logout(self) -> None:
        # Logout

        self.imap.close()
        self.imap.logout()
        self.logged_in = False
        return


    def send(RECIPIANT : str, SUBJECT : str, MESSAGE : str, FILES : list = None) -> None:
        # Sends Gmail with or without attachemnts

        if self.username == None or self.password == None:
            raise AuthenticationError('Log in first')

        for PARAM in [RECIPIANT, SUBJECT, MESSAGE]: # Checks that parameters are strings
            if not isinstance(PARAM, str):
                raise TypeError

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = RECIPIANT
        msg['Subject'] = SUBJECT

        msg.attach(MIMEText(MESSAGE, 'plain'))

        if FILES: # Checks for files to append
            if not isinstance(FILES, list):
                raise TypeError('FILES should be a list')
            # Appends attachments to the email
            for FILE in FILES:
                if not isinstance(FILE, str):
                    raise TypeError('FILES list should only contain strings')
                if not os.path.isfile(FILE): # Check if file exists
                    raise FileNotFoundError("'{}' not found".format(FILE))
                filename = os.path.basename(FILE) # Gets file location
                attachment = open(FILE, "rb") # Opens attachment
                part = MIMEBase('application', 'octet-stream') # Creates PART
                part.set_payload((attachment).read()) # Attaches payload to PART
                encoders.encode_base64(part) # base64 encodes the PART
                part.add_header('Content-Disposition', "attachment; filename= %s" % filename) # Adds Header to PART

                msg.attach(part) # Attaches PART to mail

        with smtplib.SMTP_SSL(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT) as smtp: # Creates encrypted connection
            smtp.login(self.username, self.password) # Logs in
            text = msg.as_string() # Stores mail as string
            smtp.sendmail(self.username, RECIPIANT, text) # Sends email
            smtp.quit() # Closes connection
        return
