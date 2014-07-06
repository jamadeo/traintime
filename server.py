#!/usr/bin/python

import os
import sys

# Needs to execute before any other imports
import google

vendor_dir = os.path.join(os.path.dirname(__file__), 'vendor')
google.__path__.append(os.path.join(vendor_dir, 'google'))

sys.path.insert(0, vendor_dir)

import web
import time
import model

urls = (
    '/trains/(.*\\.css)', 'styles',
    '/trains/(.*)', 'traintime'
)

render = web.template.render('templates')

class cache:
    def __init__(self, threshold):
        self.threshold = threshold
        self.last_update = 0
        self.content = {}

    def get_content(self, train_stops):
        if (int(time.time()) - self.last_update) > self.threshold:
            self.last_update = int(time.time())
            self.content = model.get_trains_for_stops('google_transit_2014_07_04', '7cecfe7c2a37b4301cc351b57aaaed9f', train_stops)
        return self.content

cache = cache(30)

class traintime:
    def GET(self, train_stops):
        return render.arrivals(cache.get_content(train_stops.split(',')))

class styles:
    def GET(self, style):
        f = open(style)
        style_str = f.read()
        f.close()
        return style_str

app = web.application(urls, globals())

app = app.gaerun()

# def main():
#     app = web.application(urls, globals())
#     app.run()

# if __name__ == '__main__':
#     main()