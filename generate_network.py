import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections


class Social_Net():

	def __init__(self, complete_net=False, n=1000):
		self.G = nx.Graph()
		self.set_parameters()
		if complete_net:
			self.start_network(n)
		else:
			pass

	def start_network(self, n):
		self.family_graph(n, self.G)
		self.workplace_BA()
		self.workplace_random()
		self.interaction()
		self.social()
		#print 'Graph constructed'

	def return_graph(self):
		return self.G

	def family_graph(self, n, G):
		for j, val in enumerate([int(round(i*n)) for i in self.family_sizes]):
			for k in range(int(round(val/(j+1)))):
				self.add_clique(j+1, G)

	def workplace_BA(self):
		n_work = 0
		working_nodes = []
		for n in self.G.nodes():
			if self.G.nodes[n]['working'] and not self.G.nodes[n]['essential']:
				n_work += 1
				working_nodes.append(n)
		BAG = nx.barabasi_albert_graph(n_work, self.ba_degree)
		for pair in list(BAG.edges()):
			self.G.add_edge(working_nodes[pair[0]],
			                working_nodes[pair[1]], lockdown=False)
			self.G[working_nodes[pair[0]]][working_nodes[pair[1]]]['relation'] = 'work'
		return None

	def workplace_random(self):
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
          ][essential_nodes[pair[1]]]['relation'] = 'essential'

	def interaction(self):
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
		print('Social interaction will add', len(select), 'edges')
		for i, j in select:
			self.G.add_edge(i, j, lockdown=False)
			self.G[i][j]['relation'] = 'social'
			socG.add_edge(i, j)
			
	def set_parameters(self, family_sizes=[0.3, 0.35, 0.18, 0.17], workrate=0.7, essential=0.2, ba_degree=3, essential_connection=0.6, interaction_prob=0.20, social_prob=0.001, rand_degree=5):
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
		if G.nodes():
			l = max(G.nodes)+1
		else:
			l = 0
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
			G.add_node(l+i, working=works[i], essential=ess)
		for i, j in list(it.combinations(nodes_to_add, 2)):
			G.add_edge(i, j, lockdown=True)
			G[i][j]['relation'] = 'family'

	def draw_graph(self):
		pos = nx.circular_layout(self.G)
		family, social, ess_ess, ess_non, non_non = [], [], [], [], []
		for i, j in self.G.edges:
			if G[i][j]['relation'] == 'family':
				family.append((i, j))
			if G[i][j]['relation'] == 'social':
				social.append((i, j))
			if G[i][j]['relation'] == 'essential':
				ess_ess.append((i, j))
			if G[i][j]['relation'] == 'ess_non':
				ess_non.append((i, j))
			if G[i][j]['relation'] == 'work':
				non_non.append((i, j))
		nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=200)
		nx.draw_networkx_edges(G=self.G, pos=pos, width=2.0,
		                       edgelist=family, edge_color='green')
		nx.draw_networkx_edges(G=self.G, pos=pos, edgelist=ess_ess, edge_color='red')
		nx.draw_networkx_edges(
			G=self.G, pos=pos, edgelist=ess_non, edge_color='blue')
		nx.draw_networkx_edges(
			G=self.G, pos=pos, edgelist=non_non, edge_color='yellow')
		nx.draw_networkx_edges(
			G=self.G, pos=pos, edgelist=social, edge_color='orange')
		plt.show()

	def degree_histogram(self, G=None, hist_file='temp_hist.png', loglog_file=None):
		if not G:
			G = self.G
		degree_sequence = sorted([d for n, d in G.degree()],reverse=True)
		degreeCount = collections.Counter(degree_sequence)
		degreeCount = sorted(degreeCount.items())
		print(type(degreeCount))
		deg, cnt = zip(*degreeCount)
		print('deg', deg)
		print('cnt', cnt)

		fig, ax = plt.subplots()
		plt.bar(deg, cnt)

		plt.title("Degree Histogram")
		plt.ylabel("Count")
		plt.xlabel("Degree")
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
	My = Social_Net(complete_net=False)
	My.set_parameters(ba_degree=4, social_prob=0.025, rand_degree=5)
	My.start_network(100)
	G = My.return_graph()
	My.draw_graph()
	nx.write_graphml(G, 'tenk_net.graphml')
