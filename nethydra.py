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

def main():
	setup_org_folder()


if __name__ == '__main__':
	main()
