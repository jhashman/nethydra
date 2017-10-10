#!/usr/bin/env python

# The primary goal of nethydra is to connect to an organiation's network infrastructure devices that support a CLI and make
# small configuration changes to allow OneTeam's primary monitoring tools access to the devices

import sys
from ciscoconfparse import CiscoConfParse
import logging
import os
from datetime import datetime
import local
import nethydra

con_log = logging.getLogger('NetHydra')


def main():
	try:
		# Open all config files in a directory and parse them based on our criteria
		for filename in os.listdir(local.config_file_path):
			config_file = local.config_file_path + filename
			con_log.debug(config_file)
			parse_cisco_config(config_file)
			#parse_cisco_config('/home/nocops/scripts/nethydra/output/configs/192.168.48.240-config-20170922')
	except Exception:
		con_log.error('ERROR', exc_info=True)


def parse_cisco_config(config_file):
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
		#	print obj.text
		#print active_intfs

	except Exception:
	 		con_log.error('ERROR parsing config - {0}'.format(config_file), exc_info=True)


if __name__ == '__main__':
    main()
