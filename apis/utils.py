from math import *

pi = 3.1415926
tile_size = 256
origin_shift = 2 * pi * 6378137 / 2.0

def coordinate_to_meters(lat, lon):
    x = lon * origin_shift / 180.0
    y = log(tan((90 + lat) * pi / 360.0)) / (pi / 180.0)
    y = y * origin_shift / 180.0
    return y, x