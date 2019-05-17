# Python-Gmail-Module
Easily Send, Read and Download attachments from Gmail with Python  

# Setup  
  
SMTP login method is not enabled by default.  
Enable it [here](https://myaccount.google.com/lesssecureapps)  
  
Alternatively if you have 2fa enabled,  
you will need to create a app password [here](https://myaccount.google.com/apppasswords)  
  
# Install  
```  
Install Latest Release:  
pip install Python-Gmail-Module  
  
Install GitHub Repo:  
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
LIST_OF_MAIL_IDS = MyMail.get_mail_ids()  
```  
### Get body of email by its ID  
```  
MAIL_BODY = MyMail.get_mail_body(MAIL_ID)  
```  
### Get raw email by ID  
```  
RAW_MAIL = MyMail.get_raw(MAIL_ID)  
```  
### Get Subject, Author, received date, recipiant and body of email by ID  
```  
MAIL = MyMail.get_mail(MAIL_ID)
```  
### Checks for email attachment by ID  
```
ATTACHMENT_NAMES = MyMail.attachment_state(MAIL_ID)  
```  
  
### Download attachment by ID and Attachment name ( returned by attachment_state function) to DIR  
```  
get_attachment(MAIL_ID, ATTACHMENT_NAMES[0], SAVE_PATH)  
```  
### Get a list of all mails in your inbox  
```  
all_emails = MyMail.list_mails()  
```  
### Delete email by ID  
```  
MyMail.delete_mail(MAIL_ID)  
```  
### Disconnect from smtp  
```  
MyMail.disconnect()  
```  
