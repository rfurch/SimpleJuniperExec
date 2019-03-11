#!/usr/bin/env python

# RFurch, March 2019
#
# mdified version for Juniper execution. 
# config file reading routines still available but not used
#

import  os
import  argparse
import  paramiko
import  time
import  os.path

try:
    from Configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

_verbose=False

functionalityList = []

#------------------------------------------------------------------------------------------------

# basic class to represent functionality 
class functionality(object):
    name = None
    commandToRun = None
    enableMode = False
    configTermMode = False
    presentWords = []
    notPresentWords = []
   	
	# ---------------------   
    def __init__(self, name, command=None, enable=False, configt=False, present=None, notPresent=None): 
        self.name = name or None
        self.commandToRun = command or None
        self.enableMode = enable or False
        self.configTermMode = configt or False
        self.presentWords = present or []
        self.notPresentWords = notPresent or []
        
        
    def printData(self):
        print "\n Name: " + str(self.name) + " Command: " + str(self.commandToRun)
        print "\n Enable: " + str(self.enableMode) + " Conf t: " + str(self.configTermMode)
        print "\n Present: \n"
        for i in self.presentWords:
            print "|" + str(i)
        print "\n Not Present: \n"
        for i in self.notPresentWords:
            print "|" + str(i)       
        
        
#------------------------------------------------------------------------------------------------

# reads config file in INI format, like: 

'''
[EXTENDED_ACL]
command="ip access-list extended"
enableMode=true
configTermMode=true
present="Incomplete"
[VLAN_INTERFACE]
command="int vlan"
enableMode=true
configTermMode=true
notPresent="Incomplete"
[FEXIBLE_NETFLOW]
command="show flow"
enableMode=true
notPresent="Incomplete"
'''

def readIniFile(fileName):

    # instantiate
    config = ConfigParser()
    config.optionxform = str

    if os.path.isfile(fileName):
        # parse existing file
        config.read(fileName)
        
        sections = config.sections()
        for section in sections:
#            print section

            cmd = None
            ena = False
            conft = False
            presentWords = []
            notPresentWords = [] 

            for option in config.options(section):
                
                option=option.strip()
                value = config.get(section, option).strip()
#                print "---%s---%s---" % (str(option), value)

                if str(option) == 'globalOption':
                    pass
                else:
                    if str(option) == "command":
                        cmd = str( value )
                    elif str(option) == 'enableMode':
                        if str(value).find("rue") >= 0:
                            ena = True
                    elif str(option) == 'configTermMode':
                        if str(value).find("rue") >= 0:
                            conft = True
                    elif str(option) == 'present':
                        presentWords.append(str( value ))                                    
                    elif str(option) == 'notPresent':
                        notPresentWords.append(str(value))   

            d = functionality(name=section, command = cmd, enable=ena, configt = conft, present = presentWords, notPresent = notPresentWords)
            #d.printData()
            functionalityList.append(d)
        
        return(functionalityList)
    else:
        return None                        

#------------------------------------------------------------------------------------------------

# very basic version to check ssh login and IP ACCESS LIST Features

def executeCommand(host, username, password, command):

    remoteConnectionSetup = paramiko.SSHClient()
    remoteConnectionSetup.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
	remoteConnectionSetup.connect(host, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5, banner_timeout=5, auth_timeout=5)
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials: ")
	return 
    except paramiko.SSHException as sshException:
	print("Unable to establish SSH connection: %s" % sshException)
	return 
    except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
	return 
    except:
        print("Connection error: Unable to connect to %s" % host)
	return 
    
    print "SSH connection established to %s" % host

    remoteConnection = remoteConnectionSetup.invoke_shell()
    if _verbose:
        print "Interactive SSH session established"

    remoteConnection.send("\n")
    remoteConnection.send("set cli screen-length 0\n")
    time.sleep(1)

    remoteConnection.send("configure \n")
    time.sleep(1)
    received = remoteConnection.recv(1000)
    print received

    remoteConnection.send(command)
    remoteConnection.send("\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output

    # login out 
    command='exit'
    remoteConnection.send(command)
    remoteConnection.send("\n")
    remoteConnection.send("yes\n")  #  exit without changes
    if _verbose:
        print "Executing Command: %s" % command
        time.sleep(0.5)
        output = remoteConnection.recv(10000)
        print output

    print "Closing Connection to %s" % host

    
#--------------------------------------------------------------------------------

def main():
    
    device=''
    username=''
    password=''
    configFile=''
    CLICommand=''
    global _verbose

    parser = argparse.ArgumentParser(description='Cisco Features validation via SSH.')
    parser.add_argument('-d', '--device', help='Specify a device (target router) IP', required=True)
    parser.add_argument('-u', '--username', help='Specify a login username for ssh connection', required=True)
    parser.add_argument('-p', '--password', help='Specify a password for ssh connection', required=True)
    parser.add_argument('-v', '--verbose', nargs='?', default=False, help='Enables a verbose debugging mode')
    parser.add_argument('-c', '--command', nargs='?', default=False, help='Enables a verbose debugging mode', required=True)

    args = vars(parser.parse_args())

    if args['device']:
        device = args['device']
    if args['username']:
        username = args['username']
    if args['password']:
        password = args['password']
    if args['verbose'] != False:
        _verbose = True
    if args['command']:
        CLICommand = args['command']           

    #functionList = readIniFile(configFile)

    if _verbose:
        print "verbose mode activated!  "
        print "Paramiko version is: %s" % paramiko.__version__

    executeCommand(device, username, password, CLICommand)

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    
#--------------------------------------------------------------------------------
    
