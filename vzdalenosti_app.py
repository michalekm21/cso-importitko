import math
from osgeo import ogr


ogr.

def planar_dist(x1, x2, y1, y2):
    return math.sqrt((x2-x1) ^ 2 + (y2-y1) ^ 2)

