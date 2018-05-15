[![Build Status](https://travis-ci.org/pynetscript/fantasy.svg?branch=master)](https://travis-ci.org/pynetscript/fantasy)
[![GitHub release](https://img.shields.io/badge/version-1.1-blue.svg)](https://github.com/pynetscript/fantasy)


# fantasy


### Script use           
- SSH into Cisco IOS devices and run config commands
  - Commands are send all at once (not one by one)
  - Supports both IPv4 and IPv6 addresses and FQDNs
  - Both Py2 and Py3 compatible
- The script needs 3 arguments to work:
  - 1st argument: `cmdrunner.py`
  - 2nd argument: `/x.json`
  - 3rd argument: `/x.txt`
    - A full command looks like: `./cmdrunner.py router/7200.json router/cmd.txt`

### Script input    
- Change Control/Ticket ID
- Username/Password
- Specify devices as a .json file
  - See `router/7200.json` as an example
- Specify config commands as a .txt file
  - See `router/cmd.txt` as an example   

### Script output
- Cisco IOS command output
- Statistics
- Log success/erros in `cmdrunner.log`
- Travis CI build notification to Slack private channel


# Prerequisites

- SSH (TCP/22) reachability to devices.    
- Username with privilege 15 (example: `user a.lambreca priv 15 secret cisco`).
- Alias command to save configuration: `alias exec wr copy run start`


# Installation

```
mkdir /fantasy/ && cd /fantasy/
sudo apt-get install -y python-pip
sudo apt-get install -y git
git clone -b https://github.com/pynetscript/fantasy.git . 
pip install -r requirements.txt
```

# .travis.yml

- [Travis CI](https://travis-ci.org/pynetscript/fantasy)
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
    - If password don't match each other we will get an error message `>> Passwords do not match. Please try again. ` and the script will prompt us again until passwords match each other.
        


# 3rd argument (.txt)

Create a txt file with the config commands that you want to run on the devices:    

```
router ospf 1
 network 0.0.0.0 255.255.255.255 area 0
 passive-interface default
```

        
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


# 1st argument (cmdrunner.py)

This is the main script that we will run.   

Legal examples:   
- `python2 <1st_argument> <2nd_argument> <3rd_argument>`
- `python3 <1st_argument> <2nd_argument> <3rd_argument>`

Let's use the following example to explain the script:    
- `python3 cmdrunner.py router/7200.json router/cmd.txt`

First the script will:     
- Create a log file named "cmdrunner.log".
- Prompt us for Change Control/Ticket ID.
- Prompt us for a username and a password
  - For more information on password part look "Function (get_credentials)" at **tools.py** section.

```
===============================================================================
Username: a.lambreca
Password: 
Retype password: 
===============================================================================
```
  
Then the script will:    
- Run `main()` function:
  - Timestamp the date & time the script started in D/M/Y H:M:S format.
  - Define a queue with size of 40.
  - Use multiple processors and run the ` processor(device, output_q)` function: 
    - SSH to all the devices at once in the <2nd_argument> (.json)
      - Log the successful connection in cmdrunner.log
    - Send "log" command to log "begin timestamp" & "Change Control/Ticket ID" locally on the device.
    - Get device's "hostname" from netmiko.
    - Get device's "ip" from .json
    - Run all the commands at once found in the <3rd argument> (.txt) - put into variable "output".
    - Save the running-config to startup-config - put into variable "output". 
    - Put everything from variable "output" into "output_dict".
    - Put "output_dict" into queue named "output_q".
    - Send "log" command to log "end timestamp" & "Change Control/Ticket ID" locally on the device.
    - Disconnect the SSH sessions.
    - Log the successful configuration in cmdrunner.log
    - Errors:
      - If there is an authentication error we will get an error message `23/04/2018 19:38:20 - Authentication error: r1.a-corp.com`
      - If there is a connectivity (TCP/22) error we will get an error message `23/04/2018 19:38:34 - TCP/22 connectivity error: 192.168.1.120`
      - Errors are logged in cmdrunner.log
  - Makes sure all processes have finished
  - Uses a queue to pass the output back to the parent process.
  - Timestamp the date & time the script ended in D/M/Y H:M:S format.
  - Subtract start timestamp and end timstamp to get the time (in H:M:S format) of how long the script took to run.
  - Print SCRIPT STATISTICS

```
+-----------------------------------------------------------------------------+
|                              SCRIPT STATISTICS                              |
|-----------------------------------------------------------------------------|
| Change Control/Ticket:   11111                                              |
| Script started:          23/04/2018 19:36:26                                |
| Script ended:            23/04/2018 19:36:56                                |
| Script duration (h:m:s): 0:00:30                                            |
+-----------------------------------------------------------------------------+
```

# cmdrunner.py (successful)

```
aleks@acorp:~/fantasy$ python3 cmdrunner.py router/7200.json router/cmd.txt 
===============================================================================
Change Control/Ticket: 11111
Username: a.lambreca
Password: 
Retype password: 
===============================================================================
23/04/2018 19:36:26 - Connecting to device: r1.a-corp.com
23/04/2018 19:36:26 - Connecting to device: 192.168.1.120
23/04/2018 19:36:26 - Connecting to device: 2001:db8:acab:a001::130

23/04/2018 19:36:33 - Connection to device successful: 192.168.1.120

23/04/2018 19:36:33 - Connection to device successful: 2001:db8:acab:a001::130

23/04/2018 19:36:33 - Connection to device successful: r1.a-corp.com
===============================================================================
[R3] [2001:db8:acab:a001::130] >> router/cmd.txt

config term
Enter configuration commands, one per line.  End with CNTL/Z.
R3(config)#router ospf 1
R3(config-router)# network 0.0.0.0 255.255.255.255 area 0
R3(config-router)# passive-interface default
R3(config-router)#end
R3#
-------------------------------------------------------------------------------
[R3] [2001:db8:acab:a001::130] >> write memory

Building configuration...

===============================================================================
[R2] [192.168.1.120] >> router/cmd.txt

config term
Enter configuration commands, one per line.  End with CNTL/Z.
R2(config)#router ospf 1
R2(config-router)# network 0.0.0.0 255.255.255.255 area 0
R2(config-router)# passive-interface default
R2(config-router)#end
R2#
-------------------------------------------------------------------------------
[R2] [192.168.1.120] >> write memory


Building configuration...
[OK]
===============================================================================
[R1] [r1.a-corp.com] >> router/cmd.txt

config term
Enter configuration commands, one per line.  End with CNTL/Z.
R1(config)#router ospf 1
R1(config-router)# network 0.0.0.0 255.255.255.255 area 0
R1(config-router)# passive-interface default
R1(config-router)#end
R1#
-------------------------------------------------------------------------------
[R1] [r1.a-corp.com] >> write memory

Building configuration...
[OK]
===============================================================================
+-----------------------------------------------------------------------------+
|                              SCRIPT STATISTICS                              |
|-----------------------------------------------------------------------------|
| Change Control/Ticket:   11111                                              |
| Script started:          23/04/2018 19:36:26                                |
| Script ended:            23/04/2018 19:36:56                                |
| Script duration (h:m:s): 0:00:30                                            |
+-----------------------------------------------------------------------------+
```

### syslog (successful)

```
*Apr 23 2018 19:36:33: %SYS-6-USERLOG_INFO: Message from tty2(user id: a.lambreca): "Begin Change Control/Ticket: 11111"
*Apr 23 2018 19:36:53: %SYS-6-USERLOG_INFO: Message from tty2(user id: a.lambreca): "End Change Control/Ticket: 11111"
```

### cmdrunner.log (successful)

```
23/04/2018 19:36:33 - INFO - Connection to device successful: 192.168.1.120
23/04/2018 19:36:33 - INFO - Connection to device successful: 2001:db8:acab:a001::130
23/04/2018 19:36:33 - INFO - Connection to device successful: r1.a-corp.com
23/04/2018 19:36:53 - INFO - Configuration to device successful: 2001:db8:acab:a001::130
23/04/2018 19:36:56 - INFO - Configuration to device successful: 192.168.1.120
23/04/2018 19:36:56 - INFO - Configuration to device successful: r1.a-corp.com
```

# cmdrunner.py (unsuccessful)

- R1 (r1.a-corp.com): I have misconfigured authentication.
- R2 (192.168.1.120): I have no SSH (TCP/22) reachability.
- R3 (2001:db8:acab:a001::130): This router is configured correctly.

```
aleks@acorp:~/fantasy$ python3 cmdrunner.py router/7200.json router/cmd.txt 
===============================================================================
Change Control/Ticket: 22222
Username: a.lambreca
Password: 
Retype password: 
===============================================================================
23/04/2018 19:38:16 - Connecting to device: r1.a-corp.com
23/04/2018 19:38:16 - Connecting to device: 192.168.1.120
23/04/2018 19:38:16 - Connecting to device: 2001:db8:acab:a001::130

23/04/2018 19:38:20 - Authentication error: r1.a-corp.com


23/04/2018 19:38:22 - Connection to device successful: 2001:db8:acab:a001::130

23/04/2018 19:38:34 - TCP/22 connectivity error: 192.168.1.120

===============================================================================
[R3] [2001:db8:acab:a001::130] >> router/cmd.txt

config term
Enter configuration commands, one per line.  End with CNTL/Z.
R3(config)#router ospf 1
R3(config-router)# network 0.0.0.0 255.255.255.255 area 0
R3(config-router)# passive-interface default
R3(config-router)#end
R3#
-------------------------------------------------------------------------------
[R3] [2001:db8:acab:a001::130] >> write memory

Building configuration...
[OK]
===============================================================================
+-----------------------------------------------------------------------------+
|                              SCRIPT STATISTICS                              |
|-----------------------------------------------------------------------------|
| Change Control/Ticket:   22222                                              |
| Script started:          23/04/2018 19:38:16                                |
| Script ended:            23/04/2018 19:38:43                                |
| Script duration (h:m:s): 0:00:26                                            |
+-----------------------------------------------------------------------------+
```


### syslog (unsuccessful)

```
*Apr 23 2018 19:38:23: %SYS-6-USERLOG_INFO: Message from tty2(user id: a.lambreca): "Begin Change Control/Ticket: 22222"
*Apr 23 2018 19:38:40: %SYS-6-USERLOG_INFO: Message from tty2(user id: a.lambreca): "End Change Control/Ticket: 22222"
```

### cmdrunner.log (unsuccessful)

```
23/04/2018 19:38:20 - WARNING - Authentication failure: unable to connect cisco_ios r1.a-corp.com:22
Authentication failed.
23/04/2018 19:38:22 - INFO - Connection to device successful: 2001:db8:acab:a001::130
23/04/2018 19:38:34 - WARNING - Connection to device timed-out: cisco_ios 192.168.1.120:22
23/04/2018 19:38:43 - INFO - Configuration to device successful: 2001:db8:acab:a001::130
```
