#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *
from collections import Counter

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

    print 'histogram'
    print row_black_pixel_histogram

    all_staff_row_indices = []
    num_stafflines = 5
    threshold = 0.2
    staff_length = (num_stafflines * (line_width + line_spacing)) - line_spacing
    iter_range = num_rows - staff_length + 1

    print {
        'num_rows':num_rows
       ,'num_cols':num_cols
       ,'num_stafflines':num_stafflines
       ,'threshold     ':threshold
       ,'staff_length  ':staff_length
       ,'iter_range    ':iter_range
        ,'line_width':line_width
        ,'line_spacing':line_spacing
    }


    # Find stafflines by finding sum of rows that occur according to
    # staffline width and staffline space which contain as many black pixels
    # as a thresholded value (based of width of page)
    #
    # Filter out using condition that all lines in staff
    # should be above a threshold of black pixels
    current_row = 0
    while (current_row < iter_range):

        # List of 5 ranges of line_width
        staff_lines = [row_black_pixel_histogram[j: j + line_width] for j in
                       range(current_row, current_row + (num_stafflines - 1) * (line_width + line_spacing) + 1,
                             line_width + line_spacing)]
        pixel_avg = sum(sum(staff_lines, [])) / (num_stafflines * line_width)

        #print 'row: ', current_row, 'staff_lines: ' , staff_lines
        #print 'sum of 5 lines at row ', current_row, 'is ', sum(sum(staff_lines,[]))

        for line in staff_lines:
            if (sum(line) / line_width < threshold * num_cols):
                current_row += 1
                break
            else:

                #found a single staff line, thus the top of a staff
                #List of 5 ranges
                staff_row_indices = [list(range(j, j + line_width)) for j in
                                    range(current_row,
                                        current_row + (num_stafflines - 1) * (line_width + line_spacing) + 1,
                                        line_width + line_spacing)]

                #List of Staffs (staff is a list of 5 ranges)
                all_staff_row_indices.append(staff_row_indices)

                #skip a whole staff's length
                current_row = current_row + staff_length

    return all_staff_row_indices




myInput = 'input/music.png'
def extract(arg):

    img = img_orig = cv2.imread(arg, 0)

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

    # ============ Invert ============
    img = img = ~img

    # ============ Find Staff Reference Lengths ============

    img = img
    line_width, line_spacing = get_staff_reference_lengths(img)
    print 'Staff width: %d , spacing: %d' %(line_width, line_spacing)


    # ============ Find Staff Line Rows ============

    img = img
    all_staffline_vertical_indices = find_staffline_rows(img_orig, line_width, line_spacing)
    print("[INFO] Found ", len(all_staffline_vertical_indices), " sets of staff lines")
    print all_staffline_vertical_indices
    print("\n\n")

    #for staff in all_staffline_vertical_indices:
    #    print '\nstaff: ' , staff


    concat_images = \
    (
        img_orig,
        imgHorizontalLines
    )

    showlist(concat_images)

    #vis = np.concatenate(concat_images, axis=0)
    #cv2.imshow('image',vis)
    #k = cv2.waitKey(0) & 0xff
    #print 'k is ' , k



if __name__ == '__main__':
    extract(sys.argv[1])

