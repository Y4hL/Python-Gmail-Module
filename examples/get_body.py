from PGM import MailReader

# PGM Example
#
# Get Body of a Mail

if __name__ == '__main__':

    # Initialize Connection
    Client = MailReader('Gmail Address', 'Gmail Password')

    # Get list of mail ids
    MAIL_IDS = Client.get_mail_ids()

    # Check if MAIL_IDS is empty
    if MAIL_IDS == []: 

        # Raise Exception if there are no emails
        raise Exception('You have no mails in your Indox')

    else:

         # Deletes latest mail
        BODY = Client.get_mail_body(MAIL_IDS[0])

        # Prints Body
        print(BODY)

    # Disconnect Client
    Client.disconnect()