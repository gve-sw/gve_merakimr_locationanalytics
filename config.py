# this config file contains multiple variables utilized throughout the functionality of this code
MERAKI_API_KEY = "<Put your Meraki user API Key>"
ORG_IDS = ["<Org ID 1>", '<Org ID 2>'] #Only need 1 if only 1 org
validators = ["52a4447858e1ef31614951ff808b5e603873e759", "6fe1dd14f7e82a09d2e99e0f4a03e49c884cb101"] #Only need 1 if only 1 org


#these are the parameters and thresholds used by the cmxsummary.py script, change as you desire
initialRSSIThreshold=15
visitorRSSIThreshold=10
maxSecondsAwayNewVisit=120
minMinutesVisit=5
theTimeZone='US/Central'
#how long to wait until running summary: Daily='D', Hourly='H', Test='T' (10 min interval), Manual='M'
summaryTimePeriod='D'
