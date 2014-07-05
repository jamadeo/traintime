#!/usr/bin/python

import web
import StringIO
import time
from gtfs_test import write_arrival_board

urls = (
    '/trains/(.*\\.css)', 'styles',
    '/trains/(.*)', 'traintime'
)

class cache:
    def __init__(self, threshold):
        self.threshold = threshold
        self.last_update = 0
        self.content = ""

    def get_content(self, train_stops):
        if (int(time.time()) - self.last_update) > self.threshold:
            self.last_update = int(time.time())
            out_str = StringIO.StringIO()
            write_arrival_board('google_transit_2014_07_04', train_stops.split(','), out_str)
            self.content = out_str.getvalue()
        return self.content

cache = cache(30)

class traintime:
    def GET(self, train_stops):
        return cache.get_content(train_stops)

class styles:
    def GET(self, style):
        f = open(style)
        style_str = f.read()
        f.close()
        return style_str

def main():
    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    main()