from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from colorama import init
from colorama import Fore
from colorama import Style
from getpass import getpass


# Function - Get input that is Py2/Py3 compatible.
def get_input(prompt=''):
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line


# Function - Prompts for, and returns a username and password.
def get_credentials():
    print(Fore.WHITE + '='*79 + Style.RESET_ALL)
    username = get_input('Username: ')
    password = None
    while not password:
        password = getpass()
        password_verify = getpass('Retype password: ')
        if password != password_verify:
            print(Fore.RED+'>> Passwords do not match. Please try again.' + Style.RESET_ALL)
            password = None
            continue
        print(Fore.WHITE + '='*79 + Style.RESET_ALL)
        return username, password
