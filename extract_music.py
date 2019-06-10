#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *

def filter_contours_by_area(contours):
    areas = []
    for c in contours:
        areas.append(cv2.contourArea(c))

    #print areas

    mean = np.mean(areas)
    median = np.median(areas)
    #print 'radius mean median: ' , mean, median

    acceptedContours = []
    for i in range(0,len(contours)):
        if areas[i] < (median/1.5) or areas[i] > (median*1.5):
            continue

        acceptedContours.append(contours[i])

    print 'BY AREA: there are %d accepted contours' % len(acceptedContours)
    return acceptedContours

def filter_contours_by_radius_of_bounding_circle(contours):
    circleRadii = []
    for c in contours:
        hull = cv2.convexHull(c)
        minCircle = cv2.minEnclosingCircle(c)
        circleRadii.append(minCircle[1])
        #print minCircle[1]

    mean = np.mean(circleRadii)
    median = np.median(circleRadii)
    #print 'radius mean median: ' , mean, median

    acceptedContours = []
    for i in range(0,len(contours)):
        if circleRadii[i] < (median/1.5) or circleRadii[i] > (median*1.5):
            continue

        acceptedContours.append(contours[i])

    print 'BY BOUNDING CIRCLE: there are %d accepted contours' % len(acceptedContours)
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

def check_region_area_threshold(r):
    countNonBlack = 0.0
    rows = len(r)
    cols = len(r[0])
    for i in range(1,rows):
        for j in range(1,cols):
            if r[i][j] != 0:
                countNonBlack = countNonBlack + 1.0
    return countNonBlack/(rows*cols)


def filter_contours_by_minimum_bounding_rectangle(contours):
    accepted_contours = []
    for c in contours:
        minRect = cv2.minAreaRect(c)
        minRectArea = minRect[1][0] * minRect[1][1]
        contourArea = cv2.contourArea(c)
        ratio = contourArea/minRectArea
        #print '\n\n'
        #print 'minRect: ' , minRect
        #print 'minRect Area: ' , minRectArea
        #print 'Area: ', contourArea
        #print 'Ratio: ' , ratio
        img = draw_contours([c])
        box = cv2.boxPoints(minRect)
        box = np.int0(box)
        cv2.drawContours(img,[box],0,(0,0,255),1)
        #show(img)

    return contours



def note_head_exists(contours):

    for c in contours:
        area = cv2.contourArea(c)
        hull = cv2.convexHull(c)
        minCircle = cv2.minEnclosingCircle(c)
        ratio =  (area/(3.14*minCircle[1]*minCircle[1]))
        #print ratio,  ' is the ratio'
        if ratio > 0.50:
            #print 'ZZZPASS'
            #show(draw_contours([c]))
            return True

    #print 'ZZZZREJECTED'
    #show(draw_contours([c]))
    return False


def filter_regions_with_notes(regions):

    accepted_regions = []
    for r in regions:

        # Pre Process
        r_orig = r
        r = ~r #do everything with white on black
        r = remove_lines_horizontal(r)
        r = remove_lines_vertical(r)
        r = otsu_thresh(r)
        r = r_filtered = cv2.dilate(r,kernel_square(3),iterations = 1)
        #show(r)

        # Contours
        contours, hierarchy = cv2.findContours(r,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #print 'there are %d contours\n\n' %len(contours)

        # Filter by Number of Non-Black
        percent_result = check_region_area_threshold(r)
        #print percent_result

        if percent_result > 0.24 or percent_result < 0.05:
            print 'REJECTED by Threshold: %f' % percent_result
            #showlisthorizontal((r_orig,np.ones_like(r_orig)*255,r))
            continue


        # Filter Contours: Remove Rectangular Contours
        # If Contour Area is close to Area of Minimum Bounding Rectangle
        contours = contours_nonrectangular = filter_contours_by_minimum_bounding_rectangle(contours)
        if len(contours) == 0:
            print 'REJECTED: All Contours Filtered Out'
            continue



        # Filter:  Check existence of Note Head
        if False == note_head_exists(contours):
            print 'REJECTED: No Note Head Contour Exists'
            continue


        accepted_regions.append(r)

    return accepted_regions

#################################################################

# Load Image
img = img_orig = cv2.imread(sys.argv[1],0)

# Pre Process
img = ~img #do everything with white on black
img = img_rm_lines_h  = remove_lines_horizontal(img)
img = img_rm_lines_v  = remove_lines_vertical(img)
img = img_thresh      = otsu_thresh(img)
#img = img_dilate      = cv2.dilate(img,kernel_square(3),iterations = 1)

# Get All Contours
contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours_orig = contours
print 'there are %d TOTAL contours\n\n' %len(contours)
img = img_all_contours = draw_contours(contours)

# Circular Contours By Radius of Bounding Circle
contours = circular_contours = filter_contours_by_radius_of_bounding_circle(contours)
print 'there are %d CIRUCLAR contours\n\n' %len(contours)
img = img_circular_contours = draw_contours(contours)

# Circular Contours By AREA
contours = circular_contours_2 = filter_contours_by_area(contours)
print 'there are %d CIRUCLAR contours\n\n' %len(contours)
img = img_circular_contours_2 = draw_contours(contours)

#######
# Here we have all the note contours but also some non-notes.
# To filter out non-notes, apply filters on a slice
# of the original image that contains the contour,
# so we have more information to filter out non-notes

regions = map_contours_to_bounding_slices(contours, img_orig)
regions = regions_filtered = filter_regions_with_notes(regions)
print 'there are %d ACCEPTED regions' % len(regions)

showlisthorizontal(regions)

concat_images = \
(
     img_orig
    ,img_rm_lines_h
    ,img_rm_lines_v
    ,img_thresh
    #,img_dilate
    ,img_all_contours
    ,img_circular_contours
    ,img_circular_contours_2
)
showlist(concat_images)
