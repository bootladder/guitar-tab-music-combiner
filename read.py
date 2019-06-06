#!/usr/bin/python
import cv2
import sys
import numpy as np
import time

def normalize(arr):
    sum = 0
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            sum += arr[i][j]

    for i in range(len(arr)):
        for j in range(len(arr[0])):
            arr[i][j] = float(arr[i][j]) / sum
    return arr

def pre_smooth(img):
    arr = \
    [[10,10,10,10,00,00,10,10,10,10],
    [10,10,10,10,00,00,10,10,10,10],
    [10,10,10,10,00,00,10,10,10,10],
    [10,10,10,15,15,15,15,10,10,10],
    [00,00,00,15,40,40,15,00,00,00],
    [00,00,00,15,40,40,15,00,00,00],
    [10,10,10,15,15,15,15,10,10,10],
    [10,10,10,10,00,00,10,10,10,10],
    [10,10,10,10,00,00,10,10,10,10],
    [10,10,10,10,00,00,10,10,10,10]
    ]
    arr = normalize(arr)
    kernel = np.array(arr)
    img_smooth = cv2.filter2D(img_orig,-1,kernel)
    return img_smooth

def pre_thresh(img):
    thresh_val = 200
    ret,img_thresh = cv2.threshold(img_smooth,thresh_val,255,cv2.THRESH_BINARY)
    return img_thresh

def do_cool_stuff(img):
    img_before_contours = img
    contours, hierarchy = cv2.findContours(img_before_contours,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    img_contours = cv2.drawContours(np.ones_like(img_orig)*255, contours, -1, (0,255,0), 3)

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

        # draw the center of the shape on the image
        cv2.circle(img_blank, (cX, cY), 5, (0, 0, 255))

        # cut the sub-image out of the original
        imgSection = img_orig[cY-10:cY+10,cX-10:cX+10]

        # add to the list
        tabGlyphs.append(imgSection)

        # draw it
        img_blank[cY-10:cY+10,cX-10:cX+10] = imgSection
        #cv2.imshow('image',img_blank)
        cv2.waitKey(100)
        catter = np.concatenate((catter, imgSection), axis=1)
        #cv2.imshow('image',imgSection)

    return img_blank


def remove_lines(img):
    arr = \
    [
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10],
    [-90,-90,-90,-90,-90,-90,-90,-90,-90,-90],
    [-90,-90,-90,-90,-90,-90,-90,-90,-90,-90],
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,10,10,10]
    ]
    arr = normalize(arr)
    kernel = np.array(arr)
    return cv2.filter2D(img,-1,kernel)

def remove_lines_horizontal(img):
    img = ~img  #inverse
    kernel = np.ones((1,7),np.uint8)
    eroded = cv2.erode(img,kernel,iterations = 1)
    return ~eroded  #inverse

def remove_lines_vertical(img):
    img = ~img  #inverse
    kernel = np.ones((7,1),np.uint8)
    eroded = cv2.erode(img,kernel,iterations = 1)
    return ~eroded  #inverse

def extract_lines_horizontal(img):
    img = ~img  #inverse
    kernel = np.ones((1,70),np.uint8)
    eroded = cv2.erode(img,kernel,iterations = 1)
    eroded = ~eroded
    thresh_val = 200
    ret,img_thresh = cv2.threshold(eroded,thresh_val,255,cv2.THRESH_BINARY)
    return img_thresh


#read stuff
img_orig = cv2.imread(sys.argv[1],0)

#do stuff
img_inverse = ~img_orig
img1 = remove_lines_horizontal(img_orig)
img2 = extract_lines_horizontal(img_orig)
img3 = remove_lines_vertical(remove_lines_horizontal(img_orig))

img_smooth = pre_smooth(img_orig)
img_thresh = pre_thresh(img_smooth)
img_with_contours = do_cool_stuff(img_thresh)

concat_images = \
(
    img_orig,
    img1,
    img2,
    img3,
    img_thresh,
    img_with_contours
)

vis = np.concatenate(concat_images, axis=0)


#output stuff
output = vis
cv2.imshow('image',output)
k = cv2.waitKey(0)



#blah
#
#    [
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10],
#    [10,10,10,10,10,10,10,10,10,10]
