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
		#poll_devices_folder(local.tech_support_file_path)
		poll_devices_online(local.nethydra_input_file)
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

			get_management_ip(tech_support_file)

	except Exception:
		con_log.error('ERROR', exc_info=True)



def poll_devices_online(device_list):
# This function will connected to each device in the device_list and collect the running-config
# and tech-support info and save it to the Linux server
	try:
		with open(device_list) as csvfile:
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

				# Get info from the devices
				try:
					net_connect.enable()
					#get_running_config_file(net_connect, ip, local.config_file_path)
					#get_techsupport_file(net_connect, ip, local.tech_support_file_path)
					get_cdp_file(net_connect, ip, local.cdp_neighbor_file_path)
					net_connect.disconnect()
				except netmiko_exceptions as e:
					con_log.error('NetMiko Error', exc_info=True)
					continue
				except Exception:
					con_log.error('ERROR', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)


def get_running_config_file(net_connect, ip, file_path):
	try:
		con_log.info('{0} - Executing show running-config'.format(ip))
		output = net_connect.send_command("show running-config")

		con_log.info('{0} - Saving running-config to file'.format(ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + ip + '-config-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve the config'.format(ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(ip), exc_info=True)


def get_techsupport_file(net_connect, ip, file_path):
	try:
		con_log.info('{0} - Executing show tech-support'.format(ip))
		output = net_connect.send_command("show tech-support")

		con_log.info('{0} - Saving tech-support to file'.format(ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + ip + '-tech-support-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve tech-support'.format(ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(ip), exc_info=True)


def get_cdp_file(net_connect, ip, file_path):
	try:
		con_log.info('{0} - Executing show cdp neighbors'.format(ip))
		output = net_connect.send_command("show cdp neighbors")

		con_log.info('{0} - Saving cdp neighbors to file'.format(ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + ip + '-cdp-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve cdp neighbors'.format(ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(ip), exc_info=True)


def get_parse_test(blob):
	try:
		con_log.debug("Parsing the config")

		parse = CiscoConfParse(config_file, syntax='ios')

		print '-----' + config_file + '-----'

		for obj in parse.find_objects("^hostname"):
			print '-----' + obj.text + '-----'

		for obj in parse.find_objects("^snmp"):
			#print "Object:", obj
			#print "Text:", obj.text
			print obj.text

		print '\n'

		for obj in parse.find_objects("^access-list"):
			print obj.text

		print '\n'

		#for obj in parse.find_parents_w_child( "^interf", "switchport mode trunk" ):
		#   print obj.text
		#print active_intfs

	except Exception:
		con_log.error('ERROR parsing config - {0}'.format(config_file), exc_info=True)



def get_device_csv_info(blob):
	pass



def get_ip_subnets(blob):
	pass


def get_management_ip(file):
	try:
		parse = CiscoConfParse(file)

		with open(file, 'r') as input_file:
			blob = input_file.read()
 
		if (is_ios(blob)):
			int_mgmt = parse.find_objects(r"^interfa")
			for obj in int_mgmt:
				if obj.re_search_children(r"description mgmt") or obj.re_search_children(r"description management"):
					print obj

			int_vlan1 = parse.find_objects(r"^interface Vlan1")
			for obj in int_vlan1:
				if obj.re_search_children(r"ip address"):
					print obj.children
	except Exception:
		con_log.error('get_management_ip', exc_info=True)


def get_cdp_neighbors(blob):
	pass


def get_version_info(blob):
	# See the template file for the order each show version command returns its fields
	try:
		if (is_ios(blob)):
			template = open('{0}cisco_ios_show_version.template'.format(local.textfsm_templates), 'r')
			re_table = textfsm.TextFSM(template)
			fsm_results = re_table.ParseText(blob)
			return fsm_results

		if (is_asa(blob)):
			template = open('{0}cisco_asa_show_version.template'.format(local.textfsm_templates), 'r')
			re_table = textfsm.TextFSM(template)
			fsm_results = re_table.ParseText(blob)
			return fsm_results
	except Exception:
		con_log.error('get_version_info', exc_info=True)


def set_trunk_desc_with_cdp_suffix():
	pass


def is_stack():
	pass


def is_ios(blob):
	if 'Cisco IOS' in blob:
		return True
	else:
		return False


def is_asa(blob):
	if 'Adaptive Security Appliance' in blob:
		return True
	else:
		return False


def is_nexus(blob):
	if 'Nexus' in blob:
		return True
	else:
		return False


def audit_password_encryption():
	pass


def audit_tty():
	pass


def audit_ssh():
	pass


def audit_management_acl():
	pass


def get_snmp_2_community():
	pass


if __name__ == '__main__':
    main()


