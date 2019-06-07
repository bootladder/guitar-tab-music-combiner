#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *


def do_cool_stuff(img):
    img_before_contours = img
    contours, hierarchy = cv2.findContours(img_before_contours,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    img_contours = cv2.drawContours(np.ones_like(img)*255, contours, -1, (0,255,0), 1)

    img_blank = np.ones_like(img_contours)*255
    catter = np.ones((20,20),np.float32)/(100)

    tabGlyphs = []

    for c in contours:

        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        area = cv2.contourArea(c)
        print 'area of contour: ' , area
        if area > 200 or area < 100:
            print 'rejecting area ' , area
            continue

        # draw the center of the shape on the image
        cv2.circle(img_blank, (cX, cY), 5, (0, 0, 255))

        # cut the sub-image out of the original
        imgSection = img[cY-10:cY+10,cX-10:cX+10]

        # add to the list
        tabGlyphs.append(imgSection)

        # draw it
        img_blank[cY-10:cY+10,cX-10:cX+10] = imgSection
        #cv2.imshow('image',img_blank)
        cv2.waitKey(100)
        catter = np.concatenate((catter, imgSection), axis=1)
        #cv2.imshow('image',imgSection)

    return img_blank


def filter_contours_by_area(contours):
    accepted_contours = []
    for c in contours:

        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        area = cv2.contourArea(c)
        print 'area of contour: ' , area
        if area > 200 or area < 100:
            print 'rejecting area ' , area
            continue

        accepted_contours.append(c)

    return accepted_contours

def map_contours_to_glyphs(contours, img):

    glyphs = []
    for c in contours:
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # cut the sub-image out of the original
        imgSection = img[cY-10:cY+10,cX-10:cX+10]

        # add to the list
        glyphs.append(imgSection)

    return glyphs


def draw_glpyhs_on_blank_image(glyphs, img):
    for g in glyphs:
        img[cY-10:cY+10,cX-10:cX+10] = g
    return img_blank

#read stuff
img = img_orig = cv2.imread(sys.argv[1],0)

#pre process
img = img_pre_thresh = otsu_thresh(img)
img = img_smooth = pre_smooth(img)
img = img_thresh = pre_thresh(img)
#img = img_with_contours = do_cool_stuff(img)


#contours
contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
accepted_contours = filter_contours_by_area(contours)
glyphs = map_contours_to_glyphs(accepted_contours, img_orig)
showlisthorizontal(glyphs)

print 'there are %d contours' % len(accepted_contours)
showlist((img_orig, img_pre_thresh,img_smooth, img_thresh))
