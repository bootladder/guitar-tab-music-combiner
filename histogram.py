#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *

p_init = pipeline_init
p_add  = pipeline_add
p_get  = pipeline_get

def draw_image_histogram(image, channels, color='k'):
    hist = cv2.calcHist([image], channels, None, [256], [0, 256])
    plt.plot(hist, color=color)
    plt.xlim([0, 256])

def extract_horizontal_lines(img):
    img = imgHorizontalLines = ~img
    kernel = np.ones((1,40),np.uint8)
    img = imgHorizontalLines = cv2.erode(imgHorizontalLines,kernel,iterations = 1)
    img = imgHorizontalLines = ~imgHorizontalLines
    thresh_val = 200
    ret,imgHorizontalLines = cv2.threshold(imgHorizontalLines,thresh_val,255,cv2.THRESH_BINARY)
    img = imgHorizontalLines
    return img

def remove_non_lines(img):
    kernel = np.zeros((21,21),np.uint8)
    kernel[11,...] = 1
    img = img = cv2.erode(img,kernel,iterations = 1)
    return img

def extract_horizontal_lines_version2(img):

    return img


img = img_orig = cv2.imread(sys.argv[1], 0)

p_init(img)
p_add('noiseremoval',  lambda img: cv2.fastNlMeansDenoising(img, None, 10, 7, 21))
p_add('thresh1',       otsu_thresh)
##p_add('open1',         lambda img: morph_open_square(img,5))
p_add('horizontal_lines', extract_horizontal_lines)
p_add('horizontal_lines_version2', extract_horizontal_lines_version2)
##p_add('invert1',       lambda img: ~img)
##p_add('remove_non_lines', remove_non_lines)

showlist(pipeline_all(True))
#show(pipeline_get('thresh1', True))

img = pipeline_last()

staff_width,staff_spacing = get_staff_reference_lengths(img)
print 'STAFF: ', staff_width,staff_spacing

all_staffline_rows = find_staffline_rows(img, staff_width, staff_spacing)
print all_staffline_rows
print 'THERE ARE %d STAFFS'%len(all_staffline_rows)


#########################################
img = ~img

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
