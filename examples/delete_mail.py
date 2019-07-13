from mailpy import Gmail

# mailpy Example
#
# Delete a Mail

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
        Client.delete_mail(MAIL_IDS[-1])

    # Disconnect Client
    Client.logout()
