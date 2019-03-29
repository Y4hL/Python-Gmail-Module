# PGM
# Python Gmail Module

# Imports
import base64
import imaplib
import email
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class read():

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
        _, get_latest_data = self.con.search(None, "ALL")

        mail_id_str = get_latest_data[0] # get_latest_data is a list
        if mail_id_str == b'': # checks if there are no mails
            return [] # returns empty list
        return mail_id_str.split(b' ') # returns list of mail ids


    def get_email_body(self, mail_id):
        # Gets the body of a given mail_id

        mail_id_list = self.get_mail_ids()

        if type(mail_id) != bytes:
            raise TypeError("mail_id should be a bytes object")

        if not mail_id in mail_id_list:
            raise ValueError("invalid mail_id")

        _, mail_message = self.con.fetch(mail_id, "(RFC822)")
        raw = email.message_from_bytes(mail_message[0][1])
        for part in raw.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload()
                try:
                    body = base64.b64decode(body).decode()
                except Exception:
                    pass
                return body

    def get_raw(self, mail_id):
        # Gets raw email

        if type(mail_id) != bytes:
            raise TypeError("mail_id should be a bytes object")

        mail_id_list = self.get_mail_ids()
        if not mail_id in mail_id_list:
            raise ValueError("Invalid mail_id")
        _, mail_message = self.con.fetch(mail_id, "(RFC822)")
        return mail_message


    def get_mail(self, mail_id):
        # Same as list_mails function, but only returns it for one given mail

        if type(mail_id) != bytes:
            raise TypeError("mail_id should be a bytes object")

        mail_id_list = self.get_mail_ids()
        if not mail_id in mail_id_list:
            raise ValueError("Invalid mail_id")
        _, mail_message = self.con.fetch(mail_id, "(RFC822)")
        str_message = mail_message[0][1].decode("utf-8")
        email_message = email.message_from_string(str_message)
        email_subject = email_message['Subject'] # Gets Email Subject
        email_sender = email_message['From'] # Gets Email Sender
        date = email_message['Date'] # Gets Date Email was sent
        recipiant = email_message['To'] # Gets Email Recipiant

        body = self.get_email_body(mail_id) # Gets Body

        message = {
                "Id": mail_id,
                "Subject": email_subject,
                "From": email_sender,
                "Date": date,
                "To": recipiant,
                "Body": body
            }
        return message


    def list_mails(self):
        # returns a list of dictionarys ( each dictinary is a mail )

        mail_id_list = self.get_mail_ids()

        messages = []

        for mail_id in mail_id_list:
            _, mail_message = self.con.fetch(mail_id, "(RFC822)")
            str_message = mail_message[0][1].decode("utf-8")
            email_message = email.message_from_string(str_message)
            email_subject = email_message['Subject'] # Gets Email Subject
            email_sender = email_message['From'] # Gets Email Sender
            date = email_message['Date'] # Gets Date Email was sent
            recipiant = email_message['To'] # Gets Email Recipiant

            body = self.get_email_body(mail_id) # Gets Body

            messages.append({
                "id": mail_id,
                "subject": email_subject,
                "from": email_sender,
                "date": date,
                "to": recipiant,
                "body": body
            })
        return messages


    def attachment_state(self, mail_id):
        # Returns False if no attachment is found
        # or the file name if one is found

        mail_id_list = self.get_mail_ids()
        
        if type(mail_id) != bytes:
            raise TypeError("mail_id should be a bytes object")
        
        if not mail_id in mail_id_list:
            raise ValueError("Invalid mail_id")
        _, mail_message = self.con.fetch(mail_id, "(RFC822)")
        raw = email.message_from_bytes(mail_message[0][1])  # gets email from list
        for part in raw.walk():
            if part.get_content_maintype() == "multipype":
                continue
            if part.get("Content-Disposition") is None:
                continue
            fileName = part.get_filename() # Gets download file name
            return fileName
        return False


    def get_attachment(self, mail_id, save_dir):
        # Returns True or False, depending if a attachment was downloaded
        
        mail_id_list = self.get_mail_ids()
        
        if type(mail_id) != bytes:
            raise TypeError("mail_id should be a bytes object")
        
        if not mail_id in mail_id_list:
            raise ValueError("Invalid mail_id")
        _, mail_message = self.con.fetch(mail_id, "(RFC822)")
        raw = email.message_from_bytes(mail_message[0][1])  # gets email from list
        for part in raw.walk():
            if part.get_content_maintype() == "multipype":
                continue
            if part.get("Content-Disposition") is None:
                continue
            fileName = part.get_filename() # Gets download file name

            if bool(fileName):
                filePath = os.path.join(save_dir, fileName)
                with open(filePath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                return filePath
            return False


    def delete_email(self, mail_id):
        mail_id_list = self.get_mail_ids()

        if type(mail_id) !=  bytes:
            raise TypeError("mail_id should be a bytes object")

        if not mail_id in mail_id_list:
            raise ValueError("Invalid mail_id")
        if self.imap_url == "imap.gmail.com":
            self.con.store(mail_id, '+X-GM-LABELS', '\\Trash') # Moved email to trash
        else:
           self.con.store(mail_id, '+FLAGS', '\\Deleted')
        self.con.expunge()
        return

    def disconnect(self):
        self.con.close()
        self.con.logout()
        return


def send_gmail(user_email, password, send_to_email, subject, message, file_location=False):
    # Returns True if email was sent successfully
    
    # Without 2FA:
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps

    # With 2FA:
    # create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords
    
    if type(user_email) != str:
        raise TypeError("email should be a string")
    if type(password) != str:
        raise TypeError("password should be a string")
    if type(send_to_email) != str:
        raise TypeError("recipiant should be a string")
    if type(subject) != str:
        raise TypeError("subject should be a string")
    if type(message) != str:
        raise TypeError("message should be a string")

    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    if not file_location == False:
        file_locations = []
        if type(file_location) == str:
            file_locations.append(file_location)
        if type(file_location) == list:
            file_locations = file_location
        for files in file_locations:
            files = str(files)
            if not os.path.isfile(files):
                raise ValueError("File '{files}' does not exist, remember to enter the path")
            filename = os.path.basename(file_location)
            attachment = open(file_location, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(user_email, password)
        text = msg.as_string()
        smtp.sendmail(user_email, send_to_email, text)
        smtp.quit()
        return True
    return False

