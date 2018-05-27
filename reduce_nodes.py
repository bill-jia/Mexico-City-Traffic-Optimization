from utils import *
from TrafficGraph import TrafficGraph

# f = open("googlemapskey.txt")
# apikey = f.readline()[0:-1]
# mplt.register_api_key(apikey)
g = TrafficGraph("2018-05-24T04.59.44.000.in")
plot_graph_as_map(g)