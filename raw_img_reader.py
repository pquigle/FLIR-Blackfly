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
## Error Handling
##############################

## Sanitize inputs
if len(sys.argv) != 2 and len(sys.argv) != 3:
    raise ValueError("Usage: python3 raw_img_reader.py RAW_IMG_PATH [OUTPUT_PATH]")
elif not os.path.isfile(sys.argv[1]):
    raise ValueError("File does not exist")
elif not sys.argv[1].lower().endswith(".raw"):
    raise ValueError("File is not a .raw type")


## Detect output path and determine if the output is of PNG format to save as
## a 16-bit image, instead of 8-bit
if len(sys.argv) == 3:
    OUT = sys.argv[2]
    
    if OUT.lower().endswith(".png"):
        PNG = True

else:
    PNG = False


##############################
## Read Raw File
##############################

## Import image data and define dimensions
PATH     = sys.argv[1]
img_data = np.fromfile(PATH,dtype=np.uint16)
X_DIM    = 1024
Y_DIM    = 768

## Convert 12bit format to 16bit
#img_data = conv_12to16(img_data)
#Y_DIM    = Y_DIM*2//3

## Try to reshape the data into a recognizable image
try:
    img_data = img_data.reshape((Y_DIM,X_DIM))
except:
    raise ValueError(f"Wrong size reshape: Image {img_data.shape}")
    

##############################
## Generate 8-bit Image Using Imshow
##############################

if PNG == False or len(sys.argv) == 2:

    ## Create cmap and normalization instance
    cmap = plt.cm.gray
    norm = plt.Normalize(vmin=np.min(img_data),vmax=np.max(img_data))
    inst = cmap(norm(img_data))

    ## Either display the image or save the image
    if len(sys.argv) == 2:
        plt.imshow(img_data,cmap="gray")
        plt.show()
    else:
        plt.imsave(OUT,inst)


##############################
## Generate 16-bit Image Using pypng
##############################

elif PNG == True:
    
    with open(OUT,'wb') as f:
        writer = png.Writer(width=X_DIM, height=Y_DIM, bitdepth=16, greyscale=True)
        writer.write(f,img_data)