#!/usr/bin/python
import cv2
import sys
import numpy as np
import time

#read stuff
img_orig = cv2.imread(sys.argv[1])

print 'Dimensions: %dx%d' % (img_orig.shape[0],img_orig.shape[1])
