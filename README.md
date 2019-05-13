# Python-Gmail-Module
Easily Send, Read and Download attachments from Gmail with Python  

# Setup  
  
SMTP login method is not enabled by default.  
Enable it [here](https://myaccount.google.com/lesssecureapps)  
  
Alternatively if you have 2fa enabled,  
you will need to create a app password [here](https://myaccount.google.com/apppasswords)  
  
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

### Get a list of email ids and print the amount of mails
```
list_of_mail_ids = MyMail.get_mail_ids()
amount_of_mails = str(len(list_of_mail_ids))
print("The amount of mails is " + amount_of_mails)
```
### Get body of first email in the list and prints it
```
body_of_email = MyMail.get_mail_body(list_of_mail_ids[0])
print(body_of_email)
```
### Get raw email
```
raw_email = MyMail.get_raw(list_of_mail_ids[0])
print(raw_email)
```
### Get Subject, Author, received date, recipiant and body of the second email in the list and print it
```
second_email = MyMail.get_mail(list_of_mail_ids[1])
print(second_email)
```
### Check if the second email has a attachment. If so, download it
```
state = MyMail.attachment_state(list_of_mail_ids[2])
if not state:
    print("There is no attachment")
else:
    print("There is a attachment")
    MyMail.get_attachment(list_of_mail_ids[2], "save_path")
```

### Get a list of all mails in your inbox
```
all_emails = MyMail.list_mails()
for email in all_emails:
    print(email)
```
### Delete first email
```
MyMail.delete_mail(list_of_mail_ids[0])
```
### Disconnect from smtp
```
MyMail.disconnect()
```
