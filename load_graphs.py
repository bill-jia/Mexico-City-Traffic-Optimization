import pandas as pd
#from graph_tool.all import *

data = pd.read_csv("2018-05-17T20.18.23.000.txt", sep="\t", index_col=False, encoding="ISO-8859-1")
g = Graph()

coordinates = g.new_vertex_property("string")
path = g.new_edge_property("string")
functional_class = g.new_edge_property("int")
length = g.new_edge_property("float")
freeflow_speed = g.new_edge_property("float")
actual_speed = g.new_edge_property("float")
jam_factor = g.new_edge_property("float")


vertex_ids = {}

for idx, row in data.iterrows():
	v1 = graph_tool.utils.find_vertex(g, coordinates, row["start_point"])
	v2 = graph_tool.utils.find_vertex(g, coordinates, row["end_point"])
	if v1 is None:
		v1 = g.add_vertex()
		coordinates[v1] = row["start_point"]
	if v2 is None:
		v2 = g.add_vertex()
		coordinates[v2] = row["end_point"]
	e = g.add_edge(v1, v2)
	path[e] = row["path"]
	functional_class[e] = row["functional_class"]
	length[e] = row["length"]
	freeflow_speed = row["freeflow_speed"]
	actual_speed = row["actual_speed"]
	jam_factor = row["jam_factor"]