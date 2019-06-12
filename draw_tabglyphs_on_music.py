#!/usr/bin/python
import cv2
import sys
import numpy as np
import time
from myutil import *
from extract_tabs import *
from extract_music import *




def draw_glyphs_on_image(glyphs, coords, img):


    return


############################################################

def draw_tabglyphs_on_music(img_music, img_tab):


    glyphs = imgtab_to_glyphs(img_tab)
    coords = imgmusic_to_notecoordinates(img_music)

    print 'Found ', len(glyphs), ' tab notes and ',len(coords), 'music notes'
    if len(glyphs) != len(coords):
        print 'NOT THE SAME!!'
        sys.exit(1)


    for i in range(0,len(coords)):
        coord = coords[i]
        col = coord[0]
        row = coord[1]

        glyphRowSize = len(glyphs[i])
        glyphColSize = len(glyphs[i][0])
        #print 'Glyph Size: rows ',glyphRowSize,' col ',glyphColSize

        coord_row_start = (row - (glyphRowSize/2))
        coord_col_start = (col - (glyphColSize/2))

        img_music[ coord_row_start:coord_row_start+glyphRowSize,
                coord_col_start:coord_col_start+glyphColSize] = glyphs[i]
        #print 'row ',row,' col ',col

    return img_music


if __name__ == '__main__':

    # Load Images
    img_music =  cv2.imread(sys.argv[1],0)
    img_tab   =  cv2.imread(sys.argv[2],0)

    img = draw_tabglyphs_on_music(img_music,img_tab)

    show(img)
