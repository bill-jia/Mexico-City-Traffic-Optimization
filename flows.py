from utils import *
from TrafficGraph import TrafficGraph
from graph_tool.all import *

D_CRIT = 0.09*1000
V_FF = 40
MAX_LANES = 6
SINK_MAX_FLOW = 10

# Parabolic jam density based on Tadaki et al.
def fundamental_traffic_eqn(Uf, Us, functional_class):
	if Uf > 0:
		Dj = D_CRIT * V_FF/Uf * 2 * (MAX_LANES - functional_class)
		max_flow = Dj*Uf/4
		actual_flow = Dj*Us - Dj/Uf * Us**2
	else:
		max_flow = actual_flow = 0
	return max_flow, actual_flow

def calculate_flows(g):
	# g.set_edge_filter(g.is_master_edge, inverted=True)
	for e in g.edges():
		g.max_flow[e], g.actual_flow[e] = fundamental_traffic_eqn(g.freeflow_speed[e], g.actual_speed[e], g.functional_class[e])
	# g.set_edge_filter(None)

def vertex_violates_flow_conservation(g, v):
	# g.set_edge_filter(g.is_master_edge, inverted=True)
	if v.in_degree() == 0 or v.out_degree() == 0:
		return (0, 0,0)
	in_edges = g.get_in_edges(v)
	out_edges = g.get_out_edges(v)
	total_inflow = 0
	total_outflow = 0
	delta = 0
	for ie in in_edges:
		total_inflow = total_inflow + g.actual_flow[ie]
	for oe in out_edges:
		total_outflow = total_outflow + g.actual_flow[oe]
	if total_outflow > total_inflow:
		delta = total_outflow - total_inflow
	else:
		delta = 0
	# g.set_edge_filter(None)
	return (delta, total_inflow, total_outflow)

def check_flow_violations(g):
	violators = g.new_vertex_property("bool")
	for v in g.vertices():
		violators[v] = False
	# g.set_edge_filter(g.is_master_edge, inverted=True)
	# g.set_vertex_filter(g.is_master_node, inverted=True)
	number_of_vertices = len(g.get_vertices())
	number_of_violators = 0
	max_delta = 0
	max_in = 0
	max_out = 0
	v_max = 0
	for v in g.vertices():
		delta, fin, fout = vertex_violates_flow_conservation(g, v)
		if delta > 0:
			violators[v] = True
			number_of_violators = number_of_violators + 1
			if delta > max_delta:
				max_delta = delta
				max_in = fin
				max_out = fout
				v_max = v
		else:
			violators[v] = False
	print("%d violators out of %d vertices" %(number_of_violators,number_of_vertices))
	print(max_delta)
	print(max_in)
	print(max_out)
	print(v_max.in_degree())
	print(v_max.out_degree())
	# g.set_edge_filter(None)
	# g.set_vertex_filter(None)	
	return violators


def flow_from_sources(g, flow_map):
	total_flow = 0
	for vertex in find_vertex(g, g.is_source, True):
		for edge in vertex.out_edges():
			total_flow = total_flow + flow_map[edge]
	return total_flow

def flow_from_master_source(g, flow_map):
	total_flow = 0
	for vertex in find_vertex(g, g.is_master_source, True):
		for edge in vertex.out_edges():
			total_flow = total_flow + flow_map[edge]
	return total_flow


def flow_to_sink(g, flow_map):
	total_flow = 0
	for vertex in find_vertex(g, g.is_master_sink, True):
		for edge in vertex.in_edges():
			total_flow = total_flow + flow_map[edge]
	return total_flow

def get_source_vertices(g):
	source_vertices = []
	for vertex in g.vertices():
		if (vertex.in_degree() == 0 or (vertex.in_degree() == 1 and g.is_master_source[g.get_in_neighbors(vertex)[0]] == True)) and g.is_master_source[vertex] == False:
			source_vertices.append(vertex)
			g.is_source[vertex] = True
	return source_vertices

def master_source(g, SOURCE_FLOW):
	master_sources = find_vertex(g, g.is_master_source, True)
	if len(master_sources) == 0:
		master_source = g.add_vertex()
		g.is_master_node[master_source] = True
		g.is_master_source[master_source] = True
		g.is_source[master_source] = False
		g.coordinates[master_source] = [0,0]
		# for vertex in g.vertices():
		# 	if not g.is_master_source[vertex]:
		# 		delta = vertex_violates_flow_conservation(g, vertex)
		# 		if delta > 0:
		# 			e = g.add_edge(master_source, vertex)
		# 			g.is_master_edge[e] = True
		# 			g.freeflow_speed[e] = 0
		# 			g.actual_speed[e] = 0
		# 			g.length[e] = 0
		# 			g.max_flow[e] = g.actual_flow[e] = delta
	else:
		master_source = master_sources[0]
	source_vertices = get_source_vertices(g)
	for source_vertex in source_vertices:
		e = g.edge(master_source, source_vertex) 
		if e is None: 
			e = g.add_edge(master_source, source_vertex)
			g.is_master_edge[e] = True
			g.freeflow_speed[e] = 0
			g.actual_speed[e] = 0
			g.functional_class[e] = 1
			g.length[e] = 0
			g.max_flow[e] = SOURCE_FLOW
			g.actual_flow[e] = 0
		else:
			g.freeflow_speed[e] = 0
			g.actual_speed[e] = 0
			g.functional_class[e] = 1
			g.length[e] = 0
			g.max_flow[e] = SOURCE_FLOW
			g.actual_flow[e] = 0
	return master_source

def master_sink(g, master_source, SINK_FLOW):
	master_sinks = find_vertex(g, g.is_master_sink, True)
	if len(master_sinks) == 0:
		master_sink = g.add_vertex()
		g.coordinates[master_sink] = [0,0]
		g.is_master_sink[master_sink] = True
		g.is_master_node[master_sink] = True
		g.is_source[master_sink] = False
		for vertex in g.vertices():
			if not g.is_master_node[vertex] and not g.is_source[vertex]:
				# For now represent the leakage as a sink at every node with max flow 10km/hr
				e = g.add_edge(vertex, master_sink)
				g.freeflow_speed[e] = 0
				g.actual_speed[e] = 0
				g.is_master_edge[e] = True
				g.functional_class[e] = 4
				g.length[e] = 0
				g.max_flow[e] = g.actual_flow[e] = SINK_FLOW

	else:
		master_sink = master_sinks[0]
		for e in master_sink.in_edges():
			g.freeflow_speed[e] = SINK_MAX_FLOW
			g.actual_speed[e] = SINK_FLOW
			g.is_master_edge[e] = True
			g.functional_class[e] = 4
			g.length[e] = 0
			g.max_flow[e] = g.actual_flow[e] = SINK_FLOW
	return master_sink

def set_sink_max_flow(g, vertices, SINK_FLOW):
	master_sink = find_vertex(g, g.is_master_sink, True)[0]
	for vertex in vertices:
		if not g.is_master_node[vertex] and not g.is_source[vertex]:
			e = g.edge(vertex, master_sink)
			g.max_flow[e] = SINK_FLOW

def set_sink_actual_flow(g, vertices, SINK_FLOW):
	master_sink = find_vertex(g, g.is_master_sink, True)[0]
	for vertex in vertices:
		if not g.is_master_node[vertex] and not g.is_source[vertex]:
			e = g.edge(vertex, master_sink)
			g.max_actual_flow[e] = SINK_FLOW

def draw_max_flow(g, max_flow):
	graph_draw(g, pos=g.coordinates, vertex_fill_color = g.is_source, edge_pen_width=prop_to_size(max_flow, mi=5, ma=50, power=0.5), output_size = (4000,4000), output="plots/"+ g.filename + "_max.png")

def draw_actual_flow(g):
	graph_draw(g, pos=g.coordinates, vertex_fill_color = g.is_source, edge_pen_width=prop_to_size(g.actual_flow, mi=5, ma=50, power=0.5), output_size = (4000,4000), output="plots/"+ g.filename + "_actual.png")

def apply_without_masters(func, g, *args, **kwargs):
	g.set_edge_filter(g.is_master_edge, inverted=True)
	g.set_vertex_filter(g.is_master_node, inverted=True)
	output = func(g, *args, **kwargs)
	g.set_edge_filter(None)
	g.set_vertex_filter(None)
	return output

def reconstruct_graph_from_leak(leak_graph, maxflow):
	reconst = TrafficGraph(graph=leak_graph)
	reconst.sinkage = reconst.new_vertex_property("float")
	reconst.leakage = reconst.new_edge_property("float")
	reconst.inflow = reconst.new_vertex_property("float")
	msink = find_vertex(reconst, reconst.is_master_sink, True)[0]
	intermediate_vertices = []
	for v in find_vertex(reconst, reconst.is_master_node, False):
		reconst.sinkage[v] = 0
		reconst.inflow[v] = 0
		for edge in reconst.get_out_edges(v):
			e1 = reconst.edge(edge[0], edge[1])
			e1old = leak_graph.edge(edge[0], edge[1])
			if reconst.is_master_node[e1.target()] and not reconst.is_master_sink[e1.target()]:
				v_intermediate = e1.target()
				intermediate_vertices.append(v_intermediate)
				e2 = None
				leakage = 0
				for e2s in v_intermediate.out_edges():
					if e2s.target() != msink:
						e2 = e2s
					else:
						leakage = maxflow[e2s]
				reconst.sinkage[v] += leakage
				e_reconst = reconst.add_edge(v, e2.target())
				reconst.transfer_edge_properties(e1, e_reconst)
				reconst.is_master_edge[e_reconst] = False
				reconst.max_flow[e_reconst] = maxflow[e1old]
				reconst.leakage[e_reconst] = leakage
	reconst.remove_vertex(intermediate_vertices)
	for v in find_vertex(reconst, reconst.is_master_sink, False):
		for e in v.in_edges():
			reconst.inflow[v] += reconst.max_flow[e] - reconst.leakage[e]
	return reconst

# Sink flow equation
def add_leak_nodes(g,k, use_actual = False):
	msink = find_vertex(g, g.is_master_sink, True)[0]
	for v in find_vertex(g, g.is_master_node, False):
		for edge in g.get_out_edges(v):
			e = g.edge(edge[0], edge[1])
			if e.target() != msink:
				v_intermediate = g.add_vertex()
				e1 = g.add_edge(v, v_intermediate)
				e2 = g.add_edge(v_intermediate, e.target())
				g.transfer_edge_properties(e, e1)
				g.transfer_edge_properties(e, e2)
				g.length[e2] = 0
				eleak = g.add_edge(v_intermediate, msink)
				if use_actual:
					g.max_flow[eleak] = g.length[e]*k*g.actual_flow[e]
				else:
					g.max_flow[eleak] = g.length[e]*k*g.max_flow[e]
				g.is_master_edge[e1] = g.is_master_edge[e2] = g.is_master_edge[eleak] = True
				g.is_master_node[v_intermediate] = True
				g.remove_edge(e)
			else:
				g.remove_edge(e)
			

def get_leak_graph(g, k, use_actual = False):
	leak_graph = TrafficGraph(graph=g)
	add_leak_nodes(leak_graph, k, use_actual)
	return leak_graph

def rank_property(g, prop, number, include_sources=True):
	vertices_by_prop = []
	if include_sources:
		vertices = g.vertices()
	else:
		vertices = find_vertex(g, g.is_source, False)
	for vertex in vertices:
		if not g.is_master_node[vertex]:
			vertices_by_prop.append((vertex, prop[vertex]))
	vertices_prop_sorted = sorted(vertices_by_prop, key=lambda v: v[1], reverse = True)
	top_vertices = g.new_vertex_property("bool")
	for idx, vertex in enumerate(vertices_prop_sorted):
		if idx < number:
			top_vertices[vertex[0]] = True
		else:
			top_vertices[vertex[0]] = False
	return top_vertices, vertices_prop_sorted[0:number]

def prop_as_string(g, isvertex, prop):
	if isvertex:
		newprop = g.new_vertex_property("string")
		for v in g.vertices():
			newprop[v] = "%d" %prop[v]
	else:
		newprop = g.new_edge_property("string")
		for v in g.edges():
			newprop[v] = "%d" %prop[v]
	return newprop