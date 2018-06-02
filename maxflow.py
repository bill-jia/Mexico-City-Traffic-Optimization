from utils import *
from TrafficGraph import TrafficGraph
from graph_tool.all import *

def get_source_vertices(g):
	source_vertices = []
	for vertex in g.vertices():
		if vertex.in_degree() == 0:
			source_vertices.append(vertex)
			g.is_source[vertex] = True
	return source_vertices

def master_source(g):
	master_source = g.add_vertex()
	g.is_master_node[master_source] = True
	g.coordinates[master_source] = [0,0]
	source_vertices = get_source_vertices(g)
	for source_vertex in source_vertices:
		e = g.add_edge(master_source, source_vertex)
		g.is_master_edge[e] = True
		g.freeflow_speed[e] = 9999
	return master_source

def master_sink(g, master_source):
	master_sink = g.add_vertex()
	g.coordinates[master_sink] = [0,0]
	g.is_master_node[master_sink] = True
	for vertex in g.vertices():
		if int(vertex) != int(master_sink) and int(vertex) != int(master_source):
			# For now represent the leakage as a sink at every node with max flow 0.1km/hr
			e = g.add_edge(vertex, master_sink)
			g.freeflow_speed[e] = 0.1
			g.is_master_edge[e] = True
	return master_sink



g = TrafficGraph("2018-05-23T23.59.44.000.in")
master_source = master_source(g)
master_sink = master_sink(g, master_source)
res = edmonds_karp_max_flow(g, master_source, master_sink, g.freeflow_speed)
res.a = g.freeflow_speed.a - res.a
g.set_edge_filter(g.is_master_edge, inverted=True)
g.set_vertex_filter(g.is_master_node, inverted=True)
graph_draw(g, pos=g.coordinates, vertex_color = g.is_source, edge_pen_width=prop_to_size(res, mi=5, ma=50, power=0.5), output_size = (4000,4000), output="max_flow.png")
graph_draw(g, pos=g.coordinates, vertex_color = g.is_source, edge_pen_width=prop_to_size(g.actual_speed, mi=5, ma=50, power=0.5), output_size = (4000,4000), output="actual_flow.png")

# fig = plt.figure()
# ax2 = fig.add_subplot(1,1,1)
# for edge in g.edges():
# 	start = g.coordinates[edge.source()]
# 	end = g.coordinates[edge.target()]
# 	ax2.plot([start[0], end[0]], [start[1], end[1]], 'bo', markersize=6)
# 	if np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) > 0:
# 		ax2.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1], width=10, head_width = 100, length_includes_head=True)
# source_vertices = get_source_vertices(g)
# for vertex in source_vertices:
# 	coords = g.coordinates[vertex]
# 	ax2.plot(coords[0], coords[1], 'ro', markersize=6)


# plt.show(block=True)