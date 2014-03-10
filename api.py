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
    latlong = me.GeoPointField()
    heading = me.FloatField(default=None)
    fov = me.FloatField(default=90)
    pitch = me.FloatField(default=0)
    size = me.ListField(me.IntField(), default=(640, 640))
    pano_id = me.StringField()
    image = me.ImageField()

    @property
    def url(self):
        loc = self.location or self.latlong
        return generate_pano_url(loc, self.heading, self.fov, self.pitch, self.size, self.pano_id)
    
    @property
    def image_md5(self):
        '''return the md5 hash of the stored image'''
        if self.image:
            return self.image.md5
        return None

    @property
    def PIL_image(self):
        if not hasattr(self, '_PIL_image'):
            self._PIL_image = Image.open(cStringIO.StringIO(self.image.read()))
        return self._PIL_image

    def show_image(self):
        return self.PIL_image.show()

    def __repr__(self):
        return '<Pano: location=%r, latlong=%r, image_md5=%r>' % (self.location, self.latlong, self.image_md5)


api_base = 'http://maps.googleapis.com/maps/api/streetview'

def generate_pano_url(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
    params = {
        'location': location if isinstance(location, str) else '%f,%f' % location,
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


def new_pano(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
    image = cStringIO.StringIO(get_pano(location, heading, fov, pitch, size, pano_id, key))
    if isinstance(location, str):
        pano = Pano(location=location, heading=heading, fov=fov, pitch=pitch, size=size, pano_id=pano_id, image=image)
    else:
        # location is provided as a latlong pair
        pano = Pano(latlong=location, heading=heading, fov=fov, pitch=pitch, size=size, pano_id=pano_id, image=image)
    return pano


if __name__ == '__main__':
    print generate_pano_url('Chicago')

    db = me.connect('streetview')
    for l in [(0,0), (180, 30), 'Chicago', 'San Francisco', 'London', 'Berlin', 'New York', 'Washington DC']:
        p = new_pano(l)
        print repr(p)
        p.save()

