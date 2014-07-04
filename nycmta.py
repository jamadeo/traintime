import gtfs_realtime_pb2
import time
import datetime
import csv
import json
import urllib2
from pprint import pprint

def loadStops(stopsFileName):
    stopsDict = dict()
    f = open(stopsFileName, "rb")
    reader = csv.reader(f, delimiter=',')

    headerRow = next(reader)
    stop_id_ix = headerRow.index('stop_id')
    stop_name_ix = headerRow.index('stop_name')
    stop_type_ix = headerRow.index('stop_type')

    for row in reader:
        print row
        stopsDict[row[stop_id_ix]] = {"stop_name" : row[stop_name_ix], "stop_type" : row[stop_type_ix]}
    return stopsDict
    
def loadRoutes(routesFileName):
    routesDict = dict()
    f = open(routesFileName, "rb")
    reader = csv.reader(f, delimiter=',')

    headerRow = next(reader)
    route_id_ix = headerRow.index('route_id')
    route_short_name_ix = headerRow.index('route_short_name')
    route_long_name_ix = headerRow.index('route_long_name')
    for row in reader:
        routesDict[row[route_id_ix]] = {"route_short_name" : row[route_short_name_ix], "route_long_name" : row[route_long_name_ix]}
    return routesDict
    
def loadTrips(tripsFileName):
    tripsDict = dict()
    f = open(tripsFileName, "rb")
    reader = csv.reader(f, delimiter=',')
    
    headerRow = next(reader)
    trip_id_ix = headerRow.index('trip_id')
    route_id_ix = headerRow.index('route_id')
    service_id_ix = headerRow.index('service_id')
    for row in reader:
        tripsDict[row[trip_id_ix]] = {"route_id" : row[route_id_ix], "service_id" : row[service_id_ix]}
    return tripsDict

def loadPartialTrips(tripsFileName):
    tripsDict = dict()
    f = open(tripsFileName, "rb")
    reader = csv.reader(f, delimiter=',')
    
    headerRow = next(reader)
    trip_id_ix = headerRow.index('trip_id')
    route_id_ix = headerRow.index('route_id')
    service_id_ix = headerRow.index('service_id')
    for row in reader:
        tripsDict[row[trip_id_ix]] = {"route_id" : row[route_id_ix], "service_id" : row[service_id_ix]}
    return tripsDict
    
def loadStopTimes(stopTimesFileName):
    stopTimesDict = dict()
    f = open(stopTimesFileName, "rb")
    reader = csv.reader(f, delimiter=',')
    
    headerRow = next(reader)
    trip_id_ix = headerRow.index('trip_id')
    stip_id_ix = headerRow.index('stop_id')
    arrival_time_ix = headerRow.index('arrival_time')
    departure_time_ix = headerRow.index('departure_time')
    stop_sequence_ix = headerRow.index('stop_sequence')
    for row in reader:
        tripId = row[trip_id_ix].split('_')
        if len(tripId) < 3:
            continue
        tripIdKey = tripId[1] + '_' + tripId[2]
        stopTimesDict[(tripIdKey, row[stop_id_ix])] = { "arrival_time"      : row[arrival_time_ix], \
                                                        "departure_time"    : row[departure_time_ix], \
                                                        "stop_sequence"     : row[stop_sequence_ix]}
    return stopTimesDict
    
def loadCalendar(calendarFileName):
    calendarDict = dict()
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
        calendarDict[row[0]] = {"monday"    : row[monday_ix], \
                                "tuesday"   : row[tuesday_ix], \
                                "wednesday" : row[wednesday_ix], \
                                "thursday"  : row[thursday_ix], \
                                "friday"    : row[friday_ix], \
                                "saturday"  : row[saturday_ix], \
                                "sunday"    : row[sunday_ix], \
                                "start_date": row[start_date_ix], \
                                "end_date"  : row[end_date_ix]  \
                                }
    return calendarDict
    
def loadCalendarDates(calendarDatesFileName):
    calendarDatesDict = dict()
    f = open(calendarDatesFileName, "rb")
    reader = csv.reader(f, delimiter=',')
    
    headerRow = next(reader)
    service_id_ix = headerRow.index('service_id')
    date_ix = headerRow.index('date')
    exception_type_ix = headerRow.index('exception_type')
    for row in reader:
        calendarDatesDict[(row[service_id_ix], row[date_ix])] = {"exception_type" : row[exception_type_ix]}
    return calendarDatesDict
    
def loadTransfers(transfersFileName):
    transfersDict = dict()
    f = open(transfersFileName, "rb")
    reader = csv.reader(f, delimiter=',')
    
    headerRow = next(reader)
    from_stop_id_ix = headerRow.index('from_stop_ix')
    to_stop_id_ix = headerRow.index('to_stop_id')
    transfer_type_ix = headerRow.index('transfer_type')
    for row in reader:
        transfersDict[(row[from_stop_id_ix], row[to_stop_id_ix])] = {"transfer_type" : row[transfer_type_ix]}
    return transfersDict

def printEntity(entity, stops, stopTimes):
    if entity.vehicle.trip.route_id != '':
        try:
            train = entity.vehicle.trip.route_id
            stop = stops[entity.vehicle.stop_id]['stop_name']
            direction = entity.vehicle.trip.trip_id[10]
            timediff = time.time() - entity.vehicle.timestamp
            
            status = ''
            if entity.vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('IN_TRANSIT_TO'):
                status = "in transit"
            elif entity.vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('STOPPED_AT'):
                status = "stopped"
            elif entity.vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Value('INCOMING_AT'):
                status = "incoming"
            print "{0} train is {1} at {2}, direction {3}, {4:.0f} seconds ago".format(train, status, stop, direction, timediff)
            
        except RuntimeError as e:
            print "Error", e
        except AttributeError as e:
            print "Attribute error", e
        except:
            print "Other error for entity:", entity
            
        try:
            stopTime = stopTimes[(str(entity.vehicle.trip.trip_id), str(entity.vehicle.stop_id))]
            print "\tScheduled Arrival:", stopTime['arrival_time'], ", Scheduled Departure:", stopTime['departure_time']
        except KeyError as ke:
            #print "Could not find scheduled stop time."
            pass
        except Exception as e:
            #print "Error for entity", entity
            print "Error:", e
    # print entity
    # print entity.vehicle
    # print entity.trip_update.trip.trip_id
    # print trips[entity.trip_update.trip.trip_id]
    
def getRealtimeFile(key):
    url = 'http://datamine.mta.info/mta_esi.php?key='+key
    realtimeFile = urllib2.urlopen(url)
    return realtimeFile
    
    