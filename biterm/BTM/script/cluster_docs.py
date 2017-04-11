#!/usr/bin/env python
#coding=utf-8
# Function: translate the results from BTM
# Input:
#    mat/pw_z.k20

import sys
from sklearn.cluster import KMeans
import numpy as np

# return:    {wid:w, ...}
def read_voca(pt):
    voca = {}
    for l in open(pt):
        wid, w = l.strip().split('\t')[:2]
        voca[int(wid)] = w
    return voca

def read_pz(pt):
    return [float(p) for p in open(pt).readline().split()]



def cluster_docs(pt, voca, pz, K):
	docs = []
	for l in open(pt):
		vs = [float(v) for v in l.split()]
		docs.append(vs)

	kmeans = KMeans(n_clusters=K).fit_predict(np.array(docs))
	


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

    dz_pt = model_dir + 'k%d.pz_d' %K

    pz_pt = model_dir + 'k%d.pz' % K
    pz = read_pz(pz_pt)
    
    zw_pt = model_dir + 'k%d.pw_z' %  K
    dispTopics(zw_pt, voca, pz)

    cluster_docs(dz_pt, voca, pz, K)