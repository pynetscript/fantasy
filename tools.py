###############################################################################
# Written by:           Aleks Lambreca
# Creation date:        24/03/2018
# Last modified date:   23/04/2018
###############################################################################


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Standard library modules
from colorama import Fore, Style
from getpass import getpass
from collections import Counter


# Get input that is Py2/Py3 compatible.
def get_input(prompt=''):
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line


# Prompts for, and returns a username and password.
def get_credentials():
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


# Count how many chars are in a string
def count_letters(x):
    counter = Counter()
    for word in x.split():
        counter.update(word)
    return sum(counter.values())
