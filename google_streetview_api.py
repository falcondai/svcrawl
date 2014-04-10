import requests
import urllib

api_base = 'http://maps.googleapis.com/maps/api/streetview'
#no_image = open('no-image.jpg').read()
# md5 generated from MongoDB by saving no_image.jpg
no_image_md5 = 'e8bedec32bf7863c1899fa1e6eee1f44'

def generate_pano_url(location=None, heading=None, fov=90, pitch=0, size=(640, 640), pano_id=None, key=None):
    params = {
        # assume (long, lat) pair
        'location': location if isinstance(location, str) else '%f,%f' % (location[1], location[0]), 
        'pano': pano_id,
        # heading will be pointing to the street address if None
        'heading': heading % 360 if heading else None, 
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
