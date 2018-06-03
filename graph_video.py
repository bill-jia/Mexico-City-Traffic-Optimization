from TrafficGraph import TrafficGraph
from utils import *
from flows import *
from graph_tool.all import *
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import os

graphs = []
for file in list_files("Monday", 1):
	g = TrafficGraph(graphpath=graph_path(file))
	calculate_flows(g)
	graphs.append(g)

if not os.path.exists("frames"):
	os.mkdir("frames")

for i in range(60):
	g = graphs[i]
	graph_draw(g, pos=g.coordinates, vertex_fill_color = g.is_source, edge_pen_width=prop_to_size(g.actual_flow, mi=5, ma=25, power=1), output_size = (4000,4000), output=r'frames/monday%06d.png' % i)