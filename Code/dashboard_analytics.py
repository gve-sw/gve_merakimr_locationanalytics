from csv import DictReader
from typing import Dict
from cmxsummary import datetime_handler, timestamp_converter, csv

occurence_count = dict() #mapping mac address to occurence
overall_network_stats = dict() #storing overall stats for each network

visitors =  set()
passerbys = set()

# counters to track engagement 

#5 to 20 mins
first_zone = 0
#20 to 60 mins
second_zone = 0
#1 to 6 hrs
third_zone = 0
#6+ hrs
fourth_zone = 0

#Engagement data processing
def update_counters(network, time, date) :
    time = float(time)
    if (network, date) in overall_network_stats :
        items = overall_network_stats[(network, date)]
            
        if time>=5 and time <= 20 :
            items['first_zone'] +=1
        elif time > 20 and time <=60 :
            items['second_zone'] +=1
        elif time> 60 and time <= 6*60 :
            items['third_zone'] += 1
        elif time > 6*60 :
            items['fourth_zone'] += 1
        else :
            print('disregarding time because its too short')
        # print(items)
        overall_network_stats[(network, date)] =  items
    else :
        items = {'first_zone' : 0, 'second_zone' : 0, 'third_zone' : 0, 'fourth_zone' : 0}
        overall_network_stats[(network, date)] = items



with open('cmxSummary.csv', 'r') as csvfile :
    reader = csv.DictReader(csvfile)
    next(reader, None) #skip the header row
    for row in reader :
        update_counters(row['NETNAME'], row['length'], row['date'])
        if (row['CLIENT_MAC'], row['date']) in occurence_count :

            occurence_count[(row['CLIENT_MAC'], row['date'])]['unique_visits'] += 1
        else :
             items = {}
             items['network'] = row['NETNAME']
             items['date'] = row['date']
             items['mac_address'] = row['CLIENT_MAC']
             items['unique_visits'] = 1

             key = tuple()
             key = (row['CLIENT_MAC'], row['date'])

             occurence_count[key] = items

            



#Write engagement data to file
with open('customervisitData.csv', 'w') as outputfile :
    fieldnames = ['Network Name', 'Date', 'Client MAC Address', 'Unique visits']
    writer= csv.DictWriter(outputfile, fieldnames=fieldnames)
    writer.writeheader()

    occurence_count_list  = tuple(occurence_count)
    print(occurence_count_list)
    # occurence_count_list.sort(key= 'network')

    for occurence in occurence_count :
        writer.writerow({
            'Network Name': occurence_count[occurence]['network'],
            'Date': occurence[1],
            'Client MAC Address': occurence[0],
            'Unique visits': occurence_count[occurence]['unique_visits']
            })


#sorting the data in CSV
with open('customervisitData.csv', newline='') as csvfile:
    rdr = csv.reader(csvfile)
    l = sorted(rdr, key=lambda x: x[0], reverse=True)

with open('customervisitData.csv', 'w') as csvout:
    wrtr = csv.writer(csvout)
    wrtr.writerows(l)


#Write loyalty date to file
with open('engagementData.csv', 'w') as outputfile :
    occurence_count
    fieldnames = ['Network Name', 'Date', '5 to 20 mins dwelling', '20 to 60 mins dwelling', '1hr to 6 hrs dwelling', '6 hrs+ dwelling']
    writer= csv.DictWriter(outputfile, fieldnames=fieldnames)
    writer.writeheader()
    for stat in overall_network_stats :
        writer.writerow({
            'Network Name': stat[0],
            'Date': stat[1],
            '5 to 20 mins dwelling': overall_network_stats[stat]['first_zone'],
            '20 to 60 mins dwelling': overall_network_stats[stat]['second_zone'],
            '1hr to 6 hrs dwelling':overall_network_stats[stat]['third_zone'],
            '6 hrs+ dwelling': overall_network_stats[stat]['fourth_zone']
            })




#Get capture rate

#Number of unique MAC addresses that are counted as a visit:
with open('cmxData.csv', 'r') as csvfile:
    reader = DictReader(csvfile)
    next(reader, None) #skip the header row
    for row in reader:
        passerbys.add(row['CLIENT_MAC'])

with open('cmxSummary.csv', 'r') as csvfile:
    reader = DictReader(csvfile)
    next(reader, None) #skip the header row
    for row in reader:
        visitors.add(row['CLIENT_MAC'])


print("CAPTURE RATE:", len(visitors)/len(passerbys)) #Run cmxsummary.py before checking capture rate !

    


        

        
print(overall_network_stats)



