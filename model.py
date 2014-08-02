from nycmta import GtfsCollection, TrainTrip
import collections
import time

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
        print "Loading GtfsDataCache. Last loaded {0}".format(self.timestamp)
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
    return cache.getCollection().get_supported_stops(['1', '2', '3', '4', '5', '6'])

def get_trains_for_stops(stops, sort=True):
    cache.assertInitialized()

    unicode_map = {
        '1' : u'\u2460',
        '2' : u'\u2461',
        '3' : u'\u2462',
        '4' : u'\u2463',
        '5' : u'\u2464',
        '6' : u'\u2465'
    }

    Station = collections.namedtuple('Station', ['name', 'trains'])
    StatusRow = collections.namedtuple('StatusRow', ['arrival_string',
                                                     'status_string',
                                                     'route',
                                                     'arrival_estimate',
                                                     'arrival_estimate_class',
                                                     'unicode_route'])
    ret_stops = []

    gtfs = cache.getCollection()

    for stop in stops:
        trains = gtfs.get_upcoming_trains_at_stop(stop)
        stop_name = gtfs.get_stop(stop)

        station = Station(stop_name, [])

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

                station.trains.append(StatusRow(arrival_string,
                                                status_string,
                                                train.route_id,
                                                arrival_estimate,
                                                min(arrival_estimate, 10),
                                                unicode_map[train.route_id]))

        if sort:
            station.trains.sort(lambda trainA, trainB: int(trainA.arrival_estimate - trainB.arrival_estimate))

        ret_stops.append(station)
    return ret_stops