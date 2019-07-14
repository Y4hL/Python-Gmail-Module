from mailpy import Gmail

# mailpy Example
#
# Send mails with and without attachments

if __name__ == '__main__':

    Client = Gmail()

    Client.login('Gmail Address', 'Gmail Password')

    # Mail without attachment
    Client.send('Recipiant Email Address', 'Subject', 'Body')

    # Give Attachements with Paths
    ATTACHMENTS = ['MyPath/File.txt', 'MyPath/File2.pdf']

    # NOTE:
    # You cannot send files that are a security risk
    # For Example: File.exe

    # Send Mail with Attachments
    Client.send('Recipiant Email Address', 'Subject', 'Body', FILE_LOCATION=ATTACHMENTS)

    # Close connection
    Client.logout()
