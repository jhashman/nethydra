#!/usr/bin/env python
# New method for automating scans through masscan and nmap and parsing the results

import sys
import socket
import logging
import logging.config
import os
import subprocess
import json
from libnmap.parser import NmapParser
import csv
import re
from collections import defaultdict
import socket
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
scan_log = logging.getLogger('scan')


def masscan_parse():
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
			scan_log.info("Parsing file {0}".format(filename))
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
					parsed_masscan.write(IP[0] + '\n')

		scan_log.info('Parsed output: {0}'.format(local.masscan_parsed_file))
	except:
		e = sys.exc_info()
		print e


def masscan_scan():
    try:
        scan_log.info('Using this file for subnets to scan: {0}'.format(local.masscan_input_file))
        with open(local.masscan_input_file) as f:
            for line in f:
                line = line.strip()
                subnet = line.split('/')

                masscan_output_file = local.masscan_output_folder + subnet[0]

                scan_log.info('{0}: Initiating masscan'.format(line))
                p = subprocess.Popen(['masscan', '-p22,23,515,9100', line, '--open-only', '-oG', masscan_output_file], stdin=subprocess.PIPE)
                p.wait()
                if p.returncode == 0:
                    scan_log.info('{0}: Masscan Complete'.format(line))
    except Exception as e:
        print e


def nmap_network_device_scan():
	try:
		scan_log.info('Using this file for IPs to scan: {0}'.format(local.masscan_parsed_file))
		scan_log.info('Initiating nmap scan...')
		subprocess.Popen('nmap -p22,23,80,443 -A -v --open -iL %s -oX %s' % (local.masscan_parsed_file, local.nmap_xml), shell=True).wait()
		scan_log.info('Nmap scan complete')
	except Exception as e:
		print e


def nmap_xml_parse():
	try:
		rep = NmapParser.parse_fromfile(local.nmap_xml)

		scan_log.info('Opening {0} to create nethydra input'.format(local.nethydra_input_file))
		nethydra_file = open(local.nethydra_input_file,'w')
		nethydra_file.write("ip,port,device_type\n")
		nethydra_file.close()
		nethydra_file = open(local.nethydra_input_file,'a')

		scan_log.info('Opening {0} for nmap services csv'.format(local.nmap_csv))
		nmap_file = open(local.nmap_csv, 'w+')

	except:
		e = sys.exc_info()
		print e

	for _host in rep.hosts:
		host_output = ''
		ip = ''
		port = ''
		device_type = ''

		if _host.is_up():
			ip = _host.address

			open_ports = _host.get_open_ports()

			if ((22, 'tcp') in open_ports):
				port = 22
			elif ((23, 'tcp') in open_ports):
				port = 23

			if (('Cisco' in _host.vendor) and (port is 22)):
				device_type = 'cisco_ios'
			elif (('Cisco' in _host.vendor) and (port is 23)):
				device_type = 'cisco_ios_telnet'

			cpe = ''
			ssl_subject = ''
			ssl_valid_date = ''

			for s in _host.services:
				for _serv_cpe in s.cpelist:
					if ('cpe:/a' not in _serv_cpe.cpestring):
						cpe = _serv_cpe.cpestring
						if (('Cisco' in cpe) or ('cisco' in cpe)):
							device_type = 'cisco_ios'
				# Check for HTTPS to add SSL cert info
				if (s.port == 443):
					for p in s.scripts_results:
						arr = p['output'].split('\n')
						for a in arr:
							if 'Subject' in a:
								subject = a.split(':')
								ssl_subject = subject[1].strip()
							if 'Not valid after' in a:
								valid = a.split(':')
								valid_date = valid[1].split('T')
								ssl_valid_date = valid_date[0].strip()
					if (_host.hostnames):
						host_output = _host.address + '|' + _host.hostnames[0] + '|'  + _host.mac + '|' + _host.vendor + '|' + str(s.port) + '|' + cpe + '|' + ssl_subject + '|' + ssl_valid_date + '\n'
					else:
						host_output = _host.address + '||' + _host.mac + '|' + _host.vendor + '|' + str(s.port) + '|' + cpe + '|' + ssl_subject + '|' + ssl_valid_date + '\n'
				else:
					if (_host.hostnames):
						host_output = _host.address + '|' + _host.hostnames[0] + '|' + _host.mac + '|' + _host.vendor + '|' + str(s.port) + '|' + cpe + '\n'
					else:
						host_output = _host.address + '||' + _host.mac + '|' + _host.vendor + '|' + str(s.port) + '|' + cpe + '\n'

				scan_log.debug(host_output)
				nmap_file.write(host_output)

		if (('cisco' in device_type) and (port is 22)):
 			device_type = 'cisco_ios'
		elif (('cisco' in device_type) and (port is 23)):
			device_type = 'cisco_ios_telnet'

		if ('cisco' in device_type):
			nethydra_input = ip + ',' + str(port) + ',' + device_type + '\n'
			scan_log.debug(nethydra_input)
			nethydra_file.write(nethydra_input)


	scan_log.info('Closing {0}'.format(local.nethydra_input_file))
	nethydra_file.close()
	scan_log.info('Closing {0}'.format(local.nmap_csv))
	nmap_file.close()



def main():
	masscan_scan()
	masscan_parse()
	nmap_network_device_scan()
	nmap_xml_parse()


if __name__ == '__main__':
	main()
