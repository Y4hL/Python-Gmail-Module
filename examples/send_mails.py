from mailpy import send_gmail

# mailpy Example
#
# Send mails with and without attachments

if __name__ == '__main__':

    # Mail without attachment
    send_gmail('Gmail Address', 'Gmail Password', 'Recipiant Email Address', 'Subject', 'Body')

    # Give Attachements with Paths
    ATTACHMENTS = ['MyPath/File.txt', 'MyPath/File2.pdf']

    # NOTE:
    # You cannot send files that are a security risk
    # For Example: File.exe

    # Send Mail with Attachments
    send_gmail('Gmail Address', 'Gmail Password', 'Recipiant Email Address', 'Subject', 'Body', FILE_LOCATION=ATTACHMENTS)
