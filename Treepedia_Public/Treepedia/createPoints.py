# This program is used in the first step of the Treepedia project to get points along street
# network to feed into GSV python scripts for metadata generation.
# Copyright(C) Ian Seiferling, Xiaojiang Li, Marwa Abdulhai, Senseable City Lab, MIT
# First version July 21 2017

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import fiona
import os,os.path
import sys
import pyproj
from shapely.geometry import shape,mapping
from shapely.ops import transform
from functools import partial
from fiona.crs import from_epsg

# now run the python file: createPoints.py, the input shapefile has to be in projection of WGS84, 4326
def createPoints(inshp, outshp, mini_dist):

    '''
    This function will parse throigh the street network of provided city and
    clean all highways and create points every mini_dist meters (or as specified) along
    the linestrings
    Required modules: Fiona and Shapely

    parameters:
        inshp: the input linear shapefile, must be in WGS84 projection, ESPG: 4326
        output: the result point feature class
        mini_dist: the minimum distance between two created point

    last modified by Xiaojiang Li, MIT Senseable City Lab

    '''



    count = 0

    ## TODO (mtourne): query what is a primary, secondary, tertiary
    ## etc

    ignore_list = {
        None, ' ',
        'trunk', 'trunk_link',

        'motorway','motorway_link',
        'steps',

        ## some ped and footway have streetview
        #'pedestrian',
        #'footway',

        #'primary',
        # 'secondary',
        #'tertiary',

        'primary_link', 'secondary_link', 'tertiary_link',
        'bridleway','service'}

    # the temporaray file of the cleaned data
    root = os.path.dirname(inshp)
    basename = 'clean_' + os.path.basename(inshp)
    temp_cleanedStreetmap = os.path.join(root,basename)

    # if the tempfile exist then delete it
    if os.path.exists(temp_cleanedStreetmap):
        fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')

    # clean the original street maps by removing highways, if it the street map not from Open street data, users'd better to clean the data themselve
    with fiona.open(inshp) as source, fiona.open(temp_cleanedStreetmap, 'w', driver=source.driver, crs=source.crs,schema=source.schema) as dest:

        for feat in source:
            try:
                i = feat['properties']['highway'] # for the OSM street data
                if i in ignore_list:
                    continue
            except:
                # if the street map is not osm, do nothing. You'd better to clean the street map, if you don't want to map the GVI for highways
                key = list(dest.schema['properties'].keys())[0] # get the field of the input shapefile and duplicate the input feature
                i = feat['properties'][key]
                if i in s:
                    continue

            dest.write(feat)

    schema = {
        'geometry': 'Point',
        'properties': {'id': 'int'},
    }

    # Create pointS along the streets
    with fiona.Env():
        with fiona.open(outshp, 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as output:
            for line in fiona.open(temp_cleanedStreetmap):
                line_geom = line['geometry']
                featureType = line_geom['type']

                try:
                    if featureType == 'MultiLineString':
                        continue
                        # TODO: transform to LineString

                    elif featureType == 'LineString':
                        line_geom_degree = shape(line_geom)

                        # convert degree to meter, in order to split by distance in meter
                        project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                        line_geom_meter = transform(project, line_geom_degree)

                        for distance in range(0, int(line_geom_meter.length), mini_dist):
                            point = line_geom_meter.interpolate(distance)

                            # convert the local projection back the the WGS84 and write to the output shp
                            project2 = partial(pyproj.transform, pyproj.Proj(init='EPSG:3857'), pyproj.Proj(init='EPSG:4326'))
                            point_deg = transform(project2, point)
                            output.write(
                                {
                                    'geometry': mapping(point_deg),
                                    'properties': {'id': 1}
                                }
                                )
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    print("You should make sure the input shapefile is WGS84")
                    print(sys.exc_info())

    print("Process Complete")

    # delete the temprary cleaned shapefile
    fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')


# Example to use the code,
# Note: make sure the input linear featureclass (shapefile) is in WGS 84 or ESPG: 4326
# ------------main ----------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    #os.chdir("sample-spatialdata/")
    #root = os.getcwd()
    #inputShp = os.path.join(root,'CambridgeStreet_wgs84.shp')
    #outputShp = os.path.join(root,'CambridgeStreet_20m.shp')
    mini_dist = 20 #the minimum distance between two generated points, in meter

    createPoints(args.input, args.output, mini_dist)
