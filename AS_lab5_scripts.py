# Lab 5 scripts

import AS_lab5_functions as l5

#  Part 1:

#  Assign a variable to the Landsat file 
# Pass this to your new smart raster class
landsat_file = l5.SmartRaster(r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS\landsat_image_corv.tif")
import AS_lab5_functions as l5


# Calculate NDVI and save to and output file
ok, ndvi_array = landsat_file.calculate_ndvi("NDVI_corv.tif")

out_ndvi_file = "NDVI_corv.tif"
# The function itself handles the save, this is error handling + existence check
if os.path.exists(out_ndvi_file):
    print(f"{out_ndvi_file} already exists. Skipping save.")
else:
    ok, ndvi_array = landsat_file.calculate_ndvi(out_ndvi_file)
    if ok:
        print(f"{out_ndvi_file} written successfully.")
    else:
        print("NDVI calculation failed.")

print(f"ok: {ok}, ndvi type: {type(ndvi_array)}")




# Part 2:
import importlib
import sys
importlib.reload(l5)

# Remove the broken cached import if it exists
if 'AS_lab5_functions' in sys.modules:
    del sys.modules['AS_lab5_functions']

# Re-import from scratch
import AS_lab5_functions as l5

# Assign a variable to the parcels data shapefile path
parcels_file = r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS\Benton_County_TaxLots.shp"

#  Pass this to your new smart vector class

smart_vector = l5.SmartVectorLayer(parcels_file)

#  Calculate zonal statistics and add to the attribute table of the parcels shapefile
# Calculate zonal statistics and add to the attribute table of the parcels shapefile
ok = smart_vector.zonal_stats_to_field(
    r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS\NDVI_corv.tif",
    statistic_type="mean",
    output_field="NDVI_mean"
)

if ok:
    print("Zonal stats calculated successfully.")
    smart_vector.save_as(r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS\Benton_parcels_plusNDVI.shp")
else:
    print("Zonal stats calculation failed.")


#  Part 3: Optional
#  Use matplotlib to make a map of your census tracts with the average NDVI values
importlib.reload(l5)

ok = smart_vector.map_ndvi(
    ndvi_field="NDVI_mean",
    output_path=r"R:\2026\Spring\GEOG562\Students\shinzaas\Lab5_AS\NDVI_map.png"
)
if ok:
    print("Map created successfully.")
else:
    print("Mapping failed.")






