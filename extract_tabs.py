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

    #get average, mean, mode area
    areas = []
    for c in contours:
        areas.append(cv2.contourArea(c))

    avg = np.mean(areas)
    median = np.median(areas)
    #print 'avg median: ', avg,median
    time.sleep(1)

    accepted_contours = []
    for c in contours:

        (cX,cY) = coordinates_of_contour_center(c)

        area = cv2.contourArea(c)
        if area > (3*median) or area < (median/3):
            continue
        #print 'accepted area of contour: ' , area

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
            #print '\nrejecting glyph center: %d %d\n' %(cX,cY)
            continue

        # cut the sub-image out of the original
        imgSection = img[cY-10:cY+10,cX-10:cX+10]

        # add to the list
        glyphs.append(imgSection)

        #print '\nglpyph size: %d %d\n'%(len(imgSection), len(imgSection[0]))

    return glyphs


#################################################################

def imgtab_preprocess(img):

    p_init(img)
    p_add('img_inverse   '   , lambda img: ~img)
    p_add('img_thresh_1  '   , otsu_thresh)
    p_add('img_rm_lines_h'   , remove_lines_horizontal)
    p_add('img_rm_lines_v'   , remove_lines_vertical)
    p_add('img_dilate    '   , lambda img: cv2.dilate(img,kernel_square(3),iterations = 1))
    p_add('img_laplace   '   , laplace)
    p_add('img_dilate_2  '   , lambda img: cv2.dilate(img,kernel_square(3),iterations = 1))
    p_add('img_erode     '   , lambda img: cv2.erode(img,kernel_square(3),iterations = 1))
    p_add('img_thresh_2  '   , otsu_thresh)

    img = pipeline_last()
    return img




def imgtab_to_glyphs(img):
    #pre process
    img_orig = img
    img = img_inverse       = ~img #do everything with white on black
    img = img_thresh_1      = otsu_thresh(img)
    img = img_rm_lines_h    = remove_lines_horizontal(img)
    img = img_rm_lines_v    = remove_lines_vertical(img)
    img = img_dilate        = cv2.dilate(img,kernel_square(3),iterations = 1)
    img = img_laplace       = laplace(img)
    img = img_dilate_2      = cv2.dilate(img,kernel_square(3),iterations = 1)
    img = img_erode         = cv2.erode(img,kernel_square(3),iterations = 1)
    img = img_thresh_2      = otsu_thresh(img)

    img = img_smooth        = pre_smooth(img)
    img = img_thresh_3      = otsu_thresh(img)
    img = img_open2         = morph_close_square(img,4)


    # try another image in the pipe
    img = img_thresh_2

    #contours 2 glyphs
    contours, hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    img_with_contours = draw_contours_on_image_like(contours,img_orig)
    contours = accepted_contours = filter_contours_by_area(contours)
    img_with_contours_accepted = draw_contours_on_image_like(contours,img_orig)
    contours = sorted_contours = sort_contours_by_column_position(contours)
    glyphs = map_contours_to_glyphs(contours, img_orig)

    print 'there are %d glyphs' % len(glyphs)
    #showlisthorizontal(glyphs)
    #showlist(
    #    ( img_orig
    #      , img_inverse   
    #      , img_thresh_1  
    #      , img_rm_lines_h
    #      , img_rm_lines_v
    #      , img_dilate    
    #      , img_laplace   
    #      , img_dilate_2  
    #      , img_erode     
    #      , img_thresh_2  
    #      
    #      
    #      
    #      
    #      
    #      , img_with_contours
    #      , img_with_contours_accepted
    #    ))

    return glyphs


#################################################################



if __name__ == '__main__':
    img = cv2.imread(sys.argv[1],0)
    imgtab_to_glyphs(img)
