from datastream_py import records, set_api_key
from dotenv import load_dotenv
import os, csv

# Load API key
load_dotenv()
set_api_key(os.getenv('API_KEY'))

# Constants
FIELDNAMES = [
    'MonitoringLocationName', 'MonitoringLocationID', 'ActivityType',
    'ActivityMediaName', 'ActivityStartDate', 'CharacteristicName',
    'ResultSampleFraction', 'ResultValue', 'ResultUnit', 'ResultValueType'
]

GREAT_LAKES = {
    'Georgian Bay', 'Lake Huron', 'Lake Erie', 'Lake Ontario', 'Lake Superior'
}

BASE_FILTER = (
    "RegionId eq 'hub.greatlakes' "
    "and ActivityStartYear gte '2021' "
    "and MonitoringLocationType in ('Great Lake') "
    "and ActivityMediaName eq 'Surface Water'"
)

# Reusable function
def fetch_and_save(characteristics, filename):
    query = {
        '$select': ','.join(FIELDNAMES),
        '$filter': f"{BASE_FILTER} and CharacteristicName in ({format_list(characteristics)})",
        '$top': 10000
    }

    results = records(query)

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for record in results:
            if record['MonitoringLocationName'] in GREAT_LAKES:
                writer.writerow(record)


def format_list(items):
    """Format list into OData string ('a', 'b', 'c')"""
    return ', '.join(f"'{item}'" for item in items)


if __name__ == "__main__":
    # Run queries
    fetch_and_save(
        ['pH', 'Chloride', 'Escherichia coli', 'Dissolved oxygen (DO)', 'Chlorophyll a'],
        'milligram.csv'
    )

    fetch_and_save(
        ['Temperature, water'],
        'celsius.csv'
    )

    fetch_and_save(
        ['Turbidity'],
        'ntu.csv'
    )