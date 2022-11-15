#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename:   analyzeframes.py
Author(s):  Peter Quigley
Contact:    pquigley@uwo.ca
Created:    Wed Oct 19 10:19:07 2022
Updated:    Wed Oct 19 10:19:07 2022
    
Usage:
$Description$
"""

# Module Imports
import os,sys
import png
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


##############################
## Get Time Between Frames
##############################

def convNameToTime(fname):
    """
    Converts
    
    """
    
    ## Sanitize and strip inputs
    if fname.lower().endswith(".png"):
        obs_time = fname.lower().strip(".png").split("_")
    elif fname.lower().endswith(".raw"):
        obs_time = fname.lower().strip(".raw").split("_")
    else:
        raise NotImplementedError("Only .raw and .png filenames are currently supported")

    ## Convert hr, min, msec to second and return added value
    return float(obs_time[0])*60*60 +\
           float(obs_time[1])*60 +\
           float(obs_time[2]) +\
           float(obs_time[3])/1000
    

def trueFrameRate(frame_dir, plot=False):
    """
    
    """

    
    ## Sanitize inputs
    if not os.path.isdir(frame_dir):
        raise NotADirectoryError(f"{frame_dir} is not a valid directory")
    
    ## Iterate through the directory and convert names to obs_times (in sec)
    t = []
    for fname in os.listdir(frame_dir):
        try:
            t.append(convNameToTime(fname))
        except NotImplementedError:
            pass
    
    ## Convert t to a numpy array find the difference between frames
    arr_t = np.array(sorted(t))
    dt    = arr_t[1:]-arr_t[:-1]
    
    ## Plot time between frames if true
    if plot == True:
        plt.plot(arr_t[:-1],dt)
        plt.title(f"Time Between Frames for Observations on {frame_dir}")
        plt.xlabel("Observed Time (s)")
        plt.ylabel("Time Between Frames (s)")
        plt.grid()
        plt.show()
        
    return dt


##############################
## 8-bit/16-bit RAW to PNG Converter
##############################

def readRAW(img_path,bitdepth=16):
    """
    
    """
    
    ## Identify and use the correct image bitdepth to load in the image
    if bitdepth == 16:
        img_data = np.fromfile(img_path,dtype=np.uint16)
    elif bitdepth == 8:
        img_data = np.fromfile(img_path,dtype=np.uint8)
    else:
        raise NotImplementedError("Only 8-bit and 16-bit images are currently supported")
    
    ## Load in the image
    X_DIM    = 1024
    Y_DIM    = 768

    ## Reshape 1D bit array into proper 1024x768 pixel shape
    try:
        img_data = img_data.reshape((Y_DIM,X_DIM))
    except:
        raise ValueError(f"Invalid image shape {img_data.shape}")
        
    return img_data
    
    
    

##############################
## Import Frames & Medstack
##############################

def importFramesRAW(frame_dir,num_frames=-1,bias=np.zeros((1,1),dtype=np.uint16)):
    """
    Reads in frames from .rcd files starting at a specific frame
    
        Parameters:
            frame_dir (str/Path): path to image directory to read in
            num_frames (int): How many frames to read in. -1 if all
            bias (arr): 2D array of fluxes from bias image
            
        Returns:
            img_array (arr): Image data
            img_times (arr): Header times of these images
    """
    
    ## Sanitize inputs
    if not os.path.isdir(frame_dir):
        raise NotADirectoryError(f"{frame_dir} is not a valid directory")

    ## Define pixel dimensions of the rectangular image and depth of the memory array
    X_DIM   = 1024
    Y_DIM   = 768
    if num_frames == -1:
        num_frames = len(os.listdir(frame_dir))
    img_arr = np.zeros((num_frames,Y_DIM,X_DIM),dtype=np.uint16) 

    ## Loop which iteratively reads in the files and processes them
    frame = 0
    for fname in os.listdir(frame_dir):
        # Check if we exceed the requested frames
        if frame >= num_frames:
            break
        
        if fname.lower().endswith(".raw"):
            # Load in the image data substitute into the array
            fpath = os.path.join(frame_dir,fname)
            img_arr[frame] = np.subtract(readRAW(fpath), bias, dtype=np.uint16)
        
            # Add 1 to the current frame
            frame += 1
        
    
    ## Check if only one frame was called: if so, ndim=3 -> ndim=2
    if num_frames == 1:
        img_arr = img_arr[0]
    
    ## Check if we ran out of frames
    elif num_frames != frame:
        img_arr = img_arr[:frame]
        print(f"We ran out of frames! Only {frame} of {num_frames}.")
        print("Contracting array...")
        
    return img_arr

        
        
def stackImages(frame_dir,
                save_path=None,
                num_frames=-1,
                bias=None):
    """
    Make median combined image of first numImages in a directory
    
        Parameters:
            frame_dir (str/Path): Directory of images to be stacked
            save_path (str): Filename to save stacked image as
            num_frames (int): Number of images to combine
            bias (arr): 2D flux array from the bias image
            
        Returns:
            median_img (arr): Median combined, bias-subtracted image
    """

    ## Sanitize inputs
    if not os.path.isdir(frame_dir):
        raise NotADirectoryError(f"{frame_dir} is not a valid directory")
    
    ## Read in stack of .raw images and median combine them
    if bias == None:
        RAW_imgs = importFramesRAW(frame_dir,num_frames)
        median_img = np.median(RAW_imgs, axis=0).astype(np.uint16)
    else:
        RAW_imgs = importFramesRAW(frame_dir,num_frames,bias)
        median_img = np.median(RAW_imgs, axis=0).astype(np.uint16)
        
    ## Save the image as a png if requested
    if save_path != None:
        if save_path.lower().endswith(".png"):
            with open(save_path,"wb") as f:
                    writer = png.Writer(width=median_img.shape[1], 
                                        height=median_img.shape[0],
                                        bitdepth=16,
                                        greyscale=True)
                    writer.write(f,median_img)
        else:
            raise NotImplementedError("Only .png filenames are permitted")
        
    
    return median_img


def meanedImages(frame_dir,
                save_path=None,
                num_frames=-1,
                bias=None):
    """
    Make mean combined image of first numImages in a directory
    
        Parameters:
            frame_dir (str/Path): Directory of images to be stacked
            save_path (str): Filename to save stacked image as
            num_frames (int): Number of images to combine
            bias (arr): 2D flux array from the bias image
            
        Returns:
            median_img (arr): Median combined, bias-subtracted image
    """

    ## Sanitize inputs
    if not os.path.isdir(frame_dir):
        raise NotADirectoryError(f"{frame_dir} is not a valid directory")
    
    ## Read in stack of .raw images and median combine them
    if bias == None:
        RAW_imgs = importFramesRAW(frame_dir,num_frames)
        median_img = np.mean(RAW_imgs, axis=0).astype(np.uint16)
    else:
        RAW_imgs = importFramesRAW(frame_dir,num_frames,bias)
        median_img = np.mean(RAW_imgs, axis=0).astype(np.uint16)
        
    ## Save the image as a png if requested
    if save_path != None:
        if save_path.lower().endswith(".png"):
            with open(save_path,"wb") as f:
                    writer = png.Writer(width=median_img.shape[1], 
                                        height=median_img.shape[0],
                                        bitdepth=16,
                                        greyscale=True)
                    writer.write(f,median_img)
        else:
            raise NotImplementedError("Only .png filenames are permitted")
        
    
    return median_img


def maxedImages(frame_dir,
                save_path=None,
                num_frames=-1,
                bias=None):
    """
    Make max-combined image of first numImages in a directory
    
        Parameters:
            frame_dir (str/Path): Directory of images to be stacked
            save_path (str): Filename to save stacked image as
            num_frames (int): Number of images to combine
            bias (arr): 2D flux array from the bias image
            
        Returns:
            median_img (arr): Median combined, bias-subtracted image
    """

    ## Sanitize inputs
    if not os.path.isdir(frame_dir):
        raise NotADirectoryError(f"{frame_dir} is not a valid directory")
    
    ## Read in stack of .raw images and median combine them
    if bias == None:
        RAW_imgs = importFramesRAW(frame_dir,num_frames)
        median_img = np.max(RAW_imgs, axis=0).astype(np.uint16)
    else:
        RAW_imgs = importFramesRAW(frame_dir,num_frames,bias)
        median_img = np.max(RAW_imgs, axis=0).astype(np.uint16)
        
    ## Save the image as a png if requested
    if save_path != None:
        if save_path.lower().endswith(".png"):
            with open(save_path,"wb") as f:
                    writer = png.Writer(width=median_img.shape[1], 
                                        height=median_img.shape[0],
                                        bitdepth=16,
                                        greyscale=True)
                    writer.write(f,median_img)
        else:
            raise NotImplementedError("Only .png filenames are permitted")
        
    
    return median_img
    