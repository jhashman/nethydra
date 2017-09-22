#!/usr/bin/env python
# This uses the python-nmap module which did not work for all hosts tested, some caused exceptions and crashed the script, changed to python-libnmap

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
import nmap

logging.basicConfig(filename='./output/parse-masscan.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')


def main():
	masscan_output_regex = re.compile(r'^Host: ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) \(\)\s+Ports: (.*)')

	hosts_all = defaultdict(list)
	hosts_remove = {}

	try:
		with open('./output/192.168.0.0') as f:
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

		for key in hosts_remove.keys():
			try:
				del hosts_all[key]
			except KeyError:
				pass

		#for k,v in hosts_all.iteritems():
			#print k
			#for item in v:
				#print k, ":", item

		parsed_masscan = open('./output/192.168.0.0-nmap-input', 'w')
		IPs = sorted(hosts_all.items(), key=lambda item: socket.inet_aton(item[0]))

		nmapscan = nmap.PortScanner()

		for IP in IPs:
			ip = IP[0]
			print ip
			nmapscan.scan(hosts=ip, arguments='-A -T4 -p 22,23,80')
			print 'HOSTNAME: ' + str(nmapscan[ip].hostname())
			print 'MAC: ' + str(nmapscan[ip]['vendor'])
			print 'OS: ' + str(nmapscan[ip]['osmatch'][0]['osclass'][0]['osfamily'])
			print 'VENDOR: ' + str(nmapscan[ip]['osmatch'][0]['osclass'][0]['vendor'])

			if (nmapscan[ip]['tcp'][22]['state'] == 'open'):
				print "SSH: OPEN"
				print str(nmapscan[ip]['tcp'][22]['product'])
				print (nmapscan[ip]['tcp'][22]['cpe'])
				try:
					print str(nmapscan[ip]['tcp'][22]['script'])
				except:
					pass

			if (nmapscan[ip]['tcp'][23]['state'] == 'open'):
				print "TELNET: OPEN"
				print str(nmapscan[ip]['tcp'][23]['cpe'])

			if (nmapscan[ip]['tcp'][80]['state'] == 'open'):
				print "HTTP: OPEN"
				print str(nmapscan[ip]['tcp'][23]['cpe'])

			# This will throw an exception on some servers
			#if (nmapscan[ip]['tcp'][443]['state'] == 'open'):
			#	print "HTTPS: OPEN"
			#	try:
			#		print str(nmapscan[ip]['tcp'][443]['script']['ssl-cert'])
			#	except:
			#		pass

			print "\n"

		parsed_masscan.close()
	except:
		e = sys.exc_info()
		print e


if __name__ == '__main__':
	main()
