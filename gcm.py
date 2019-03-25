# PGM
# Python Gmail Module

# Imports
import base64
import email
import imaplib
import os
import smtplib


def auth(user, password, imap_url="imap.gmail.com", inbox="INBOX"): # Google Server Authentication
    # returns a connection

    if type(user) == bytes:
        user = user.decode()
    if type(password)  == bytes:
        password = password.decode()
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, password)
    con.select(inbox)
    return con


def get_mail_ids(con):
    # Gets a list of all mail ids in a inbox
    _, get_latest_data = con.search(None, "ALL")

    mail_id_str = get_latest_data[0] # get_latest_data is a list
    return mail_id_str.split(b' ')


def get_email_body(con, mail_id):
    # Gets the body of a given mail_id

    mail_id_list = get_mail_ids(con)

    if type(mail_id) != bytes:
        raise TypeError("mail_id should be a bytes object")

    if not mail_id in mail_id_list:
        raise ValueError("mail id '{}' does not correspond to a email".format(mail_id))

    _, mail_message = con.fetch(mail_id, "(RFC822)")
    raw = email.message_from_bytes(mail_message[0][1])
    for part in raw.walk():
        if part.get_content_type() == 'text/plain':
            body = part.get_payload()
            try:
                body = base64.b64decode(body).decode()
            except Exception:
                pass
            return body


def get_mail(con, mail_id):
    # Same as list_mails function, but only returns it for one given mail

    if type(mail_id) != bytes:
        raise TypeError("mail_id should be a bytes object")

    mail_id_list = get_mail_ids(con)
    if not mail_id in mail_id_list:
        raise ValueError("mail id '{}' does not correspond to a email".format(mail_id))
    _, mail_message = con.fetch(mail_id, "(RFC822)")
    str_message = mail_message[0][1].decode("utf-8")
    email_message = email.message_from_string(str_message)
    email_subject = email_message['Subject'] # Gets Email Subject
    email_sender = email_message['From'] # Gets Email Sender
    date = email_message['Date'] # Gets Date Email was sent
    recipiant = email_message['To'] # Gets Email Recipiant

    body = get_email_body(con, mail_id) # Gets Body

    message = {
            "Id": mail_id,
            "Subject": email_subject,
            "From": email_sender,
            "Date": date,
            "To": recipiant,
            "Body": body
        }
    return message

def list_mails(con):
    # returns a list of dictionarys ( each dictinary is a mail )

    mail_id_list = get_mail_ids(con)

    messages = []

    for mail_id in mail_id_list:
        _, mail_message = con.fetch(mail_id, "(RFC822)")
        str_message = mail_message[0][1].decode("utf-8")
        email_message = email.message_from_string(str_message)
        email_subject = email_message['Subject'] # Gets Email Subject
        email_sender = email_message['From'] # Gets Email Sender
        date = email_message['Date'] # Gets Date Email was sent
        recipiant = email_message['To'] # Gets Email Recipiant

        body = get_email_body(con, mail_id) # Gets Body

        messages.append({
            "id": mail_id,
            "subject": email_subject,
            "from": email_sender,
            "date": date,
            "to": recipiant,
            "body": body
        })
    return messages


def attachment_state(con, mail_id):
    # Returns False if no attachment is found
    # or the file name if one is found

    mail_id_list = get_mail_ids(con)
    
    if type(mail_id) != bytes:
        raise TypeError("mail_id should be a bytes object")
    
    if not mail_id in mail_id_list:
        raise ValueError("mail id '{}' does not correspond to a email".format(mail_id))
    _, mail_message = con.fetch(mail_id, "(RFC822)")
    raw = email.message_from_bytes(mail_message[0][1])  # gets email from list
    for part in raw.walk():
        if part.get_content_maintype() == "multipype":
            continue
        if part.get("Content-Disposition") is None:
            continue
        fileName = part.get_filename() # Gets download file name
        return fileName
    return False


def send_gmail(email, password, send_to_email, subject, message, file_location=False):
    # Returns True if email was sent successfully
    
    # Activate less secure apps to use, at: https://myaccount.google.com/lesssecureapps
    # OR 
    # RECOMMENDED:
    #if you have 2fa, create a app password and use it instead of the real password
    # at: https://myaccount.google.com/apppasswords
    
    if type(email) != str:
        raise TypeError("email should be a string")
    if type(password) != str:
        raise TypeError("password should be a string")
    if type(send_to_email) != str:
        raise TypeError("recipiant should be a string")
    if type(subject) != str:
        raise TypeError("subject should be a string")
    if type(message) != str:
        raise TypeError("message should be a string")

    msg = email.mime.multipart.MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    msg.attach(email.mime.text.MIMEText(message, 'plain'))

    if not file_location==False:
        if type(file_location) != str:
            raise ValueError("file_location should be a string or left empty")
        if not os.path.isfile(file_location):
            raise ValueError("File '{}' does not exist, remember to enter the path")
        filename = os.path.basename(file_location)
        attachment = open(file_location, "rb")
        part = email.MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        msg.attach(part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(email, password)
        text = msg.as_string()
        smtp.sendmail(email, send_to_email, text)
        smtp.quit()
        return True


def get_attachment(con, mail_id, save_dir):
    # Returns True or False, depending if a attachment was downloaded
    
    mail_id_list = get_mail_ids(con)
    
    if type(mail_id) != bytes:
        raise TypeError("mail_id should be a bytes object")
    
    if not mail_id in mail_id_list:
        raise ValueError("mail id '{}' does not correspond to a email".format(mail_id))
    _, mail_message = con.fetch(mail_id, "(RFC822)")
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


def delete_email(con, mail_id):
    mail_id_list = get_mail_ids(con)

    if type(mail_id) !=  bytes:
        raise TypeError("mail_id should be a bytes object")

    if not mail_id in mail_id_list:
        raise ValueError("mail id '{}' does not correspond to a email".format(mail_id))

    con.store(mail_id, '+FLAGS', '\\Deleted')

    return


def clear_deleted(con):
    con.expunge()
    return
