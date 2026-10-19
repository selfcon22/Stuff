#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np


def ccwithstats(img_gray, Threshold_Max, MaxValue, Radio_Connect, area_size):
    """ Reshow Closed Widgets for the user """

    # Simple Thresholding
    ret, binary_map = cv2.threshold(img_gray, Threshold_Max, MaxValue, cv2.THRESH_BINARY_INV)

    # Perform the operation -> output = cv2.connectedComponentsWithStats(pic, connectivity, cv2.CV_32S)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, Radio_Connect, cv2.CV_32S)

    # get CC_STAT_AREA component as stats[label, COLUMN]
    areas = stats[1:, cv2.CC_STAT_AREA]
    result = np.zeros(labels.shape, np.uint8)
    # For every component in the image, keep it only if it's area is greater than the User defined size
    for i in range(0, nlabels - 1):
        if areas[i] > area_size:  # keep
            result[labels == i + 1] = 255

    # Invert Pic Black -> White
    CV2_Complete = cv2.bitwise_not(result)

    return CV2_Complete


def pic_stitch(pic_source, Grids, Start_X):
    """ Concatenate Cropped Pictures for Extraction so same X Co-ordinates as Pic shown to User """

    # Clean to residual 'noise' between the GRID and Start of the X Co-ord
    h, w = np.shape(pic_source)
    pic_grid = pic_source[0: h, 0: Grids]    # Cropping for GRID IDs
    pic_cords = pic_source[0: h, Start_X: w]    # Cropping for (X, Y, Z)
    pic_pad = np.zeros([h, Start_X - Grids], np.uint8)    # Black Fill between GRID & Co-ords
    pic_pad = cv2.bitwise_not(pic_pad)    # Convert Fill to White
    pic_concat = cv2.hconcat([pic_grid, pic_pad, pic_cords])    # Stitch 3 Pics together

    return pic_concat
