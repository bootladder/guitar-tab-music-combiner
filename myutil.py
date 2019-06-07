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
    img_smooth = cv2.filter2D(img,-1,kernel)
    return img_smooth

def pre_thresh(img):
    thresh_val = 200
    ret,img_thresh = cv2.threshold(img,thresh_val,255,cv2.THRESH_BINARY)
    return img_thresh

def otsu_thresh(img):
    retval, imgOtsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return imgOtsu


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




def show(img):
    cv2.imshow('image',img)
    k = cv2.waitKey(0) & 0xff

def showlist(l):
    vis = np.concatenate(l, axis=0)
    cv2.imshow('image',vis)
    k = cv2.waitKey(0) & 0xff

def showlisthorizontal(l):
    vis = np.concatenate(l, axis=1)
    cv2.imshow('image',vis)
    k = cv2.waitKey(0) & 0xff

#   #do stuff
#   img_inverse = ~img_orig
#   img1 = remove_lines_horizontal(img_orig)
#   img2 = extract_lines_horizontal(img_orig)
#   img3 = remove_lines_vertical(remove_lines_horizontal(img_orig))
#   
#   
#   concat_images = \
#   (
#       img_orig,
#       img1,
#       img2,
#       img3,
#       img_thresh,
#       img_with_contours
#   )
#   
#   vis = np.concatenate(concat_images, axis=0)
#   
#   
#   #output stuff
#   output = vis
#   cv2.imshow('image',output)
#   k = cv2.waitKey(0)



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
