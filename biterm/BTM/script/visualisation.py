import networkx as nx
import sys
from itertools import combinations
from collections import Counter

def read_voca(pt):
    voca = {}
    for l in open(pt):
        wid, w = l.strip().split('\t')[:2]
        voca[int(wid)] = w
    return voca

def read_pz(pt):
    return [float(p) for p in open(pt).readline().split()]

def term_cooccurence(pt, voca, pz, threshold=0.01):
	filter = lambda pw_z: pw_z>=threshold

	G = nx.MultiGraph()
	topic = 0
	for l in open(pt):
		vs = [float(v) for v in l.split()]
		wvs = zip(range(len(vs)), vs)
		feature = [(voca[d], topic, pwz) for d, pwz in wvs if filter(pwz)]
		for pair in combinations(feature, 2):
			weight = pair[0][2] + pair[1][2]
			edge_attr = {'weight':weight, 'topic':topic}
			G.add_edge(str(pair[0][0]), str(pair[1][0]), weight=weight, topic=topic)
		topic +=1
	return G

def cotopics(pt, voca, pz, k, threshold=0.01):
	filter = lambda pz_d: pz_d>=threshold


	G = nx.Graph()
	edges = Counter()
	for l in open(pt):
		vs = [float(v) for v in l.split()]
		wvs = zip(range(len(vs)), vs)
		wvs = [(k, v) for k,v in wvs if filter(v)]

		for pair in combinations(wvs, 2):
			edges[(pair[0][0], pair[1][0])] += 1

		

	for combo in edges:
		#print edges[combo]
		G.add_edge(combo[0], combo[1], weight=edges[combo])

	node_attr = dict(zip(range(k), pz))
	nx.set_node_attributes(G, 'probability', node_attr)
	return G

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: python %s <model_dir> <K> <voca_pt>' % sys.argv[0]
        print '\tmodel_dir    the output dir of BTM'
        print '\tK    the number of topics'
        print '\tvoca_pt    the vocabulary file'
        exit(1)
        
    model_dir = sys.argv[1]
    K = int(sys.argv[2])
    voca_pt = sys.argv[3]
    voca = read_voca(voca_pt)    
    W = len(voca)
    print 'K:%d, n(W):%d' % (K, W)

    pz_pt = model_dir + 'k%d.pz' % K
    pz = read_pz(pz_pt)
    
    zw_pt = model_dir + 'k%d.pw_z' %  K
    G1=term_cooccurence(zw_pt, voca, pz, threshold=0.005)
    nx.write_gml(G1, 'term.gml')

    dz_pt = model_dir + 'k%d.pz_d' %K
    G2 = cotopics(dz_pt, voca, pz, K, threshold=0.1)
    nx.write_gml(G2, 'cotopics.gml')