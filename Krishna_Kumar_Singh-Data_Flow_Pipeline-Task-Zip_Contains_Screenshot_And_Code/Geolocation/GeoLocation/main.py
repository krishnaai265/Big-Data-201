import csv
from opencage.geocoder import OpenCageGeocode, RateLimitExceededError
import pygeohash as gh
from kafka import KafkaProducer

# API OenCage API Key
key = 'API-Key'
geocoder = OpenCageGeocode(key)

# Generate GeoHash from latitude & longitude
def generate_geohash(latitude, longitude):
    return gh.encode(latitude, longitude, precision=4)

# Producer to write data on a topic
def producer(id, hotels_latitude, hotels_longitude, address, geohash):
    row = id + "," + hotels_latitude + "," + hotels_longitude + "," + address + "," + geohash
    kafka_producer = KafkaProducer(bootstrap_servers='localhost:9092')
    kafka_producer.send('test', bytes(row, 'utf-8'))


# check geocoordinate
def check_geocoordinate(reader):
    i = 0
    for row in reader:
        # Only run 10 times due to limited free api calls
        i = i + 1
        if i > 10:
            break
        # reading address from csv file
        id = row['Id'].strip()
        city = row['City'].strip()
        country = row['Country'].strip()
        home = row['Address'].strip()
        address = home + "," + city + "," + country
        # reading latitude & longitude from api by passing address
        results = geocoder.geocode(address, no_annotations='1')

        if results and len(results):
            longitude = "{:.0f}".format(results[0]['geometry']['lng'])
            latitude = "{:.0f}".format(results[0]['geometry']['lat'])
            hotels_latitude = "{:.0f}".format(float(row['Latitude'].strip()))
            hotels_longitude = "{:.0f}".format(float(row['Longitude'].strip()))
            if hotels_latitude == latitude and hotels_longitude == longitude:
                geohash = generate_geohash(float(latitude), float(longitude))
                producer(id, hotels_latitude, hotels_longitude, address, geohash)
                print(u"Valid Coordinates %s, %s, %s, %s, Geohash: %s" % (
                    id, hotels_latitude, hotels_longitude, address, geohash))
            else:
                print(u'InValid CSV Coordinates %s, %s, %s not match with %s, %s' % (
                    id, hotels_latitude, hotels_longitude, latitude, longitude))
        else:
            IndexError("not found: %s\n" % address)


# read csv from resources
def read_csv(hotelsfile):
    try:
        with open(hotelsfile, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            check_geocoordinate(reader)
    except IOError:
        raise FileNotFoundError('Error: File %s does not appear to exist.' % hotelsfile)
    except RateLimitExceededError as ex:
        raise RateLimitExceededError("Error: Rate Limit exceed error")



if __name__ == '__main__':
    hotelsfile = 'resource/hotels.csv'
    read_csv(hotelsfile)
