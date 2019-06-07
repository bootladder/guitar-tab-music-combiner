#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
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



def get_ref_lengths(img):
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

# Open
def morph_open(img):
    kernel = np.ones((10,10),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# Close
def morph_close(img):
    kernel = np.ones((9,9),np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

def kernel_square(i):
    return np.ones((i,i),np.uint8)


myInput = 'input/music.png'
def extract(arg):

    img = cv2.imread(arg, 0)

    # ============ Noise Removal ============

    imgNoiseRemoval = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)

    # ============ Binarization ============

    # Global Thresholding
    retval, imgThreshold = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    cv2.imwrite('scratch/binarized.jpg', imgThreshold)

    # Otsu's Thresholding
    retval, imgOtsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imwrite('scratch/otsu.jpg', imgOtsu)

    # ============ Opening ============

    kernel = np.ones((5,5),np.uint8)
    imgOpen = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    # ============ Extract Lines ============
    imgHorizontalLines = ~imgOpen  #inverse
    kernel = np.ones((1,40),np.uint8)
    imgHorizontalLines = cv2.erode(imgHorizontalLines,kernel,iterations = 1)
    imgHorizontalLines = ~imgHorizontalLines
    thresh_val = 200
    ret,imgHorizontalLines = cv2.threshold(imgHorizontalLines,thresh_val,255,cv2.THRESH_BINARY)

    # ============ Invert ============
    imgHorizontalLines = ~imgHorizontalLines

    # ============ Remove Non-Lines ============
    img = imgHorizontalLines
    kernel = np.zeros((21,21),np.uint8)
    kernel[11,...] = 1
    img = cv2.erode(img,kernel,iterations = 1)

    # ============ Invert ============
    img = ~img

    # ============ Find Staff Reference Lengths ============

    show(img)
    img = img
    line_width, line_spacing = get_ref_lengths(img)
    print 'Staff width: %d , spacing: %d' %(line_width, line_spacing)


    # ============ Find Staff Line Rows ============

    img = img
    all_staffline_vertical_indices = find_staffline_rows(img, line_width, line_spacing)
    print("[INFO] Found ", len(all_staffline_vertical_indices), " sets of staff lines")
    print("\n\n")

    #for staff in all_staffline_vertical_indices:
    #    print '\nstaff: ' , staff

    concat_images = \
    (
        img,
        imgThreshold,
        imgOpen
    )

    vis = np.concatenate(concat_images, axis=0)
    cv2.imshow('image',vis)
    k = cv2.waitKey(0) & 0xff
    print 'k is ' , k



if __name__ == '__main__':
    extract(sys.argv[1])

