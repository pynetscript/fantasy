#!/usr/bin/python

###############################################################################
# Written by:           Aleks Lambreca
# Creation date:        05/04/2018
# Last modified date:   05/08/2018
# Version:              v1.1
#
# Script use:           SSH into Cisco IOS devices and run config commands
#                       Note: Commands are send all at once (not one by one)
#                             Supports both IPv4 and IPv6 addresses and FQDNs
#                             Both Py2 and Py3 compatible
#                       The script needs 3 arguments to work:
#                       - 1st argument: cmdrunner.py
#                       - 2nd argument: /x.json
#                       - 3rd argument: /x.txt
#                       Note: A full command looks like:
#                       ./cmdrunner.py router/7200.json router/cmd.txt
#
# Script input:         Change Control/Ticket ID
#                       Username/Password
#                       Specify devices as a .json file
#                       Note: See "router/7200.json" as an example
#                       Specify show/config commands as a .txt file
#                       Note: See "router/cmd.txt" as an example
#
# Script output:        Cisco IOS command output
#                       Statistics
#                       Log success/erros in cmdrunner.log
#                       Travis CI build notification to Slack private channel
###############################################################################


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard library modules
import netmiko
import json
import sys                      
import signal                   # Capture and handle signals past from the OS.
import datetime
import time
import logging
import os
import re

from multiprocessing import Process, Queue
from colorama import Fore, Style

# Local modules
import tools


# Logs on the working directory on the file named cmdrunner.log
logger = logging.getLogger('__name__')
hdlr = logging.FileHandler('cmdrunner.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOERror: Broken pipe
signal.signal(signal.SIGINT, signal.SIG_DFL)   # KeyboardInterrupt: Ctrl-C


# If connection times out, the script will continue to run.
# If authentication fails, the script will continue to run.
netmiko_ex_time = (netmiko.ssh_exception.NetMikoTimeoutException)
netmiko_ex_auth = (netmiko.ssh_exception.NetMikoAuthenticationException)


# If arguments not equal to 3 we get an error.
if len(sys.argv) != 3:
    print('>> Usage:', sys.argv[0].split('/')[-1], '/x.json /x.txt')
    exit()

    
with open(sys.argv[1]) as dev_file:
    devices = json.load(dev_file)

with open(sys.argv[2]) as cmd_file:
    path = (sys.argv[2])
    commands = cmd_file.readlines()

    
# Prompt for Change Control/Ticket ID
print(Fore.WHITE + '='*79 + Style.RESET_ALL)
cc = tools.get_input('Change Control/Ticket: ')
    
    
# Prompt for username and password
username, password = tools.get_credentials()


def processor(device, output_q):
    device['username'] = username
    device['password'] = password
    try:
        current_timestamp = datetime.datetime.now()
        current_time = current_timestamp.strftime('%d/%m/%Y %H:%M:%S')
        print(current_time, '- Connecting to device:', device['ip'])

        output_dict = {}

        # SSH into each device from "x.json" (2nd argument).
        connection = netmiko.ConnectHandler(**device)

        print()
        current_timestamp = datetime.datetime.now()
        current_time = current_timestamp.strftime('%d/%m/%Y %H:%M:%S')
        success_connected = (current_time, '- Connection to device successful:', device['ip'])
        success_connected_str = ' '.join(success_connected)
        print(Fore.GREEN + success_connected_str + Style.RESET_ALL)
        
        # Log the successful connection on the working directory in "cmdrunner.log".
        # Parse out the date & time.
        regex = r'(\d+/\d+/\d+\s+\d+:\d+:\d+\s+-\s+)(.*)'
        m_conn = re.match(regex, success_connected_str)
        logger.info(m_conn.group(2))
        
        # Get device's "hostname" from netmiko, and "ip" from .json
        hostname = connection.base_prompt
        ip = (device['ip'])

        # Log "start" locally on the device.
        connection.send_command('send log 6 "Begin Change Control/Ticket: {}"'.format(cc))
        
        # Send all commands at once from "x.txt" to each device (3rd argument).
        # Put into "output". 
        output = ('') + "\n"
        output += connection.send_config_set(commands) + "\n"
        output += ('-'*79) + "\n"

        # Save running-config to startup-config.
        # Put into "output". 
        save_conf = connection.send_command_timing('write memory')
        if 'Overwrite the previous NVRAM configuration?[confirm]' in save_conf:
            save_conf = connection.send_command_timing('')
        if 'Destination filename [startup-config]' in save_conf:
            save_conf = connection.send_command_timing('')
        output += ('[{0}] [{1}] >> write memory'.format(hostname, ip)) + "\n"
        output += ('') + "\n"
        output += (save_conf)
        
        # Put everything from "output" into "output_dict" in the format "[hostname]  IP".
        output_dict[Fore.WHITE + '='*79 + Style.RESET_ALL + '\n' + '[{0}] [{1}] >> '.format(hostname, ip) + path] = output
        
        # Put "output_dict" into queue named "output_q".
        output_q.put(output_dict)

        
        # Log "end" locally on the device.
        connection.send_command('send log 6 "End Change Control/Ticket: {}"'.format(cc))
        
        # Disconnect SSH session.
        connection.disconnect()

        # Log the successful configuration on the working directory in cmdrunner.log
        success_configured = ('Configuration to device successful:', device['ip'])
        success_configured_str = ' '.join(success_configured)
        logger.info(success_configured_str)
        
        
    except netmiko_ex_auth as ex_auth:
        print()
        current_timestamp = datetime.datetime.now()
        current_time = current_timestamp.strftime('%d/%m/%Y %H:%M:%S')
        print(Fore.RED + current_time, '- Authentication error:', device['ip'] + Style.RESET_ALL)
        # Log the error on the working directory in cmdrunner.log
        logger.warning(ex_auth)
        print()

    except netmiko_ex_time as ex_time:
        print()
        current_timestamp = datetime.datetime.now()
        current_time = current_timestamp.strftime('%d/%m/%Y %H:%M:%S')
        print(Fore.RED + current_time, '- TCP/22 connectivity error:', device['ip'] + Style.RESET_ALL)
        # Log the error on the working directory in cmdrunner.log
        logger.warning(ex_time)
        print()


def main():
    # Script start timestamp and formatting
    start_timestamp = datetime.datetime.now()
    start_time = start_timestamp.strftime('%d/%m/%Y %H:%M:%S')
    
    output_q = Queue(maxsize=40)

    # Use processes and run the "processor" function. 
    procs = []
    for device in devices:
        my_proc = Process(target=processor, args=(device, output_q))
        my_proc.start()
        procs.append(my_proc)

    # Make sure all processes have finished
    for a_proc in procs:
        a_proc.join()

    # Use a queue to pass the output back to the parent process.
    while not output_q.empty():
        my_dict = output_q.get()
        for k, val in my_dict.items():
            print(k)
            print(val)

    # Script end timestamp and formatting
    end_timestamp = datetime.datetime.now()
    end_time = end_timestamp.strftime('%d/%m/%Y %H:%M:%S')

    # Script duration and formatting
    total_time = end_timestamp - start_timestamp
    total_time = str(total_time).split(".")[0]

    # Count how many chars is Change Control/Ticket and subtract 50 from it.
    # Result (rest) used in SCRIPT STATISTICS
    cc_counter = tools.count_letters(cc)
    rest = 50 - cc_counter
    
    # SCRIPT STATISTICS
    print(Fore.WHITE + '='*79 + Style.RESET_ALL)
    print("+" + "-"*77 + "+")
    print("|" + " "*30 + "SCRIPT STATISTICS" +       " "*30 + "|")
    print("|" + "-"*77 + "|")
    print("| Change Control/Ticket:  ", cc,          " "*rest + "|")
    print("| Script started:          ", start_time, " "*30 + "|")
    print("| Script ended:            ", end_time,   " "*30 + "|")
    print("| Script duration (h:m:s): ", total_time, " "*42 + "|")
    print("+" + "-"*77 + "+")


if __name__ == "__main__":
    main()
