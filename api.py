# description: download Google StreetViews images and save them
# the Google StreeView API is documented here:
# https://developers.google.com/maps/documentation/streetview/
# author: Falcon Dai

import requests
import urllib, csv, cStringIO
import mongoengine as me
from PIL import Image


class Pano(me.Document):
    location = me.StringField()
    longlat = me.PointField(auto_index=True) # note that the coordinates are (long, lat) pairs
    heading = me.FloatField(default=None)
    fov = me.FloatField(default=90)
    pitch = me.FloatField(default=0)
    size = me.ListField(me.IntField(), default=(640, 640))
    pano_id = me.StringField()
    image = me.ImageField()

    meta = {
        'indexes': ['pano_id']
    }

    @property
    def url(self):
        loc = self.location or self.longlat
        return generate_pano_url(loc, self.heading, self.fov, self.pitch, self.size, self.pano_id)
    
    @property
    def image_md5(self):
        '''return the md5 hash of the stored image'''
        if self.image:
            return self.image.md5
        return None

    @property
    def PIL_image(self):
        return Image.open(cStringIO.StringIO(self.image.read()))

    def show_image(self):
        return self.PIL_image.show()

    def __repr__(self):
        return '<Pano: location=%r, longlat=%r, image_md5=%r>' % (self.location, self.longlat, self.image_md5)

    @staticmethod
    def new_pano(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
        image = cStringIO.StringIO(get_pano(location, heading, fov, pitch, size, pano_id, key))
        if isinstance(location, str):
            pano = Pano(location=location, heading=heading, fov=fov, pitch=pitch, size=size, pano_id=pano_id, image=image)
        else:
            # location is provided as a (long, lat) pair
            pano = Pano(longlat=location, heading=heading, fov=fov, pitch=pitch, size=size, pano_id=pano_id, image=image)
        return pano


api_base = 'http://maps.googleapis.com/maps/api/streetview'

def generate_pano_url(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
    params = {
        'location': location if isinstance(location, str) else '%f,%f' % (location[1], location[0]), # assume (long, lat) pair
        'pano': pano_id,
        'heading': heading % 360 if heading else None, # heading will be pointing to the street address if None
        'fov': min(fov, 120),
        'pitch': min(max(-90, pitch), 90),
        'size': '%dx%d' % size,
        'key': key,
        'sensor': 'false'
    }

    # remove None parameters
    for k in filter(lambda k: params[k]==None, params.iterkeys()):
        params.pop(k)

    url = '%s?%s' % (api_base, urllib.urlencode(params))
    return url


def get_pano(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
    url = generate_pano_url(location, heading, fov, pitch, size, pano_id, key)
    r = requests.get(url)
    r.raise_for_status()
    return r.content


if __name__ == '__main__':
    print 'testing...'
    print generate_pano_url((-0.0004797, 51.4769351))

    db = me.connect('test')
    for l in [(-0.0004797, 51.4769351), 'downtown chicago', 'Golden Gate Bridge', 'Big Ben', 'Empire State Building', 'White House']:
        p = Pano.new_pano(l, fov=120)
        p.show_image()
        print repr(p)
        p.save()
        p.delete()

