#!/usr/bin/env python

# The primary goal of nethydra is to connect to an organiation's network infrastructure devices that support a CLI and make
# small configuration changes to allow OneTeam's primary monitoring tools access to the devices

import sys
import logging
import logging.config
import os
import errno
import json
import csv
from datetime import datetime
import local
import cisco
import fortinet
import connect

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
def poll_devices_online(device_list):
 This function will connected to each device and run different commands
	try:
		with open(device_list) as csvfile:
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


def main():
	setup_org_folder()


if __name__ == '__main__':
	main()
