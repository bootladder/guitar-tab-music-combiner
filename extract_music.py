#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *

p_init = pipeline_init
p_add = pipeline_add
p_last = pipeline_last
p_all = pipeline_all

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
        #img = draw_contours_on_image_like([c], img_orig)
        #box = cv2.boxPoints(minRect)
        #box = np.int0(box)
        #cv2.drawContours(img,[box],0,(0,0,255),1)
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
            #show(draw_contours_on_image_like([c], np.ones((50,50))*255))
            return True

        else:
            continue
            #print 'ZZZZREJECTED'
            #show(draw_contours_on_image_like([c], np.ones((200,200))*255))
    return False


def boundingslice_contains_note(img_slice):

    ## Pre Process
    p_init(img_slice)
    p_add('inverse',     lambda img: ~img)
    p_add('horiz',       remove_lines_horizontal)
    p_add('vert',        remove_lines_vertical)
    p_add('thresh',      otsu_thresh)
    p_add('dilate',      lambda img: cv2.dilate(img,kernel_square(3),iterations = 1))

    r = pipeline_last()


    # Contours
    contours, hierarchy = cv2.findContours(r,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #print 'there are %d contours\n\n' %len(contours)

    # Filter by Number of Non-Black
    percent_result = check_region_area_threshold(r)
    #print percent_result
    if percent_result > 0.24 or percent_result < 0.05:
        print 'REJECTED by Threshold: %f' % percent_result
        #showlisthorizontal((r_orig,np.ones_like(r_orig)*255,r))
        return False

    # Filter Contours: Remove Rectangular Contours
    # If Contour Area is close to Area of Minimum Bounding Rectangle
    contours = contours_nonrectangular = filter_contours_by_minimum_bounding_rectangle(contours)
    if len(contours) == 0:
        print 'REJECTED: All Contours Filtered Out'
        return False

    # Filter:  Check existence of Note Head
    if False == note_head_exists(contours):
        print 'REJECTED: No Note Head Contour Exists'
        showlisthorizontal(p_all(True))
        return False


    return True



def contour_to_boundingslice(contour, img):
    #img is rowsxcolumns
    #rectangles are x,y
    #x is column, y is row
    #print 'img size: ',len(img),len(img[0])

    # Add a couple pixels of padding to catch stems on the edges

    x,y,w,h = cv2.boundingRect(contour)
    newRegion = img[0:len(img),x-2:x+w+2]  #return slice of entire Height
    return newRegion


def filter_contours_by_note_match(contours, img):
    acceptedContours = []
    for c in contours:
        bounding_slice = contour_to_boundingslice(c,img)
        if False == boundingslice_contains_note(bounding_slice):
            continue

        acceptedContours.append(c)

    return acceptedContours


def map_contours_to_center_coordinates(contours):
    centers = []
    for c in contours:
        centers.append(coordinates_of_contour_center(c))
    return centers


#################################################################

def imgmusic_to_notecoordinates(img):
    # Pre Process
    img_orig = img
    img = ~img #do everything with white on black
    img = img_rm_lines_h  = remove_lines_horizontal(img)
    img = img_rm_lines_v  = remove_lines_vertical(img)
    img = img_thresh      = otsu_thresh(img)
    #img = img_dilate      = cv2.dilate(img,kernel_square(3),iterations = 1)

    # Get All Contours
    contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours_orig = contours
    print 'there are %d TOTAL contours\n\n' %len(contours)
    img = img_all_contours = draw_contours_on_image_like(contours, img_orig)

    # Circular Contours By Radius of Bounding Circle
    contours = circular_contours = filter_contours_by_radius_of_bounding_circle(contours)
    print 'there are %d CIRUCLAR contours\n\n' %len(contours)
    img = img_circular_contours = draw_contours_on_image_like(contours, img_orig)

    # Circular Contours By AREA
    contours = circular_contours_2 = filter_contours_by_area(contours)
    print 'there are %d CIRUCLAR contours\n\n' %len(contours)
    img = img_circular_contours_2 = draw_contours_on_image_like(contours, img_orig)

    #######
    # Here we have all the note contours but also some non-notes.
    # To filter out non-notes, apply filters on a slice
    # of the original image that contains the contour,
    # so we have more information to filter out non-notes

    print 'Checking for Note Head'
    contours = contours_with_notes = filter_contours_by_note_match(contours, img_orig)
    print 'there are %d contours WITH NOTES' % len(contours)

    img_contours_done = draw_contours_on_image_like(contours, img_orig)

    # Sort Contours by X ie. column index ie. left to right
    contours = contours_sorted = sort_contours_by_column_position(contours)

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
        ,img_contours_done
    )
    showlist(concat_images)

    centers = map_contours_to_center_coordinates(contours)
    return centers


if __name__ == '__main__':
    img = cv2.imread(sys.argv[1],0)
    imgmusic_to_notecoordinates(img)

