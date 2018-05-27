import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
		start = g.coordinates[edge.source()][0]
		end = g.coordinates[edge.target()][0]
		ax2.plot([start[0], end[0]], [start[1], end[1]], 'bo', markersize=6)
		if np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) > 0:
			ax2.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1], width=10, head_width = 100, length_includes_head=True)


	plt.show(block=True)