from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def arrivals (stations):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'\n'])
    extend_([u'<!-- template to render a table of upcoming trains, for use with web.py -->\n'])
    extend_([u'\n'])
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<table>\n'])
    extend_([u'<link rel="stylesheet" href="../stylesheets/arrivals.css">\n'])
    for station in loop.setup(stations):
        extend_([u'<th colspan="2"><h4>', escape_(station.name, True), u'</h4></th>\n'])
        for train in loop.setup(station.trains):
            extend_([u'<tr class="r', escape_(train.route, True), u'">\n'])
            extend_([u'    <td>', escape_(train.arrival, True), u'</td>\n'])
            extend_([u'    <td>', escape_(train.status, True), u'</td>\n'])
            extend_([u'<tr>\n'])
    extend_([u'</table>\n'])

    return self

arrivals = CompiledTemplate(arrivals, 'templates/arrivals.html')
join_ = arrivals._join; escape_ = arrivals._escape

