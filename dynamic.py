import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections
import math as m
from scipy.stats import truncnorm

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
        return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


class Dynamic():

    
    def __init__(self, G, immune_time, infect_rate, infect_time, death_rate, death_time, recover_time, begin_infected_number, allowed_measures):
        
        self.G = G
        self.immune_time = immune_time
        self.infect_rate = infect_rate
        self.infect_time = infect_time
        self.death_rate = death_rate
        self.recover_time = recover_time
        self.death_time = death_time
        self.begin_infected_number = begin_infected_number
        self.allowed_measures = allowed_measures

    def rand_immune_times(self,times):
        immune_t = get_truncated_normal(mean=self.immune_time, sd=2, low=max(1,self.immune_time-5), upp = max(self.immune_time,self.immune_time+5))
        vals = immune_t.rvs(times)
        print(vals)
        return vals
        
    def rand_infect_times(self,times):
        infect_t = get_truncated_normal(mean=10, sd=2, low=7, upp = self.infect_time)
        vals = infect_t.rvs(times)
        return vals
    
    def init_Graph_state(self):
        infected = set(random.sample(
            self.G.nodes(), self.begin_infected_number))
        for n in self.G.nodes():
            if n in infected:
                self.G.nodes[n]['status'] = 'infected'
                self.G.nodes[n]['day_to_change_state'] = self.recover_time
                self.G.nodes[n]['future'] = 'immune'
            else:
                self.G.nodes[n]['status'] = 'healthy'
                self.G.nodes[n]['day_to_change_state'] = 0
                self.G.nodes[n]['future'] = 'healthy'



    def updat_time(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] != 'death' and self.G.nodes[node]['day_to_change_state'] != 0:
                self.G.nodes[node]['day_to_change_state'] -= 1

    def death_event(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'infected' and (
                self.G.nodes[node]['future'] == 'death' and self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'death'

    def recovery(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'infected' and (
                    self.G.nodes[node]['future'] == 'immune' and self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'immune'
                self.G.nodes[node]['future'] = 'healthy'
                self.G.nodes[node]['day_to_change_state'] = self.immune_time

    def infection(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'infected':
                victim_list = []
                for neighbor in list(self.G.neighbors(node)):
                    if self.G.nodes[neighbor]['status'] == 'healthy' and self.G.nodes[neighbor]['future'] == 'healthy' and self.G[node][neighbor]['relation'] != self.allowed_measures:
                        victim_list.append(neighbor)
                destiny = np.random.binomial(1, self.infect_rate, len(victim_list))
                for i in range(len(destiny)):
                    if destiny[i] == 1:
                        self.G.nodes[victim_list[i]]['future'] = 'infected'
                        self.G.nodes[victim_list[i]]['day_to_change_state'] = self.infect_time

    def be_infected(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'healthy' and (
                    self.G.nodes[node]['future'] == 'infected' and self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'infected'
                destiny = np.random.choice(np.arange(0, 2), p=[1-self.death_rate, self.death_rate])
                if destiny:
                    self.G.nodes[node]['future'] = 'death'
                    self.G.nodes[node]['day_to_change_state'] = self.death_time
                else:
                    self.G.nodes[node]['future'] = 'immune'
                    self.G.nodes[node]['day_to_change_state'] = self.recover_time


    def quit_immune(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'immune' and (
                    self.G.nodes[node]['future'] == 'healthy' and self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'healthy'
                self.G.nodes[node]['future'] = 'healthy'
                self.G.nodes[node]['day_to_change_state'] = 0

    def record_print(self):
        death_nodes = []
        death_num = 0
        infected_nodes = []
        infected_num = 0
        recovered_nodes = []
        recover_num = 0
        healthy_nodes = []
        healthy_num = 0
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'immune':
                recovered_nodes.append(node)
                recover_num += 1
            if self.G.nodes[node]['status'] == 'healthy':
                healthy_nodes.append(node)
                healthy_num += 1
            if self.G.nodes[node]['status'] == 'death':
                death_nodes.append(node)
                death_num += 1
            if self.G.nodes[node]['status'] == 'infected':
                infected_nodes.append(node)
                infected_num += 1
        # print("death node:", death_nodes)
        # print("death number:", len(death_nodes))
        # print("infected node:", infected_nodes)
        # print("infected number:", len(infected_nodes))
        # print("recovered node:", recovered_nodes)
        # print("recovered number:", len(recovered_nodes))
        # print("healthy node:", healthy_nodes)
        # print("healthy number:", len(healthy_nodes))
        return [recover_num, healthy_num, death_num, infected_num]
    

    def draw_distribution(self, times):
        self.death_num_list = []
        self.recovered_num_list = []
        self.infected_num_list = []
        self.healthy_num_list = []
        self.time_list = []
        self
        immune_times = self.rand_immune_times(times)
        infect_times = self.rand_infect_times(times)
        
        for i in range(times):
            self.immune_time = m.ceil(immune_times[i])
            self.infect_time = m.ceil(infect_times[i])
            self.dayrun()
            recover_num, healthy_num, death_num, infected_num = self.record_print()
            self.death_num_list.append(death_num)
            self.recovered_num_list.append(recover_num)
            self.infected_num_list.append(infected_num)
            self.healthy_num_list.append(healthy_num)
            self.time_list.append(i)

        plt.plot(self.time_list, self.death_num_list, label='death')
        plt.plot(self.time_list, self.recovered_num_list, label='immune')
        plt.plot(self.time_list, self.infected_num_list, label='infected')
        plt.plot(self.time_list, self.healthy_num_list, label='healthy')
        plt.legend()
        plt.show()

        
        


    def dayrun(self):
        self.updat_time()
        self.death_event()
        self.recovery()
        self.quit_immune()
        self.be_infected()
        self.infection()


'''class limit_social(Dynamic):
    def __init__(self, G, immune_time, infect_rate, infect_time, death_rate, death_time, recover_time, begin_infected_number):
         super().__init__(self, G, immune_time, infect_rate, infect_time, death_rate, death_time, recover_time, begin_infected_number)
    
    def infection(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'infected':
                victim_list = []
                for neighbor in list(self.G.neighbors(node)):
                    if self.G.nodes[neighbor]['status'] == 'healthy' and self.G.nodes[neighbor]['future'] == 'healthy' and self.G.get_edge_data(node,neighbor) == 'ess_non':
                        victim_list.append(neighbor)
                destiny = np.random.binomial(1, self.infect_rate, len(victim_list))
                for i in range(len(destiny)):
                    if destiny[i] == 1:
                        self.G.nodes[victim_list[i]]['future'] = 'infected'
                        self.G.nodes[victim_list[i]]['day_to_change_state'] = self.infect_time'''