"""
Filename: raw_img_reader.py
Author(s): Peter Quigley
Contact: pquigle@uwo.ca
Created: 2022/10/11
Updated: 2022/10/11

Usage: python3 raw_img_reader.py RAW_IMG_PATH [OUTPUT_PATH]
Description: reads in an image in .raw format
"""

## Module Imports
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import png

## Custom Script Imports
from bitconverter import conv_12to16


##############################
## 8-bit/16-bit RAW to PNG Converter
##############################

def RAWtoPNG(img_path,save_path=None,bitdepth=16):
    """
    
    """
    
    ## Identify and use the correct image bitdepth to load in the image
    if bitdepth == 16:
        img_data = np.fromfile(img_path,dtype=np.uint16)
    elif bitdepth == 8:
        img_data = np.fromfile(img_path,dtype=np.uint8)
    else:
        raise ValueError("Only 8-bit and 16-bit images are currently supported")
    
    ## Load in the image
    X_DIM    = 1024
    Y_DIM    = 768

    ## Reshape 1D bit array into proper 1024x768 pixel shape
    try:
        img_data = img_data.reshape((Y_DIM,X_DIM))
    except:
        raise ValueError(f"Invalid image shape {img_data.shape}")
    
    
    ## Either show image using matplotlib or save using png
    if save_path == None:
        plt.imshow(img_data,cmap="gray")
        plt.show()
        
    elif save_path.lower().endswith(".png"):
        with open(save_path,"wb") as f:
            writer = png.Writer(width=X_DIM, height=Y_DIM, bitdepth=16, greyscale=True)
            writer.write(f,img_data)
    

##############################
## Directory Iterator
##############################

def RAW_PNG_DirIter(target_dir,output_dir):
    """
    
    """
    
    ## Sanitize inputs and create output directory
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"{target_dir} is not an existing directory")
    elif os.path.exists(output_dir):
        if os.path.isdir(output_dir):
            os.rmdir(output_dir)
        else:
            raise NotADirectoryError(f"{target_dir} is an existing file")
    os.mkdir(output_dir)
    
    ## Convert RAW files in target_dir into PNG files in output_dir
    for fname in os.listdir(target_dir):
        if fname.lower().endswith((".raw")):
            # Replace .raw with .png
            png_name = fname[:-4] + ".png"
            
            # Call RAWtoPNG() on current raw file
            RAWtoPNG(target_dir+fname, output_dir+png_name)
            
    print("All files converted successfully")


##############################
## Main
##############################

if __name__ == "__main__":
    
    ## Sanitize inputs and run RAWtoPNG()
    if len(sys.argv) == 1:
        print("Usage: python3 raw_img_reader.py RAW_IMG_PATH [OUTPUT_PATH]")
        sys.exit()
        
    elif len(sys.argv) == 2:
        if not os.path.isfile(sys.argv[1]):
            sys.exit(f"{sys.argv[1]} does not exist")
        elif not sys.argv[1].lower().endswith(".raw"):
            sys.exit(f"{sys.argv[1]} is not .raw type")
        
        RAWtoPNG(sys.argv[1])
            
    elif len(sys.argv) == 3:
        if not os.path.isfile(sys.argv[1]):
            sys.exit(f"{sys.argv[1]} does not exist")
        elif not sys.argv[1].lower().endswith(".raw"):
            sys.exit(f"{sys.argv[1]} is not .raw type")
        elif not sys.argv[2].lower().endswith(".png"):
            sys.exit(f"{sys.argv[2]} is not .png type")
            
        RAWtoPNG(sys.argv[1],sys.argv[2])