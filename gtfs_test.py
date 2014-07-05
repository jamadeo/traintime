#!/usr/bin/python

import sys
import time
import argparse
from nycmta import GtfsCollection, TrainTrip

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-G", "--GTFSDirectory", help="Directory containing MTA's static GTFS data")
    parser.add_argument("-s", "--stations", nargs="+", help="List of interested stations")
    parser.add_argument("-H", "--htmlOutput", help="Optionally output HTML to a specified file")
    return parser.parse_args()


class Writer():
    def __init__(self, fp=sys.stdout, use_html=False):
        self.fp = fp
        self.use_html = use_html

    def start_write(self):
        if self.use_html:
            self.fp.write("<!DOCTYPE html>\n")
            self.fp.write("<table>\n")
            self.fp.write('<link rel="stylesheet" href="styles.css">\n')

    def write_header_row(self, header_text):
        if self.use_html:
            str_to_write = "\t<th colspan=\"2\"><h3>" + header_text + "</h3></th>\n"
        else:
            str_to_write = header_text + "\n"
        self.fp.write(str_to_write)

    def write_status_row(self, arrival_col, status_col):
        if self.use_html:
            str_to_write = "\t<tr><td>" + arrival_col + "</td><td>" + status_col + "</td></tr>\n"
        else:
            str_to_write = arrival_col + "\n\t" + status_col + "\n"
        self.fp.write(str_to_write)

    def end_write(self):
        if self.use_html:
            self.fp.write("</table>\n")


def write_arrival_board(gtfs_dir, interested_stops, htmlOutput=None):
    gtfs = GtfsCollection("7cecfe7c2a37b4301cc351b57aaaed9f")

    gtfs.load_real_time_data()
    real_time_data = gtfs.real_time_data
    gtfs.load_stops("{0}/stops.txt".format(gtfs_dir))
    gtfs.load_stop_times("{0}/stop_times.txt".format(gtfs_dir))

    if htmlOutput is not None:
        writer = Writer(htmlOutput, use_html=True)
    else:
        writer = Writer()

    if interested_stops is None:
        raise RuntimeError('No stops supplied') 
        return

    writer.start_write()
    for stop in interested_stops:
        trains = gtfs.get_upcoming_trains_at_stop(stop)
        writer.write_header_row("{0}:".format(gtfs.get_stop(stop)))

        if len(trains) == 0:
            writer.write_status_row("No data for this stop.","")

        for train_arrival in trains:
            arrival = train_arrival[1]
            seconds_from_now = arrival - int(time.time())
            q, r = divmod(seconds_from_now, 60)
            arrival_estimate = q + (0 if r is 0 else 1)
            writer.write_status_row("{0} will arrive in {1} minute(s)".format(train_arrival[0].get_name(), arrival_estimate if arrival_estimate > 0 else 0), \
                                    "Current status: {0}".format(train_arrival[0].get_status(gtfs)))
    writer.end_write()


########################################################################
# Main Program Begin
########################################################################

def main():
    args = parse_args()
    if args.htmlOutput is not None:
        write_arrival_board(args.GTFSDirectory, args.stations, open(args.htmlOutput,'w'))
    else:
        write_arrival_board(args.GTFSDirectory, args.stations)

if __name__ == '__main__':
    main()

#End Main Program