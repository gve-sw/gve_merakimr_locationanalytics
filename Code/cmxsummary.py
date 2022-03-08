"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# code pulls cmx observation data from the CMXData.csv file and creates a summary of visits
# in CMXSummary.csv
# Libraries

from datetime import datetime
from pytz import timezone
import csv
from config import initialRSSIThreshold, visitorRSSIThreshold, maxSecondsAwayNewVisit, minMinutesVisit, theTimeZone

csvinputfile = None
csvoutputfile = None


def timestamp_converter(time) :
    date,time = time.split('T')
    time = time.replace('Z','')
    # print(date)
    # print(time)
    return date,time

def datetime_handler(date, time) :
      time_components= [int(x) for x in time.split(':') ]
      date_components = [int(x) for x in date.split('-') ]
    #   print(date_components)
      datetime_obj = datetime(date_components[0], date_components[1],date_components[2],time_components[0],time_components[1],time_components[2])
      return datetime_obj


if __name__ == '__main__':
    theObservations={}
    fieldnamesin = ['NETNAME', 'APNAME', 'APMAC', 'CLIENT_MAC', 'time', 'rssi']

    with open('cmxdata.csv', newline='') as csvinputfile:
        datareader = csv.DictReader(csvinputfile, fieldnames=fieldnamesin)
        next(datareader, None) #skip the header row
        for row in datareader:
            #print(row['NETNAME'], row['APNAME'],row['APMAC'], row['MAC'], row['time'], row['rssi'])
            #assigning client MAC address from the row from the input file to a separate variable for better
            #readability of the code
            newMAC=row['CLIENT_MAC']
            #first check to see if we have seen this potential visitor
            if newMAC in theObservations:
                # if we have seen it, check to see if this record is from a different AP at the same time
                # focus on the latest visit from the visits array o the observation
                print("HI", theObservations[newMAC][-1])
                print("from excel,",row['time'], " from observation,", theObservations[newMAC][-1])
                if theObservations[newMAC][-1]['latest_ts']==row['time']:
                    #if so, assign the largest RSSI to the data structure we keep in memory so we do not make a decision
                    #about the end of a visit based on an AP that is not the one closest to the visitor
                    theObservations[newMAC][-1]['latest_rssi']=max(int(row['rssi']),theObservations[newMAC][-1]['latest_rssi'])
                else:
                    # if not the same, there is a new timestamp for the same unique client ID, so we must check against
                    # let latest visit in the array and update the
                    # latest_ts and latest_rssi fields, but only if above the rssi threshold to still consider a visitor
                    # and the new timestamp cannot be more than maxSecondsAwayNewVisit from the latest recorded
                    # if it is, then we have to add a new visit record to the array
                    if abs(int(row['rssi']))>=visitorRSSIThreshold:
                        time = datetime_handler(timestamp_converter(row['time'])[0], timestamp_converter(row['time'])[1])
                        latest_ts_time =  datetime_handler(timestamp_converter(theObservations[newMAC][-1]['latest_ts'])[0], timestamp_converter(theObservations[newMAC][-1]['latest_ts'])[1])
                        # if (int(row['time'])-theObservations[newMAC][-1]['latest_ts'])<=maxSecondsAwayNewVisit:
                        if (time.timestamp()-latest_ts_time.timestamp())<=maxSecondsAwayNewVisit:
                            theObservations[newMAC][-1]['latest_ts'] = row['time']
                            theObservations[newMAC][-1]['latest_rssi'] = int(row['rssi'])
                        elif abs(int(row['rssi']))>=initialRSSIThreshold:
                            #this is a new visit (also checked RSSI above new visti threshold), append new entry to
                            # the array of visits with all relevant values
                            newVisit={}
                            newVisit['first_ts'] = row['time']
                            newVisit['latest_ts'] = row['time']
                            newVisit['latest_rssi'] = int(row['rssi'])
                            newVisit['netname'] = row['NETNAME']
                            theObservations[newMAC].append(newVisit)

            else:
                #if we have not seen it , time to create a visits array for that MAC if the RSSI is larger than initialRSSIThreshold
                print(row['rssi'])
                if row['rssi'] == 'rssi' :
                    newMAC=row['CLIENT_MAC']
                if abs(int(row['rssi']))>=initialRSSIThreshold:
                    theObservations[newMAC]=[]
                    firstVisit= {}
                    firstVisit['first_ts']= row['time']
                    firstVisit['latest_ts'] = row['time']
                    firstVisit['latest_rssi'] = int(row['rssi'])
                    firstVisit['netname'] = row['NETNAME']
                    theObservations[newMAC].append(firstVisit)


    print("Done reading and mapping, starting to generate summary file...")
    print("dict of observations:\n", theObservations)

    fieldnamesout = ['NETNAME', 'CLIENT_MAC', 'date', 'time', 'length']
    with open('cmxSummary.csv', 'w', newline='') as csvoutputfile:
        localTZ = timezone(theTimeZone)
        writer = csv.DictWriter(csvoutputfile, fieldnames=fieldnamesout)
        writer.writeheader()
        for theKey in theObservations:
            for theVisitInstance in theObservations[theKey]:
                [first_date, first_time] = timestamp_converter(theVisitInstance['first_ts'])
                theTime= datetime_handler(first_date, first_time)
                theLocalTime=theTime.astimezone(localTZ)
                # theDeltaSeconds=theVisitInstance['latest_ts']-theVisitInstance['first_ts']
                [latest_date, latest_time] = timestamp_converter(theVisitInstance['latest_ts'])
                theDeltaSeconds = datetime_handler(latest_date, latest_time).timestamp() - theTime.timestamp()
                theVisitLength=round(theDeltaSeconds / 60,2)



                if theVisitLength>=minMinutesVisit:
                    print("Network which meets visit length:", theVisitInstance['netname'],'\n')

                    writer.writerow({'NETNAME': theVisitInstance['netname'],
                                     'CLIENT_MAC': theKey,
                                     'date': theLocalTime.strftime('%m/%d/%Y'),
                                     'time': theLocalTime.strftime('%H:%M'),
                                     'length': theVisitLength})

    print("Summary File generated.")


