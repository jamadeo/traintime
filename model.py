from nycmta import GtfsCollection, TrainTrip
import collections
import time

def get_trains_for_stops(gtfs_dir, api_key, stops):
    Station = collections.namedtuple('Station', ['name', 'trains'])
    StatusRow = collections.namedtuple('StatusRow', ['arrival', 'status', 'route'])
    ret_stops = []

    gtfs = GtfsCollection("7cecfe7c2a37b4301cc351b57aaaed9f")
    gtfs.load_real_time_data()
    real_time_data = gtfs.real_time_data
    gtfs.load_stops("{0}/stops.txt".format(gtfs_dir))
    gtfs.load_stop_times("{0}/stop_times.txt".format(gtfs_dir))

    for stop in stops:
        trains = gtfs.get_upcoming_trains_at_stop(stop)
        stop_name = gtfs.get_stop(stop)

        station = Station(stop_name, [])

        for train, arrival in trains:
            seconds_from_now = arrival - int(time.time())
            q, r = divmod(seconds_from_now, 60)
            arrival_estimate = q + (0 if r is 0 else 1)

            #If the estimate is in the past, we suspect bad data and ignore.
            if arrival_estimate >= 0 or train.is_status_known:
                station.trains.append(StatusRow("{0} will arrive in {1} minute(s)".format(train.get_name(), arrival_estimate if arrival_estimate > 0 else 0), \
                                    "Current status: {0}".format(train.get_status(gtfs)), train.route_id))

        ret_stops.append(station)

    return ret_stops