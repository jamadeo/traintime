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
import json
from web import form

urls = (
    '/trains/?', 'index',
    '/trains/(.+)', 'traintime'
)

render = web.template.render('templates')
app_config = json.load(open('gtfs.config'))
model.initialize(app_config['api_key'], app_config['gtfs_directory'], app_config['cache_max_age'])

class index:
    def GET(self):
        return render.index(sorted(model.get_stops(), key=lambda stop:stop[1]))

    def POST(self):
        user_input = web.input(stations=[])
        raise web.seeother('/trains/' + ','.join(user_input.stations))

class traintime:
    def GET(self, train_stops):
        return render.arrivals(model.get_trains_for_stops(train_stops.split(',')))

class styles:
    def GET(self, style):
        f = open(style)
        style_str = f.read()
        f.close()
        return style_str

app = web.application(urls, globals())

app = app.gaerun()