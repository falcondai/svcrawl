# description: download Google StreetViews images and save them
# the Google StreeView API is documented here:
# https://developers.google.com/maps/documentation/streetview/
# author: Falcon Dai

import cStringIO
import mongoengine as me
from PIL import Image

from google_streetview_api import *

class Pano(me.Document):
    location = me.StringField()
    longlat = me.PointField(auto_index=True) # note that the coordinates are (long, lat) pairs
    heading = me.FloatField(default=None)
    fov = me.FloatField(default=90)
    pitch = me.FloatField(default=0)
    pano_id = me.StringField()
    image = me.ImageField()

    meta = {
        'indexes': ['pano_id']
    }

    @property
    def size(self):
        return self.image.size

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
        if hasattr(self, '_PIL_image'):
            return self._PIL_image
        self._PIL_image = Image.open(cStringIO.StringIO(self.image.read()))
        return self._PIL_image

    @property
    def has_image(self):
        '''return False if the image is a null image'''
        return self.image_md5 != no_image_md5

    def show_image(self):
        return self.PIL_image.show()

    def __repr__(self):
        return '<Pano: location=%r, longlat=%r, image_md5=%r>' % (self.location, self.longlat['coordinates'], self.image_md5)

    @staticmethod
    def new_pano(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
        image = cStringIO.StringIO(get_pano(location, heading, fov, pitch, size, pano_id, key))
        params = dict(heading=heading, fov=fov, pitch=pitch, size=size, pano_id=pano_id, image=image)
        if isinstance(location, str):
            pano = Pano(location=location, **params)
        else:
            # location is provided as a (long, lat) pair
            pano = Pano(longlat=location, **params)
        return pano


if __name__ == '__main__':
    print 'testing...'
    print generate_pano_url((-0.0004797, 51.4769351))

    me.connect('test')
    for l in [(0, 0), (-0.0004797, 51.4769351), 'downtown chicago', 'Golden Gate Bridge', 'Big Ben', 'Empire State Building', 'White House']:
        p = Pano.new_pano(l, fov=120)
        p.show_image()
        print repr(p), p.has_image
        p.save()
        Pano.drop_collection()

