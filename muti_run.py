import networkx as nx
import matplotlib.pyplot as plt
from dynamic import Dynamic
from generate_network import Social_Network
import time

sim_times = 7
times = 180
num_graphs = 5
cumdict = {'healthy':[[] for i in range(times)], 'recovered':[[] for i in range(times)], 'infected':[[] for i in range(times)], 'death':[[] for i in range(times)]}
measures = {"limit_social" : ['ess_non', 'ess_ess','work'], "No" : None}
immune_time= 180
infect_rate=0.05
infect_time=14
death_rate=0.05
lockdown_start=20 
lockdown_stop=40
begin_infected_number=5
allowed_measures=measures["limit_social"]

for i in range(num_graphs):
    for j in range(sim_times):
        if j == 0 :
            SN = Social_Network(complete=False)
            SN.set_parameters(ba_degree=3, social_prob=0.05, rand_degree=25)
            SN.setup_network(5000)
            G = SN.get_graph()
            spread = Dynamic(G,immune_time , infect_rate, infect_time, death_rate, lockdown_start, lockdown_stop, begin_infected_number, allowed_measures)
            spread.init_Graph_state()
            data = spread.many_dayrun(times) 
        else:
            spread = Dynamic(G,immune_time , infect_rate, infect_time, death_rate, lockdown_start, lockdown_stop, begin_infected_number, allowed_measures)
            spread.init_Graph_state()
            data = spread.many_dayrun(times) 
        
        for k in data.keys():
                for ind in range(times):
                    cumdict[k][ind].append(data[k][ind])
    
spread.avg_std(times,cumdict)
