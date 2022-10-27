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
from datetime import datetime

## Custom Script Imports
from bitconverter import conv_12to16


##############################
## 8-bit/16-bit RAW to PNG Converter
##############################

def RAWtoPNG(img_path,save_path=None,bitdepth=16):
    """
    Convert .raw file into a .png. Saves the file if a savepath is specified.
    Otherwise, just displays it.
    
    Parameters:
        img_path (str): Filepath to the .raw image
        save_path (str): Savepath for the output png file. "None" only
                         displays the image.
        bitdepth (int): Bitdepth of output image. 8-bit and 16-bit are
                        currently supported
                            
    Returns:
        None
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
            writer = png.Writer(width=X_DIM, height=Y_DIM, bitdepth=bitdepth, greyscale=True)
            writer.write(f,img_data)
    

def RAW_PNG_DirIter(target_dir,output_dir):
    """
    Iterates through a target directory and converts all .raw files present
    into .png files in the given output directory. Uses RAWtoPNG function.
    
    Parameters:
        target_dir (str): Filepath to target directory
        output_dir (str): Filepath to save directory. Must either not exist
                          or must be an empty directory.
                              
    Returns:
        None
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
## 16-bit RAW to VID Converter
##############################

def RAWtoVID(target_dir,save_path):
    """
    Converts all .raw files in target directory into a single .vid file at
    save_path. Assumes 16-bit data and 1024x768 pixelshape and that the .raw
    filename is of the format "hh_mm_ss_fff.raw".
    
    Credit to Mike Mazur, who's code formed the foundation for this function

    Args:
        target_dir (str): Filepath to target directory. Assumes first 8
                          characters are YYYYMMDD of observation.
        save_path (str): Savepath for the output .vid file

    Returns:
        None

    """

    ## Sanitize inputs
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"{target_dir} is not an existing directory")
    elif not save_path.lower().endswith(".vid"):
        sys.exit(f"{save_path} is not a .vid file")
    elif os.path.exists(save_path):
        print(f"Warning: Deleting old .vid file at {save_path}")
        os.remove(save_path)
        
    ## Get date from target_dir
    target_basename = os.path.basename(os.path.normpath(target_dir))
    try:
        YYYY = int(target_basename[:4])
        MM   = int(target_basename[4:6])
        DD   = int(target_basename[6:8])
    except ValueError:
        raise ValueError(f"{target_basename} needs to have YYYYMMDD as the first 4 characters")
    
    
    ## Iterate through .raw files in target_dir and write them to a vid file
    ## taking the time from the filename (assuming)
    n = 0 #frame number
    for fname in os.listdir(target_dir):
        if fname.lower().endswith(".raw"):
            print(fname)
            # Define image dimensions
            X_DIM = 1024
            Y_DIM = 768
            
            # Define image header for this frame (number of bytes == inline
            # comment). Not well-understood flags have ? in the inline comment
            magic = 809789782 # 4?
            seqlen = X_DIM*Y_DIM # 4
            headerlen = 112 # 4
            flags = 999 # 4?
            seq = n # 4
            num = 1 # 2
            width = X_DIM # 2
            height = Y_DIM # 2
            depth = 16 # 2
            hx = 0 # 2?
            ht = 0 # 2?
            cam = 15 # 2?
            reserved0 = 000 # 2?
            exposure = 33 # 4
            reserved2 = 000 # 4?
            text = "FLIR-BF" # 64
            
            # Get time from filename and generate timestamp
            obs_time  = fname.strip(".raw")
            if int(obs_time[:2]) < 16: # set day to next if over 24h
                DD += 1
            timestamp = datetime.strptime(f"{target_basename[:8]} {obs_time} UTC",
                                          "%Y%m%d %H_%M_%S_%f %Z")
            unixtime = datetime.timestamp(timestamp)
            unixtime = int(unixtime)
            
            
            # Write to file in big endian order
            with open(save_path, "ab") as f:
                # Write header information
                f.write((magic).to_bytes(4, byteorder='little'))
                f.write((seqlen).to_bytes(4, byteorder='little'))
                f.write((headerlen).to_bytes(4, byteorder='little'))
                f.write((flags).to_bytes(4, byteorder='little'))
                f.write((seq).to_bytes(4, byteorder='little'))
                f.write((unixtime).to_bytes(4, byteorder='little'))
                f.write((num).to_bytes(2, byteorder='little'))
                f.write((width).to_bytes(2, byteorder='little'))
                f.write((height).to_bytes(2, byteorder='little'))
                f.write((depth).to_bytes(2, byteorder='little'))
                f.write((hx).to_bytes(2, byteorder='little'))
                f.write((ht).to_bytes(2, byteorder='little'))
                f.write((cam).to_bytes(2, byteorder='little'))
                f.write((reserved0).to_bytes(2, byteorder='little'))
                f.write((exposure).to_bytes(4, byteorder='little'))
                f.write((reserved2).to_bytes(4, byteorder='little'))
                f.write(text.encode())
                for i in range(52):
                    f.write((0).to_bytes(1,byteorder='little'))
                    
                # Read in the data and write to file
                fpath = os.path.join(target_dir, fname)
                img_data = np.fromfile(fpath, dtype=np.uint16)
                img_data.tofile(f)
                
            n += 1 # add 1 to the frame number
    

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