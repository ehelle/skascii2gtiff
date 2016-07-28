#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     Statenskartverk ascii (href) -> GeoTiff
#
# Author:      ehelle
#
# Created:     27.01.2015
# Copyright:   (c) ehelle 2015
# Licence:     MIT
#-------------------------------------------------------------------------------

import numpy as np
import gdal, osr
import re
import argparse

def skascii2gtiff(infile, outfile):
    with open(infile) as ascii:
        head = ascii.next()
        header = map(float, re.findall(r"\d+[.]\d+", head))
        lat_min, lat_max, lon_min, lon_max, delta_lat, delta_lon = header
        lon_c = int((lon_max - lon_min) / delta_lon + 1)
        lat_c = int((lat_max - lat_min) / delta_lat + 1)
        zdata = []
        for line in ascii:
            nums = map(float, re.findall(r"\d+[.]\d+", line))
            for num in nums:
                zdata.append(num)
    array = np.zeros([lat_c,lon_c])
    for z in range(len(zdata)):
        array[z / lon_c, z % lon_c] = zdata[z]
    
    # array 2 raster
    driver = gdal.GetDriverByName('GTiff')
    outraster = driver.Create(outfile, lon_c, lat_c, 1, gdal.GDT_Float32)
    outraster.SetGeoTransform((lon_min-(delta_lon/2), delta_lon, 0, lat_min-(delta_lat/2), 0, delta_lat))
    outband = outraster.GetRasterBand(1)
    outband.WriteArray(array[::-1])
    outband.SetNoDataValue(9999)
    outrasterSRS = osr.SpatialReference()
    outrasterSRS.ImportFromEPSG(4326)
    outraster.SetProjection(outrasterSRS.ExportToWkt())
    outband.FlushCache
    outraster = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Statens Kartverk href .ascii file \n~ C:\mypath\myfile.ascii")
    parser.add_argument("outfile", help="Outfile (tif) \n~ C:\mypath\myfile.tif")
    args = parser.parse_args()
    skascii2gtiff(args.infile, args.outfile)
    
    
if __name__ == '__main__':
    main()
