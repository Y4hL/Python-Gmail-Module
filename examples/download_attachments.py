from mailpy import Gmail
import platform
import os

# mailpy Example
#
# Download Attachments with PGM

# CAUTION
#
# This example downloads ALL attachments in all mails.
# Use this with extreme caution!

if __name__ == '__main__':

    # Get OS
    OS = platform.platform()
    
    # Set Download Path depending on OS
    if OS == "Linux" or OS == 'Darwin': # If OS is Linux or Mac

        Path = os.environ['HOME'] + '/Desktop'
    
    elif OS == 'Windows': # If OS is Windows

        Path = os.environ['USERPROFILE'] + '\\Desktop'

    else: # If OS is something else

        raise SystemError('{} is not supported.'.format(OS))

    
    # Initialize Connection
    Client = Gmail()

    # Login
    Client.login('Gmail Address', 'Gmail Password')

    # Get list of mail ids
    MAIL_IDS = Client.get_mail_ids()

    # Loop through list of mail ids
    for MAIL_ID in MAIL_IDS:

        # Get attachment names
        Attachments = Client.attachment_state(MAIL_ID)

        # Check if there is an attachment(s)
        if Attachments == []:

            continue
        
        # Loop through attacgments in mail
        for Attachment in Attachments:

            # Download Attachment
            Client.get_attachment(MAIL_ID, Attachment, Path)
    
    # Disconnect Client
    Client.logout()

    
