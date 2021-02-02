
# This function is used to collect the metadata of the GSV panoramas based on the sample point shapefile

# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT

API_KEY="AIzaSyAm-tBwVc6PmbL6DDdL2XY9C8cfEp63Pwg"

from datetime import datetime
import requests

def GSVpanoMetadataCollector(samplesFeatureClass, ouputTextFolder, batchNum, greenmonth, year=""):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file

    Parameters:
        samplesFeatureClass: the shapefile of the create sample sites
        batchNum: the number of sites proced every time. If batch size is 1000, the code will save metadata of every 1000 point to a txt file.
        ouputTextFolder: the output folder for the panoinfo
        greenmonth: a list of the green season, for example in Boston, greenmonth = ['05','06','07','08','09']
        year: optional. if specified, only panos dated in that year or older will be returned

    '''

    import xmltodict
    from osgeo import ogr, osr, gdal
    import time
    import os,os.path
    import math
    import streetview
    import pprint

    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    if driver is None:
        print('Driver is not available.')

    dataset = driver.Open(samplesFeatureClass)
    if dataset is None:
        print('Could not open %s' % (samplesFeatureClass))

    layer = dataset.GetLayer()
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326) # change the projection of shapefile to the WGS84

    # if GDAL version is 3.0 or above
    if gdal.__version__.startswith('2.') is False:
        targetProj.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    transform = osr.CoordinateTransformation(sourceProj, targetProj)

    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    batch = math.ceil(featureNum/batchNum)

    for b in range(batch):
        # for each batch process num GSV site
        start = b*batchNum
        end = (b+1)*batchNum
        if end > featureNum:
            end = featureNum

        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)

        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue

        time.sleep(1)

        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)
                geom = feature.GetGeometryRef()

                # trasform the current projection of input shapefile to WGS84
                #WGS84 is Earth centered, earth fixed terrestrial ref system
                geom.Transform(transform)
                lon = geom.GetX()
                lat = geom.GetY()

                # get the meta data of panoramas
                # urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)
                urlAddress = "https://maps.googleapis.com/maps/api/streetview/metadata?key={}&location={},{}".format(API_KEY, lat, lon)

                time.sleep(0.05)
                # the output result of the meta data is a xml object
                resp = requests.get(urlAddress)
                panoInfo = resp.json()

                try:
                    panoDate, panoId, panoLat, panoLon = getPanoItems(panoInfo)
                except KeyError:
                    print(urlAddress)
                    print(panoInfo)
                    continue

                if check_pano_month_in_greenmonth(panoDate, greenmonth) is False or year != "":
                    panoLst = streetview.panoids(lon=lon, lat=lat)
                    sorted_panoList = sort_pano_list_by_date(panoLst)
                    panoDate, panoId, panoLat, panoLon = get_next_pano_in_greenmonth(sorted_panoList, greenmonth, year)

                print('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s\n'%(panoId, panoDate, panoLon, panoLat)
                panoInfoText.write(lineTxt)

        panoInfoText.close()


def getPanoItems(panoInfo):
    # get the meta data of the panorama
    panoDate = panoInfo['date']
    panoId = panoInfo['pano_id']
    panoLat = panoInfo['location']['lat']
    panoLon = panoInfo['location']['lng']
    return panoDate, panoId, panoLat, panoLon


def check_pano_month_in_greenmonth(panoDate, greenmonth):
    month = panoDate[-2:]
    return month in greenmonth


def sort_pano_list_by_date(panoLst):
    def func(x):
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=1, month=1, day=1)
    panoLst.sort(key=func, reverse=True)
    return panoLst


def get_next_pano_in_greenmonth(panoLst, greenmonth, year):
    greenmonth_int = [int(month) for month in greenmonth]

    for pano in panoLst:
        if 'month' not in pano.keys():
            continue
        month = pano['month']
        pano_year = pano['year']
        if month in greenmonth_int and (year == "" or year >= pano_year):
            return get_pano_items_from_dict(pano)

    print(f"No pano with greenmonth {greenmonth} found. ")
    if year != "":
        print(f"No pano with year {year} found. ")
    print("Returning info of latest pano")
    return get_pano_items_from_dict(panoLst[0])


def get_pano_date_str(panoMonth, panoYear):
    return str(panoYear) + '-' + str(panoMonth).zfill(2)


def get_pano_items_from_dict(pano):
    panoDate = get_pano_date_str(pano['month'], pano['year'])
    panoId = pano['panoid']
    panoLat = pano['lat']
    panoLon = pano['lon']
    return panoDate, panoId, panoLat, panoLon


# ------------Main Function -------------------
if __name__ == "__main__":
    import os, os.path
    import argparse

    #os.chdir("sample-spatialdata")
    #root = os.getcwd()
    #inputShp = os.path.join(root,'Cambridge20m.shp')
    #outputTxtFolder = os.path.join(root, "metadata")
    batchNum = 1000


    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output_folder")
    args = parser.parse_args()

    #greenmonth = ['01','02','03','04','05','06','07','08','09','10','11','12']
    greenmonth = ['04','05','06','07','08','09','10']
    GSVpanoMetadataCollector(args.input, args.output_folder, batchNum, greenmonth)

    # to get pano dated in 2018 or older (optional)
    # year = 2018
    # GSVpanoMetadataCollector(inputShp, outputTxtFolder, batchNum, greenmonth, year)
