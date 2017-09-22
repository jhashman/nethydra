#!/usr/bin/env python

import sys
from netmiko import ConnectHandler
import netmiko
import socket
import logging
import local


def direct(ip, port, device_type, username, password, secret):
    #iport = int(port)
    # Need to see if ssh_config_file is supplied, if not don't use it in the ConnecHandler
    #if check_port(ip, iport): #Had to disable for SSH proxy routing - can't directly ping
    #   logger.debug('{0} - Port {1} is open'.format(ip, port))
    #try:
    device = {}
    device['ip'] = ip
    device['port'] = port
    device['device_type'] = device_type
    device['username'] = username
    device['password'] = password
    device['secret'] = secret
    device['verbose'] = False
    net_connect = ConnectHandler(**device)
    return net_connect
    #except netmiko_exceptions as e:
    #   con_log.warn('{0} - Connection failed for {1}'.format(ip, username))
    #else:
    #   logger.debug('{0} - Port {1} is not open'.format(ip, port), exc_info=True)


def tunnel(ip, port, device_type, username, password, secret, ssh_config_file):
    iport = int(port)
    # Need to see if ssh_config_file is supplied, if not don't use it in the ConnecHandler
    #if check_port(ip, iport): #Had to disable for SSH proxy routing - can't directly ping
    try:
        device = {}
        device['ip'] = ip
        device['port'] = port
        device['device_type'] = device_type
        device['username'] = username
        device['password'] = password
        device['secret'] = secret
        device['ssh_config_file'] = ssh_config_file
        device['verbose'] = False
        net_connect = ConnectHandler(**device)
        return net_connect
    except netmiko_exceptions as e:
        logger.warn('{0} - Connection failed for {1}'.format(ip, username), exc_info=True)


def check_port(ip, port):
    # Create a TCP socket
    s = socket.socket()
    con_log.info('{0} - Connecting on port {1}'.format(ip, port))
    try:
        s.connect((ip, port))
        con_log.info('{0} - Port {1} OPEN'.format(ip, port))
        return True
    except socket.error, e:
        logger.error('{0} - Port {1} CLOSED'.format(ip, port), exc_info=True)
        return False


