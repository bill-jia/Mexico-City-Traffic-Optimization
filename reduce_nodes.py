import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mapsplotlib import mapsplot as mplt

R = 6371e3
print(R)
f = open("googlemapskey.txt")
apikey = f.readline()[0:-1]
mplt.register_api_key(apikey)

def haversine_distance(coord1, coord2):
	lat1,long1 = coord1
	lat2,long2 = coord2
	lat1R = np.radians(lat1)
	lat2R = np.radians(lat2)
	dLong = np.radians(long2-long1)
	dLat = np.radians(lat2-lat1)
	
	a = np.sin(dLat/2)**2 + np.cos(lat1R)*np.cos(lat2R)*np.sin(dLong/2)**2
	c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
	d = R*c
	return abs(d)

unique_vertices = set()
intersections = {}
near_existing_vertex = 0


# def get_path_vertices(path):
# 	add_vertex(path[0])
# 	add_vertex(path[-1])
# 	get_path_intersections()

def add_vertex(point, unique_vertices, intersections):
	min_dist = 9999
	for ref_pt in unique_vertices:
		if ref_pt == point:
			intersections[ref_pt] = intersections[ref_pt] + 1
			return 0
		elif haversine_distance(ref_pt, point) < 50:
			intersections[ref_pt] = intersections[ref_pt] + 1
			return 1
	unique_vertices |= set([point])
	intersections[point] = 0
	return 0

def calculate_min_dists(vertex_set):
	min_dists = []
	for v1 in vertex_set:
		min_dist = 9999
		for v2 in vertex_set - set([v1]):
			dist = haversine_distance(v1,v2)
			if dist < min_dist:
				min_dist = dist
		min_dists.append(min_dist)
	return min_dists
data = pd.read_csv("2018-05-24T04.59.44.000.in", sep="\t", index_col=False, encoding="ISO-8859-1")

for idx, row in data.iterrows():
	start_point = string_to_coordinate_pair(row["start_point"])
	end_point = string_to_coordinate_pair(row["end_point"])
	near_existing_vertex = near_existing_vertex + add_vertex(start_point, unique_vertices, intersections)
	near_existing_vertex = near_existing_vertex + add_vertex(end_point, unique_vertices, intersections)

print("Number of unique vertices: " + str(len(unique_vertices)))
print("Number determined by colocalization: " + str(near_existing_vertex))

#min_distance_to_nearest_node = calculate_min_dists(unique_vertices)
#print(intersections.values())
fig1 = plt.figure()
ax1 = fig1.add_subplot(1,1,1)
ax1.hist(list(intersections.values()))
dct = {'latitude': [], 'longitude': []}
for point in unique_vertices:
	dct['latitude'].append(point[0])
	dct['longitude'].append(point[1])
df = pd.DataFrame(data=dct)
mplt.density_plot(df['latitude'], df['longitude'])
plt.show(block=True)