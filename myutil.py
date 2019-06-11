#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from collections import Counter


pipeline = []
def pipeline_init(img_orig):
    d_init = {'img': img_orig, 'name': 'init'}
    pipeline.append(d_init)

def pipeline_add(name, func):
    img = pipeline[-1]['img']
    new_img = func(img)
    d_new = {'img': new_img, 'name':name}

    pipeline.append(d_new)

def put_text(img,text):
    img_new = img
    cv2.putText(img_new,text, (10,len(img)), cv2.FONT_HERSHEY_PLAIN, 1, (127), 2, cv2.LINE_AA)
    return img_new

def pipeline_get(name, annotate=False):
    for d in pipeline:
        if d['name'] == name:
            img = d['img']
            name = d['name']
            if annotate == True:
                print 'yay'
                img = put_text(img,name)
            return img
    return pipeline[0]['key_error']

def pipeline_all(annotate=False):
    if annotate == False:
        return [d['img'] for d in pipeline]
    else:
        return [ put_text(d['img'],d['name']) for d in pipeline]

#return [pipeline[i]['img'] for i in range(0,len(pipeline))]

def pipeline_last():
    return pipeline[-1]['img']




def get_staff_reference_lengths(img):
    num_rows = img.shape[0]  # Image Height (number of rows)
    num_cols = img.shape[1]  # Image Width (number of columns)
    rle_image_white_runs = []  # Cumulative white run list
    rle_image_black_runs = []  # Cumulative black run list
    sum_all_consec_runs = []  # Cumulative consecutive black white runs

    for i in range(num_cols):
        col = img[:, i]
        rle_col = []
        rle_white_runs = []
        rle_black_runs = []
        run_val = 0  # (The number of consecutive pixels of same value)
        run_type = col[0]  # Should be 255 (white) initially
        for j in range(num_rows):
            if (col[j] == run_type):
                # increment run length
                run_val += 1
            else:
                # add previous run length to rle encoding
                rle_col.append(run_val)
                if (run_type == 0):
                    rle_black_runs.append(run_val)
                else:
                    rle_white_runs.append(run_val)

                # alternate run type
                run_type = col[j]
                # increment run_val for new value
                run_val = 1

        # add final run length to encoding
        rle_col.append(run_val)
        if (run_type == 0):
            rle_black_runs.append(run_val)
        else:
            rle_white_runs.append(run_val)

        # Calculate sum of consecutive vertical runs
        sum_rle_col = [sum(rle_col[i: i + 2]) for i in range(len(rle_col))]

        # Add to column accumulation list
        rle_image_white_runs.extend(rle_white_runs)
        rle_image_black_runs.extend(rle_black_runs)
        sum_all_consec_runs.extend(sum_rle_col)

    white_runs = Counter(rle_image_white_runs)
    black_runs = Counter(rle_image_black_runs)
    black_white_sum = Counter(sum_all_consec_runs)

    line_spacing = white_runs.most_common(1)[0][0]
    line_width = black_runs.most_common(1)[0][0]
    width_spacing_sum = black_white_sum.most_common(1)[0][0]

    assert (line_spacing + line_width == width_spacing_sum), "Estimated Line Thickness %d + Spacing %d doesn't correspond with Most Common Sum %d" %(line_width,line_spacing,width_spacing_sum)

    return line_width, line_spacing


def find_staffline_rows(img, line_width, line_spacing):
    num_rows = img.shape[0]  # Image Height (number of rows)
    num_cols = img.shape[1]  # Image Width (number of columns)
    row_black_pixel_histogram = []

    # Determine number of black pixels in each row
    for i in range(num_rows):
        row = img[i]
        num_black_pixels = 0
        for j in range(len(row)):
            if (row[j] == 0):
                num_black_pixels += 1

        row_black_pixel_histogram.append(num_black_pixels)

    # plt.bar(np.arange(num_rows), row_black_pixel_histogram)
    # plt.show()

    all_staff_row_indices = []
    num_stafflines = 5
    threshold = 0.2
    staff_length = num_stafflines * (line_width + line_spacing) - line_spacing
    iter_range = num_rows - staff_length + 1

    # Find stafflines by finding sum of rows that occur according to
    # staffline width and staffline space which contain as many black pixels
    # as a thresholded value (based of width of page)
    #
    # Filter out using condition that all lines in staff
    # should be above a threshold of black pixels
    current_row = 0
    while (current_row < iter_range):
        staff_lines = [row_black_pixel_histogram[j: j + line_width] for j in
                       range(current_row, current_row + (num_stafflines - 1) * (line_width + line_spacing) + 1,
                             line_width + line_spacing)]
        pixel_avg = sum(sum(staff_lines, [])) / (num_stafflines * line_width)

        for line in staff_lines:
            if (sum(line) / line_width < threshold * num_cols):
                current_row += 1
                break
        else:
            staff_row_indices = [list(range(j, j + line_width)) for j in
                                 range(current_row,
                                       current_row + (num_stafflines - 1) * (line_width + line_spacing) + 1,
                                       line_width + line_spacing)]
            all_staff_row_indices.append(staff_row_indices)
            current_row = current_row + staff_length

    return all_staff_row_indices




def draw_contours_on_image_like(contours, img_orig):
    img_blank = np.ones_like(img_orig)*255
    cv2.drawContours(img_blank,contours,-1,(0,255,0),1)
    return img_blank

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

def binary_thresh(img, val):
    ret,img_thresh = cv2.threshold(img,val,255,cv2.THRESH_BINARY)
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

