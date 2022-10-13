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

## Custom Script Imports
from bitconverter import conv_12to16


##############################
## Error Handling
##############################

## Sanitize inputs
if len(sys.argv) != 2 and len(sys.argv) != 3:
    raise ValueError("Usage: python3 raw_img_reader.py RAW_IMG_PATH [OUTPUT PATH]")
elif not os.path.isfile(sys.argv[1]):
    raise ValueError("File does not exist")
elif not sys.argv[1].endswith(".raw"):
    raise ValueError("File is not a .raw type")


## Detect output path
if len(sys.argv) == 3:
    OUT = sys.argv[2]


##############################
## Read Raw File
##############################

## Import image data and define dimensions
PATH     = sys.argv[1]
img_data = np.fromfile(PATH,dtype=np.uint8)
X_DIM    = 1024
Y_DIM    = 768
print(len(img_data))

## Convert 12bit format to 16bit
img_data = conv_12to16(img_data)
#Y_DIM    = Y_DIM*2//3

## Try to reshape the data into a recognizable image
try:
    img_data = img_data.reshape((Y_DIM,X_DIM))
except:
    raise ValueError(f"Wrong size reshape: Image {img_data.shape}")

plt.imshow(img_data,cmap="gray")
if len(sys.argv) == 3:
    plt.savefig(OUT)
else:
    plt.show()
