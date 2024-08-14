#!/usr/bin/env python3

import csv
from datetime import datetime
import sys

snowDataFile = sys.argv[1] # CSV for ServiceNow data
jamfDataFile = sys.argv[2] # CSV for Jamf data
savePath = sys.argv[3] # Location for save without final slash ex: /Users/mjerome/Desktop

date = datetime.today().strftime('%m%d%Y-%H%M')
#print(date)

##### Gather Service Now Data From CSV
with open(f'{snowDataFile}', 'r', encoding='utf-8', errors='replace') as snowData:
    file = csv.DictReader(snowData)
    snowComputerSerialsAssetTags = {}
    snowComputerSerialsUsers = {}
    snowComputerStatus = {}
    for serialNumbers in file:
        try:
            snowComputerSerialsAssetTags[serialNumbers['serial_number']] = serialNumbers['asset_tag']
            snowComputerSerialsUsers[serialNumbers['serial_number']] = serialNumbers['assigned_to.email']
            snowComputerStatus[serialNumbers['serial_number']] = serialNumbers['install_status']
        except KeyError:
            print("invalid serial")

##### Gather Jamf Data From CSV
with open(f'{jamfDataFile}', 'r', encoding='utf-8', errors='replace') as jamfData:
    file = csv.DictReader(jamfData)
    jamfComputerSerialsAssetTags = {}
    jamfComputerSerialsUsers = {}
    jamfComputerLastCheckin = {}
    jamfComputerLastUpdate = {}
    for serialNumbers in file:
        try:
            jamfComputerSerialsAssetTags[serialNumbers['Serial Number']] = serialNumbers['Asset Tag']
            jamfComputerSerialsUsers[serialNumbers['Serial Number']] = serialNumbers['Email Address']
            jamfComputerLastCheckin[serialNumbers['Serial Number']] = serialNumbers['Last Check-in']
            jamfComputerLastUpdate[serialNumbers['Serial Number']] = serialNumbers['Last Inventory Update']
        except KeyError:
            print("invalid serial")

##### Output to CSV
mismatchCount = 0
with open(f'{savePath}/snow_jamf_comparison_{date}.csv', 'w', newline='') as csvfile:
    fieldnames = ['ServiceNow State','Validation', 'Serial Number', 'ServiceNow Asset Tag', 'ServiceNow User', 'Jamf Asset Tag', 'Jamf User', 'Last Jamf Checkin', 'Last Jamf Inventory']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for jamfComputer in jamfComputerSerialsAssetTags:
        if jamfComputer in snowComputerSerialsAssetTags:
            valid = "Match"
            if (snowComputerSerialsAssetTags[jamfComputer] != jamfComputerSerialsAssetTags[jamfComputer] or 
                snowComputerSerialsUsers.get(jamfComputer) != jamfComputerSerialsUsers.get(jamfComputer)) or snowComputerSerialsAssetTags[jamfComputer] == "" or snowComputerSerialsUsers[jamfComputer] == "" or jamfComputerSerialsUsers[jamfComputer] == "" or jamfComputerSerialsAssetTags[jamfComputer] == "":
                valid = "Mismatch"
                mismatchCount += 1
            writer.writerow({
                'ServiceNow State': snowComputerStatus.get(jamfComputer,'N/A'),
                'Validation': valid,
                'Serial Number': jamfComputer,
                'ServiceNow Asset Tag': snowComputerSerialsAssetTags.get(jamfComputer, 'N/A'),
                'ServiceNow User': snowComputerSerialsUsers.get(jamfComputer, 'N/A'),
                'Jamf Asset Tag': jamfComputerSerialsAssetTags[jamfComputer],
                'Jamf User': jamfComputerSerialsUsers.get(jamfComputer, 'N/A'),
                'Last Jamf Checkin' : jamfComputerLastCheckin.get(jamfComputer,'N/A'),
                'Last Jamf Inventory' : jamfComputerLastUpdate.get(jamfComputer, 'N/A')
            })
        else:
            writer.writerow({
                'Validation': "Missing from ServiceNow",
                'Serial Number': jamfComputer,
                'ServiceNow Asset Tag': 'N/A',
                'ServiceNow User': 'N/A',
                'Jamf Asset Tag': jamfComputerSerialsAssetTags[jamfComputer],
                'Jamf User': jamfComputerSerialsUsers.get(jamfComputer, 'N/A')
            })

    # Write the mismatch count as a summary row
    writer.writerow({
        'Validation': 'Mismatch Count',
        'Serial Number': mismatchCount,
        'ServiceNow Asset Tag': '',
        'ServiceNow User': '',
        'Jamf Asset Tag': '',
        'Jamf User': ''
    })

    print(f"Mismatch Count: {mismatchCount}")
