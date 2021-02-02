import argparse

from deepforest import deepforest
from deepforest import get_data

#Geospatial packages

import shapely
import geopandas
import rasterio


test_model = deepforest.deepforest()
test_model.use_release()

# Find the tutorial data using the get data function.
# For non-tutorial images, you do not need the get_data function,
# provide the full path to the data anywhere on your computer.

parser = argparse.ArgumentParser()
parser.add_argument("input_geotiff")
parser.add_argument("output_shapefile")
args = parser.parse_args()

raster_path = args.input_geotiff

# We encourage users to try out a variety of patch sizes. For 0.1m
# data, 400-800px per window is appropriate, but it will depend on the
# density of tree plots. For coarser resolution tiles, >800px patch
# sizes have been effective, but we welcome feedback from users using
# a variety of spatial resolutions.

# 400 px images with 15% overlap between tiles
boxes = test_model.predict_tile(
    raster_path,
    # return_plot draws the image
    # return_plot = True,
    patch_size=400,
    patch_overlap=0.15)


with rasterio.open(raster_path) as dataset:
    bounds = dataset.bounds
    pixelSizeX, pixelSizeY  = dataset.res

#subtract origin. Recall that numpy origin is top left! Not bottom left.
boxes["xmin"] = (boxes["xmin"] *pixelSizeX) + bounds.left
boxes["xmax"] = (boxes["xmax"] * pixelSizeX) + bounds.left
boxes["ymin"] = bounds.top - (boxes["ymin"] * pixelSizeY)
boxes["ymax"] = bounds.top - (boxes["ymax"] * pixelSizeY)

# combine column to a shapely Box() object, save shapefile
boxes['geometry'] = boxes.apply(lambda x: shapely.geometry.box(x.xmin,x.ymin,x.xmax,x.ymax), axis=1)
boxes = geopandas.GeoDataFrame(boxes, geometry='geometry')

#set same epsg as source data
boxes.crs = {'init' :'epsg:3857'}

# from https://epsg.io/3857
prj = '''PROJCS["WGS 84 / Pseudo-Mercator",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    PROJECTION["Mercator_1SP"],
    PARAMETER["central_meridian",0],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["X",EAST],
    AXIS["Y",NORTH],
    EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],
    AUTHORITY["EPSG","3857"]]'''

# Write shapefile
boxes.to_file(args.output_shapefile, driver='ESRI Shapefile',crs=prj)
