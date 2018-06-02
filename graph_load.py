## Full Load Graph for later
from TrafficGraph import TrafficGraph
from utils import *
from multiprocessing import Pool
import time
import os

def load(file):
    graphpath = graph_path(file)
    if not os.path.exists(graphpath):
        g=TrafficGraph(filepath=file)
        g.save("graph_files/" + g.filename[g] + ".gt", fmt="gt")

p = Pool(7)
p.map(load, list_files("Monday"))