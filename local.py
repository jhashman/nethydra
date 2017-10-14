base_path = 'c:/netsmart/nethydra'
org = 'UCC'
org_path = base_path + '/' + org

# nethydra.py
log_config = base_path + '/etc/logging.json'
nethydra_input_file = org_path + '/input/nethydra_input.csv'
username1 = 'nocops'
password1 = 'Cyber780'
username2 = ''
password2 = ''
enable_pass = 'Cyber780'
ssh_config_file = ''

# scan.py
masscan_input_file = org_path + '/input/' + org + '_subnets'
masscan_output_folder = org_path + '/output/masscan/'
masscan_parsed_file = org_path + '/input/nmap/' + org + '-masscan-parsed'
nmap_xml = org_path + '/output/nmap/' + org + '-devices.xml'
nmap_csv = org_path + '/output/' + org + '-devices.csv'

# cisco.py
config_file_path = org_path + '/output/configs/'
tech_support_file_path = org_path + '/output/tech-support/'
cdp_neighbor_file_path = org_path + '/output/cdp/'
commands_file_path = base_path + '/commands/'
textfsm_templates = base_path + '/etc/templates/'
