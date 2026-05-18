#####################
# Block 1:  Import the packages you'll need
# 
# 

import os, sys
import rasterio
import geopandas as gpd



from rasterio.mask import mask
import pandas as pd
from shapely.geometry import mapping

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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


class SmartVectorLayer:
    def __init__(self, shapefile_path):
        """Initialize with a path to a shapefile."""
        self.shapefile_path = shapefile_path

        if not os.path.exists(self.shapefile_path):
            raise FileNotFoundError(f"{self.shapefile_path} does not exist.")

        # Load the shapefile as a GeoDataFrame on init
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            print(f"Loaded shapefile with {len(self.gdf)} features | CRS: {self.gdf.crs}")
        except Exception as e:
            raise RuntimeError(f"Problem loading shapefile: {e}")


    def summarize_field(self, field):
        """Return the mean of a numeric field, ignoring NaN."""
        okay = True

        # Check field exists
        if field not in self.gdf.columns:
            print(f"Field '{field}' not found in attribute table.")
            return False, None

        # Check field is numeric
        if not pd.api.types.is_numeric_dtype(self.gdf[field]):
            print(f"Field '{field}' is not numeric (dtype: {self.gdf[field].dtype}).")
            return False, None

        try:
            mean = self.gdf[field].mean(skipna=True)
            print(f"Mean of '{field}': {mean:.4f}")
            return okay, mean
        except Exception as e:
            print(f"Problem calculating mean: {e}")
            return False, None


    def zonal_stats_to_field(self, raster_path, statistic_type="mean", output_field="ZonalStat"):
        """
        For each feature in the vector layer, calculates the zonal statistic
        from the raster and writes it as a new column.

        Parameters:
        - raster_path: path to the raster (.tif)
        - statistic_type: "mean", "sum", "min", "max", "median"
        - output_field: name of the new column to store results
        """
        okay = True

        # Check output field doesn't already exist
        if output_field in self.gdf.columns:
            print(f"Field '{output_field}' already exists. Please choose a different name.")
            return False

        # Check raster exists
        if not os.path.exists(raster_path):
            print(f"Raster '{raster_path}' not found.")
            return False

        # Validate statistic type
        valid_stats = ["mean", "sum", "min", "max", "median"]
        if statistic_type.lower() not in valid_stats:
            print(f"Invalid statistic '{statistic_type}'. Choose from: {valid_stats}")
            return False

        # Open raster and check CRS match
        try:
            with rasterio.open(raster_path) as src:
                raster_crs = src.crs

                # Reproject vector to match raster CRS if needed
                if self.gdf.crs != raster_crs:
                    print(f"CRS mismatch — reprojecting vector from {self.gdf.crs} to {raster_crs}")
                    gdf_proj = self.gdf.to_crs(raster_crs)
                else:
                    gdf_proj = self.gdf

                # Loop through each feature and compute zonal stat
                zonal_results = []
                fail_count = 0

                for idx, row in gdf_proj.iterrows():
                    try:
                        # Mask raster to feature geometry
                        geom = [mapping(row.geometry)]
                        out_image, _ = mask(src, geom, crop=True, nodata=np.nan)
                        data = out_image[0].astype(float)  # first band

                        # Replace nodata with NaN
                        data[data == src.nodata] = np.nan

                        # Calculate requested statistic
                        if statistic_type.lower() == "mean":
                            result = np.nanmean(data)
                        elif statistic_type.lower() == "sum":
                            result = np.nansum(data)
                        elif statistic_type.lower() == "min":
                            result = np.nanmin(data)
                        elif statistic_type.lower() == "max":
                            result = np.nanmax(data)
                        elif statistic_type.lower() == "median":
                            result = np.nanmedian(data)

                        zonal_results.append(result)

                    except Exception as e:
                        # Feature may not overlap raster — store NaN
                        zonal_results.append(np.nan)
                        fail_count += 1

                print(f"Processed {len(zonal_results)} features | {fail_count} failed (stored as NaN)")

        except Exception as e:
            print(f"Problem opening raster: {e}")
            return False

        # Write results back to the GeoDataFrame as a new column
        try:
            self.gdf[output_field] = zonal_results
            print(f"Zonal stat '{statistic_type}' written to column '{output_field}'.")
            print(f"Sample results:\n{self.gdf[[output_field]].head()}")
        except Exception as e:
            print(f"Problem writing results to GeoDataFrame: {e}")
            return False

        return okay


    def extract_to_dataframe(self, fields=None):
        """
        Extract attribute table to a pandas DataFrame.

        Parameters:
        - fields: list of column names to extract (default: all non-geometry columns)
        """
        okay = True

        # Get all non-geometry columns
        available_fields = [c for c in self.gdf.columns if c != "geometry"]

        if fields is None:
            fields = available_fields
        else:
            # Check user-supplied fields are valid
            disallowed = [f for f in fields if f not in available_fields]
            if disallowed:
                print(f"These fields are not valid for this table: {disallowed}")
                return False, None

        try:
            df = self.gdf[fields].copy()
            print(f"Extracted {len(df)} rows and {len(fields)} fields.")
            return okay, df
        except Exception as e:
            print(f"Problem extracting to DataFrame: {e}")
            return False, None


    def save_as(self, output_path):
        """Save the current GeoDataFrame to a new shapefile."""
        try:
            self.gdf.to_file(output_path)
            print(f"Saved to {output_path}")
            return True
        except Exception as e:
            print(f"Problem saving shapefile: {e}")
            return False
        
    #Block 3 addition    
    # Use matplotlib to map NDVI by parcels
    def map_ndvi(self, ndvi_field="NDVI_mean", output_path="NDVI_map.png"):
        """
        Maps parcels colored by average NDVI value.
        
        Parameters:
        - ndvi_field: name of the column containing NDVI values
        - output_path: path to save the map
        """
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors

        # Pull the GeoDataFrame
        gdf = self.gdf.copy()

        # Check field exists
        if ndvi_field not in gdf.columns:
            print(f"Field '{ndvi_field}' not found. Run zonal_stats_to_field first.")
            return False

        # Drop rows with no NDVI value for cleaner mapping
        gdf_valid = gdf[gdf[ndvi_field].notna()]
        print(f"Mapping {len(gdf_valid)} of {len(gdf)} features with valid NDVI values.")

        # Set up the plot
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Plot parcels with no NDVI data in gray as background
        gdf[gdf[ndvi_field].isna()].plot(
            ax=ax,
            color="lightgray",
            edgecolor="none",
            label="No Data"
        )

        # Plot valid parcels colored by NDVI value
        gdf_valid.plot(
            column=ndvi_field,
            ax=ax,
            cmap="RdYlGn",
            edgecolor="none",
            legend=False,
            vmin=gdf_valid[ndvi_field].quantile(0.05),
            vmax=gdf_valid[ndvi_field].quantile(0.95)
        )

        # Add a colorbar
        sm = plt.cm.ScalarMappable(
            cmap="RdYlGn",
            norm=mcolors.Normalize(
                vmin=gdf_valid[ndvi_field].quantile(0.05),
                vmax=gdf_valid[ndvi_field].quantile(0.95)
            )
        )
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
        cbar.set_label("Mean NDVI", fontsize=12)

        # Labels and formatting
        ax.set_title("Mean NDVI by Parcel\nBenton County, Oregon", fontsize=16, fontweight="bold")
        ax.set_xlabel("Longitude", fontsize=10)
        ax.set_ylabel("Latitude", fontsize=10)
        ax.tick_params(labelsize=8)

        # Add basic stats as a text box
        stats_text = (
            f"n = {len(gdf_valid):,} parcels\n"
            f"Mean NDVI: {gdf_valid[ndvi_field].mean():.3f}\n"
            f"Min NDVI:  {gdf_valid[ndvi_field].min():.3f}\n"
            f"Max NDVI:  {gdf_valid[ndvi_field].max():.3f}"
        )
        ax.text(
            0.02, 0.02, stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
        )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.show()
        print(f"Map saved to {output_path}")
        return True