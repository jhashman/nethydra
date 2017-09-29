#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script parses nmap xml output into a csv file for examination and a nethydra input file
import sys
from libnmap.parser import NmapParser
import local

try:
    rep = NmapParser.parse_fromfile(local.nmap_xml)

    nethydra_file = open(local.nethydra_input,'w')
    nethydra_file.write("ip,port,device_type\n")
    nethydra_file.close()
    nethydra_file = open(local.nethydra_input,'a')

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

        #os_desc = ''
        #
        #if _host.os_fingerprinted:
        #    flag = 0
        #    for osm in _host.os.osmatches:
        #        for osc in osm.osclasses:
        #            if (osc.accuracy == 100):
        #                flag = 1
        #    if flag:
        #        os_desc = osc.description
        #        if ('general' in os_desc):
        #            os_desc = ''
        #            host_output = host_output + ',' + os_desc
        #        elif ('Cisco' in os_desc):
        #            os_desc = ''
        #            host_output = host_output + ',' + os_desc
        #        elif ('Adtran' in os_desc):
        #            os_desc = 'Adtran'

        cpe = ''
        ssl_subject = ''
        ssl_valid_date = ''

        for s in _host.services:
            for _serv_cpe in s.cpelist:
                if ('cpe:/a' not in _serv_cpe.cpestring):
                    cpe = _serv_cpe.cpestring
                    if (('Cisco' in _serv_cpe.cpestring) or ('cisco' in _serv_cpe.cpestring)):
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

            #print host_output
            nmap_file.write(host_output)

    if (('cisco' in device_type) and (port is 22)):
        device_type = 'cisco_ios'
    elif (('cisco' in device_type) and (port is 23)):
        device_type = 'cisco_ios_telnet'

    if ('cisco' in device_type):
        nethydra_output = ip + ',' + str(port) + ',' + device_type + '\n'
        #print nethydra_output
        nethydra_file.write(nethydra_output)

nethydra_file.close()
nmap_file.close()
