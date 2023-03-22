import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections

class Dynamic():
    def __init__(self, G, immune_time, infect_rate, infect_time, death_rate, death_time, recover_rate, begin_infected_number):
        self.G = G
        self.immune_time = immune_time
        self.infect_rate = infect_rate
        self.infect_time = infect_time
        self.death_rate = death_rate
        self.recover_rate = recover_rate
        self.death_time = death_time
        self.begin_infected_number = begin_infected_number


    def init_Graph_state(self):
        infected = set(random.sample(
            self.G.nodes(), self.begin_infected_number))
        for n in self.G.nodes():
            if n in infected:
                self.G.nodes[n]['status'] = 'infected'
                self.G.nodes[n]['day_to_change_state'] = self.immune_time


    def updat_time(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] != 'death' & self.G.nodes[node]['day_to_change_state'] != 0:
                self.G.nodes[node]['day_to_change_state'] -= 1

    def death_event(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] != 'infected' & (
                self.G.nodes[node]['future'] == 'death' & self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'death'

    def recovery(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] == 'infected' & (
                    self.G.nodes[node]['future'] == 'immune' & self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'immune'
                self.G.nodes[node]['future'] = 'healthy'
                self.G.nodes[node]['day_to_change_state'] = self.immune_time

    def infaction(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] == 'infected':
                victim_list = []
                for neighbor in list(self.G.neighbors(node)):
                    if self.G.nodes[neighbor]['status'] == 'healthy' & self.G.nodes[neighbor]['future'] == 'healthy':
                        victim_list.append(neighbor)
                destiny = np.random.binomial(1, self.infect_rate, len(victim_list))
                for i in len(destiny):
                    if destiny[i] == 1:
                        self.G.nodes[victim_list[i]]['future'] = 'infected'
                        self.G.nodes[victim_list[i]]['day_to_change_state'] = self.infect_time

    def be_infected(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] == 'healthy' & (
                    self.G.nodes[node]['future'] == 'infected' & self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'infected'
                destiny = np.random.choice(np.arange(0, 2), p=[1-self.death_rate, self.death_rate])
                if destiny:
                    self.G.nodes[node]['future'] = 'death'
                    self.G.nodes[node]['day_to_change_state'] = self.death_time
                else:
                    self.G.nodes[node]['future'] = 'immune'
                    self.G.nodes[node]['day_to_change_state'] = self.recover_time


    def quit_immune(self):
        for node in self.G.__iter__:
            if self.G.nodes[node]['status'] == 'immune' & (
                    self.G.nodes[node]['future'] == 'healthy' & self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'healthy'
                self.G.nodes[node]['future'] = 'healthy'
                self.G.nodes[node]['day_to_change_state'] = 0


    def dayrun(self):
        self.updat_time()
        self.death_event()
        self.recovery()
        self.be_infected()
        self.infaction()

