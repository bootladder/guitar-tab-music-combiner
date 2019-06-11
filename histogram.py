#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *
from collections import Counter

def draw_image_histogram(image, channels, color='k'):
    hist = cv2.calcHist([image], channels, None, [256], [0, 256])
    plt.plot(hist, color=color)
    plt.xlim([0, 256])


img = img_orig = cv2.imread(sys.argv[1], 0)
#img = img_inverse = ~img
#img = img_otsu = otsu_thresh(img)


img = img_noiseremoval = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
img = img_otsu = otsu_thresh(img)
img = img_open = morph_open_square(img, 5)

# ============ Extract Lines ============
img = imgHorizontalLines = ~img
kernel = np.ones((1,40),np.uint8)
img = imgHorizontalLines = cv2.erode(imgHorizontalLines,kernel,iterations = 1)
img = imgHorizontalLines = ~imgHorizontalLines
thresh_val = 200
ret,imgHorizontalLines = cv2.threshold(imgHorizontalLines,thresh_val,255,cv2.THRESH_BINARY)
img = imgHorizontalLines

# ============ Invert ============
img = imgHorizontalLines = ~imgHorizontalLines

# ============ Remove Non-Lines ============
img = img = imgHorizontalLines
kernel = np.zeros((21,21),np.uint8)
kernel[11,...] = 1
img = img = cv2.erode(img,kernel,iterations = 1)
show(img)



row_sums = []
for row in img:
    count = 0
    for pixel in row:
        if (pixel > 0):
            count = count + 1

    row_sums.append(count)

print len(row_sums)
print len(img[0])

# Smooth out row sums
new_row_sums = []
for i in range(0,len(row_sums)-3):
    sum = (row_sums[i] + row_sums[i+1] + row_sums[i+2]) / 3
    new_row_sums.append(sum)

row_sums = new_row_sums

print len(row_sums) , 'is length'

img_blank = np.zeros_like(img)
for i in range(0,len(row_sums)):

    row_sum = row_sums[i]

    for j in range(0,row_sum):
        img_blank[i][j] = 255

show(img_blank)




hist = cv2.calcHist([img], [0], None, [256], [0, 256])
