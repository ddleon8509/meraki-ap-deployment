#!/usr/bin/env python3
import csv

output = []
inventory = []

def main():
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

if __name__ == '__main__':
	main()