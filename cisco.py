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
import re
import json
from collections import defaultdict
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
		#poll_devices_folder(local.config_file_path)

		#create_spreadsheet_online(local.nethydra_input_file)

	except Exception:
		con_log.error('ERROR', exc_info=True)


def poll_devices_online(input_file):
# This function will connected to each device in the device_list and collect the running-config
# and tech-support info and save it to the Linux server
	try:
		with open(input_file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if "cisco" in row['device_type']:
					net_connect = connect.direct(row['ip'], row['port'], row['device_type'], local.username1, local.password1, local.enable_pass)
					net_connect.enable()

 					# ---Get info from the devices and save to the server---
					#get_running_config_file(net_connect, local.config_file_path)
					#get_techsupport_file(net_connect, local.tech_support_file_path)
					#get_cdp_file(net_connect, local.cdp_neighbor_file_path)

					# ---Run commands against the devices---
					rc = net_connect.send_command_timing("more system:running-config", delay_factor=2)
					ts = net_connect.send_command_timing("show tech-support", delay_factor=2)

					hostname = get_hostname(rc)
					print hostname

					#snmp_lines = get_snmp(rc)
					#print snmp_lines
					#update_snmp(rc)
					update_dhcp(rc)

					#dhcp_lines = get_dhcp(rc)
					#print dhcp_lines

					#access_lines = get_access_lists(rc)
					#print access_lines

#					version = get_version_info(ts)
#					print version

#					cdp_neighbors = get_cdp_neighbors(net_connect)
#					print cdp_neighbors

					net_connect.disconnect()
	except netmiko_exceptions as e:
		con_log.error('NetMiko Error', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)


def poll_devices_folder(folder_path):
# This function is a workspace where multiple commands can be run against the
# files that have previously been retrieved
	try:
		# Open al; files in a directory and parse them based on our criteria
		for filename in os.listdir(folder_path):
			file_path = folder_path + filename
			con_log.debug(file_path)

			with open(file_path, 'r') as input_file:
				raw_text_data = input_file.read()

			# Now use raw_text_data to pull information from, this glob of data can just as easily
			# come directly from the output of running the command show tech-support

			#version_info = get_version_info(raw_text_data)
			#print version_info

			#get_parse_test(file_path)
			#get_management_ip(file_path)

	except Exception:
		con_log.error('ERROR', exc_info=True)


def create_spreadsheet_online(input_file):
	try:
		devices = defaultdict(list)

		with open(input_file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if "cisco" in row['device_type']:
					net_connect = connect.direct(row['ip'], row['port'], row['device_type'], local.username1, local.password1, local.enable_pass)
					net_connect.enable()

					ts = net_connect.send_command_timing("show tech-support", delay_factor=2)
					ip = row['ip']
					device_info = get_version_info(ts)
					devices[ip].append(ip)
					devices[ip].append(device_info[0][2])
					devices[ip].append(device_info[0][0])
					image = device_info[0][4].split("/")
					devices[ip].append(image[1])
					devices[ip].append(device_info[0][5][0])
					devices[ip].append(device_info[0][6][0])

					net_connect.disconnect()

			print(json.dumps(devices, indent=4))

	except netmiko_exceptions as e:
		con_log.error('NetMiko Error', exc_info=True)
	except Exception:
		con_log.error('ERROR', exc_info=True)



def get_running_config(net_connect):
	try:
		con_log.info('{0} - Executing more system:running-config'.format(net_connect.ip))
		output = net_connect.send_command_timing("more system:running-config", delay_factor=2)
		return output
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve the config'.format(net_connect.ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(net_connect.ip), exc_info=True)


def get_running_config_file(net_connect, file_path):
	try:
		con_log.info('{0} - Executing more system:running-config'.format(net_connect.ip))
		output = net_connect.send_command("more system:running-config")

		hostname = get_hostname(output)
		con_log.info('{0} - Saving running-config to file'.format(net_connect.ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + net_connect.ip + '-' + hostname + '-config-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve the config'.format(net_connect.ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(net_connect.ip), exc_info=True)


def get_techsupport_file(net_connect, file_path):
	try:
		con_log.info('{0} - Executing show tech-support'.format(net_connect.ip))
		output = net_connect.send_command("show tech-support")

		hostname = get_hostname(output)
		con_log.info('{0} - Saving tech-support to file'.format(net_connect.ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + net_connect.ip + '-' + hostname + '-tech-support-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve tech-support'.format(net_connect.ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(net_connect.ip), exc_info=True)


def get_cdp_file(net_connect, file_path):
	try:
		con_log.info('{0} - Executing show cdp neighbors'.format(net_connect.ip))
		output = net_connect.send_command("show cdp neighbors")

		con_log.info('{0} - Saving cdp neighbors to file'.format(net_connect.ip))
		date = datetime.now().strftime("%Y%m%d")
		config_file = file_path + net_connect.ip + '-cdp-' + date

		f=open(config_file, 'w+')
		f.write(output)
		f.close()
	except netmiko_exceptions as e:
		con_log.error('{0} - Failed to retrieve cdp neighbors'.format(net_connect.ip), exc_info=True)
	except Exception:
		con_log.error('{0} - COMMAND EXECUTION FAILED'.format(net_connect.ip), exc_info=True)


def get_parse_test(config_file):
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

#		print '\n'

#		for obj in parse.find_objects("^access-list"):
#			print obj.text

#		print '\n'

		for obj in parse.find_objects("^dhcp"):
			print obj.text

		print '\n'

		#for obj in parse.find_parents_w_child( "^interf", "switchport mode trunk" ):
		#   print obj.text
		#print active_intfs

	except Exception:
		con_log.error('ERROR parsing config - {0}'.format(config_file), exc_info=True)



def get_ip_subnets(blob):
	pass


def get_management_ip(blob):
	try:
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



def get_dhcp(blob):
	match = re.findall(r'^dhcp .*$', blob, re.MULTILINE)
	return match


def update_dhcp(blob):
	dhcp_update = []
	dhcp_lines = get_dhcp(blob)

	if any(re.match('dhcpd enable inside') for entry in dhcp_lines):
		for line in dhcp_lines:
			if 'dhcpd dns' in line:
				dhcp_update.append('no {}'.format(line))
			if 'dhcpd wins' in line:
				dhcp_update.append('no {}'.format(line))
			if 'dhcpd domain' in line:
				dhcp_update.append('no {}'.format(line))

			dhcp_update.append('dhcpd dns 192.168.1.10 192.168.1.4')
			dhcp_update.append('dhcpd domain nyap.local')
			dhcp_update.append('dhcpd dns 192.168.1.10 192.168.1.4 interface inside')
			dhcp_update.append('dhcpd lease 86400 interface inside')
			dhcp_update.append('dhcpd ping_timeout 20 interface inside')
			dhcp_update.append('dhcpd domain nyapit interface inside')

	return dhcp_update


def get_snmp(blob):
	match = re.findall(r'^snmp-server .*$', blob, re.MULTILINE)
	return match


def update_snmp(blob):
	snmp_lines = get_snmp(blob)
	for line in snmp_lines:
		print line
		match = re.findall(r'.* access (\d+)$', line)
		if match:
			print match[0]
	return match


def get_access_lists(blob):
	match = re.findall(r'^access-list .*$', blob, re.MULTILINE)
	return match


def get_hostname(blob):
	match = re.findall(r'^hostname (.*)$', blob, re.MULTILINE)
	return match


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


def get_cdp_neighbors(net_connect):
	# See the template file for the order each show version command returns its fields
	try:
		cdp = net_connect.send_command_timing("show cdp neighbor detail", delay_factor=2)
		template = open('{0}cisco_ios_show_cdp_neighbors_detail.template'.format(local.textfsm_templates), 'r')
		re_table = textfsm.TextFSM(template)
		fsm_results = re_table.ParseText(cdp)
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


