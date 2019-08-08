# Input Handling
import platform
import getpass

# Communication
import mailpy

# Logo
import os
from pyfiglet import Figlet

def win_getpass(prompt='Password: ', stream=None):
    """Prompt for password with echo off, using Windows getch()."""

    """Credit: https://stackoverflow.com/a/16670956"""

    # Windows Import
    import sys
    
    if sys.stdin is not sys.__stdin__:
        print('Warning: Password input may be echoed.')
        PASSWORD = input(prompt)
        return PASSWORD

    # Windows Import
    import msvcrt
    
    for c in prompt:
        msvcrt.putwch(c)
    pw = ""
    while 1:
        c = msvcrt.getwch()
        if c == '\r' or c == '\n':
            break
        if c == '\003':
            raise KeyboardInterrupt
        if c == '\b':
            if pw == '':
                pass
            else:
                pw = pw[:-1]
                msvcrt.putwch('\b')
                msvcrt.putwch(" ")
                msvcrt.putwch('\b')
        else:
            pw = pw + c
            # msvcrt.putwch("")
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    return pw


def get_password(prompt='Password: '):
    
    PLATF = platform.system()

    if PLATF == 'Windows':
        PASSWORD = win_getpass(prompt=prompt)
    elif PLATF == 'Linux':
        PASSWORD = getpass.getpass(prompt=prompt)
    else:
        print('Warning: Password input may be echoed.')
        PASSWORD = input(prompt)

    return PASSWORD


def cli():

    if platform.system() == 'Windows':
        os.system('title mailpy - v{}'.format(mailpy.__version__))

    LOGO = """
                        _ __           
       ____ ___  ____ _(_) /___  __  __
      / __ `__ \/ __ `/ / / __ \/ / / /
     / / / / / / /_/ / / / /_/ / /_/ / 
    /_/ /_/ /_/\__,_/_/_/ .___/\__, /  
                       /_/    /____/   
                v{}
""".format(mailpy.__version__)
    
    print(LOGO)

    Client = mailpy.Gmail()

    login = False

    while not login:
    
        EMAIL = input('Gmail: ')
        PASSWORD = get_password()

        try:
            Client.login(EMAIL, PASSWORD)
            login = True
        except:
            continue

    print('Login Successful!')

    MAILS = Client.list_mails()

    for MAIL in MAILS:

        print("""ID: {}\n
From: {}\n
Date: {}\n
Subject: {}
\n
Body:\n
{}\n\n""".format(MAIL['Id'], MAIL['From'], MAIL['Date'], MAIL['Subject'], MAIL['Body']))


if __name__ == '__main__':
    cli()
