Google StreetView Crawler
=========================

Created for UChicago Knowledge Lab StreetScope Project.


features
--------

- downloads StreetView images from Google API
- provides a MongoDB database model for panoramas with convenient functions 
- utility scripts 


dependencies
------------

- You might have to install `libjpeg-dev` and `python-dev` on Ubuntu for `PIL` to build and work:
(http://stackoverflow.com/questions/8915296/python-image-library-fails-with-message-decoder-jpeg-not-available-pil). 

- `requirements.txt` contians python libraries that you can install by `$ pip install -r requirements.txt`


usage
-----

To scrape streetview images for locations from a CSV file and save them into MongoDB:
`$ ./latlong_to_sv.py chicago-crime-sample.csv --lat Latitude --long Longitude`

author
------
Falcon Dai

license
-------
MIT License