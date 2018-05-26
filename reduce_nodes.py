import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mapsplotlib import mapsplot as mplt
from utils import *

f = open("googlemapskey.txt")
apikey = f.readline()[0:-1]
mplt.register_api_key(apikey)

unique_vertices = set()
intersections = {}
near_existing_vertex = 0
edges = []


# def get_path_vertices(path):
# 	add_vertex(path[0])
# 	add_vertex(path[-1])
# 	get_path_intersections()

def add_vertex(point, unique_vertices, intersections):
	min_dist = 9999
	nearest_vertex = None
	for ref_pt in unique_vertices:
		d = dist(ref_pt, point)
		if ref_pt == point:
			intersections[ref_pt] = intersections[ref_pt] + 1
			return (ref_pt, 1)
		elif d < min_dist:
			min_dist = d
			nearest_vertex = ref_pt
	if min_dist < 100:
		intersections[nearest_vertex] = intersections[nearest_vertex] + 1
		return (nearest_vertex, 1)
	unique_vertices |= set([point])
	intersections[point] = 0
	return (point, 0)

def calculate_min_dists(vertex_set):
	min_dists = []
	for v1 in vertex_set:
		min_dist = 9999
		for v2 in vertex_set - set([v1]):
			dist = dist(v1,v2)
			if dist < min_dist:
				min_dist = dist
		min_dists.append(min_dist)
	return min_dists

data = prep_data(pd.read_csv("2018-05-24T04.59.44.000.in", sep="\t", index_col=False, encoding="ISO-8859-1"))
#print(data["start_point"])
print(len(data))
for entry in data:
	start_point, is_near = add_vertex(entry["start_point"], unique_vertices, intersections)
	near_existing_vertex = near_existing_vertex + is_near
	end_point, is_near = add_vertex(entry["end_point"], unique_vertices, intersections)
	near_existing_vertex = near_existing_vertex + is_near
	edges.append((start_point, end_point))


print("Number of unique vertices: " + str(len(unique_vertices)))
print("Number determined by colocalization: " + str(near_existing_vertex))

#min_distance_to_nearest_node = calculate_min_dists(unique_vertices)
#print(intersections.values())
fig1 = plt.figure()
ax1 = fig1.add_subplot(1,1,1)
ax1.hist(list(intersections.values()))
dct = {'latitude': [], 'longitude': []}
fig2 = plt.figure()
ax2 = fig2.add_subplot(1,1,1)
for edge in edges:
	ax2.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'ro-')
plt.show(block=True)