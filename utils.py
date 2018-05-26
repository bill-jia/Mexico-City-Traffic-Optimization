import numpy as np
import pandas as pd


def string_to_latlon(inp):
	spl = inp.split(",")
	return (float(spl[0]), float(spl[1]))

def latlon_to_coords(lat, lon):
	lat0, lon0 = 19.4308, -99.1597
	R=6371000
	x = R*(np.radians(lat-lat0))
	y = R*(np.radians(lon-lon0))*np.cos(np.radians(lat)+np.radians(lat0)/2)
	return (x,y)

def dist(pt1, pt2):
	x1, y1 = pt1
	x2, y2 = pt2
	return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def string_to_coords(inp):
	(lat, lon) = string_to_latlon(inp)
	return latlon_to_coords(lat, lon)

def path_to_coords(inp):
	splt = inp.split(" ")
	output = []
	for dat in splt[1:]:
		output.append(string_to_coords(dat))
	return output

def prep_data(df):
	data = df.to_dict('records')
	for entry in data:
		entry["start_point"] = string_to_coords((entry["start_point"]))
		entry["end_point"] = string_to_coords((entry["end_point"]))
		entry["path"] = path_to_coords((entry["path"]))
	return data