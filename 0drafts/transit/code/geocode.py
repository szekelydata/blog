import simplejson, urllib
import re
import time
import operator
import os
import sys
import argparse
from collections import defaultdict

REMOVE_HTML_TAGS = r'<[^>]+>'

GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
DIRECTIONS_BASE_URL = 'http://maps.googleapis.com/maps/api/directions/json'

def geocode(address, **geo_args):
    geo_args.update({
        'address': address
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    return result['results']

def reverse_geocode(lat, lng):
    geo_args = {
        'latlng': "%s,%s" % (lat, lng)
    }

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    return result['results']

def directions(source, destination, **geo_args):
    geo_args.update({
        'origin': source,
        'destination': destination
    })

    url = DIRECTIONS_BASE_URL + '?' + urllib.urlencode(geo_args)
    return simplejson.load(urllib.urlopen(url))

def output_routes(mode, routes):
    timings = defaultdict(lambda: 0)
    distances = defaultdict(lambda: 0)
    for route in routes:
        for leg in route['legs']:
            print "Distance: ", leg['distance']['text']
            print "Duration: ", leg['duration']['text']
            for step in leg['steps']:
                travel_mode = step['travel_mode']
                if 'html_instructions' in step:
                    direction_text = re.sub(REMOVE_HTML_TAGS, ' ', step['html_instructions'])
                else:
                    direction_text = '(no direction text)'

                distance = step['distance']
                duration = step['duration']
                encoded_direction_text = direction_text.encode('latin1', errors='ignore')
                print "%s (%s, %s, %s)" % (encoded_direction_text, travel_mode,
                    duration['text'], distance['text'])
                timings["%s-%s" % (mode, travel_mode)] += duration['value']
                distances["%s-%s" % (mode, travel_mode)] += distance['value']
    return timings, distances

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", required=False,  default=False,
        action='store_true', help="Don't make API calls")
    ap.add_argument("--min-lng", required=False, default=103.73,
        type=float, help="Minimum longitude (Default 103.73)")
    ap.add_argument("--max-lng", required=False, default=103.84,
        type=float,  help="Maximum longitude (Default 103.84)")
    ap.add_argument("--min-lat", required=False, default=1.27,
        type=float, help="Minimum latitude (Default 1.27)")
    ap.add_argument("--max-lat", required=False, default=1.345,
        type=float, help="Maximum latitude (Default 1.345)")
    ap.add_argument("--step-lng", required=False, default=0.00125,
        type=float, help="Increment longitude amount (Default 0.00125)")
    ap.add_argument("--step-lat", required=False, default=0.00125,
        type=float, help="Increment latitude amount (Default 0.00125)")
    args = vars(ap.parse_args())

    print args

    # load existing timings
    if os.path.exists('timings.csv'):
        timings = [ row.strip().split('\t') for row in file('timings.csv') ]
    else:
        timings = []
    print 'Found %d existing timings' % len(timings)
    latlngs = dict(('%s,%s' % (k,v), True) for (k,v,_,_,_,_) in timings)

    if not args['dry_run']:
        results = geocode(address="The Pinnacle @ Duxton")
        data = results[0]
        location = data['geometry']['location']
        lat, lng = location['lat'], location['lng']
        source = "%s,%s" % (lat, lng)
        print source
        with open('source.txt', 'w') as sourcef:
            sourcef.write("%s,%s\n" % (lat, lng))
        results = reverse_geocode(lat, lng)
        print 'Reverse geocoded address for lat,lng: %.3f,%.3f' % (lat, lng)
        print '\n'.join([ x['formatted_address'] for x in results ])
        print

        time.sleep(5)

    eight_am = int(time.mktime(time.struct_time([2014,7,14,8,0,0,0,0,0])))

    # starting longitude
    lng_f = args['min_lng']

    min_lat_f = args['min_lat']

    while lng_f < args['max_lng']:

        # starting latitude
        lat_f = args['max_lat']

        while lat_f >= min_lat_f:
            print 'Querying directions for (%.6f, %.6f)' % (lat_f, lng_f)

            key = '%.6f,%.6f' % (lat_f, lng_f)
            if latlngs.has_key(key):
                lat_f -= args['step_lat']
                print 'Timing already exists - skipping.'
                continue

            if not args['dry_run']:
                results = reverse_geocode(lat_f, lng_f)
                print 'Reverse geocoded address for lat,lng: %.3f,%.3f' % (lat_f, lng_f)
                print '\n'.join([ x['formatted_address'] for x in results ])
                print

            durations = defaultdict(lambda: 0)
            distances = defaultdict(lambda: 0)

            if not args['dry_run']:
                for mode in ['driving','walking','transit']:
                    params = {
                            'mode': mode,
                            'region': 'sg',
                            'alternatives': 'false',
                            'departure_time': eight_am
                            }

                    data = directions(source, '%s,%s' % (lat_f, lng_f), **params)
                    print data['status']

                    while data['status'] == 'OVER_QUERY_LIMIT':
                        print 'Pausing for five minutes...'
                        time.sleep(300)
                        data = directions(source, '%s,%s' % (lat_f, lng_f), **params)

                    if len(data['routes']) > 0:
                        timings, dist = output_routes(mode, data['routes'])
                        durations.update(timings)
                        distances.update(dist)
                        print 'Timings:'
                        print timings.viewitems()
                        print 'Distances:'
                        print dist.viewitems()

                    time.sleep(2)

                print sorted(durations.iteritems(), key=operator.itemgetter(1))

                get_stats = lambda d: [ d['driving-DRIVING'], d['transit-TRANSIT'],
                    d['transit-WALKING'], d['walking-WALKING'] ]

                with open('timings.csv','a+') as outf:
                    stats = get_stats(durations)
                    params = [lat_f, lng_f]; params.extend(stats)
                    outf.write("%.6f\t%.6f\t%s\t%s\t%s\t%s\n" % tuple(params))

                with open('distances.csv','a+') as outf:
                    stats = get_stats(distances)
                    params = [lat_f, lng_f]; params.extend(stats)
                    outf.write("%.6f\t%.6f\t%s\t%s\t%s\t%s\n" % tuple(params))

            lat_f -= args['step_lat']

        lng_f += args['step_lng']