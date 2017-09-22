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
from datetime import datetime
import connect
import local

# Setup logging - the default_level is only used if the logging.json file cannot be found
default_level=logging.WARN
logging_config_file = local.log_config
if os.path.exists(logging_config_file):
	with open(logging_config_file, 'rt') as f:
		config = json.load(f)
		logging.config.dictConfig(config)
else:
	logging.basicConfig(level=default_level)

logger = logging.getLogger(__name__)
con_log = logging.getLogger('NetHydra')

# Uncomment this line to enable debug output to the console
#logging.getLogger().setLevel(logging.DEBUG)

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException)


def main():
	try:
		# The nethydra_input file will be an script argument in the future
		with open(local.nethydra_input) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
           		# For connections to local devices the IP can be used, through a tunnel use the hostname
				ip = row['ip']
				port = row['port']
				device_type = row['device_type']

				con_log.info('{0} - CONNECTING...'.format(ip))

				# Make the connection to the network device
				try:
					net_connect = connect.direct(ip, port, device_type, local.username1, local.password1, local.enable_pass)
					con_log.info('{0} - CONNECTION SUCCESSFUL'.format(ip))
				except Exception:
					con_log.warn('{0} - CONNECTION FAILED'.format(ip))
					try:
						net_connect = connect.direct(ip, port, device_type, local.username2, local.password2, local.enable_pass)
						con_log.info('{0} - CONNECTION SUCCESSFUL - 2nd user'.format(ip))
					except Exception:
						con_log.error('{0} - CONNECTION FAILED - 2nd user'.format(ip))
						continue

				# Run functions against the network device
				try:
					net_connect.enable()
					get_cisco_config(net_connect, ip, local.config_file_path)
					get_cisco_techsupport(net_connect, ip, local.tech_support_file_path)
					net_connect.disconnect()
				except netmiko_exceptions as e:
					con_log.error('NetMiko Error', exc_info=True)
					continue
				except Exception:
					con_log.error('ERROR', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)


def get_cisco_config(net_connect, ip, config_file_path):
	try:
		con_log.info('{0} - Executing show running-config'.format(ip))
		output = net_connect.send_command("show running-config")

		con_log.info('{0} - Saving running-config to file'.format(ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = config_file_path + ip + '-config-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
			con_log.error('{0} - Failed to retrieve the config'.format(ip), exc_info=True)
	except Exception:
	 		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(ip), exc_info=True)


def get_cisco_techsupport(net_connect, ip, config_file_path):
	try:
		con_log.info('{0} - Executing show tech-support'.format(ip))
		output = net_connect.send_command("show tech-support")

		con_log.info('{0} - Saving tech-support to file'.format(ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = config_file_path + ip + '-tech-support-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
			con_log.error('{0} - Failed to retrieve tech-support'.format(ip), exc_info=True)
	except Exception:
	 		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(ip), exc_info=True)


if __name__ == '__main__':
    main()
