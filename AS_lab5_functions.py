#####################
# Block 1:  Import the packages you'll need
# 
# 

import os, sys
import rasterio
import geopandas as gpd




##################
# Block 2: 
# set the working directory to the directory where the data are
# Change this to the directory where your data are

data_dir = r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS"
os.chdir(data_dir)
print(os.getcwd())


##################
# Block 3: 
#   Set up a new smart raster class using rasterio  
#    that will have a method called "calculate_ndvi"

import rasterio
import numpy as np
import math
import os

class SmartRaster:
    def __init__(self, raster_path):
        """Initialize with a path to a multi-band raster file."""
        self.raster_path = raster_path
        
        if not os.path.exists(self.raster_path):
            raise FileNotFoundError(f"{self.raster_path} does not exist.")
        
        # Read and store metadata on init
        with rasterio.open(self.raster_path) as src:
            self.crs = src.crs
            self.transform = src.transform
            self.profile = src.profile
            self.band_count = src.count
            print(f"Loaded raster with {self.band_count} bands | CRS: {self.crs}")

        # Will be populated after calculate_ndvi is called
        self.ndvi_array = None
        self.ndvi_path = None

    # function to calculate NDVI
    def calculate_ndvi(self, band4_index = 4, band3_index = 3):
        #"""Calculate NDVI using the NIR and Red bands."""
        # set up an indicator about whether things work for later
        okay = True

        # embed everything in a try/except block
        # First get the bands. You can use the band numbers to get the bands from the raster.
        try:
            if arcpy.Exists(self.raster_path):
                # load just the NIR band into a raster object
                nir = arcpy.Raster(self.raster_path + f"\\Band_4")

                # load just the red band into a raster object
                # Your code:
                red = arcpy.Raster(self.raster_path + f"\\Band_3")

                # In the case of the image I provided you
                # the NIR band is "Band_4" and the red band is "Band_3"
            else:   # in this case, the image does not exist
                okay = False
                returnval = f"{image_name} does not appear to exist in the workspace: {arcpy.env.workspace}"
                return okay, returnval
        
        except Exception as e:  # this is some problem reading the image
            okay = False
            returnval = e
            return okay, returnval

        # Now we have the two bands.
        # Calculate (NIR-Red)/(NIR+red), which is the formula for NDVI.
        # Embed in a try/except block, so we can catch any errors that might occur
        try:
            ndvi_result = (nir - red) / (nir + red)
            return okay, ndvi_result
        except Exception as e:
            okay = False
            return okay, f"Problem in calculating NDVI: {e}"



##################
# Block 4: 
#   Set up a new smart vector class using geopandas
#    that will have a method similar to what did in lab 4
#    to calculate the zonal statistics for a raster
#    and add them as a column to the attribute table of the vector







