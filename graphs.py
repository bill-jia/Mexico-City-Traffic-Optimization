class Graph:
	def __init__(self, data):
		self.vertices = {}
		self.edges = {}
		for dataRow in data:
			self.addEdge(dataRow)

	def addEdge(self, dataRow):
		if dataRow["start_point"] not in self.vertices:
			self.vertices[dataRow["start_point"]] = ([], [])

		if dataRow["end_point"] not in self.vertices:
			self.vertices[dataRow["end_point"]] = []

		newEdge = Edge(dataRow["start_point"], dataRow["end_point"], dataRow["length"], dataRow["freeflow_speed"], dataRow["queuing_direction"])

		self.edges |= newEdge
		self.vertices[dataRow["start_point"]][0].append(newEdge)
		self.vertices[dataRow["end_point"]][1].append(newEdge)


class Edge:
	def __init__(self, v1, v2, length, capacity, queuing_direction):
		self.v1 = v1
		self.v2 = v2
		self.length = length
		self.capacity = capacity
		# What to do with queuing direction?