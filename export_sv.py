#!/usr/bin/env python

if __name__ == '__main__':
    import mongoengine as me
    from models import Pano
    import argparse, csv, os, sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', default='mongodb://localhost/test', help='MongoDB URI')
    parser.add_argument('-o', '--output', default='sv-export', help='output directory')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite existing output folders if any')

    args = parser.parse_args()

    me.connect('', host=args.db)

    try:
        print 'creating directory %s' % args.output
        os.mkdir(args.output)
    except:
        if not args.force:
            print 'ERROR output directory %s already exists' % args.output
            sys.exit(1)

    pano_dir = os.path.join(args.output, 'panos')
    try:
        print 'creating directory %s' % pano_dir
        os.mkdir(pano_dir)
    except:
        if not args.force:
            print 'ERROR output directory %s already exists' % pano_dir
            sys.exit(1)

    csv_path = os.path.join(args.output, 'panos.csv')
    print 'writing pano meta data to %s' % csv_path

    with open(csv_path, 'wb') as f:
        r = csv.DictWriter(f, ['longitude', 'latitude', 'heading', 'filename'])
        r.writeheader()
        for i, pano in enumerate(Pano.objects):
            if pano.has_image and pano.image.format == 'JPEG':
                filename = '%d.jpg' % i
                with open(os.path.join(pano_dir, filename), 'wb') as img_fp:
                    img_fp.write(pano.image.read())
                    r.writerow({
                        'longitude': pano.longlat['coordinates'][0],
                        'latitude': pano.longlat['coordinates'][1],
                        'heading': pano.heading,
                        'filename': os.path.join('panos', filename),
                    })
    print 'done exporting streetview images'
