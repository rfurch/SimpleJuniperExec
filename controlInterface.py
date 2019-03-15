#!/usr/bin/env python

# RFurch, March 2019
#
# mdified version for Juniper execution. 
# config file reading routines still available but not used
# This program set interface status to ENABLE / DISABLE, 
# testing condition via: 
#
# run show interfaces NAME terse | match up | count
#
# or 
#
# run show interfaces NAME terse | match down | count
#
# Command to DISABLE interface:    
# set interfaces NAME disable 
#
# Command to ENABLE interface:    
# delete interfaces NAME disable 
#
#

import  os
import  argparse
import  paramiko
import  time
import  os.path

_verbose=False

#------------------------------------------------------------------------------------------------

# very basic version to check ssh login and IP ACCESS LIST Features

def setInterfaceStatus(host, username, password, interface, requiredStatus):

    command=""
    currentInterfaceStatus=''
    finalInterfaceStatus=''
	
    paramiko.util.log_to_file('output.txt')
    
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
    #print received

    time.sleep(1) 
    remoteConnection.send("set cli screen-length 0\n")
    time.sleep(1) 
    received = remoteConnection.recv(1000)
    #print received

    remoteConnection.send("configure \n")
    time.sleep(1)
    received = remoteConnection.recv(1000)
    #print received

	# get interface status by checking:
	# run show interfaces NAME terse | trim 20 | find up
    remoteConnection.send("run show interfaces " + interface + " terse | trim 20 | find up\n")
    time.sleep(1)
    output = remoteConnection.recv(10000)
    #print output

    if output.find('attern not found') >= 0:
        print "interface " + interface + " seems to be Admin. DOWN" 	
        currentInterfaceStatus=False
    else:
        print "interface " + interface + " seems to be Admin. UP" 	
        currentInterfaceStatus=True

    if (currentInterfaceStatus == True and requiredStatus ==  True) or (currentInterfaceStatus == False and requiredStatus ==  False):    
        print "NOTHING TO DO!!!  ---- ABORTING !!!"
    else:
        print "Interface " + interface + " will be set to " + ("UP" if requiredStatus == True else "DOWN")
		
		# build and execute ENABLE / DISABLE commands	
        if requiredStatus == True:
			command = "delete interfaces " + interface + " disable" 
        else:
            command = "set interfaces " + interface + " disable" 

#        print command
        remoteConnection.send(command + "\n")
        time.sleep(1)
        remoteConnection.send("commit\n")
        time.sleep(1)
        output = remoteConnection.recv(10000)

		# get interface FINAL status
        remoteConnection.send("run show interfaces " + interface + " terse | trim 20 | find up\n")
        time.sleep(1)
        output = remoteConnection.recv(10000)
        #print output
        
        
        if output.find('attern not found') >= 0:		
			print "interface " + interface + " successfully set to Admin. DOWN" 	
			finalInterfaceStatus=False
        else:
			print "interface " + interface + " successfully set to Admin. UP" 	
			finalInterfaceStatus=True
			
        if (finalInterfaceStatus == True and requiredStatus ==  True) or (finalInterfaceStatus == False and requiredStatus ==  False):
			print "ALL DONE!"
        else:
			print "ERROR setting Interface " + interface + " will be set to " + ("UP" if requiredStatus == True else "DOWN")




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
	interface=''
	status=''
	global _verbose

	parser = argparse.ArgumentParser(description='Cisco Features validation via SSH.')
	parser.add_argument('-d', '--device', help='Specify a device (target router) IP', required=True)
	parser.add_argument('-u', '--username', help='Specify a login username for ssh connection', required=True)
	parser.add_argument('-p', '--password', help='Specify a password for ssh connection', required=True)
	parser.add_argument('-i', '--interface', help='Specify a INTERFACE NAME to enable / disable ', required=True)
	parser.add_argument('-s', '--status', help='Specify desired STATUS: 0 -> DISABLE   1 -> ENABLE', required=True)
	parser.add_argument('-v', '--verbose', nargs='?', default=False, help='Enables a verbose debugging mode')

	args = vars(parser.parse_args())

	if args['device']:
		device = args['device']
	if args['username']:
		username = args['username']
	if args['password']:
		password = args['password']
	if args['interface']:
		interface = args['interface']
	if args['status']:
		status = True if args['status'] == '1' else False 
	if args['verbose'] != False:
		_verbose = True

	if _verbose:
		print "verbose mode activated!  "
		print "Paramiko version is: %s" % paramiko.__version__

	setInterfaceStatus(device, username, password, interface, status)

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    
#--------------------------------------------------------------------------------
    
