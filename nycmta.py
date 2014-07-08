import gtfs_realtime_pb2
import csv
import urllib2
from pprint import pprint

class TrainTrip:
    def __init__(self, trip_id, route_id):
        self.trip_id = trip_id
        self.route_id = route_id
        self.stop_id = None
        self.status = None
        self.status_timestamp = None
        self.stops = []

    def __repr__(self):
        return "[trip_id:{0}, route_id:{1}, stop:{2}, status:{3}]".format(self.trip_id, self.route_id, self.stop_id, self.status)

    def set_status(self, stop_id, status, timestamp):
        self.stop_id = stop_id
        self.status = status
        self.status_timestamp = timestamp

    def update_status(self, stop_id, status, timestamp):
        if self.status_timestamp is None or timestamp > self.status_timestamp:
            self.set_status(stop_id, status, timestamp)

    def set_stops(self, stops):
        self.stops = stops

    def get_name(self):
        return "{0} train".format(self.route_id)

    def is_status_known(self):
        return self.stop_id is not None and self.status is not None

    def get_status(self, gtfs_collection):
        if not self.is_status_known():
            return "[unknown: probably has not started run]"

        stop_name = gtfs_collection.get_stop(self.stop_id)

        if self.status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('IN_TRANSIT_TO'):
            status = "in transit"
        elif self.status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('STOPPED_AT'):
            status = "stopped"
        elif self.status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('INCOMING_AT'):
            status = "incoming"
        return "{0} at {1}".format(status, stop_name)

            

class GtfsCollection:
    def __init__(self, api_key):
        self.api_key = api_key

        #Static data
        self.stops = {}
        self.routes = {}
        self.trips = {}
        self.stop_times = {}
        self.calender = {}
        self.calendar_dates = {}
        self.transfers = {}

        #Real-time data
        self.trips = {}
        self.trips_by_stop = {}


    def load_stops(self, stopsFileName):
        f = open(stopsFileName, "rb")
        reader = csv.reader(f, delimiter=',')

        headerRow = next(reader)
        stop_id_ix = headerRow.index('stop_id')
        stop_name_ix = headerRow.index('stop_name')
        parent_station_ix = headerRow.index('parent_station')

        for row in reader:
            self.stops[row[stop_id_ix]] = {"stop_name" : row[stop_name_ix], "parent_station" : row[parent_station_ix]}

    def get_supported_stops(self, supported_stops):
        stops = []
        for stop_id, stop in self.stops.iteritems():
            if stop_id[0] not in supported_stops:
                continue

            if stop_id[-1] == 'N':
                direction = ' (Northbound)'
            elif stop_id[-1] == 'S':
                direction = ' (Southbound)'
            else:
                continue

            stops.append((stop_id, stop['stop_name'] + direction))
        return stops
        
    def load_routes(self, routesFileName):
        f = open(routesFileName, "rb")
        reader = csv.reader(f, delimiter=',')

        headerRow = next(reader)
        route_id_ix = headerRow.index('route_id')
        route_short_name_ix = headerRow.index('route_short_name')
        route_long_name_ix = headerRow.index('route_long_name')
        for row in reader:
            self.routes[row[route_id_ix]] = {"route_short_name" : row[route_short_name_ix], "route_long_name" : row[route_long_name_ix]}
        
    def load_trips(self, tripsFileName):
        f = open(tripsFileName, "rb")
        reader = csv.reader(f, delimiter=',')
        
        headerRow = next(reader)
        trip_id_ix = headerRow.index('trip_id')
        route_id_ix = headerRow.index('route_id')
        service_id_ix = headerRow.index('service_id')
        for row in reader:
            self.trips[row[trip_id_ix]] = {"route_id" : row[route_id_ix], "service_id" : row[service_id_ix]}

    def load_stop_times(self, stopTimesFileName):
        f = open(stopTimesFileName, "rb")
        reader = csv.reader(f, delimiter=',')
        
        headerRow = next(reader)
        trip_id_ix = headerRow.index('trip_id')
        stop_id_ix = headerRow.index('stop_id')
        arrival_time_ix = headerRow.index('arrival_time')
        departure_time_ix = headerRow.index('departure_time')
        stop_sequence_ix = headerRow.index('stop_sequence')
        for row in reader:
            tripId = row[trip_id_ix].split('_')
            if len(tripId) < 3:
                continue
            tripIdKey = tripId[1] + '_' + tripId[2]
            self.stop_times[(tripIdKey, row[stop_id_ix])] = { "arrival_time"      : row[arrival_time_ix], \
                                                              "departure_time"    : row[departure_time_ix], \
                                                              "stop_sequence"     : row[stop_sequence_ix]}
        
    def load_calendar(self, calendarFileName):
        f = open(calendarFileName, "rb")
        reader = csv.reader(f, delimiter=',')
        
        headerRow = next(reader)
        monday_ix       = headerRow.index('monday')
        tuesday_ix      = headerRow.index('tuesday')
        wednesday_ix    = headerRow.index('wednesday')
        thursday_ix     = headerRow.index('thursday')
        friday_ix       = headerRow.index('friday')
        saturday_ix     = headerRow.index('saturday')
        sunday_ix       = headerRow.index('sunday')
        start_date_ix   = headerRow.index('start_date')
        end_date_ix     = headerRow.index('end_date')

        for row in reader:
            self.calendar[row[0]] = { "monday"    : row[monday_ix], \
                                      "tuesday"   : row[tuesday_ix], \
                                      "wednesday" : row[wednesday_ix], \
                                      "thursday"  : row[thursday_ix], \
                                      "friday"    : row[friday_ix], \
                                      "saturday"  : row[saturday_ix], \
                                      "sunday"    : row[sunday_ix], \
                                      "start_date": row[start_date_ix], \
                                      "end_date"  : row[end_date_ix]  \
                                      }
        
    def load_calendar_dates(self, calendarDatesFileName):
        f = open(calendarDatesFileName, "rb")
        reader = csv.reader(f, delimiter=',')
        
        headerRow = next(reader)
        service_id_ix = headerRow.index('service_id')
        date_ix = headerRow.index('date')
        exception_type_ix = headerRow.index('exception_type')
        for row in reader:
            self.calendar_dates[(row[service_id_ix], row[date_ix])] = {"exception_type" : row[exception_type_ix]}
        
    def load_transfers(self, transfersFileName):
        f = open(transfersFileName, "rb")
        reader = csv.reader(f, delimiter=',')
        
        headerRow = next(reader)
        from_stop_id_ix = headerRow.index('from_stop_ix')
        to_stop_id_ix = headerRow.index('to_stop_id')
        transfer_type_ix = headerRow.index('transfer_type')
        for row in reader:
            self.transfers[(row[from_stop_id_ix], row[to_stop_id_ix])] = {"transfer_type" : row[transfer_type_ix]}

    def get_stop(self, stop_id):
        try:
            stop = self.stops[stop_id]['stop_name']

            if stop_id[-1] == 'S':
                direction = ' (Southbound)'
            elif stop_id[-1] == 'N':
                direction = ' (Northbound)'
            else:
                direction = ''
            return stop + direction
        except KeyError:
            return "[unknown stop]"

    def __get_trip(self, trip_id, route_id):
        trip = self.trips[trip_id] = self.trips.get(trip_id, TrainTrip(trip_id, route_id))
        return trip

    def __get_stop(self, stop_id):
        stops = self.trips_by_stop[stop_id] = self.trips_by_stop.get(stop_id, [])
        return stops

    def __ingest_trip_update(self, trip_update):
        trip = self.__get_trip(trip_update.trip.trip_id, trip_update.trip.route_id)

        for stop in trip_update.stop_time_update:
            if stop.stop_id is not None:
                time = stop.arrival.time if stop.arrival is not None else stop.departure.time
                stops = self.__get_stop(stop.stop_id)
                stops.append((trip, time))

    def __ingest_vehicle_status(self, vehicle):
        trip = self.__get_trip(vehicle.trip.trip_id, vehicle.trip.route_id)
        trip.update_status(vehicle.stop_id, vehicle.current_status, vehicle.timestamp)

    def __ingest_real_time_data(self):
        for entity in self.real_time_data.entity:
            if entity.trip_update is not None:
                self.__ingest_trip_update(entity.trip_update)
            if entity.vehicle is not None:
                self.__ingest_vehicle_status(entity.vehicle)

    def __clear_real_time_data(self):
        self.trips = {}
        self.trips_by_stop = {}

    def load_real_time_data(self):
        self.__clear_real_time_data()
        print "Fetching data from mta.info..."
        url = 'http://datamine.mta.info/mta_esi.php?key='+self.api_key
        real_time_data_file = urllib2.urlopen(url)
        print "Parsing data..."
        real_time_data = real_time_data_file.read()
        self.real_time_data  = gtfs_realtime_pb2.FeedMessage()
        self.real_time_data.ParseFromString(real_time_data)
        real_time_data_file.close()
        self.__ingest_real_time_data()

    def get_upcoming_trains_at_stop(self, stop):
        return self.__get_stop(stop)
    
    # def get_train_status(self, train):
    #     trip_id = 