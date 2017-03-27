import re
import nltk
import sklearn
import pandas as pd 
import numpy as np
import sklearn.svm
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
def processTweet(tweet):
	tweet = tweet.lower()
	tweet = re.sub(r'{(\s)*link(\s)*}','||U||',tweet)
	tweet = re.sub(r'@(\s)*(\w)+','||T||',tweet)
	tweet = re.sub(r'[\s]+',' ',tweet)
	tweet = re.sub(r'#(\s)*(\w)+',r'\2',tweet)
	tweet = tweet.strip('\'"')
	return tweet

def replace2ormorewords(word):
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
		word = replace2ormorewords(word)
		word = word.strip('\'"?,.')
		val = re.search(r'^[a-zA-Z][a-zA-Z0-9]*$',word)
		if word in StopWords or val is None:
			continue

		else:
			featureVector.append(word.lower())
	return featureVector

def findmaximumArg(train,i):
	maximum = max(train["s2"][i],train["s3"][i],train["s4"][i])
	if maximum == train["s2"][i]:
		return 2
	if maximum == train["s3"][i]:
		return 3
	if maximum == train["s4"][i]:
		return 4

def extract_features(featureList,tweet):
	print tweet
	tweet_words = set(tweet)

	features ={}
	for word in featureList:
		print word
		features['contains(%s)' %word] =(word in tweet_words)

	return features
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
            word = replace2ormorewords(word)
            word = word.strip('\'"?,.')
            if word in map:
                map[word] = 1
        values = map.values()
        feature_vector.append(values)
        labels.append(tweet_opinion)
    #return the list of feature_vector and labels
    return {'feature_vector' : feature_vector, 'labels': labels}




def getFeaturesAndClassification():
	train = pd.read_csv('train.csv')
	train = train[["tweet","s2","s3","s4"]]
	tweets =[]
	featureList =[]
	for i in range(0,len(train)):
		print "Now Processing tweet",train["tweet"][i]
		sentiment = findmaximumArg(train,i)
		tweet = train["tweet"][i]
		processedTweet = processTweet(tweet)
		featureVector = getFeatureVector(processedTweet)
		featureList.extend(featureVector)
		tweets.append((featureVector,sentiment))

	featureList = list(set(featureList))
	 
	feature_SVM_Vector =getSVMFeatureVectorAndLabels(tweets,featureList)

	print len(feature_SVM_Vector['feature_vector']),len(feature_SVM_Vector['labels'])

	X_train, X_test, y_train, y_test = train_test_split(feature_SVM_Vector['feature_vector'],feature_SVM_Vector['labels'],test_size=0.25,random_state=0)

	clf = svm.SVC(kernel ='linear',C=1).fit(X_train,y_train)

	print clf.score(X_test,y_test)


getFeaturesAndClassification()









