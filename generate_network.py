import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections


class Social_Network():

    def __init__(self, complete=False, n=1000):
        #initializes the graph and sets the parameters to default
        self.G = nx.Graph()
        self.set_parameters()
        if complete:
            self.setup_network(n)
        else:
            pass

    def setup_network(self, n):
        self.family_graph(n, self.G)
        self.workplace_BA()
        self.workplace_random()
        self.interaction()
        self.social()
        self.degree_histogram(G=self.G, hist_file='Network_edge_distribution.png',
                                                    loglog_file='Network_log.png')
        #print 'Graph constructed'

    def get_graph(self):
        return self.G

    def family_graph(self, n, G):
        #print 'Size of the network is', n
        for j, val in enumerate([int(round(i*n)) for i in self.family_sizes]):
            #print 'Adding', int(round(val/(j+1))), 'cliques of size', j+1
            for k in range(int(round(val/(j+1)))):
                self.add_clique(j+1, G)
        # print('Family!')
        # self.degree_histogram(
            # G=self.G, hist_file='family_hist.png', loglog_file='family_log.png')

    def workplace_BA(self):
        #creates a scale-free network on non-essential workers
        n_work = 0
        working_nodes = []
        for n in self.G.nodes():
            if self.G.nodes[n]['working'] and not self.G.nodes[n]['essential']:
                n_work += 1
                working_nodes.append(n)
        BAG = nx.barabasi_albert_graph(n_work, self.ba_degree)
        # print('Workplace BA!')
        # self.degree_histogram(G=BAG, hist_file='workBA_hist.png',
        #                       loglog_file='workBA_log.png')
        #map the BAG to the actual network edges
        for pair in list(BAG.edges()):
            self.G.add_edge(working_nodes[pair[0]],
                            working_nodes[pair[1]], lockdown=False)
            self.G[working_nodes[pair[0]]][working_nodes[pair[1]]]['relation'] = 'non_non'
        #print 'Printing edges of the workplace BA network'
        #print BAG.edges()
        return None

    def workplace_random(self):
        #creates a random network on essential workers
        n_ess = 0
        essential_nodes = []
        for n in self.G.nodes():
            if self.G.nodes[n]['essential']:
                n_ess += 1
                essential_nodes.append(n)
        m = int(float(n_ess*self.rand_degree)/2)
        # print('m is', m)
        ER = nx.gnm_random_graph(n_ess, m)
        for pair in list(ER.edges()):
            self.G.add_edge(essential_nodes[pair[0]],
                            essential_nodes[pair[1]], lockdown=True)
            self.G[essential_nodes[pair[0]]
          ][essential_nodes[pair[1]]]['relation'] = 'ess_ess'

    def interaction(self):
        #add edges that represent interactions of everyone with essential workers
        newG = nx.Graph()
        newG.add_nodes_from([i for i in range(len(self.G.nodes()))])
        essential_nodes = []
        for n in self.G.nodes():
            if self.G.nodes[n]['essential']:
                essential_nodes.append(n)

        for n in self.G.nodes():
            connects = np.random.choice(
                np.arange(0, 2), p=[1-self.interaction_prob, self.interaction_prob])
            if connects:
                m = random.choice(essential_nodes)
                self.G.add_edge(n, m, lockdown=True)
                self.G[n][m]['relation'] = 'ess_non'
                newG.add_edge(n, m)

    def social(self):
        socG = nx.Graph()
        socG.add_nodes_from([i for i in range(len(self.G.nodes()))])
        allnodes = self.G.nodes()
        allpairs = list(it.combinations(allnodes, 2))
        select = random.sample(allpairs, k=int(self.social_prob*len(allpairs)))
        for i, j in select:
            self.G.add_edge(i, j, lockdown=False)
            self.G[i][j]['relation'] = 'social'
            socG.add_edge(i, j)

    def set_parameters(self, family_sizes=[0.3, 0.35, 0.18, 0.17], workrate=0.6, essential=0.2, ba_degree=2, essential_connection=0.6, interaction_prob=0.20, social_prob=0.001, rand_degree=5):
        self.workrate = workrate
        self.essential = essential
        self.family_sizes = family_sizes
        self.ba_degree = ba_degree
        self.essential_connection = essential_connection
        self.interaction_prob = interaction_prob
        self.social_prob = social_prob
        self.rand_degree = rand_degree

    def return_parameters(self):
        pardict = {}
        pardict['workrate'] = self.workrate
        pardict['essential'] = self.essential
        pardict['family_sizes'] = self.family_sizes
        pardict['ba_degree'] = self.ba_degree
        pardict['essential_connection'] = self.essential_connection
        pardict['interaction_prob'] = self.interaction_prob
        pardict['social_prob'] = self.social_prob
        pardict['rand_degree'] = self.rand_degree
        return pardict

    def add_clique(self, clique_size, G):
        #adds a clique of size n to graph G
        if G.nodes():
            l = max(G.nodes)+1
        else:
            l = 0
        #print 'l is', l
        works = []
        for k in range(clique_size):
            works.append(np.random.choice(np.arange(0, 2),
                         p=[1-self.workrate, self.workrate]))
        nodes_to_add = [l+i for i in range(clique_size)]
        for i in range(clique_size):
            if works[i]:
                ess = np.random.choice(
                    np.arange(0, 2), p=[1-self.essential, self.essential])
            else:
                ess = 0
            #print 'ess is', ess
            G.add_node(l+i, working=works[i], essential=ess)
        #G.add_nodes_from(nodes_to_add)        #add nodes l, l+1, l+2, l+3 (for n=4) to the graph
        #add edges between all these pairs
        for i, j in list(it.combinations(nodes_to_add, 2)):
            #print 'adding edge between', i, 'and', j
            G.add_edge(i, j, lockdown=True)
            G[i][j]['relation'] = 'family'

    def draw_graph(self):
        pos = nx.circular_layout(self.G)
        family, social, ess_ess, ess_non, non_non = [], [], [], [], []
        for i, j in self.G.edges:
            if self.G[i][j]['relation'] == 'family':
                family.append((i, j))
            if self.G[i][j]['relation'] == 'social':
                social.append((i, j))
            if self.G[i][j]['relation'] == 'ess_ess':
                ess_ess.append((i, j))
            if self.G[i][j]['relation'] == 'ess_non':
                ess_non.append((i, j))
            if self.G[i][j]['relation'] == 'non_non':
                non_non.append((i, j))
        nx.draw(self.G, pos, with_labels=True, font_weight='bold', node_size=200)
        nx.draw_networkx_edges(G=self.G, pos=pos, width=2.0,
                               edgelist=family, edge_color='green')
        nx.draw_networkx_edges(G=self.G, pos=pos, edgelist=ess_ess, edge_color='red')
        nx.draw_networkx_edges(
            G=self.G, pos=pos, edgelist=ess_non, edge_color='blue')
        nx.draw_networkx_edges(
            G=self.G, pos=pos, edgelist=non_non, edge_color='yellow')
        # nx.draw_networkx_edges(
        #     G=self.G, pos=pos, edgelist=non_non, edge_color='yellow')
        nx.draw_networkx_edges(
            G=self.G, pos=pos, edgelist=social, edge_color='orange')

        # edge_dict = dict([((i, j), d['relation'])
        #                  for i, j, d in self.G.edges(data=True)])
        # nx.draw_networkx_edge_labels(self.G, pos, edge_labels = edge_dict)
        plt.show()

    def degree_histogram(self, G=None, hist_file='temp_hist.png', loglog_file=None):
        if not G:
            G = self.G
        degree_sequence = []
        total = [0]
        ess_ess = [0]
        ess_non = [0]
        non_non = [0]
        social = [0]
        family = [0]
        degree = sorted(G.degree, key=lambda x: x[1], reverse=True)
        # print(degree)
        for i, j in self.G.edges:
            G.add_edge(i,j,is_counted=False)
        for neighbor in G.neighbors(degree[0][0]):
            n = degree[0][0]
            if self.G[n][neighbor]['relation'] == 'family':
                family[-1] += 1
            if self.G[n][neighbor]['relation'] == 'social':
                social[-1] += 1
            if self.G[n][neighbor]['relation'] == 'ess_ess':
                ess_ess[-1] += 1
            if self.G[n][neighbor]['relation'] == 'ess_non':
                ess_non[-1] += 1
            if self.G[n][neighbor]['relation'] == 'non_non':
                non_non[-1] += 1
        for node in range(1, len(degree)):
            if degree[node][1] == degree[node - 1][1]:
                for neighbor in G.neighbors(degree[node][0]):
                    n = degree[node][0]
                    if self.G[n][neighbor]['relation'] == 'family' and self.G[n][neighbor]['is_counted'] == False:
                        family[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'social' and self.G[n][neighbor]['is_counted'] == False:
                        social[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'ess_ess' and self.G[n][neighbor]['is_counted'] == False:
                        ess_ess[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'ess_non' and self.G[n][neighbor]['is_counted'] == False:
                        ess_non[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'non_non' and self.G[n][neighbor]['is_counted'] == False:
                        non_non[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
            else:
                family.append(0)
                social.append(0)
                ess_ess.append(0)
                ess_non.append(0)
                non_non.append(0)
                total.append(degree[node][1])
                for neighbor in G.neighbors(degree[node][0]):
                    n = degree[node][0]
                    if self.G[n][neighbor]['relation'] == 'family' and self.G[n][neighbor]['is_counted'] == False:
                        family[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'social' and self.G[n][neighbor]['is_counted'] == False:
                        social[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'ess_ess' and self.G[n][neighbor]['is_counted'] == False:
                        ess_ess[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'ess_non' and self.G[n][neighbor]['is_counted'] == False:
                        ess_non[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
                    if self.G[n][neighbor]['relation'] == 'non_non' and self.G[n][neighbor]['is_counted'] == False:
                        non_non[-1] += 1
                        self.G[n][neighbor]['is_counted'] = True
        # print()
        categories = {"family": family,
                      "ess_ess": ess_ess,
                      "ess_non": ess_non,
                      "non_non": non_non,
                      "social": social}
        fig, ax = plt.subplots()
        bottom = np.zeros(len(total))
        # print(family)
        for boolean, content in categories.items():
            p = ax.bar(total, content, label = boolean, bottom=bottom)
            bottom += content
        plt.title("Degree Histogram")
        plt.ylabel("Count")
        plt.xlabel("Degree")
        # ax.set_xticks([d + 0.4 for d in total])
        # ax.set_xticklabels(total)
        ax.legend(loc="upper right")
        plt.savefig("stack bar chart", dpi=500)
        plt.close()
        # print(G.degree())
        degree_sequence = sorted([d for n, d in G.degree()],
                                 reverse=True)  # degree sequence
        #print "Degree sequence", degree_sequence
        degreeCount = collections.Counter(degree_sequence)
        degreeCount = sorted(degreeCount.items())
        # print(type(degreeCount))
        deg, cnt = zip(*degreeCount)
        # print('deg', deg)
        # print("number of degree more than 100:", sum(i > 100 for i in deg))
        # print('cnt', cnt)

        fig, ax = plt.subplots()
        plt.bar(deg, cnt, label = 'number of node')

        plt.title("Degree Histogram")
        plt.ylabel("Count")
        plt.xlabel("Degree")
        ax.set_xticks([d + 0.4 for d in total])
        ax.set_xticklabels(total)
        ax.legend(loc="upper right")
        plt.savefig(hist_file, dpi=500)
        plt.close()

        if loglog_file:
            fig, ax = plt.subplots()
            #plt.loglog(deg, cnt)
            plt.plot(deg, cnt, 'ko', markersize=2)
            ax.set_xscale('log')
            ax.set_yscale('log')
            plt.title("Degree loglog plot")
            plt.ylabel("P(k)")
            plt.xlabel("Degree (k)")
            plt.savefig(loglog_file, dpi=500)
            plt.close()


if __name__ == '__main__':
    My = Social_Network(complete=False)
    My.set_parameters(ba_degree=3, social_prob=0.0025, rand_degree=10)
    My.setup_network(100)
    # G = My.return_graph()
    # My.draw_graph()
    # nx.write_graphml(G, 'tenk_net.graphml')
