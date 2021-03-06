#!/usr/bin/env python

# The primary goal of nethydra is to connect to an organiation's network infrastructure devices that support a CLI and make
# small configuration changes to allow OneTeam's primary monitoring tools access to the devices

import sys
from netmiko import ConnectHandler
import netmiko
import socket
from ciscoconfparse import CiscoConfParse
import logging
import logging.config
import os
import json
import csv

# Setup logging
default_level=logging.DEBUG
path = 'logging.json'
if os.path.exists(path):
	with open(path, 'rt') as f:
		config = json.load(f)
		logging.config.dictConfig(config)
else:
	logging.basicConfig(level=default_level)

logger = logging.getLogger(__name__)

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException)

def main():
	#devices =

	with open('nyap-devices.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
           	# For connections to local devices the IP can be used, through a tunnel use the hostname
			ip = row['ip']
			port = row['port']
			device_type = row['device_type']

			logger.debug('CONNECTING TO {0}'.format(ip)) 

			try:
				net_connect.enable()

				logger.info("Sending command...")
				output = net_connect.send_command("show running-config")

				logger.debug("Opening the temp file for config retreival")
				f=open("/home/nocops/scripts/nethydra/output/192.168.1.1-config.txt", "w+")
				f.write(output)
				f.close()

				net_connect.disconnect()

				logger.debug("Parsing the config")
				parse = CiscoConfParse("/home/nocops/scripts/nethydra/output/192.168.1.1-config.txt", syntax='ios')
				for obj in parse.find_objects(r"access-list"):
					print "Object:", obj
					print "Text:", obj.text
			except netmiko_exceptions as e:
				logger.debug('{0} - Failed to retrieve the config'.format(ip), exc_info=True)
				continue
			except Exception:
				logger.debug('SSH exception', exc_info=True)


def connect(ip, port, device_type, username, password, secret, ssh_config_file):
	iport = int(port)
	# Need to see if ssh_config_file is supplied, if not don't use it in the ConnecHandler
	#if check_port(ip, iport): #Had to disable for SSH proxy routing - can't directly ping
	try:
		device = {}
		device['ip'] = ip
		device['port'] = port
		device['device_type'] = device_type
		device['username'] = username
		device['password'] = password
		device['secret'] = secret
		device['ssh_config_file'] = ssh_config_file
		device['verbose'] = True
		net_connect = ConnectHandler(**device)
		return net_connect
	except netmiko_exceptions as e:
		logger.debug('{0} - Connection failed for {1}'.format(ip, username), exc_info=True)


def check_port(ip, port):
	# Create a TCP socket
	s = socket.socket()
	con_log.info('{0} - Connecting on port {1}'.format(ip, port))
	try:
		s.connect((ip, port))
		con_log.info('{0} - Port {1} OPEN'.format(ip, port))
		return True
	except socket.error, e:
		logger.error('{0} - Port {1} CLOSED'.format(ip, port), exc_info=True)
		return False


if __name__ == '__main__':
    main()
