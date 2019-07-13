from mailpy import Gmail

# mailpy Example
#
# Get Body of a Mail

if __name__ == '__main__':

    # Initialize Connection
    Client = Gmail()

    # Login
    Client.login('Gmail Address', 'Gmail Password')

    # Get list of mail ids
    MAIL_IDS = Client.get_mail_ids()

    # Check if MAIL_IDS is empty
    if MAIL_IDS != []: 

        # Deletes latest mail
        BODY = Client.get_mail_body(MAIL_IDS[0])

        # Prints Body
        print(BODY)

    # Disconnect Client
    Client.logout()
