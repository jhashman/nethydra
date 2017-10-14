#!/usr/bin/env python

# The primary goal of nethydra is to connect to an organiation's network infrastructure devices that support a CLI and make
# small configuration changes to allow OneTeam's primary monitoring tools access to the devices

import sys
from ciscoconfparse import CiscoConfParse
import logging
import netmiko
import socket
import connect
import csv
import os
from datetime import datetime
import local
import nethydra
import textfsm

con_log = logging.getLogger('NetHydra')

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,netmiko.ssh_exception.NetMikoAuthenticationException)


def main():
	try:
		# Use poll_devices_online to work with active network devices
		poll_devices_online(local.nethydra_input_file)
		
		# Use poll_devices_folder to work with offline file backups
		# poll_devices_folder(local.tech_support_file_path)
	except Exception:
		con_log.error('ERROR', exc_info=True)


def poll_devices_online(input_file):
# This function will connected to each device in the device_list and collect the running-config
# and tech-support info and save it to the Linux server
	try:
		with open(input_file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if "fortinet" in row['device_type']:
					net_connect = connect.direct(row['ip'], row['port'], row['device_type'], local.username1, local.password1, local.enable_pass)
					
					# ---Get info from the devices and save to the server---
					get_version_info(net_connect)
				
					net_connect.disconnect()
	except netmiko_exceptions as e:
		con_log.error('NetMiko Error', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)


def poll_devices_folder(folder_path):
# This function is a workspace where multiple commands can be run against the tech-support
# files that have previously been retrieved
	try:
		# Open all tech-support files in a directory and parse them based on our criteria
		for filename in os.listdir(folder_path):
			tech_support_file = folder_path + filename
			con_log.debug(tech_support_file)

			with open(tech_support_file, 'r') as input_file:
				raw_text_data = input_file.read()

			# Now use raw_text_data to pull information from, this glob of data can just as easily
			# come directly from the output of running the command show tech-support

			#version_info = get_version_info(raw_text_data)
			#print version_info

	except Exception:
		con_log.error('ERROR', exc_info=True)


def get_version_info(net_connect):
	# See the template file for the order each show version command returns its fields
	try:
		output = net_connect.send_command_timing("get system status", delay_factor=2)
		print output
	except Exception:
		con_log.error('get_version_info', exc_info=True)

		
def disable_paging(net_connect):
	try:
		net_connect.send_command_timing("set cli pager off", delay_factor=2)
	except Exception:
		con_log.error('set cli pager off', exc_info=True)



if __name__ == '__main__':
    main()


