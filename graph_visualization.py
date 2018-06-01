from TrafficGraph import TrafficGraph
from graph_tool.all import *

g=TrafficGraph("2018-05-23T23.59.44.000.in")
graph_draw(g, output_size=(1200,1200), output="graphtest.png")