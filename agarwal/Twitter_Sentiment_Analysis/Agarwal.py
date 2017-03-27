
# coding: utf-8

# In[1]:

from bs4 import BeautifulSoup
from bs4 import NavigableString
import re
import string
import nltk.tree
import nltk.tokenize
import nltk.corpus
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.tokenize import TweetTokenizer
from nltk.tree import *
import csv
import pandas as pd
import collections
import urllib2
import numpy as np
from sklearn import svm
from sklearn.svm import SVC


# In[2]:

def buildSlangDictionary():
    alpha = list(map(chr, range(ord('a'), ord('z')+1)))
    url = 'http://www.noslang.com/dictionary/'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
        'Accept-Charset': "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        'Accept-Encoding': 'none',
        'Connection': "keep-alive"
    }
    slang_dict = collections.defaultdict(str)
    for letter in alpha:
        url = url + letter + '/'
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response)
        abbr_list = []
        for abbr in soup.findAll('abbr'):
            abbr_list.append(abbr)
        for x in abbr_list:
            temp = x.contents[0].contents[0].contents
            if isinstance(temp[0], NavigableString):
                slang = ''.join(temp)
                slang = slang.encode('ascii', 'ignore')
                slang = slang.split(' :')[0]
                meaning = x['title']
                slang_dict[slang] = meaning
        url = url[:-2]
    return slang_dict


# In[3]:

def removeRepeatedSequence(word):
    pattern = re.compile(r'(.)\1{1,}',re.DOTALL)
    return pattern


# In[4]:

def getWordVector(tweet):
    wordVector = []
    with open('StopWords.txt', 'r') as f:
        stopWords = f.read().split('\n')[1:-1]
        f.close()
    words = tweet.split()
    for word in words:
        word = removeRepeatedSequence(word)
        word = word.strip('\'"?,.')
        s = re.search(r'^[a-zA-Z][a-zA-Z0-9]*$', word)
        if word.lower() in stopWords or s is None:
            continue
        else:
            wordVector.append(word.lower())
    return wordVector
    


# In[5]:

def preProcessTweet(tweet, emoji_dict):
    tweet = tweet.lower()
    negative_words = ['not','no','never','n\'t','cannot','isn\'t','isnt']
    tweet = re.sub(r'{(\s)*link(\s)*}','U',tweet)
    tweet = re.sub(r'@(\s)*(\w)+','@target',tweet)
    tweet = re.sub(r'[\s]+',' ',tweet)
    tweet = re.sub(r'#(\s)*(\w)+',r'\2',tweet)
    tweet = tweet.strip('\'"')
    
    tokeniser = TweetTokenizer() #Have to use something else as it is seperating the emoticon
    tweet_tokens = tokeniser.tokenize(tweet)
    for x in range(len(tweet_tokens)):
        token = tweet_tokens[x]
        if len(token) == 1 and ord(token) not in range(0,128):
            continue
        token = str(token)
        if token in negative_words:
            token = 'NOT'
        if token in emoji_dict:
            if emoji_dict[token] <= -3:
                token = 'EXTREMELY-NEGATIVE'
            if emoji_dict[token] > -3 and emoji_dict[token] < 0:
                token = 'NEGATIVE'
            if emoji_dict[token] == 0:
                token = 'NEUTRAL'
            if emoji_dict[token] > 0 and emoji_dict[token] < 3:
                token = 'POSITIVE'
            if emoji_dict[token] >= 3:
                token = 'EXTREMELY-POSITIVE'
        tweet_tokens[x] = token
    tweet = ' '.join(tweet_tokens)
    
    return tweet
                
        


# In[6]:

def buildUnigramVector(tweets, wordList):
    
    features = []
    sentiment = []
    for tweet in tweets:
        sentiment = 0
        wordMap = {}
        for word in sorted(wordList):
            wordMap[word] = 0
        
        tweetWords = tweet[0]
        for w in tweetWords:
            w = removeRepeatedSequence(w)
            w = w.strip('\'".,?')
            if w in wordMap:
                wordMap[w] = 1
            val = wordMap.values()
            features.append(val)
            sentiment.append(tweet[1])
    unigramVector = {'unigram_vector':features, 'sentiment': sentiment}
    return unigramVector
            


# In[ ]:

def sentiFeatures():
    slang_dict = DictionaryBuilder()
    negative_word_list =['not','no','never','n\'t','cannot']
    train = pd.read_csv("train.csv")

    with open('StopWords.txt', 'r') as f:
        stopWords = f.read().split('\n')[1:-1]
        f.close()
    
    emoticon_dict = collections.defaultdict(int)
    reader = csv.reader(open('emoticons.csv', 'r'), skipinitialspace=True)
    for row in reader:
        emoticon_dict[row[0].strip()] = int(row[1])
  
    prev_tag = ''
    tree_list =[]
    feature_vector =[]
    tweets_tagged =[]
    tokenizer = TweetTokenizer()
    for line in reader:
        tweets_tagged.append(line)

    featureList =[]

    tweets =[]
    for i in range(len(train)):
        tweet = train['tweet'][i]
        sentiment = train['sentiment'][i]
        
        tweet = preProcessTweet(tweet, emoticon_dict)
        f1, f2, f3, f4, f5, f6, f7, f9, f10, f11 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        tweet_tagged = tweets_tagged[i]
        
        tokens = tokenizer.tokenize(tweet)
        tagged_dict = collections.defaultdict(str)
        
        for word in tweet_tagged:
            if len(word.split('_') == 2):
                word, tag = word.split('_')
                tagged_dict[word] = tag
                
        for j in range(len(tokens)):
            token = tokens[j]
            if token == '!':
                f11=1.0
                if prev_tag == 'polar':
                    f4+=1.0
                continue
                
            if len(token) == 1 and ord(token) not in range(1, 128):
                continue
            else:
                token = str(token)
                
            if token == '@target':
                token = '||T||'
                f7+=1.0
                prev_tag = 'target'
                continue
            if token == 'U':
                token = '||U||'
                f7+=1.0
                prev_tag = 'link'
                continue
            if token.startswith('#'):
                f4+=1.0
                f7+=1.0
                prev_tag = 'hash'
                continue
            
            if not (re.match(r'a-zA-Z', token) != None or token != removeRepeatedSequence(token)):
                prev_tag = 'emp'
                continue
                
            if token in stopWords:
                prev_tag = 'stop'
                continue
                
            if token.lower() in slang_dict:
                prev_tag = 'slang'
                token = slang_dict[token.lower()]
                f6+=1.0
                continue
            
            if token == 'POSITIVE' or token == 'EXTREMENLY-POSITIVE' or token == 'NEGATIVE' or token == 'EXTREMELY-NEGATIVE':
                f3+=1.0
                continue
            
            if token == 'NOT':
                f2+=1.0
                continue
                
            synsets = swn.senti_synsets(token)
            if len(synsets) > 0:
                
                score = max([synset.pos_score(), synset.neg_score(), synset.obj_score()])
                if synset.pos_score() == synset.neg_score() or synset.obj_score() == score:
                    score = 0.0
                if synset.pos_score() < synset.neg_score():
                    score = -score
                
                if score != 0.0:
                    prev_tag = 'polar'
                    f2+=1.0
                    if token.isupper() == True:
                        f4+=1.0
                        f11=1.0
                    
                    f8 = {}
                    if token in tagged_dict and (tagged_dict[token] == 'JJ' or tagged_dict[token] == 'RB' or tagged_dict[token] == 'VB' or tagged_dict[token] == 'NN'):            
                        f1+=1.0
                        f8[tagged_dict[token]]+=score
                    else:
                        f9+=score
                else:
                    prev_tag = 'non-polar'
                    if token in tagged_dict and (tagged_dict[token] == 'JJ' or tagged_dict[token] == 'RB' or tagged_dict[token] == 'VB' or tagged_dict[token] == 'NN'):            
                        f5 += 1.0
                    if token.isupper():
                        f10 += 1.0
                        f11 = 1.0
                continue
            else:
                prev_tag = 'non-polar'
                if token in tagged_dict and (tagged_dict[token] == 'JJ' or tagged_dict[token] == 'RB' or tagged_dict[token] == 'VB' or tagged_dict[token] == 'NN'):            
                    f5 += 1.0
                if token.isupper():
                    f10 += 1.0
                    f11 = 1.0               
                continue
        tweet = ' '.join(tokens)
        word_vector = getWordVector(tweet)
        
        
        


# In[ ]:

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger('english-bidirectional-distsim.tagger') 

