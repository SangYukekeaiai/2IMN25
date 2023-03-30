import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections
import statistics as stat

class Dynamic():  

    def __init__(self, G, immune_time, infect_rate, infect_time, death_rate, lockdown_start, lockdown_stop, begin_infected_number, allowed_measures):
        self.G = G
        self.immune_time = immune_time
        self.infect_rate = infect_rate
        self.infect_time = infect_time
        self.death_rate = death_rate
        self.lockdown_stop = lockdown_stop
        self.lockdown_start = lockdown_start
        self.begin_infected_number = begin_infected_number
        self.death_list = [0.0024, 0.0037, 0.0081, 0.0159, 0.0285, 0.0465, 0.0686, 0.0918, 0.1116, 0.1229, 0.1229, 0.1116, 0.0918, 0.0686, 0.0465, 0.0285, 0.0159, 0.0081, 0.0037, 0.0024]
        self.recover_list = [0.0002, 0.0005, 0.0009, 0.0016, 0.0028, 0.0047, 0.0076, 0.0117, 0.0173, 0.0245, 0.0332, 0.0431, 0.0536, 0.0637, 0.0726, 0.0792, 0.0828, 0.0827, 0.0792, 0.0726, 0.0637, 0.0536, 0.0431, 0.0332, 0.0245, 0.0173, 0.0117, 0.0076, 0.0047, 0.0028, 0.0016, 0.0009, 0.0005, 0.0002, 0.0001]
        self.allowed_measures = allowed_measures
        self.time = 0
        mu = 5.6
        sigma = (14 - 2) / 6

        # Generate the x values from 2 to 14
        x = np.arange(2, 14)
        probs = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mu) / sigma)**2)
        probs /= np.sum(probs)
        self.to_be_infected_list = list(probs)


    def init_Graph_state(self):
        infected = set(random.sample(
            self.G.nodes(), self.begin_infected_number))
        for n in self.G.nodes():
            if n in infected:
                self.G.nodes[n]['status'] = 'infected'
                self.G.nodes[n]['day_to_change_state'] = np.random.choice(np.arange(1,36), p = self.recover_list)
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

    def infaction(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'infected':
                victim_list = []
                for neighbor in list(self.G.neighbors(node)):
                    if self.G.nodes[neighbor]['status'] == 'healthy' and self.G.nodes[neighbor]['future'] == 'healthy':
                        if self.time >self.lockdown_start and self.time<self.lockdown_stop:
                            if self.G[node][neighbor]['relation'] == self.allowed_measures:
                                victim_list.append(neighbor)                            
                        else:
                            victim_list.append(neighbor)
                destiny = np.random.binomial(1, self.infect_rate, len(victim_list))
                for i in range(len(destiny)):
                    if destiny[i] == 1:
                        self.G.nodes[victim_list[i]]['future'] = 'infected'
                        self.G.nodes[victim_list[i]]['day_to_change_state'] = np.random.choice(np.arange(2,14), p = self.to_be_infected_list)

    def be_infected(self):
        for node in self.G.__iter__():
            if self.G.nodes[node]['status'] == 'healthy' and (
                    self.G.nodes[node]['future'] == 'infected' and self.G.nodes[node]['day_to_change_state'] == 0):
                self.G.nodes[node]['status'] = 'infected'
                destiny = np.random.choice(np.arange(0, 2), p=[1-self.death_rate, self.death_rate])
                if destiny:
                    self.G.nodes[node]['future'] = 'death'
                    self.G.nodes[node]['day_to_change_state'] = np.random.choice(np.arange(5,25), p = self.death_list)
                else:
                    self.G.nodes[node]['future'] = 'immune'
                    self.G.nodes[node]['day_to_change_state'] = np.random.choice(np.arange(1,36), p = self.recover_list)


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
        for i in range(times):
            self.dayrun()
            recover_num, healthy_num, death_num, infected_num = self.record_print()
            self.death_num_list.append(death_num)
            self.recovered_num_list.append(recover_num)
            self.infected_num_list.append(infected_num)
            self.healthy_num_list.append(healthy_num)
            self.time_list.append(i)
            self.time = i
        fig, ax = plt.subplots()
        ax.plot(self.time_list, self.death_num_list, label='death', color='b')
        ax.plot(self.time_list, self.recovered_num_list, label='recovered', color='y')
        ax.plot(self.time_list, self.infected_num_list, label='infected', color='g')
        ax.plot(self.time_list, self.healthy_num_list, label='healthy', color='r')
        ax.legend()
        plt.xlabel("Days")
        plt.ylabel("number of people")
        plt.savefig('single_run.png', dpi=500)
        plt.close() 
        

    def dayrun(self):
        self.updat_time()
        self.death_event()
        self.recovery()
        self.quit_immune()
        self.be_infected()
        self.infaction()
    
    def avg_std(self, times,cumdict):
        #print(cumdict)
        avgdict = {'healthy':[0 for i in range(times)], 'recovered':[0 for i in range(times)], 'infected':[0 for i in range(times)], 'death':[0 for i in range(times)]}
        stdevdict = {'healthy':[0 for i in range(times)], 'recovered':[0 for i in range(times)], 'infected':[0 for i in range(times)], 'death':[0 for i in range(times)]}
        

        for k in cumdict.keys():
            for ind in range(times):
                avgdict[k][ind] = stat.mean(cumdict[k][ind])
                stdevdict[k][ind] = stat.stdev(cumdict[k][ind])

        self.draw_fill_graph(times, avgdict, stdevdict)
        
    def draw_fill_graph(self, times, avgdict, stdevdict):
        #print(avgdict)
        #print(stdevdict)
        x = [i+1 for i in range(times)]
        fig,ax = plt.subplots()
        ax.plot(x, avgdict['healthy'], 'r', linewidth=0.5, label='healthy')
        ax.plot(x, avgdict['infected'], 'g', linewidth=0.5, label='infected')
        ax.plot(x, avgdict['recovered'], 'y', linewidth=0.5, label='recovered')
        ax.plot(x, avgdict['death'], 'b', linewidth=0.5, label='death')
        ax.fill_between(x, [b-a for a,b in zip(stdevdict['healthy'], avgdict['healthy'])], [b+a for a,b in zip(stdevdict['healthy'], avgdict['healthy'])], color='r', alpha=0.1)
        ax.fill_between(x, [b-a for a,b in zip(stdevdict['infected'], avgdict['infected'])], [b+a for a,b in zip(stdevdict['infected'], avgdict['infected'])], color='g', alpha=0.1)
        ax.fill_between(x, [b-a for a,b in zip(stdevdict['recovered'], avgdict['recovered'])], [b+a for a,b in zip(stdevdict['recovered'], avgdict['recovered'])], color='y', alpha=0.1)
        ax.fill_between(x, [b-a for a,b in zip(stdevdict['death'], avgdict['death'])], [b+a for a,b in zip(stdevdict['death'], avgdict['death'])], color='b', alpha=0.1)
        ax.legend(['healthy', 'infected', 'recovered', 'death'], loc='best', fontsize='x-small')
        ax.legend()
        plt.xticks(fontsize='x-small')
        plt.yticks(fontsize='x-small')
        plt.xlabel("Days")
        plt.ylabel("number of people")
        plt.savefig('many_run.png', dpi=500)
        plt.close()

    def many_dayrun(self, times):
        #death_num_dict = {}
        #recovered_num_dict = {}
        #infected_num_dict = {}
        #healthy_num_dict = {}
        #time_dict = {}
        #cumdict = {'healthy':[[] for i in range(times)], 'recovered':[[] for i in range(times)], 'infected':[[] for i in range(times)], 'death':[[] for i in range(times)]}
        
        all_vals = {}
        self.death_num_list = []
        self.recovered_num_list = []
        self.infected_num_list = []
        self.healthy_num_list = []
        self.time_list = []
        for i in range(times):
                self.dayrun()
                recover_num, healthy_num, death_num, infected_num = self.record_print()
                self.death_num_list.append(death_num)
                self.recovered_num_list.append(recover_num)
                self.infected_num_list.append(infected_num)
                self.healthy_num_list.append(healthy_num)
                self.time_list.append(i)
                self.time = i
            
        all_vals = {'infected':self.infected_num_list, 'healthy':self.healthy_num_list, 'death': self.death_num_list, 'recovered':self.recovered_num_list}
        return all_vals

