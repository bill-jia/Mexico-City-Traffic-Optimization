import pandas as pd
from graph_tool.all import *

class TrafficGraph(Graph):
	def __init__(self, filepath):
		data = pd.read_csv(filepath, sep="\t", index_col=False, encoding="ISO-8859-1")
		Graph.__init__(self)



		self.coordinates = self.new_vertex_property("string")
		self.path = self.new_edge_property("string")
		self.functional_class = self.new_edge_property("int")
		self.length = self.new_edge_property("float")
		self.freeflow_speed = self.new_edge_property("float")
		self.actual_speed = self.new_edge_property("float")
		self.jam_factor = self.new_edge_property("float")


		self.vertex_ids = {}

		for idx, row in data.iterrows():
			v1 = find_vertex(self, self.coordinates, row["start_point"])
			v2 = find_vertex(self, self.coordinates, row["end_point"])
			if len(v1) == 0:
				v1 = self.add_vertex()
				self.coordinates[v1] = row["start_point"]
				self.vertex_ids[row["start_point"]] = v1
			else:
				v1 = v1[0]
			if len(v2) == 0:
				v2 = self.add_vertex()
				self.coordinates[v2] = row["end_point"]
				self.vertex_ids[row["end_point"]] = v2
			else:
				v2 = v2[0]
			e = self.add_edge(v1, v2)
			self.path[e] = row["path"]
			self.functional_class[e] = row["functional_class"]
			self.length[e] = row["length"]
			self.freeflow_speed[e] = row["freeflow_speed"]
			self.actual_speed[e] = row["actual_speed"]
			self.jam_factor[e] = row["jam_factor"]