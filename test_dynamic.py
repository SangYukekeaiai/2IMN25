import networkx as nx
import matplotlib.pyplot as plt
from dynamic import Dynamic
from generate_network import Social_Net
import time

SN = Social_Net(complete_net=False)
SN.set_parameters(ba_degree=2, social_prob=0.025, rand_degree=25)
SN.start_network(5000)
G = SN.return_graph()
# SN.draw_graph()

spread = Dynamic(G=G, immune_time=5, infect_rate=0.2, infect_time=14, death_rate=0.01, death_time=14, recover_time=14, begin_infected_number=5)

spread.init_Graph_state()

# for i in range(100):
#     print("iteration ", i, ": ")
#     spread.dayrun()
#     spread.record_print()

spread.draw_distribution(1000)
