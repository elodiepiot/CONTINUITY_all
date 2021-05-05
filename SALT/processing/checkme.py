#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os
import shutil

data = pd.read_csv("civility_brent.csv")

# loop through all the DWI files
for i in range( 0, data.shape[0] ):
	if not os.path.exists( data.iloc[i,1] ):
		print( "{0:s} DWI does not exist {1:s}".format( data.iloc[i,0], data.iloc[i,1] ) )

# loop through all the T1 files
for i in range( 0, data.shape[0] ):
	if not os.path.exists( data.iloc[i,2] ):
		print( "{0:s} T1 does not exist {1:s}".format( data.iloc[i,0], data.iloc[i,2] ) )

# loop through all the MASK files
for i in range( 0, data.shape[0] ):
	if not os.path.exists( data.iloc[i,3] ):
		print( "{0:s} MASK does not exist {1:s}".format( data.iloc[i,0], data.iloc[i,3] ) )


# loop through all the TABLE files
for i in range( 0, data.shape[0] ):
	if not os.path.exists( data.iloc[i,4] ):
		print( "{0:s} TABLE does not exist {1:s}".format( data.iloc[i,0], data.iloc[i,4] ) )

# loop through all the SURFACE files
for i in range( 0, data.shape[0] ):
	if not os.path.exists( data.iloc[i,5] ):
		print( "{0:s} SURFACE does not exist {1:s}".format( data.iloc[i,0], data.iloc[i,5] ) )

# if os.path.exists( dfile ):

