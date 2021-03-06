#!/usr/bin/env python
# Parses masscan output into a nmap host target list file

import sys
import socket
import logging
import logging.config
import os
import json
import csv
import re
from collections import defaultdict
import socket
import local


def main():
	masscan_output_regex = re.compile(r'^Host: ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) \(\)\s+Ports: (.*)')

	hosts_all = defaultdict(list)

	# Remove the printers
	hosts_remove = {}

	try:
		os.remove(local.masscan_parsed_file)
	except OSError:
		pass

	try:
		# Open each subnet file in masscan output folder
		for filename in os.listdir(local.masscan_output_folder):
			print filename
			with open('{0}{1}'.format(local.masscan_output_folder, filename)) as f:
				for line in f:
					match = masscan_output_regex.match(line)
					if match:
							ip = match.group(1)
							port_group =  match.group(2)
							port_split = port_group.split('/')
							port_num = port_split[0]
							port_prot = port_split[1]
							#print ip, port_num, port_prot
							hosts_all[ip].append(port_num)

			#Find IPs that have printer ports open
			for k,v in hosts_all.iteritems():
				for item in v:
					if item == "515":
						hosts_remove.update({k:1})
					elif item == "9100":
						hosts_remove.update({k:1})

			# Remove the IPs that have printer ports open
			for key in hosts_remove.keys():
				try:
					del hosts_all[key]
				except KeyError:
					pass

			#for k,v in hosts_all.iteritems():
			#	print k
			#	 for item in v:
			#		print k, ":", item

			with open (local.masscan_parsed_file, 'a+') as parsed_masscan:
				IPs = sorted(hosts_all.items(), key=lambda item: socket.inet_aton(item[0]))
				for IP in IPs:
					print IP[0]
					parsed_masscan.write(IP[0] + '\n')
	except:
		e = sys.exc_info()
		print e


if __name__ == '__main__':
	main()
