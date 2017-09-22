base_path = '/opt/nethydra'
org = ''

# nethydra.py
log_config = base_path + '/etc/logging.json'
nethydra_input = base_path + '/input/nethydra_input.csv'
nethydra_input_nyap = base_path + '/input/nyap-devices.csv'
username1 = ''
password1 = ''
username2 = ''
username2 = ''
enable_pass = ''
ssh_config_file = '/home/nocops/.ssh/config'

# parse_nmap_xml.py
nmap_xml = base_path + '/output/' + org + '-devices.xml'
nmap_csv = base_path + '/output/' + org + '-devices.csv'

# parse_masscan.py
subnet = '192.168.0.0'
masscan_file = base_path + '/input/' + subnet
parsed_masscan_file = base_path + '/input/' + subnet + '-parsed'

# get_cisco_info
config_file_path = base_path + '/output/configs/'
tech_support_file_path = base_path + '/output/tech-support/'

# parse_cisco_config

