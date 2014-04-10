#!/usr/bin/env python

import mongoengine as me
from models import Pano
from google_streetview_api import *

import grequests
import csv, time, cStringIO


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path', help='CSV file with header that contains lat-long coordinates')
    parser.add_argument('-d', '--db', default='mongodb://localhost/test', help='mongodb URI')
    parser.add_argument('-b', '--batch-size', type=int, default=10, help='size of each request batch')
    parser.add_argument('-k', '--key', help='Google StreetView API key')
    parser.add_argument('-n', '--dry-run', action='store_true', help='dry run')
    parser.add_argument('--lat', default='lat', help='header for latitude')
    parser.add_argument('--long', default='long', help='header for longitude')

    args = parser.parse_args()

    if not args.dry_run:
        me.connect('', host=args.db)

    with open(args.csv_path) as f:
        r = csv.DictReader(f)
        longlats = set()
        params = []
        t0 = time.time()
        t1 = t0
        for i, row in enumerate(r):
            if i % 20 == 0:
                t2 = time.time()
                print '%d done, elapsed %fs' % (i, t2-t1)
                t2 = t1

            loc = row[args.long], row[args.lat]
            if loc not in longlats:
                try:
                    floc = (float(row[args.long]), float(row[args.lat]))
                except:
                    continue

                for heading in [0, 120, 240]:
                    params.append((floc, heading))
                    l = len(params)
                    if l >= args.batch_size:
                        # build URL
                        urls = [generate_pano_url(floc, fov=120, heading=heading, key=args.key) for floc, heading in params]
                        if not args.dry_run:
                            reqs = (grequests.get(url) for url in urls)
                            # send requests and block
                            reps = grequests.map(reqs)
                        
                            for j, (param, rep) in enumerate(zip(params, reps)):
                                if rep.status_code == 200:
                                    image = cStringIO.StringIO(rep.content)
                                    pano = Pano(longlat=param[0], fov=120, heading=param[1], image=image)
                                    pano.save()
                                else:
                                    print 'error getting %r from %s' % (param, rep.url)
                                    params.append(param)

                        else:
                            print 'batch requests send to:'
                            for url in urls:
                                print url

                        params = params[l:]
                
                longlats.add(loc)

        print '%d records (%d unique coordinates) done in %fs' % (i, len(longlats), time.time() - t0)
