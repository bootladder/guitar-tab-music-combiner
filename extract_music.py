#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *

def filter_contours_by_radius_of_bounding_circle(contours):
    circleRadii = []
    for c in contours:
        hull = cv2.convexHull(c)
        minCircle = cv2.minEnclosingCircle(c)
        circleRadii.append(minCircle[1])
        print minCircle[1]

    mean = np.mean(circleRadii)
    median = np.median(circleRadii)
    print 'radius mean median: ' , mean, median

    acceptedContours = []
    for i in range(0,len(contours)):
        if circleRadii[i] < (median/1.5) or circleRadii[i] > (median*1.5):
            continue

        acceptedContours.append(contours[i])

    print 'there are %d accepted contours' % len(acceptedContours)
    return acceptedContours

def draw_contours(contours):
    img_blank = np.ones_like(img_orig)*255
    cv2.drawContours(img_blank,contours,-1,(0,255,0),1)
    return img_blank


def map_contours_to_bounding_slices(contours, img):
    #img is rowsxcolumns
    #rectangles are x,y
    #x is column, y is row
    #print 'img size: ',len(img),len(img[0])

    #return slice of entire Height
    regions = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        newRegion = img[0:len(img),x:x+w]
        regions.append(newRegion)

    return regions

def draw_regions_on_blank_image(regions):
    img_blank = np.ones_like(img_orig)*255
    for r in regions:
        show(r)
    return img_blank


def filter_regions_with_notes(regions):
    for r in regions:
        # Pre Process
        r_orig = r
        r = ~r #do everything with white on black
        r = remove_lines_horizontal(r)
        r = remove_lines_vertical(r)
        r = otsu_thresh(r)
        r = cv2.dilate(r,kernel_square(3),iterations = 1)

        # Contours
        contours, hierarchy = cv2.findContours(r,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        print 'there are %d contours\n\n' %len(contours)
        img_blank = np.ones_like(r)*255
        cv2.drawContours(img_blank,contours,-1,(0,255,0),1)

        countNonBlack = 0.0
        rows = len(r)
        cols = len(r[0])
        for i in range(1,rows):
            for j in range(1,cols):
                if r[i][j] != 0:
                    countNonBlack = countNonBlack + 1.0
        print countNonBlack/(rows*cols)
        countNonBlack = 0
        showlisthorizontal((r_orig,np.ones_like(r_orig)*255,r))
    return regions

#################################################################

# Load Image
img = img_orig = cv2.imread(sys.argv[1],0)

# Pre Process
img = ~img #do everything with white on black
img = img_rm_lines_h  = remove_lines_horizontal(img)
img = img_rm_lines_v  = remove_lines_vertical(img)
img = img_thresh      = otsu_thresh(img)
img = img_dilate      = cv2.dilate(img,kernel_square(3),iterations = 1)

# Contours
contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
print 'there are %d contours\n\n' %len(contours)
img = img_all_contours = draw_contours(contours)

# Circular Contours
circular_contours = filter_contours_by_radius_of_bounding_circle(contours)
print 'there are %d CIRUCLAR contours\n\n' %len(circular_contours)
img = img_circular_contours = draw_contours(circular_contours)

#######
# Here we have all the note contours but also some non-notes.
# To filter out non-notes, apply filters on a slice
# of the original image that contains the contour,
# so we have more information to filter out non-notes

regions = map_contours_to_bounding_slices(circular_contours, img_orig)
regions = regions_filtered = filter_regions_with_notes(regions)
print 'there are %d regions' % len(regions)

concat_images = \
(
     img_orig
    ,img_rm_lines_h
    ,img_rm_lines_v
    ,img_thresh
    ,img_dilate
    ,img_all_contours
    ,img_circular_contours
)
showlist(concat_images)
