#!/usr/bin/env python3

import csv
import re
import meraki
import json

configs = json.load(open('config.json'))
dashboard = meraki.DashboardAPI(configs['configs']['API_KEY'])

mgmtIf = {
    'wan1': {
        'wanEnabled': 'enabled', 
        'usingStaticIp': False,
        'staticIp': '',
        'staticSubnetMask': '',
        'staticGatewayIp': '',
        'staticDns': [],
        'vlan': configs['configs']["MgmtVlan"]
    },
    'wan2': {
        'wanEnabled': 'disabled',
        'usingStaticIp': False
    }
}

def findSector(bldgName):
    for s in configs['configs']["sectors"]:
        key, values = list(s.items())[0]
        if bldgName in values:        
            return key
    return 'sector-0'

def process_files():
    output = []
    inventory = []
    with open('onboarding.csv', 'r') as merakiData:
        csvReader = csv.reader(merakiData, delimiter = ',')
        lineCount = 0
        for row in csvReader:
            if lineCount != 0:
                for i in range(len(row) - 1):
                    inventory.append({'box':row[0], 'sn':row[i + 1]})
            lineCount += 1

    with open('aerohive.csv', 'r') as aeroData:
        csvReader = csv.reader(aeroData, delimiter = ',')
        lineCount = 0
        for row in csvReader:
            if lineCount != 0:
                output.append([inventory[0]['box'],inventory[0]['sn'],row[1],row[3],row[2]])
                inventory.pop(0)
            lineCount += 1

    with open('meraki.csv', 'w') as data:
        csvWriter = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(['Box','NewSerialNumber','Name','IpAddr','OldSerialNumber'])
        for i in output:
            csvWriter.writerow(i)

def main():
	inventory = []
	process_files()
	with open('meraki.csv', 'r') as merakiData:
	csvReader = csv.reader(merakiData, delimiter = ',')
	lineCount = 0
	for row in csvReader:
		if lineCount != 0:
		tags = []
		temp = re.search(r'^(\w+)-([A-Za-z]+)', row[2])
		if temp is not None:
			 tags.append(temp[1].lower())
			 tags.append('bldg-' + temp[2].lower())
			 if temp[1].lower() == configs['configs']["locations"]["0"]:
			tags.append(findSector(temp[2].lower()))
		inventory.append({'sn': row[1], 'box': row[0], 'name': row[2], 'tags': tags})
		lineCount += 1
	for i in inventory:

	# Claiming APs per network

	if configs['configs']["locations"]["0"] in i['tags']:
		response = dashboard.networks.claimNetworkDevices(configs['configs']["networks"]["0"], [i['sn']])
	elif configs['configs']["locations"]["1"] in i['tags']:
		response = dashboard.networks.claimNetworkDevices(configs['configs']["networks"]["1"], [i['sn']])
	elif configs['configs']["locations"]["2"] in i['tags']:
		response = dashboard.networks.claimNetworkDevices(configs['configs']["networks"]["2"], [i['sn']])
	elif configs['configs']["locations"]["3"] in i['tags']:
		response = dashboard.networks.claimNetworkDevices(configs['configs']["networks"]["3"], [i['sn']])
	else:
		print(r'sn: {i["sn"]}. Failed to be added to a network')

	# Naming and assigning tags to APs

	response = dashboard.devices.updateDevice(i['sn'], name=i['name'], tags=i['tags'])

	# Configuring Mgmt If

	response = dashboard.devices.updateDeviceManagementInterface(i['sn'], wan1 = mgmtIf['wan1'], wan2 = mgmtIf['wan2']) 

if __name__ == '__main__':
	main()
