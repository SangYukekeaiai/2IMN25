import networkx as nx
import matplotlib.pyplot as plt
from dynamic import Dynamic
from generate_network import Social_Network
import time

SN = Social_Network(complete=False)
SN.set_parameters(ba_degree=3, social_prob=0.0025, rand_degree=25)
SN.setup_network(10000)
G = SN.get_graph()
#SN.draw_graph()
# SN.draw_graph()
measures = {"limit_social" : ['ess_non', 'ess_ess'], "No" : None}
spread = Dynamic(G=G, immune_time=180, infect_rate=0.05, infect_time=14, death_rate=0.05, lockdown_start=20, lockdown_stop=60, begin_infected_number=5, allowed_measures=measures["No"])

spread.init_Graph_state()

# for i in range(100):
#     print("iteration ", i, ": ")
#     spread.dayrun()
#     spread.record_print()

spread.draw_distribution(200)
