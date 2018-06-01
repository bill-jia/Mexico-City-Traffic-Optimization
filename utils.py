import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from datetime import datetime
import glob

def string_to_latlon(inp):
	spl = inp.split(",")
	return (float(spl[0]), float(spl[1]))

def latlon_to_coords(lat, lon):
	lat0, lon0 = 19.4308, -99.1597
	R=6371000
	y = R*(np.radians(lat-lat0))
	x = R*(np.radians(lon-lon0))*np.cos(np.radians(lat)+np.radians(lat0)/2)
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

def plot_graph_as_map(g):
	fig = plt.figure()
	ax2 = fig.add_subplot(1,1,1)
	for edge in g.edges():
		start = g.coordinates[edge.source()]
		end = g.coordinates[edge.target()]
		ax2.plot([start[0], end[0]], [start[1], end[1]], 'bo', markersize=6)
		if np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) > 0:
			ax2.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1], width=10, head_width = 100, length_includes_head=True)


	plt.show(block=True)

def load_data(filepath):
	data = pd.read_csv(filepath, sep="\t", index_col=False, encoding="ISO-8859-1")
	return data

def list_files(day=None, time=None):
	directories = ["Monday", "Sunday", "Thursday", "Wednesday"]
	time_index = [0, 1, 2, 3]
	if day is not None:
		directories = [day]
	if time is not None:
		time_index = [time]
	all_files = []
	for directory in directories:
		dir_list = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
		for time in time_index:
			file_list = glob.glob(os.path.join(directory, dir_list[time]) +"/*.txt")
			all_files.extend(file_list)
	return all_files

def path_to_time(file_path):
	strtime = os.path.splitext(os.path.basename(file_path))[0]
	dt = datetime.strptime(strtime, "%Y-%m-%dT%H.%M.%S.000")
	return dt

def data_category(dt):
	if dt.hour < 1 or dt.hour == 23:
		return "o1"
	elif dt.hour >=6 and dt.hour <10:
		return "r1"
	elif dt.hour >=11 and dt.hour < 13:
		return "o2"
	else:
		return r2