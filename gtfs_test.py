#!/usr/bin/python

import sys
from nycmta import *

########################################################################
# Main Program Begin
########################################################################

if len(sys.argv) != 2:
	print "Usage:", sys.argv[0], "GTFS_DIR"
	sys.exit(-1)

gtfs_dir = sys.argv[1]

realtimeFile = getRealtimeFile("7cecfe7c2a37b4301cc351b57aaaed9f")

feed_message = gtfs_realtime_pb2.FeedMessage()
feed_message.ParseFromString(realtimeFile.read())

realtimeFile.close()

stops = loadStops(gtfs_dir + "/stops.txt")
routes = loadRoutes(gtfs_dir + "/routes.txt")
trips = loadTrips(gtfs_dir + "/trips.txt")
#partialTrips = loadPartialTrips(gtfs_dir + "/trips.txt")
stopTimes = loadStopTimes(gtfs_dir + "/stop_times.txt")

#for stopTime in stopTimes:
#	if stopTime[1] == "241" or stopTime[1] == "241N" or stopTime[1] == "241S":
#		print trips[stopTime[0]]
		
#print stopTimes

interested_lines = ('2','5')

for entity in feed_message.entity:
	if entity.vehicle.trip.route_id in interested_lines:
		printEntity(entity, stops, stopTimes)

#End Main Program