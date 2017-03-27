from bs4 import BeautifulSoup
from bs4 import NavigableString
import re
import string
import nltk.corpus
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
import nltk.tree
import nltk.tokenize
from nltk.tokenize import TweetTokenizer
from nltk.tree import *
import pandas as pd
import collections
import urllib2
import numpy as np

def DictionaryBuilder():
	alphabet  = []
	start = ord('a')
	end = ord('z')
	for i in range(start,end+1):
		alphabet.append(chr(i))
	site = 'http://www.noslang.com/dictionary/'
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'none','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'}
	abbr_dict =  collections.defaultdict(str)
	for char in alphabet:
		site = site+char+'/'
		req = urllib2.Request(site,headers= hdr)
		#print " Trying to open",site
		page = urllib2.urlopen(req)
		#print "Successfully opened"
		soup = BeautifulSoup(page)
		soup.prettify()
		nodelist=[]
		for node in soup.findAll('abbr'):
			nodelist.append(node)

		for node in nodelist:
			temp_list = node.contents[0].contents[0].contents
			if isinstance(temp_list[0],NavigableString):
				abbr = ''.join(node.contents[0].contents[0].contents)
				abbr = abbr.encode('ascii','ignore')
				abbr = abbr.split(' :')[0]
				meaning = node["title"]
				abbr_dict[abbr] = meaning
		site = site[:-2]
	return abbr_dict

def repeated_sequence(word):
	pattern = re.compile(r"(.)\1{1,}",re.DOTALL)
	return pattern.sub(r'\1\1',word)

def getFeatureVector(tweet):
	featureVector =[]
	stopwords = pd.read_csv('StopWords.txt')
	StopWords =[]
	for i in range(0,len(stopwords)):
		StopWords.append(stopwords["stop"][i])
	words = tweet.split()
	for word in words:
		word = repeated_sequence(word)
		word = word.strip('\'"?,.')
		val = re.search(r'^[a-zA-Z][a-zA-Z0-9]*$',word)
		if word in StopWords or val is None:
			continue

		else:
			featureVector.append(word.lower())
	return featureVector

def processTweet(tweet,emoticons_dict):
	tweet = tweet.lower()
	negative_word_list =['not','no','never','n\'t','cannot','isn\'t','isnt']
	tweet = re.sub(r'{(\s)*link(\s)*}','U',tweet)
	tweet = re.sub(r'@(\s)*(\w)+','@Fernando',tweet)
	tweet = re.sub(r'[\s]+',' ',tweet)
	tweet = re.sub(r'#(\s)*(\w)+',r'\2',tweet)
	tweet = tweet.strip('\'"')
	tknzr = TweetTokenizer()
	tokenize_tweet = tknzr.tokenize(tweet)
	for i in range(0,len(tokenize_tweet)):
		tokenize_tweet[i] = str(tokenize_tweet[i])
		if tokenize_tweet[i] in negative_word_list:
			tokenize_tweet[i] ='NOT'
		if str(tokenize_tweet[i]) in emoticons_dict:
			if emoticons_dict[tokenize_tweet[i]] >3:
				tokenize_tweet[i]='EXTREMELYPOSITIVE'

			if emoticons_dict[tokenize_tweet[i]] <=3 and emoticons_dict[tokenize_tweet[i]] >0:
				tokenize_tweet[i]= 'POSITIVE'

			if emoticons_dict[tokenize_tweet[i]] >=-3 and emoticons_dict[tokenize_tweet[i]] <0:
				tokenize_tweet[i] = 'NEGATIVE'

			if emoticons_dict[tokenize_tweet[i]] <=-3:
				tokenize_tweet[i] ='EXTREMELYNEGATIVE'

			if emoticons_dict[tokenize_tweet[i]] ==0:
				tokenize_tweet[i] ='NEUTRAL'

	tweet =' '.join(tokenize_tweet)
	return tweet


def getSVMFeatureVectorAndLabels(tweets, featureList):
    sortedFeatures = sorted(featureList)
    map = {}
    feature_vector = []
    labels = []
    for t in tweets:
        label = 0
        map = {}
        for w in sortedFeatures:
            map[w] = 0
        tweet_words = t[0]
        tweet_opinion = t[1]
        for word in tweet_words:
            word = repeated_sequence(word)
            word = word.strip('\'"?,.')
            if word in map:
                map[word] = 1
        values = map.values()
        feature_vector.append(values)
        labels.append(tweet_opinion)
    #return the list of feature_vector and labels
    return {'feature_vector' : feature_vector, 'labels': labels}

def findmaximumArg(train,i):
	maximum = max(train["s2"][i],train["s3"][i],train["s4"][i])
	if maximum == train["s2"][i]:
		return -1
	if maximum == train["s3"][i]:
		return 0
	if maximum == train["s4"][i]:
		return +1
	    

def preprocess_tweet():
	abbr_dictionry = DictionaryBuilder()
	negative_word_list =['not','no','never','n\'t','cannot']
	train = pd.read_csv("train.csv")
	emoticons = pd.read_csv("emoticons.csv")
	stopWords = pd.read_csv('StopWords.txt')

	#BUILDING EMOTICONS DICTIONARY
    #Extremely positive >=3
    #Extremely negative <=-3
    #Postive >0 and Positive<3
    #Negative <0 and Negative >-3

	emoticons_dict = collections.defaultdict(int)
	for i in range(0,len(emoticons)):
		if not emoticons["emo"][i] in emoticons_dict:
			emoticons_dict[str(emoticons["emo"][i])] = int(emoticons["count"][i]) 

	#print len(emoticons_dict)
	write_vector =open("feature_vector_test.txt","r+")
	writer_tree = open("tree_rep_test.txt","r+")
	writer2 = open("tweets.txt","r+")
	reader = open("tagged_tweet.txt","r")
	#Preprocessing the tweets
	tree_list =[]
	feature_vector =[]
	tweets_tagged =[]
	tknzr = TweetTokenizer()
	for line in reader:
		tweets_tagged.append(line)

	featureList =[]

	tweets =[]


	for i in range(0,len(train)):
		tweet = train["tweet"][i]
		sentiment = findmaximumArg(train,i)
		tweet = processTweet(tweet,emoticons_dict)
		f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11=0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1
		tagged_tweet = tweets_tagged[i]
		tree = Tree('ROOT',([]))
		tokenize_tweet = tknzr.tokenize(tweet)
		tagged_dict=collections.defaultdict(str)
		prev_tag=''
		#build a dictioanry of tagged tweet
		tagged_tweet= tagged_tweet.split(' ')
		for word in tagged_tweet:
			lista = word.split('_')
			if len(lista)==2:
				tagged_dict[str(lista[0])] = str(lista[1])
		
		for j in range(0,len(tokenize_tweet)):
			if len(tokenize_tweet[j])==1 and ord(tokenize_tweet[j]) not in range(0,128):
				continue
			else:
				tokenize_tweet[j] = str(tokenize_tweet[j])
			
			if tokenize_tweet[j]=='@Fernando':
				tokenize_tweet[j] ='||T||'
				f7+=1.0
				prev_tag = 'target'
				tree.append('||T||')
				continue
			if not re.match(r'[a-zA-Z]+',tokenize_tweet[j])==None and not tokenize_tweet[j] == repeated_sequence(tokenize_tweet[j]):
				tree.append('||EMP||')
				prev_tag = 'emp'
				continue
			if tokenize_tweet[j]=='U':
				prev_tag = 'link'
				tokenize_tweet[j]='||U||'
				f7+=1.0
				tree.append('||U||')
				continue
			if tokenize_tweet[j].lower() in abbr_dictionry:
				prev_tag = 'slang'
				abbrev = abbr_dictionry[tokenize_tweet[j].lower()]
				tokenize_tweet[j]= abbrev
				abbrev = abbrev.split(' ')
				f6+=1.0
				f10+=1.0
				tree.append('||SLANG||')
				continue
			if tokenize_tweet[j] =='NOT':
				f2+=1.0
				f10+=1.0
				tree.append('||NOT||')
				prev_tag = 'not'
				continue
			if tokenize_tweet[j] in str(stopWords["stop"]):
				prev_tag = 'stop'
				subtree = Tree("STOP",([tokenize_tweet[j]]))
				tree.append(subtree)
				continue
			if tokenize_tweet[j] == '!':
				if prev_tag =='polar':
					f4+=1.0	
				f11=1.0
				prev_tag = 'exec'
				tree.append('EXEC')
				continue
			if tokenize_tweet[j] =='EXTREMELYPOSITIVE':
				f3+=4.0
				tree.append('||EP||')
				continue
			if tokenize_tweet[j] =='POSITIVE':
				f3+=3.0
				tree.append('||P||')
				continue
			if tokenize_tweet[j] =='NEGATIVE':
				f3+=--3.0
				tree.append('||N||')
				continue
			if tokenize_tweet[j] =='EXTREMELYNEGATIVE':
				f3+=-4.0
				tree.append('||EN||')
				continue	
			if tokenize_tweet[j] == 'NEUTRAL':
				f3+=0.0
				tree.append('||NEUTRAL||')
				continue

			if tokenize_tweet[j].startswith('#'):
				prev_tag = 'hash'
				f4+=1.0
				f7+=1.0
				tokenize_tweet[j] =str(tokenize_tweet[j].split('#')[1])
				tree.append('HASTAG')
				
			
			elif not re.match(r'[a-zA-Z]+',tokenize_tweet[j])==None:
				child =[]
				if tokenize_tweet[j].isupper() == True:
					child.append('||CAPS||')
				tokenize_tweet[j] = tokenize_tweet[j].lower()
				if tokenize_tweet[j] in tagged_dict:
					child.append(tagged_dict[tokenize_tweet[j]])
					

				child.append(tokenize_tweet[j])
				Synsets= swn.senti_synsets(tokenize_tweet[j])
				word_set=[]
				if len(Synsets) ==0:
					word_set = wn.synsets(tokenize_tweet[j])

					if len(word_set)==0:
						Synsets=[]

					else:
						for syn_set in word_set:
							if len(swn.senti_synsets(syn_set))>0:
								Synsets = swn.senti_synsets(syn_set)
								break
             
				if len(Synsets)>0:
					prev_tag = 'polar'
					if tokenize_tweet[j].isupper()==True:
						f4+=1.0
					Synset = Synsets[0]
					#print "This is synset",Synset
					if Synset.pos_score() > Synset.neg_score():
						if tagged_dict[tokenize_tweet[j]] == "NN" or tagged_dict[tokenize_tweet[j]] == "JJ" or tagged_dict[tokenize_tweet[j]] == "RB" or tagged_dict[tokenize_tweet[j]] == "VB":
							f8+=Synset.pos_score()
						f9+=Synset.pos_score()						
						f1+=-1.0
						f2+=-1.0
						child.append("||P||")
					elif Synset.neg_score()> Synset.pos_score():
						if tagged_dict[tokenize_tweet[j]] == "NN" or tagged_dict[tokenize_tweet[j]] == "JJ" or tagged_dict[tokenize_tweet[j]] == "RB" or tagged_dict[tokenize_tweet[j]] == "VB":
							f8+=Synset.neg_score()	
						f9-=Synset.neg_score()	
						f1+=-1.0
						f2+=-1.0
						child.append("||N||")
					else:
						if tagged_dict[tokenize_tweet[j]] == "NN" or tagged_dict[tokenize_tweet[j]] == "JJ" or tagged_dict[tokenize_tweet[j]] == "RB" or tagged_dict[tokenize_tweet[j]] == "VB":
							f8+=Synset.obj_score()

						f9+=Synset.obj_score()							
						#just for clarity
						f1+=0.0
						child.append("||NEUT||")
				else:
					prev_tag = 'non-polar'
					child.append("||NON-POLAR||")
					f6+=1.0
					if tokenize_tweet[j].isupper() == True:
						f10+=1.0
						f11=1
					if tokenize_tweet[j] in tagged_dict:
						if tagged_dict[tokenize_tweet[j]] == "NN" or tagged_dict[tokenize_tweet[j]] == "JJ" or tagged_dict[tokenize_tweet[j]] == "RB" or tagged_dict[tokenize_tweet[j]] == "VB":
							f5+=1.0

				subtree = Tree('EW',(child))
				tree.append(subtree)
				continue
			else:
				prev_tag ='NE'
				if tokenize_tweet[j].isupper() == True:
					f10+=1.0
				stree = Tree("NE",([tokenize_tweet[j]]))
				tree.append(stree)
		tweet = ' '.join(tokenize_tweet)
		featureVector = getFeatureVector(tweet)
		featureList.extend(featureVector)
		tweets.append((featureVector,sentiment))

		feature_vector.append([f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11])
		#print len(feature_vector)
		tree_list.append(tree)
		#writer.write("||BT||"+tree.pformat(parens="()")+"||ET||"+"\n")

	featureList = list(set(featureList))

	feature_SVM_Vector =getSVMFeatureVectorAndLabels(tweets,featureList)

	for i in range(0,len(feature_SVM_Vector['feature_vector'])):
		feature_SVM_Vector['feature_vector'][i].extend(feature_vector[i])

	writethis =' '
	for i in range(0,len(train)):
		for j in range(0,len(feature_SVM_Vector['feature_vector'][i])):
			if feature_SVM_Vector['feature_vector'][i][j] !=0:
				writethis  =writethis+str(j)+":"+str(feature_SVM_Vector['feature_vector'][i][j])+" "
		writer_tree.write(str(tweets[i][1])+" "+"|BT|"+" "+' '.join(tree_list[i].pformat(parens="()").split())+" "+"|ET|"+writethis+"\n")
		write_vector.write(str(tweets[i][1])+" "+writethis)


	writer2.close()
	write_vector.close()
	reader.close()
	writer_tree.close()
	#buildvectors(tree_list)

#calling the function
preprocess_tweet()






