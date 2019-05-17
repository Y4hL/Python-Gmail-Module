# Python-Gmail-Module
Easily Send, Read and Download attachments from Gmail with Python  

# Setup  
  
SMTP login method is not enabled by default.  
Enable it [here](https://myaccount.google.com/lesssecureapps)  
  
Alternatively if you have 2fa enabled,  
you will need to create a app password [here](https://myaccount.google.com/apppasswords)  
  
```
python setup.py install 
```
  
# Example

### Importing
```
import PGM
```
### Authenticate a connection
```
MyMail = PGM.MailReader(email, password)
```
### Change inbox
```
MyMail.change_inbox("INBOX")
```

### Get a list of all email IDs
```
list_of_mail_ids = MyMail.get_mail_ids()
```
### Get body of email by its ID
```
body_of_email = MyMail.get_mail_body(MAIL_ID)
```
### Gets raw email by ID
```
raw_email = MyMail.get_raw(MAIL_ID)
```
### Get Subject, Author, received date, recipiant and body of email by ID
```
second_email = MyMail.get_mail(list_of_mail_ids[1])
print(second_email)
```
### Checks for email attachment by ID
```
state = MyMail.attachment_state(list_of_mail_ids[2])
```

### Downloads attachment by ID to given DIR
```
get_attachment(MAIL_ID, SAVE_PATH)
```
### Get a list of all mails in your inbox
```
all_emails = MyMail.list_mails()
for email in all_emails:
    print(email)
```
### Delete email by ID
```
MyMail.delete_mail(MAIL_ID)
```
### Disconnect from smtp
```
MyMail.disconnect()
```
