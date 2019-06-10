#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *


def filter_contours_by_area(contours):

    #get average, mean, mode area
    areas = []
    for c in contours:
        areas.append(cv2.contourArea(c))

    avg = np.mean(areas)
    median = np.median(areas)
    print 'avg median: ', avg,median
    time.sleep(1)

    accepted_contours = []
    for c in contours:

        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        area = cv2.contourArea(c)
        if area > (3*median) or area < (median/3):
            continue
        print 'accepted area of contour: ' , area

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

        if cX < 10 or cY < 10:
            print '\nrejecting glyph center: %d %d\n' %(cX,cY)
            continue

        # cut the sub-image out of the original
        imgSection = img[cY-10:cY+10,cX-10:cX+10]

        # add to the list
        glyphs.append(imgSection)

        print '\nglpyph size: %d %d\n'%(len(imgSection), len(imgSection[0]))

    return glyphs


#################################################################

#read stuff
img = img_orig = cv2.imread(sys.argv[1],0)

#pre process
img = ~img #do everything with white on black
img = img_rm_lines_h = remove_lines_horizontal(img)
img = img_rm_lines_v = remove_lines_vertical(img)
img = img_dilate = cv2.dilate(img,kernel_square(3),iterations = 1)
img = img_laplace = laplace(img)
img = img_dilate = cv2.dilate(img,kernel_square(3),iterations = 1)
img = img_erode = cv2.erode(img,kernel_square(3),iterations = 1)
img = img_thresh = otsu_thresh(img)
img = img_smooth = pre_smooth(img)
img = img_thresh2 = otsu_thresh(img)
img = img_open2 = morph_close_square(img,4)
#img = img_with_contours = do_cool_stuff(img)


#contours 2 glyphs
contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours = accepted_contours = filter_contours_by_area(contours)
contours = sorted_contours = sort_contours_by_column_position(contours)
glyphs = map_contours_to_glyphs(contours, img_orig)

print 'there are %d contours' % len(accepted_contours)
showlisthorizontal(glyphs)
showlist((img_orig, img_laplace,img_thresh, img_smooth, img_thresh2,img_open2))
