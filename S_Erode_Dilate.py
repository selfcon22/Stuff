#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2


def erode_pic(erode_kernel, complete_pic):
    """ Erode Picture using CV2 """

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (erode_kernel, erode_kernel))
    CV2_Erode = cv2.bitwise_not(complete_pic)  # Invert Pic Black -> White
    CV2_Erode = cv2.erode(CV2_Erode, kernel)
    # cv2.imshow("erode", CV2_Erode)
    # Simple Thresholding
    ret, CV2_Erode = cv2.threshold(CV2_Erode, 180, 255, cv2.THRESH_BINARY_INV)
    # CV2_Erode = cv2.bitwise_not(CV2_Erode)  # Invert Pic White -> Black

    return CV2_Erode


def dilate_pic(dilate_kernel, complete_pic):
    """ Dilate Picture using CV2 """

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_kernel, dilate_kernel))
    CV2_Dilate = cv2.bitwise_not(complete_pic)  # Invert Pic Black -> White
    CV2_Dilate = cv2.dilate(CV2_Dilate, kernel)
    # Simple Thresholding
    ret, CV2_Dilate = cv2.threshold(CV2_Dilate, 180, 255, cv2.THRESH_BINARY_INV)
    # CV2_Dilate = cv2.bitwise_not(CV2_Dilate)  # Invert Pic White -> Black

    return CV2_Dilate


def opening_pic(open_kernel, complete_pic):
    """ Opening Picture using CV2 """

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (open_kernel, open_kernel))
    CV2_Open = cv2.bitwise_not(complete_pic)  # Invert Pic Black -> White
    CV2_Open = cv2.morphologyEx(CV2_Open, cv2.MORPH_OPEN, kernel)
    # Simple Thresholding
    ret, CV2_Open = cv2.threshold(CV2_Open, 180, 255, cv2.THRESH_BINARY_INV)
    # CV2_Open = cv2.bitwise_not(CV2_Open)  # Invert Pic White -> Black

    return CV2_Open


def remove_hori(kernel_value, complete_pic):
    """ Remove Horizontal Line from Picture using CV2 """

    # https://stackoverflow.com/questions/46274961/removing-horizontal-lines-in-image-opencv-python-matplotlib

    thresh = cv2.threshold(complete_pic, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove Horizontal Lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    # https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contours_hierarchy/py_contours_hierarchy.html
    h_lines, hierarchy = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Draw White Lines where 'h_lines' found
    cv2_removed_lines = cv2.drawContours(complete_pic, h_lines, -1, (255, 255, 255), 2)

    # Call Dilate function to 'polish' the process
    processed_pic = dilate_pic(kernel_value, cv2_removed_lines)

    # Restore Removed "Vertical" portion...
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    cv2_removed_hori_lines = 255 - cv2.morphologyEx(255 - processed_pic, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    return cv2_removed_hori_lines
