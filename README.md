[![Build Status](https://travis-ci.org/pynetscript/fantasy.svg?branch=master)](https://travis-ci.org/pynetscript/fantasy)
[![GitHub release](https://img.shields.io/badge/version-1.1-blue.svg)](https://github.com/pynetscript/reality)
[![license](https://img.shields.io/github/license/pynetscript/fantasy.svg)](https://github.com/pynetscript/fantasy/blob/master/LICENSE)

# fantasy

```
Written by:           Aleks Lambreca
Creation date:        05/04/2018
Last modified date:   05/04/2018
Version:              v1.1

Script use:           SSH into Cisco IOS devices and run config/show commands
                      Note: Commands are all at once (not one by one)
                            Supports both IPv4 and IPv6 addresses and FQDNs
                            Both Py2 and Py3 compatible
                      The script needs 3 arguments to work:
                      - 1st argument: cmdrunner.py
                      - 2nd argument: /x.json
                      - 3rd argument: /x.txt
                      Note: A full command looks like:
                      ./cmdrunner.py router/7200.json router/cmd.txt

Script input:         SSH Username/Password
                      Specify devices as a .json file
                      Note: See "router/7200.json" as an example
                      Specify show/config commands as a .txt file
                      Note: Show commands need "do" in the front
                            See "router/cmd.txt" as an example

Script output:        Cisco IOS command output
                      Statistics
                      Erros in cmdrunner.log
                      Travis CI build notification to Slack private channel
```

# Prerequisites

0. Box with latest version of [git](https://git-scm.com/) installed.
1. Box with [netmiko 2.1.0](https://github.com/ktbyers/netmiko) installed (included in requirements.txt).
2. Box with [colorama 0.3.9](https://pypi.python.org/pypi/colorama) installed (included in requirements.txt).
3. SSH (TCP/22) reachability to devices.    
4. Local username with privilege 15 (example: `user a.lambreca priv 15 secret cisco`).
5. Alias command to save configuration: `alias exec wr copy run start`

# Installation

```
mkdir /fantasy/ && cd /fantasy/
sudo apt-get install -y git
git clone -b https://github.com/pynetscript/fantasy.git . 
pip install -r requirements.txt
```

# .travis.yml

- [Travis CI](https://travis-ci.org/pynetscript/reality)
- What language: **Python**
- What versions: **2.7** , **3.4** , **3.5** , **3.6**
- What to install: **pip install -r requirements.txt**
- What to run: **python cmdrunner.py**
- Where to send notifications: **pynetscript:3GF5L6jlBvYl9TA5mrcJ87rq** 
  - Install Travis CI on [Slack](https://pynetscript.slack.com) and at some point it will output a slack channel to use.
  - Replace **pynetscript:3GF5L6jlBvYl9TA5mrcJ87rq** with your own channel.
  - Supports private channels.


# tools.py

- tools.py is going to be imported on our main script (cmdrunner.py).
- This way we have a cleaner main script.
- Function (get_input)
    - Get input that is both Py2 and Py3 compatible
- Function (get_credentials) 
    - Prompts for username
    - Prompts for password twice but doesn't show it on screen (getpass)
        - If passwords match each other the script will continue to run
        - If password don't match each other you will get an error message `>> Passwords do not match. Try again. ` but the script will continue to run. Use Ctrl + C to cancel the script and run it again.
        
# 2nd argument (.json)

- Create a csv file like this example:  

```CSV
device_type,ip
cisco_ios,r1.a-corp.com
cisco_ios,192.168.1.120
cisco_ios,2001:db8:acab:a001::130
```

- Go to [Mr. Data Converter](https://shancarter.github.io/mr-data-converter/).
- Copy/paste the CSV input into the **Input CSV or tab-delimited data**.
- On the bottom, in the **Output as** choose  **JSON - Properties**.
- On the left, in the **Delimiter** and in the **Decimal Sign** choose **Comma**.
- This is what you should get from the example above.

```
[{"device_type":"cisco_ios","ip":"r1.a-corp.com"},
{"device_type":"cisco_ios","ip":"192.168.1.120"},
{"device_type":"cisco_ios","ip":"2001:db8:acab:a001::130"}]
```

- Finally i copy/pasted the output into router/7200.json which is going to be used by cmdrunner.py as the <2nd_argument>.   

# 3rd argument (.txt)

Create a txt file with the config/show commands that you want to run on the devices:    
Note: Show commands need "do" in the front.

```
router ospf 1
 network 0.0.0.0 255.255.255.255 area 0
 passive-interface default
```

# 1st argument (cmdrunner.py)

This is the main script that we will run.   
Legal examples:   
- `python2 <1st_argument> <2nd_argument> <3rd_argument>`
- `python3 <1st_argument> <2nd_argument> <3rd_argument>`

Let's use the following example to explain the script:    
- `python3 cmdrunner.py router/7200.json router/cmd.txt`

First the script will:     
- Create a log file named "cmdrunner.log".
- Prompt us for a username and a password (password required twice).

```
===============================================================================
Username: a.lambreca
Password: 
Retype password: 
===============================================================================
```
  
Then the script will:    
- Timestamp the date & time the script started in D/M/Y H:M:S format.
- SSH to the first device in the <2nd_argument> (.json)    
- Run all the commands in the <3rd argument> (.txt) 
- Save the running-config to startup-config.  
- Disconnect the SSH session.  

Errors:
- If the is an authentication error we will get an error message `R1.a-corp.com >> Authentication error`
- If the is an connectivity (TCP/22) error we will get an error message `192.168.1.120 >> TCP/22 connectivity error`
- Errors are logged in the cmdrunner.log

Finally the script will:
- Repeat the process for all devices in <2nd_argument> (.json) 
- Timestamp the date & time the script ended in D/M/Y H:M:S format.
- Subtract start timestamp and end timstamp to get the time (in H:M:S format) of how long the script took to run.
- Print SCRIPT STATISTICS

```
+-----------------------------------------------------------------------------+
|                              SCRIPT STATISTICS                              |
|-----------------------------------------------------------------------------|
| Script started:           24/03/2018 15:47:48                               |
| Script ended:             24/03/2018 15:49:45                               |
| Script duration (h:m:s):  0:01:57                                           |
+-----------------------------------------------------------------------------+
```

# Successful demo

```

```

# Unsuccessful demo

- R1 (r1.a-corp.com): I have misconfigured authentication.
- R2 (192.168.1.120): I have no SSH (TCP/22) reachability.
- R3 (2001:db8:acab:a001::130): This router is configured correctly.

```

```

# cmdrunner.log

```

```
