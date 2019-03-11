# Python-Gmail-Module
Easily Send, Read and Download attachments from Gmail with Python  
  
# Example
```
# Import the module
from gcm import *

# Authenticate a connection
con = auth("email", "password")

# Gets a list of email ids and prints the amount of mails
list_of_mail_ids = get_mail_ids(con)
amount_of_mails = str(len(list_of_mail_ids))
print("The amount of mails is " + amount_of_mails)

# Get body of first email in the list and prints it
body_of_email = get_email_body(con, list_of_mail_ids[0])
print(body_of_email)

# Gets Subject, Sender, received date, recipiant and body
# of the second email in the list and prints it
second_email = get_mail(con, list_of_mail_ids[1])
print(second_email)

# Checks if the second email has a attachment
# If so, downloads it
state = attachment_state(con, list_of_mail_ids[2])
if not state:
    print("There is no attachment")
else:
    print("There is a attachment")
    get_attachment(con, list_of_mail_ids[2], "save_path")

# Gets a list of all mails in your inbox
all_emails = list_mails(con)
for email in all_emails:
    print(email)

```
