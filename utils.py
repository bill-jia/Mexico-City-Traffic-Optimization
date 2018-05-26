import numpy as np
import pandas as pd


def string_to_latlon(input):
	spl = input.split(",")
	return (float(spl[0]), float(spl[1]))

def latlon_to_coords(lat, lon):
	lat0 = 19.4308
	lon0 = -99.1597
	R=6371000
	x = R*(lat-lat0)
	y = R*(lon-lon0)*np.cos((lat+lat0)/2)
	return (x,y)

def string_to_coords(input):
	(lat, lon) = string_to_latlon(input)
	return latlon_to_coords()

def path_to_coords(input):
	splt = input.split(" ")
	output = []
	for dat in splt[1:]:
		output.append(string_to_coords(dat))
	return output

def prep_data(df):
	df["start_point"].apply(string_to_coords)
	df["end_point"].apply(string_to_coords)
	df["path"].apply(path_to_coords)