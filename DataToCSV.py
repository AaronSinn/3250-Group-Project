from datastream_py import observations, records, set_api_key, locations
from dotenv import load_dotenv
import os, csv

load_dotenv()
set_api_key(os.getenv('API_KEY'))

results = observations({
    '$select': 'DOI,LocationId,ActivityStartDate,CharacteristicName,ResultValue,ResultUnit,ResultValueType,ResultStatusID',
    '$filter': "RegionId eq 'hub.greatlakes' and CharacteristicName in ('pH','Chloride', 'Escherichia coli') and ActivityStartYear gte '2021' and MonitoringLocationType eq 'Great Lake' and ActivityMediaName eq 'Surface Water'",
    '$top': 10
})

test_results =  open('test_results.csv', 'w', newline='')

fieldnames = ['DOI', 'LocationId', 'ActivityStartDate', 'CharacteristicName', 'ResultValue', 'ResultUnit', 'ResultValueType', 'ResultStatusID', 'Id']
writer = csv.DictWriter(test_results, fieldnames=fieldnames)
writer.writeheader()

for observation in results:
    writer.writerow(observation)
