#!/usr/bin/env python3
import argparse
import unicodecsv as csv
import xml.etree.ElementTree as ET
import json
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
##import reverse_geocode

def parse_args():
    parser = argparse.ArgumentParser(description='Convert museum osm files to csv')
    parser.add_argument('-i', '--input', type=str, required=True, help='input osm xml filename')
    parser.add_argument('-o', '--output', type=str, required=True, help='output csv filename')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    return parser.parse_args()

def create_entry():
    return {
        "osm_id": None,
        "name": None,
        "name:en": None,
        "int_name": None,
        "old_name": None,
        "old_name:en": None,
        "number": None,
        "street": None,
        "postal_code": None,
        "city": None,
        "country": None,
        "lat": None,
        "lon": None,
        "website": None,
        "phone": None,
        "fax": None,
        "tags": None,
        "description": None,
        "date_added": None
    }

def main():

    args = parse_args()
    locator = Nominatim(user_agent="myGeocoder", timeout=10)

    with open(args.output, 'wb') as csv_file:

        fieldnames = ['osm_id', 'name', 'name:en', 'int_name', 'old_name', 'old_name:en', 'number', 'street', 'postal_code',
                      'city', 'country', 'lat', 'lon', 'website', 'phone', 'fax', 'tags', 'description', 'date_added']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        num_rows = 0
        entry = create_entry()

        for event, elem in ET.iterparse(args.input, events=("start", "end")):
            if event == 'start':
                if elem.tag == 'node':
                    if 'id' in elem.attrib: entry['osm_id'] = elem.attrib['id']
                    if 'lat' in elem.attrib: entry['lat'] = elem.attrib['lat']
                    if 'lon' in elem.attrib: entry['lon'] = elem.attrib['lon']
                    if 'timestamp' in elem.attrib: entry['date_added'] = elem.attrib['timestamp']
                    coords = [(float(elem.attrib['lat']), float(elem.attrib['lon']))]
                    location = locator.reverse(coords)


                    print(location.raw)
                    json_dump = json.dumps(str(location.raw))
                    dictionary = json.loads(json_dump)

                    if 'postcode' in dictionary:
                        entry['postal_code'] = location.raw['address']['postcode']
                    else:
                        entry['postal_code'] = ""

                    if 'village' in dictionary:
                        entry['city'] = location.raw['address']['village']
                    elif 'town' in dictionary:
                        entry['city'] = location.raw['address']['town']
                    elif 'municipality' in dictionary:
                        entry['city'] = location.raw['address']['municipality']
                    elif 'city' in dictionary:
                        entry['city'] = location.raw['address']['city']
                    else:
                        entry['city'] = ""

                    entry['country'] = location.raw['address']['country']
            elif event == 'end':
                if elem.tag == 'tag':
                    if 'k' in elem.attrib and elem.attrib['k'] == 'name': entry['name'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'name:en': entry['name:en'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'int_name': entry['int_name'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'old_name': entry['old_name'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'old_name:en': entry['old_name:en'] = elem.attrib['v']
                    # if 'k' in elem.attrib and elem.attrib['k'] == 'addr:country': entry['country'] = elem.attrib['v']
                    # if 'k' in elem.attrib and elem.attrib['k'] == 'addr:city': entry['city'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'website': entry['website'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'phone': entry['phone'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'description': entry['description'] = elem.attrib['v']
                elif elem.tag == 'node':
                    # add to csv
                    csv_writer.writerow(entry)
                    num_rows += 1
                    entry = create_entry()
        print('wrote {} rows to {}'.format(num_rows, args.output))

if __name__ == '__main__':
    main()
