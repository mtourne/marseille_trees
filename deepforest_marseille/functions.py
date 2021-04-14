from tqdm import tqdm

import numpy as np
import pandas as pd

# image
from PIL import Image
import cv2

#Geospatial packages
import shapely
import geopandas
import rasterio

# deepforest algo
from deepforest import deepforest
from deepforest import predict

import tensorflow as tf

#############
##  BOXES  ##
#############

class RasterProject:
    def __init__(self, raster_path):
        '''
        raster_path : takes geoTIFF input
        '''
        self.raster_path = raster_path
        with rasterio.open(self.raster_path) as dataset:
            self.bounds = dataset.bounds
            self.pixelSizeX, self.pixelSizeY  = dataset.res

    def projectX(self, xpoints):
        ''' list of x axis points '''
        #subtract origin. Recall that numpy origin is top left! Not bottom left.
        return xpoints*self.pixelSizeX + self.bounds.left

    def projectY(self, ypoints):
        ''' list of y axis points'''
        #subtract origin. Recall that numpy origin is top left! Not bottom left.
        return self.bounds.top - ypoints*self.pixelSizeY

    def project_boxes(self, boxes):
        # make a copy of the dataframe
        boxes = boxes.copy()

        boxes["xmin"] = self.projectX(boxes["xmin"])
        boxes["xmax"] = self.projectX(boxes["xmax"])
        boxes["ymin"] = self.projectY(boxes["ymin"])
        boxes["ymax"] = self.projectY(boxes["ymax"])
        return boxes


def save_shapefile(output_path, boxes):
    ''' boxes with added `geometry` field from GeoPandas dataframe
    to espg3857 projection standard
    see: https://epsg.io/3857
    '''

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

    boxes.to_file(output_path, driver='ESRI Shapefile',crs=prj)


###############
##  DISPLAY  ##
###############

def draw_box(image, box, color, thickness=1):
    """ Draws a box on an image with a given color.

    # Arguments
        image     : The image to draw on.
        box       : A list of 4 elements (x1, y1, x2, y2).
        color     : The color of the box.
        thickness : The thickness of the lines to draw a box with.
    """
    b = np.array(box).astype(int)
    cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), color, thickness, cv2.LINE_AA)


def draw_all_boxes(numpy_image, boxes):
    image = numpy_image.copy()
    for box in boxes[["xmin", "ymin", "xmax", "ymax"]].values:
        draw_box(image, box, [0, 0, 255])
    return image


##############################
##  DEEPFOREST predictions  ##
##############################


def process_tile_windows(model, numpy_image, windows):

    predicted_boxes = []

    for index, window in enumerate(tqdm(windows)):
        # Crop window and predict
        crop = numpy_image[windows[index].indices()]

        # Crop is RGB channel order, change to BGR
        # crop = crop[..., ::-1]
        # XXX (mtourne): already done in our case

        boxes = model.predict_image(numpy_image=crop,
                                   return_plot=False,
                                   score_threshold=model.config["score_threshold"])


        # transform coordinates to original system
        # XX (mtourne): there is an error in the original code
        # using : xmin, ymin, xmax, ymax = windows[index].getRect()
        # when in reality getRect() returns xmin, ymin, w, h
        # Note: it worked because ymax and xmax were not used
        xmin, ymin, w, h = windows[index].getRect()
        xmax = xmin + w
        ymax = ymin + h
        boxes.xmin = boxes.xmin + xmin
        boxes.xmax = boxes.xmax + xmin
        boxes.ymin = boxes.ymin + ymin
        boxes.ymax = boxes.ymax + ymin

        predicted_boxes.append(boxes)

    return pd.concat(predicted_boxes)


def nonmax_suppression(predicted_boxes, iou_threshold=0.15):
    with tf.Session() as sess:
        print(
            "{} predictions in overlapping windows, applying non-max supression".
            format(predicted_boxes.shape[0]))
        new_boxes, new_scores, new_labels = predict.non_max_suppression(
            sess,
            predicted_boxes[["xmin", "ymin", "xmax", "ymax"]].values,
            predicted_boxes.score.values,
            predicted_boxes.label.values,
            max_output_size=predicted_boxes.shape[0],
            iou_threshold=iou_threshold)

        # Recreate box dataframe
        image_detections = np.concatenate([
            new_boxes,
            np.expand_dims(new_scores, axis=1),
            np.expand_dims(new_labels, axis=1)
        ],
                                          axis=1)

        mosaic_df = pd.DataFrame(
            image_detections,
            columns=["xmin", "ymin", "xmax", "ymax", "score", "label"])
        mosaic_df.label = mosaic_df.label.str.decode("utf-8")

        print("{} predictions kept after non-max suppression".format(
            mosaic_df.shape[0]))
        return mosaic_df
