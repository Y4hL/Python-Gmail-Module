from mailpy import Gmail

# mailpy Example
#
# Filter Mail by Subject


if __name__ == "__main__":

    # String to filter by
    FILTER = ''

    # Initialize Connection
    Client = Gmail()

    # Login
    Client.login('Gmail Address', 'Gmail Password')

    # Get list of mail ids
    MAIL_IDS = Client.get_mail_ids()

    # List to store filtered mail ids
    FILTERED_MAIL_IDS = []

    # Loop through list of mail ids
    for MAIL_ID in MAIL_IDS:

        # Filter mail subjects
        if FILTER in Client.get_mail_subject(MAIL_ID):

            # Append matched mail id
            FILTERED_MAIL_IDS.append(MAIL_ID)

    # Disconnect Client
    Client.logout()


    if FILTERED_MAIL_IDS == []:

        # If no mails matched
        print("No Mails Matched!")

    else:

        # Print filtered mail ids
        print(FILTERED_MAIL_IDS)
