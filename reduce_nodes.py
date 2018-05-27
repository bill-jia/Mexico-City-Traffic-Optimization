import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mapsplotlib import mapsplot as mplt
from utils import *
from graph_tool.all import *
from itertools import chain

# f = open("googlemapskey.txt")
# apikey = f.readline()[0:-1]
# mplt.register_api_key(apikey)
g = Graph()
coords = g.new_vertex_property("object")
g.vp.coords = coords
intersections = {}
near_existing_vertex = 0

def add_vertex(g, point, intersections):
	v_ref = find_vertex(g, g.vp.coords, [point])
	if len(v_ref) == 0:
		v_new = g.add_vertex()
		g.vp.coords[v_new] = [point]
		intersections[v_new] = 0
		return (v_new, 0)
	else:
		intersections[v_ref[0]] = intersections[v_ref[0]] + 1
		return(v_ref[0], 1)

# def set_new_vertices(unique_vertices, edge_properties, intersections):
# 	edges, start_points, end_points = edge_properties
# 	for v_list in unique_vertices:
# 		if len(v_list) > 1
#
def average_coords(coords_list):
	xs = []
	ys = []
	for coords in coords_list:
		xs.append(coords[0])
		ys.append(coords[1])
	return ([(np.mean(xs), np.mean(ys))], len(coords_list)-1)

def set_new_coords(g, intersections):
	vertex_list = g.get_vertices()
	total_new_intersections_made = 0
	for v in vertex_list:
		g.vp.coords[v], new_intersections_made = average_coords(g.vp.coords[v])
		total_new_intersections_made = total_new_intersections_made + new_intersections_made
	return total_new_intersections_made

def merge_vertices(g, intersections):
	vertex_list = g.get_vertices()
	removed_vertex_list = set()
	for v1 in vertex_list:
		v1coords_pool = g.vp.coords[v1]
		min_dist = 9999
		v1new = None
		for v2 in vertex_list:
			if v2!=v1 and v2 not in removed_vertex_list:
				v2coords_pool = g.vp.coords[v2]
				for v1coords in v1coords_pool:
					for v2coords in v2coords_pool:
						d = dist(v1coords, v2coords)
						if d < min_dist:
							min_dist = d
							v1new = v2
		if min_dist < 100:
			# print(v1)
			# print(v1new)
			old_out_edges = g.get_out_edges(v1)
			for old_out_edge in old_out_edges:
				oe = g.edge(old_out_edge[0], old_out_edge[1])
				g.add_edge(v1new, oe.target())
				g.remove_edge(oe)
			old_in_edges = g.get_in_edges(v1)
			for old_in_edge in old_in_edges:
				oe = g.edge(old_in_edge[0], old_in_edge[1])
				g.add_edge(oe.source(), v1new)
				g.remove_edge(oe)
			g.vp.coords[v1new].extend(g.vp.coords[v1])
			intersections[v1new] = intersections[v1new] + intersections[v1]
			intersections.pop(v1, None)
			removed_vertex_list |= set([v1])
	g.remove_vertex(removed_vertex_list)
	g.shrink_to_fit()
	return set_new_coords(g, intersections)

def depth_first_traversal(g, vertex, visited):
	if vertex is not None:
		graph = [vertex]
		graph_size = 1
		neighbours = chain(vertex.out_neighbors(), vertex.in_neighbors())
		for vertex_neighbour in neighbours:
			if vertex_neighbour not in visited:
				visited.append(vertex_neighbour)
				subgraph_size, subgraph = depth_first_traversal(g, vertex_neighbour, visited)
				graph.extend(subgraph)
				graph_size = graph_size + subgraph_size
		return graph_size, graph
	else:
		return 0, []



def select_largest_subgraph(g):
	explored_vertices = []
	vertices_to_remove = []
	#vertex and associated subgraph size
	max_subgraph_size = 0
	max_subgraph_list = []
	vertices = g.get_vertices()
	for vertex in vertices:
		if vertex in explored_vertices:
			continue
		explored_vertices.append(vertex)
		subgraph_size, subgraph = depth_first_traversal(g, g.vertex(vertex), explored_vertices)
		if subgraph_size > max_subgraph_size:
			vertices_to_remove.extend(max_subgraph_list)
			max_subgraph_list = subgraph
			max_subgraph_size = subgraph_size
		else:
			vertices_to_remove.extend(subgraph)
	for vertex in vertices_to_remove:
		g.clear_vertex(vertex)
	g.remove_vertex(vertices_to_remove)


data = prep_data(pd.read_csv("2018-05-24T04.59.44.000.in", sep="\t", index_col=False, encoding="ISO-8859-1"))

print(len(data))
for entry in data:
	start_point, is_near = add_vertex(g, entry["start_point"], intersections)
	near_existing_vertex = near_existing_vertex + is_near
	end_point, is_near = add_vertex(g, entry["end_point"], intersections)
	near_existing_vertex = near_existing_vertex + is_near
	g.add_edge(start_point, end_point)
near_existing_vertex = near_existing_vertex + merge_vertices(g, intersections)



print("Number of unique vertices: " + str(len(g.get_vertices())))
print("Number determined by colocalization: " + str(near_existing_vertex))

#min_distance_to_nearest_node = calculate_min_dists(unique_vertices)
#print(intersections.values())
fig1 = plt.figure()
ax1 = fig1.add_subplot(1,1,1)
ax1.hist(list(intersections.values()))
dct = {'latitude': [], 'longitude': []}

print(g.num_edges())
select_largest_subgraph(g)
print(g.num_edges())

fig2 = plt.figure()
ax2 = fig2.add_subplot(1,1,1)
for edge in g.edges():
	start = g.vp.coords[edge.source()][0]
	end = g.vp.coords[edge.target()][0]
	ax2.plot([start[0], end[0]], [start[1], end[1]], 'bo', markersize=6)
	if np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) > 0:
		ax2.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1], width=10, head_width = 100, length_includes_head=True)


plt.show(block=True)