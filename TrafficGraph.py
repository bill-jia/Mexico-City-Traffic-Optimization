import pandas as pd
from graph_tool.all import *
from utils import *
from itertools import chain

class TrafficGraph(Graph):
	def __init__(self, filepath):
		data = pd.read_csv(filepath, sep="\t", index_col=False, encoding="ISO-8859-1")
		data = prep_data(data)
		Graph.__init__(self)


		self.temp_coords = self.new_vertex_property("object")
		self.coordinates = self.new_vertex_property("vector<float>")
		self.is_master_node = self.new_vertex_property("bool")
		self.is_source = self.new_vertex_property("bool")

		self.path = self.new_edge_property("string")
		self.functional_class = self.new_edge_property("int")
		self.length = self.new_edge_property("float")
		self.freeflow_speed = self.new_edge_property("float")
		self.actual_speed = self.new_edge_property("float")
		self.jam_factor = self.new_edge_property("float")
		self.is_master_edge = self.new_edge_property("bool")


		# self.vertex_ids = {}

		for row in data:
			start_point = self.__entry_to_vertex(row["start_point"])
			end_point = self.__entry_to_vertex(row["end_point"])
			if int(start_point) != int(end_point):
				e = self.add_edge(start_point, end_point)
				self.is_master_edge[e] = False
			self.path[e] = row["path"]
			self.functional_class[e] = row["functional_class"]
			self.length[e] = row["length"]
			self.freeflow_speed[e] = row["freeflow_speed"]
			self.actual_speed[e] = min(row["actual_speed"], row["freeflow_speed"])
			self.jam_factor[e] = row["jam_factor"]
		self.__merge_vertices()
		self.__select_largest_subgraph()

	def __entry_to_vertex(self, point):
		v_ref = find_vertex(self, self.temp_coords, [point])
		if len(v_ref) == 0:
			v_new = self.add_vertex()
			self.is_master_node[v_new] = False
			self.is_source[v_new] = False
			self.temp_coords[v_new] = [point]
			return v_new
		else:
			return v_ref[0]

	def __average_coords(self, coords_list):
		xs = []
		ys = []
		for coords in coords_list:
			xs.append(coords[0])
			ys.append(coords[1])
		return [np.mean(xs), np.mean(ys)]

	def __set_new_coords(self):
		vertex_list = self.get_vertices()
		for v in vertex_list:
			self.coordinates[v] = self.__average_coords(self.temp_coords[v])

	def __merge_vertices(self):
		vertex_list = self.get_vertices()
		removed_vertex_list = set()
		self_loop_count = 0
		for v1 in vertex_list:
			v1coords_pool = self.temp_coords[v1]
			min_dist = 9999
			v1new = None
			for v2 in vertex_list:
				if v2!=v1 and v2 not in removed_vertex_list and self.edge(v1, v2) is None and self.edge(v2, v1) is None:
					v2coords_pool = self.temp_coords[v2]
					for v1coords in v1coords_pool:
						for v2coords in v2coords_pool:
							# print(v1coords)
							# print(v2coords)
							d = dist(v1coords, v2coords)
							if d < min_dist:
								min_dist = d
								v1new = v2
			if min_dist < 100:
				# print(v1)
				# print(v1new)
				old_out_edges = self.get_out_edges(v1)
				for old_out_edge in old_out_edges:
					oe = self.edge(old_out_edge[0], old_out_edge[1])
					ne = self.add_edge(v1new, oe.target())
					self.is_master_edge[ne] = False
					self.remove_edge(oe)
				old_in_edges = self.get_in_edges(v1)
				for old_in_edge in old_in_edges:
					oe = self.edge(old_in_edge[0], old_in_edge[1])
					ne = self.add_edge(oe.source(), v1new)
					self.is_master_edge[ne] = False
					self.remove_edge(oe)
				self.temp_coords[v1new].extend(self.temp_coords[v1])
				removed_vertex_list |= set([v1])
		self.remove_vertex(removed_vertex_list)
		self.shrink_to_fit()
		self.__set_new_coords()

	def __depth_first_traversal(self, vertex, visited):
		if vertex is not None:
			graph = [vertex]
			graph_size = 1
			neighbours = vertex.all_neighbors()
			for vertex_neighbour in neighbours:
				if vertex_neighbour not in visited:
					visited.append(vertex_neighbour)
					subgraph_size, subgraph = self.__depth_first_traversal(vertex_neighbour, visited)
					graph.extend(subgraph)
					graph_size = graph_size + subgraph_size
			return graph_size, graph
		else:
			return 0, []

	def __select_largest_subgraph(self):
		explored_vertices = []
		vertices_to_remove = []
		#vertex and associated subgraph size
		max_subgraph_size = 0
		max_subgraph_list = []
		vertices = self.get_vertices()
		for vertex in vertices:
			if vertex in explored_vertices:
				continue
			explored_vertices.append(vertex)
			subgraph_size, subgraph = self.__depth_first_traversal(self.vertex(vertex), explored_vertices)
			if subgraph_size > max_subgraph_size:
				vertices_to_remove.extend(max_subgraph_list)
				max_subgraph_list = subgraph
				max_subgraph_size = subgraph_size
			else:
				vertices_to_remove.extend(subgraph)
		for vertex in vertices_to_remove:
			self.clear_vertex(vertex)
		self.remove_vertex(vertices_to_remove)