from utils import *
from TrafficGraph import TrafficGraph
from graph_tool.all import *

D_CRIT = 0.09*1000
V_FF = 40
MAX_LANES = 6

def calculate_flows(g):
	for e in g.edges():
		# Parabolic jam density based on Tadaki et al.
		Uf = g.freeflow_speed[e]
		Us = g.actual_speed[e]
		Dj = D_CRIT * V_FF/Uf * 2 * (MAX_LANES - g.functional_class[e])
		g.max_flow[e] = Dj*Uf/4
		g.actual_flow[e] = Dj*Us - Dj/Uf * Us**2

def check_flow_violations(g):
	violators = g.new_vertex_property("bool")
	for v in g.vertices():
		violators[v] = False
	g.set_edge_filter(g.is_master_edge, inverted=True)
	g.set_vertex_filter(g.is_master_node, inverted=True)
	number_of_vertices = len(g.get_vertices())
	number_of_violators = 0
	max_delta = 0
	for v in g.vertices():
		if v.in_degree() == 0 or v.out_degree() == 0:
			continue
		in_edges = g.get_in_edges(v)
		out_edges = g.get_out_edges(v)
		total_inflow = 0
		total_outflow = 0
		for ie in in_edges:
			total_inflow = total_inflow + g.actual_flow[ie]
		for oe in out_edges:
			total_outflow = total_outflow + g.actual_flow[oe]
		if total_outflow > total_inflow:
			violators[v] = True
			number_of_violators = number_of_violators + 1
			if total_outflow - total_inflow > max_delta:
				max_delta = total_outflow - total_inflow
		else:
			violators[v] = False
	print("%d violators out of %d vertices" %(number_of_violators,number_of_vertices))
	print(max_delta)
	g.set_edge_filter(None)
	g.set_vertex_filter(None)	
	return violators


def get_source_vertices(g):
	source_vertices = []
	for vertex in g.vertices():
		if vertex.in_degree() == 0 or (vertex.in_degree() == 1 and g.is_master_source[g.get_in_neighbors(vertex)[0]] == True):
			source_vertices.append(vertex)
			g.is_source[vertex] = True
	return source_vertices

def master_source(g, SOURCE_MAX_FLOW):
	master_sources = find_vertex(g, g.is_master_source, True)
	if len(master_sources) == 0:
		master_source = g.add_vertex()
		g.is_master_source[master_source] = True
		g.coordinates[master_source] = [0,0]
		source_vertices = get_source_vertices(g)
		for source_vertex in source_vertices:
			e = g.add_edge(master_source, source_vertex)
			g.is_master_edge[e] = True
			g.freeflow_speed[e] = SOURCE_MAX_FLOW
			g.actual_speed[e] = g.freeflow_speed[e]/2
			g.functional_class[e] = 1
	else:
		master_source = master_sources[0]
	return master_source

def master_sink(g, master_source, SINK_MAX_FLOW):
	master_sinks = find_vertex(g, g.is_master_sink, True)
	if len(master_sinks) == 0:
		master_sink = g.add_vertex()
		g.coordinates[master_sink] = [0,0]
		g.is_master_sink[master_sink] = True
		for vertex in g.vertices():
			if int(vertex) != int(master_sink) and int(vertex) != int(master_source):
				# For now represent the leakage as a sink at every node with max flow 10km/hr
				e = g.add_edge(vertex, master_sink)
				g.freeflow_speed[e] = SINK_MAX_FLOW
				g.actual_speed[e] = g.freeflow_speed[e]/2
				g.is_master_edge[e] = True
				g.functional_class[e] = 4
	else:
		master_sink = master_sinks[0]
	return master_sink

def draw_max_flow(g, max_flow):
	outputstring = "graphs/"+ g.filename + "_max.png"
	print(outputstring)
	graph_draw(g, pos=g.coordinates, vertex_color = g.is_source, edge_pen_width=prop_to_size(max_flow, mi=5, ma=50, power=0.5), output_size = (4000,4000), output=outputstring)

def draw_actual_flow(g):
	graph_draw(g, pos=g.coordinates, vertex_color = g.is_source, edge_pen_width=prop_to_size(g.actual_flow, mi=5, ma=50, power=0.5), output_size = (4000,4000), output="graphs/"+ g.filename + "_actual.png")