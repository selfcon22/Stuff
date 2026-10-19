#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2


def sort_contours(contours, method, style):
    # initialize the reverse flag and sort index
    reverse = False
    i = 1    # Per Code Should be 0 but this works better....?!?!?!

    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    # handle if we are sorting against the y-coordinate rather than the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 0    # Per Code Should be 1 but this works better....?!?!?!

    # construct the list of bounding boxes and sort them from top to bottom
    # Note - Hard Coded..... but capture only if of a size (height in this case) likely to contain a digit!!
    if style == "Train":    # GFEM
        boundingBoxes = [cv2.boundingRect(c) for c in contours if 20 < cv2.boundingRect(c)[3] < 50]
        contours = [c for c in contours if 20 < cv2.boundingRect(c)[3] < 50]    # h - cv2.boundingRect(c)[3] = [x, y, w, h]
    else:    # Capture Loads minus "-" sign by reducing the box size
        boundingBoxes = [cv2.boundingRect(c) for c in contours if 2 < cv2.boundingRect(c)[3] < 50]
        contours = [c for c in contours if 2 < cv2.boundingRect(c)[3] < 50]

    (contour_sort, boundBoxes) = zip(*sorted(zip(contours, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return contour_sort
