from nycmta import GtfsCollection, TrainTrip
import collections
import time
from datetime import datetime
import pytz
import logging

class GtfsDataCache:
    def __init__(self):
        self.collection = {}
        self.timestamp = -1
        self.api_key = ''
        self.gtfs_dir = ''
        self.time_threshold = -1

    def initialize(self):
        self.collection = GtfsCollection(self.api_key)

    def __load(self):
        logging.info("Loading GtfsDataCache. Last loaded {0}".format(self.timestamp))
        self.collection.load_real_time_data()
        self.collection.load_stops("{0}/stops.txt".format(self.gtfs_dir))
        self.timestamp = int(time.time())

    def getCollection(self):
        if (int(time.time()) - self.timestamp) > self.time_threshold:
            self.__load()

        return self.collection

    def assertInitialized(self):
        if self.api_key == '' or self.gtfs_dir == '':
            raise RuntimeError('Cache not initalized! (Need to call init_cache())')

cache = GtfsDataCache()

def initialize(api_key, gtfs_dir, cache_time):
    cache.api_key = api_key
    cache.gtfs_dir = gtfs_dir
    cache.time_threshold = cache_time
    cache.initialize()

def get_stops():
    cache.assertInitialized()
    return cache.getCollection().get_supported_stops(['1', '2', '3', '4', '5', '6', 'L'])

def get_trains_for_stops(stops, max_later_stops=10, sort=True):
    cache.assertInitialized()

    unicode_map = {
        '1' : u'\u2460',
        '2' : u'\u2461',
        '3' : u'\u2462',
        '4' : u'\u2463',
        '5' : u'\u2464',
        '6' : u'\u2465'
    }

    Station = collections.namedtuple('Station', ['id', 'name', 'trains'])
    StatusRow = collections.namedtuple('StatusRow', ['arrival_string',
                                                     'status_string',
                                                     'route',
                                                     'arrival_estimate',
                                                     'arrival_estimate_class',
                                                     'unicode_route',
                                                     'trip_id',
                                                     'upcoming_stops'])
    ret_stops = []

    gtfs = cache.getCollection()

    for stop in stops:
        trains = gtfs.get_upcoming_trains_at_stop(stop)
        stop_name = gtfs.get_stop(stop)

        station = Station(stop, stop_name, [])

        for train, arrival in trains:
            seconds_from_now = arrival - int(time.time())
            q, r = divmod(seconds_from_now, 60)
            arrival_estimate = q + (0 if r is 0 else 1)

            #If the estimate is in the past, we suspect bad data and ignore.
            if arrival_estimate >= 0 or train.is_status_known():
                route = train.get_name()
                arrival_string = "{0} minutes".format(arrival_estimate) if arrival_estimate > 1 else \
                                 "1 minute" if arrival_estimate == 1 else \
                                 "Now arriving" if arrival_estimate == 0 else \
                                 "Unavailable"

                status_string = train.get_status(gtfs)

                route_symbol = ""
                try:
                    route_symbol = unicode_map[train.route_id]
                except KeyError:
                    route_symbol = train.route_id

                station.trains.append(StatusRow(arrival_string,
                                                status_string,
                                                train.route_id,
                                                arrival_estimate,
                                                min(arrival_estimate, 10),
                                                route_symbol,
                                                train.trip_id,
                                                get_stops_for_trip(train.trip_id, max_later_stops)))

        if sort:
            station.trains.sort(lambda trainA, trainB: int(trainA.arrival_estimate - trainB.arrival_estimate))

        ret_stops.append(station)
    return ret_stops

def get_stops_for_trip(train, bound=-1):
    cache.assertInitialized()
    gtfs = cache.getCollection()

    StatusRow = collections.namedtuple('StatusRow', ['stop_name',
                                                     'stop_id',
                                                     'arrival_time',
                                                     'arrival_string',
                                                     'arrival_time_epoch'])

    stops = []
    total = 0
    for stop_id, arrival_time_epoch in gtfs.get_stops_for_trip(train):
        if total == bound:
            break

        eastern = pytz.timezone('US/Eastern')
        arrival_time = pytz.utc.localize(datetime.fromtimestamp(arrival_time_epoch)).astimezone(eastern)
        
        seconds_from_now = arrival_time_epoch - int(time.time())
        q, r = divmod(seconds_from_now, 60)
        arrival_estimate = q + (0 if r is 0 else 1)

        stop_name = gtfs.get_stop(stop_id, False)
        arrival_string = "{0} minutes".format(arrival_estimate) if arrival_estimate > 1 else \
                         "1 minute" if arrival_estimate == 1 else \
                         "Now" if arrival_estimate == 0 else \
                         "Unavailable"

        stops.append(StatusRow(stop_name,
                               stop_id,
                               arrival_time.strftime('%I:%M %p') if arrival_time_epoch != 0 else "",
                               arrival_string,
                               arrival_time_epoch))
        total = total+1

    return stops