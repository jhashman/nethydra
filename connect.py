#!/usr/bin/env python

import sys
from netmiko import ConnectHandler
import netmiko
import socket
import logging
import local

con_log = logging.getLogger('NetHydra')

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,netmiko.ssh_exception.NetMikoAuthenticationException)


def direct(ip, port, device_type, username, password, enable):
	try:
		iport = int(port)
		check_port(ip, iport)
		
		device = {}
		device['ip'] = ip
		device['port'] = port
		device['device_type'] = device_type
		device['username'] = username
		device['password'] = password
		device['secret'] = enable
		device['verbose'] = False
		
		net_connect = ConnectHandler(**device)
		con_log.info('{0} - CONNECTION SUCCESSFUL'.format(ip))

		return net_connect
	except Exception:
		con_log.error('{0} - CONNECTION FAILED'.format(ip))
		if local.password2:
			device['username'] = local.username2
			device['password'] = local.password2
			net_connect = ConnectHandler(**device)
			con_log.info('{0} - CONNECTION SUCCESSFUL - 2nd user'.format(ip))
			return net_connect

'''				
def tunnel(ip, port, device_type, username, password, secret, ssh_config_file):
	iport = int(port)
	# Need to see if ssh_config_file is supplied, if not don't use it in the ConnecHandler
	try:
		device = {}
		device['ip'] = ip
		device['port'] = port
		device['device_type'] = device_type
		device['username'] = username
		device['password'] = password
		device['secret'] = secret
		device['ssh_config_file'] = ssh_config_file
		device['verbose'] = False
		net_connect = ConnectHandler(**device)
		return net_connect
	except netmiko_exceptions as e:
		con_log.warn('{0} - Connection failed for {1}'.format(ip, username), exc_info=True)
'''


def check_port(ip, port):
	# Create a TCP socket
	s = socket.socket()
	con_log.debug('{0} - Connecting on port {1}'.format(ip, port))
	try:
		s.connect((ip, port))
		con_log.debug('{0} - Port {1} OPEN'.format(ip, port))
		return True
	except socket.error, e:
		con_log.error('{0} - Port {1} CLOSED'.format(ip, port), exc_info=True)
		return False


