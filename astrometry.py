#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename:   astrometry.py
Author(s):  Peter Quigley
Contact:    pquigley@uwo.ca
Created:    Thu Oct 13 16:38:23 2022
Updated:    Thu Oct 13 16:38:23 2022
    
Usage:
$Description$
"""

import sys,os
import cv2 #TODO: opencv has a conflict which causes png to write a blank file
#import png
import numpy as np
import matplotlib.pyplot as plt


##############################
## Function to Mask Image
##############################

def circularMask(img_path, save_path=None):
    """
    Add a circular mask to the image. Meant for FLIR Blackfly aperture.
    
        Parameters:
            img_path (str): Path to the image
            save_path (str): Path for the output solution header

        Returns:
            None
    """
    
    ## Load in the image
    image = cv2.imread(img_path,0).astype(np.uint16)
    
    ## Create the circular mask (assumes 16-bit image)
    mask = np.zeros(image.shape, dtype=np.uint16)
    mask = cv2.circle(mask, 
                      (image.shape[1]//2,image.shape[0]//2),
                      min(image.shape)//2, 
                      (255,255,255), 
                      -1)
    
    ## Generate masked image
    masked_img = cv2.bitwise_and(image, mask)
    
    ## Decide to either show the image in a plt window or save as PNG
    if save_path == None:
        plt.imshow(masked_img,cmap="gray")
        plt.show()
    elif save_path.lower().endswith(".png"):
        """
        with open(save_path,'wb') as f:
            writer = png.Writer(width=masked_img.shape[1],
                                height=masked_img.shape[0],
                                bitdepth=16,
                                greyscale=True)
            writer.write(f,masked_img)
        """
        cv2.imwrite(save_path,masked_img)
    else:
        print("TypeError: Can only save as a png file!")
        return


##############################
## Call Astrometry.net
##############################

def astrometrySoln(img_path, save_path, soln_order):
    """
    Attempt to solve a given image's astrometry using nova.astrometry.net
    Credit to Michael Mazur and Rachel Brown for the script template
    
        Parameters:
            img_path (str): Path to the image
            save_path (str): Path for the output solution header
            soln_order (int): Order of the solution
        
        Returns:
            wcs_header (?): The solution header returned from astrometry.net
    """

    from astroquery.astrometry_net import AstrometryNet
    
    #astrometry.net API
    ast = AstrometryNet()
    
    #key for astrometry.net account
    ast.api_key = 'ibeszekxrtnatxdl'    #key for Peter Quigley's account
    wcs_header = ast.solve_from_image(img_path, crpix_center = True, tweak_order = soln_order, force_image_upload=True)

    #save solution to file
    if not save_path.exists():
            wcs_header.tofile(save_path)
            
    return wcs_header


##############################
## Main
##############################

if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print("Usage: python3 astrometry.py INPUT_FILE [OUTPUT_FILE]")
        sys.exit()
    elif len(sys.argv) == 2:
        if not os.path.isfile(sys.argv[1]):
            sys.exit(f"{sys.argv[1]} does not exist")
            
        circularMask(sys.argv[1])
            
    elif len(sys.argv) == 3:
        if not os.path.isfile(sys.argv[1]):
            sys.exit(f"{sys.argv[1]} does not exist")
            
        circularMask(sys.argv[1],sys.argv[2])