"""
Title:   allsky_events.py
Author:  Peter Quigley
Date:    2022/11/02
Purpose: Generate a list of unique events on a specific date and their magnitudes

Usage: *Must be used on Peter's personal computer, or pathing changed
Improvements: Make more general
"""

import numpy as np


###########################
## 
###########################

evdate = input("Event date (YYYYMMDD): ")
#evpath = f"../../FLIR-Data/{evdate}/evmags{evdate}.log"
evpath = f"data/{evdate}/evmags{evdate}.log"

evlist = np.loadtxt(evpath,dtype=object)[:,[0,10]]
evlist[:,0] = [ev[12:18] for ev in evlist[:,0]]

unique_ev = evlist[np.unique(evlist[:,0],return_index=True)[1]]
unique_ev = unique_ev[unique_ev[:,1].argsort()]

#np.savetxt(f"../../FLIR-Data/{evdate}/UniqueEvents{evdate}.log",
np.savetxt(f"data/{evdate}/UniqueEvents{evdate}.log",
           unique_ev[::-1],fmt="%.6s",
           delimiter=",")

