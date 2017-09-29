#!/usr/bin/env python

import subprocess
import local

def main():
	try:
		print local.masscan_input_file
		with open(local.masscan_input_file) as f:
			for line in f:
				line = line.strip()
				subnet = line.split('/')

				masscan_output_file = local.masscan_output_folder + subnet[0]

				print '\n---{0}: Initiating masscan---'.format(line)
				p = subprocess.Popen(['masscan', '-p22,23,515,9100', line, '--open-only', '-oG', masscan_output_file], stdin=subprocess.PIPE)
				p.wait()
				if p.returncode == 0:
					print '{0}: Complete'.format(line)
	except Exception as e:
		print e

if __name__ == '__main__':
    main()

