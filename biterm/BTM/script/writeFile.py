
import numpy as np
import pandas as pd
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn
import re
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import string
import collections
import urllib2
from bs4 import BeautifulSoup
from bs4 import NavigableString



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
        soup = BeautifulSoup(response, 'lxml')
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

def clean_tweet(tweet, slang_dict):
    #remove urls
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r'pic.twitter\S+', '', tweet)
    
    #remove hashtags and mentions
    tweet = re.sub(r'#\S+', '', tweet)
    tweet = re.sub(r'@\S+', '', tweet)

    stopset = stopwords.words('english') + list(string.punctuation)
    tokeniser = TweetTokenizer()
    tweet_tokens = tokeniser.tokenize(tweet.lower())
    tokens = [i for i in tweet_tokens if i not in stopset and len(i) > 2]
    tweet = ' '.join(tokens)
    print tweet

    return tweet

if __name__ == '__main__':
    input_dir='../input_data'
    slang_dict = buildSlangDictionary()

    tweets = pd.read_csv('{0}/output_got_Dec.csv'.format(input_dir), delimiter='\t', quotechar='"')

    text = tweets['text']
    text = text.str.decode('utf-8')
    text = text.str.encode('ascii', errors='ignore')

    text_clean = text.apply(clean_tweet,args=(slang_dict,))

    indexes = []
    for i in range(len(text_clean)):
        tokens = text_clean[i].split()
        

        for x in tokens:
            if x.isdigit():
                text_clean[i] = text_clean[i].replace(x, '')
        text_clean[i] = str(text_clean[i]).strip()
        if len(tokens) < 3:
            indexes.append(i)
        if re.search(r'[A-Za-z]', text_clean[i]) == None:
            indexes.append(i)
        text_clean[i] = re.sub(r'\s+', ' ', text_clean[i])
        
    text_clean.drop(indexes, inplace=True)
    del indexes

    tweets['text'] = text_clean
    tweets['text'].to_csv('{0}/tweet_text.csv'.format(input_dir), sep='\t', index=False, header=False)