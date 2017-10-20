#!/usr/bin/env python

# The primary goal of nethydra is to connect to an organiation's network infrastructure devices that support a CLI and make
# small configuration changes to allow OneTeam's primary monitoring tools access to the devices

import sys
import logging
import logging.config
import os
import errno
import netmiko
import json
from collections import defaultdict
import csv
from datetime import datetime
import local
import cisco
import fortinet
import connect
import socket

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

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,netmiko.ssh_exception.NetMikoAuthenticationException)


def main():
	#setup_org_folder()
	validate_input_file(local.nethydra_input_file)


def setup_org_folder():
	try:
		os.makedirs(local.org_path)
		os.makedirs(local.org_path + '/input/nmap')
		os.makedirs(local.org_path + '/output/configs')
		os.makedirs(local.org_path + '/output/tech-support')
		os.makedirs(local.org_path + '/output/cdp')
		os.makedirs(local.org_path + '/output/nmap')
		os.makedirs(local.org_path + '/output/masscan')
	except OSError as Exception:
		if Exception.errno != errno.EEXIST:
			con_log.error('setup_org_folder', exc_info=True)
			raise


'''
def poll_devices_online(input_file):
 This function will connected to each device and run different commands
	try:
		with open(input_file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				net_connect = connect.direct(row['ip'], row['port'], row['device_type'], local.username1, local.password1, local.enable_pass)

				 Get info from the devices
				try:
					if (row['device_type'] contains 'cisco'):
						net_connect.enable()
						cisco.get_running_config_file(net_connect, local.config_file_path)
						cisco.get_techsupport_file(net_connect, local.tech_support_file_path)
						cisco.get_cdp_file(net_connect, local.cdp_neighbor_file_path)
						net_connect.disconnect()

					if (row['device_type'] contains 'fortinet'):
						fortinet.disable_paging(net_connect)
						fortinet.get_version(net_connect)
						fortinet.get_running_config_file(net_connect, local.config_file_path)
				except netmiko_exceptions as e:
					con_log.error('NetMiko Error', exc_info=True)
					continue
				except Exception:
					con_log.error('ERROR', exc_info=True)
					continue
	except Exception:
		con_log.error('ERROR', exc_info=True)
'''


def validate_input_file(input_file):
	con_log.info('Validating the nethydra input file')
	try:
		# Create variable to hold the updated string that will be written to nethydra_input.csv
		devices = defaultdict(list)
		with open(input_file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				net_connect = connect.direct(row['ip'], row['port'], row['device_type'], local.username1, local.password1, local.enable_pass)

				# Determine if the device in the input file is correct, if not update with the correct one
				output = net_connect.send_command('show inventory')
				output = output.split('\n')
				if ('ASA' in output[0]):
					# Update the device_type to cisco_asa
					con_log.info('ASA detected - updating device_type')
					devices[row['ip']].append(row['ip'])
					devices[row['ip']].append(row['port'])
					devices[row['ip']].append('cisco_asa')

				else:
					devices[row['ip']].append(row['ip'])
					devices[row['ip']].append(row['port'])
					devices[row['ip']].append(row['device_type'])

				net_connect.disconnect()

		con_log.debug(json.dumps(devices, indent=4))

		with open(input_file, 'w') as nethydra_file:
			nethydra_file.write('ip,port,device_type\n')
			for device in devices:
				info = devices[device]
				nethydra_input_line = info[0] + ',' + info[1] + ',' + info[2] + '\n'
				nethydra_file.write(nethydra_input_line)

	except netmiko_exceptions as e:
		con_log.error('NetMiko Error', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)




if __name__ == '__main__':
	main()
