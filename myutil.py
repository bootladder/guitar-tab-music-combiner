#!/usr/bin/python
import cv2
import sys
import numpy as np
import time

def coordinates_of_contour_center(contour):
    # compute the center of the contour
    M = cv2.moments(contour)
    if M["m00"] == 0:
        #raise('wat')
        return (0,0)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return (cX,cY)

def sort_contours_by_column_position(contours):
    #put the column position in a tuple
    tuples = []
    for c in contours:
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        tuples.append((c,cX))

    tuples = sorted(tuples, key=lambda tup:tup[1])
    return [t[0] for t in tuples]


# Open Square
def morph_open_square(img, n):
    kernel = np.ones((n,n),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# Open
def morph_open(img):
    kernel = np.ones((10,10),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# Close Square
def morph_close_square(img, n):
    kernel = np.ones((n,n),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

# Close
def morph_close(img):
    kernel = np.ones((9,9),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def kernel_square(i):
    return np.ones((i,i),np.uint8)


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

def laplace(img):
    arr = \
    [
        [0,1,0],
        [1,-4,1],
        [0,1,0]
    ]
    kernel = np.array(arr)
    return cv2.filter2D(img,-1,kernel)


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
    #need a white on black picture
    kernel = np.ones((3,1),np.uint8)
    #eroded = cv2.erode(img,kernel,iterations = 1)
    opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return opened

def remove_lines_vertical(img):
    #need a white on black picture
    kernel = np.ones((1,3),np.uint8)
    opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return opened

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
    while (cv2.waitKey(0) & 0xff) != 113:
        cv2.imshow('image',img)

def showlist(l):
    vis = np.concatenate(l, axis=0)
    cv2.imshow('image',vis)
    while (cv2.waitKey(0) & 0xff) != 113:
        cv2.imshow('image',vis)

def showlisthorizontal(l):
    vis = np.concatenate(l, axis=1)
    cv2.imshow('image',vis)
    while (cv2.waitKey(0) & 0xff) != 113:
        cv2.imshow('image',vis)

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
