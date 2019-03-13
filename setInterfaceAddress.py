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

_verbose=False

#------------------------------------------------------------------------------------------------

# very basic version to check ssh login and IP ACCESS LIST Features

def executeCommand(host, username, password):

    command=""
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

    time.sleep(1) 
    remoteConnection.send("cli\n")
    received = remoteConnection.recv(1000)
    print received

    time.sleep(1) 
    remoteConnection.send("set cli screen-length 0\n")
    time.sleep(1) 
    received = remoteConnection.recv(1000)
    print received

    remoteConnection.send("configure \n")
    time.sleep(1)
    received = remoteConnection.recv(1000)
    print received

    # set ip on loopback 
    remoteConnection.send("set interfaces lo0.2001 family inet  address 10.10.10.1/24\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output

    # commit and show
    remoteConnection.send("commit\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output


    remoteConnection.send("run show configu\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output

    # delete  ip on loopback 
    remoteConnection.send("delete interfaces lo0.2001 family inet  address 10.10.10.1/24\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output

    # commit and show
    remoteConnection.send("commit\n")
    print "Executing Command: %s" % command
    time.sleep(1)
    output = remoteConnection.recv(10000)
    print output


    remoteConnection.send("run show configu\n")
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
    global _verbose

    parser = argparse.ArgumentParser(description='Cisco Features validation via SSH.')
    parser.add_argument('-d', '--device', help='Specify a device (target router) IP', required=True)
    parser.add_argument('-u', '--username', help='Specify a login username for ssh connection', required=True)
    parser.add_argument('-p', '--password', help='Specify a password for ssh connection', required=True)
    parser.add_argument('-v', '--verbose', nargs='?', default=False, help='Enables a verbose debugging mode')

    args = vars(parser.parse_args())

    if args['device']:
        device = args['device']
    if args['username']:
        username = args['username']
    if args['password']:
        password = args['password']
    if args['verbose'] != False:
        _verbose = True

    #functionList = readIniFile(configFile)

    if _verbose:
        print "verbose mode activated!  "
        print "Paramiko version is: %s" % paramiko.__version__

    executeCommand(device, username, password)

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    
#--------------------------------------------------------------------------------
    
