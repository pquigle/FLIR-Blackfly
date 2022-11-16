#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename:      
Author(s):  Peter Quigley
Contact:    pquigley@uwo.ca
Created:    Wed Nov 16 10:25:26 2022
Updated:    Wed Nov 16 10:25:26 2022
    
Usage:
$Description$
"""

import os,sys
from PIL import Image
from pathlib import Path


imgpath = Path(sys.argv[1])
outpath = imgpath.parent/(imgpath.stem+'-rot')

if not outpath.is_dir():
    outpath.mkdir()

for file in imgpath.glob('*.png'):
    print(file,type(file))
    with Image.open(file) as unrotated:
        rotated = unrotated.rotate(180)
        rotated.save(outpath/file.name)
    
    