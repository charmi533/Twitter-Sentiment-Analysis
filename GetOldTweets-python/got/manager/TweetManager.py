import urllib,urllib2,json,re,datetime,sys,cookielib, os
from .. import models
from pyquery import PyQuery
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from functools import wraps
import time
from retrying import retry
import cyberoam_login
import re
import codecs
import pickle

	
def visible(element):
	if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
		return False
	elif re.match('<!--.*-->', str(element.encode('utf-8'))):
		return False
	return True

class TweetManager:
	
	def __init__(self):
		pass
	

		
	@staticmethod
	def getTweets(tweetCriteria, receiveBuffer = None, bufferLength = 100, refreshCursor = '', cachefile = None):
		
	
		results = []
		resultsAux = []
		cookieJar = cookielib.CookieJar()

		"""if os.path.exists(cachefile+'.results'):
			results_file = codecs.open(cachefile+'.results', 'rb')
			while True:
				try:
					resultsAux.append(pickle.load(results_file))
				except EOFError:
					break"""
		
		if hasattr(tweetCriteria, 'username') and (tweetCriteria.username.startswith("\'") or tweetCriteria.username.startswith("\"")) and (tweetCriteria.username.endswith("\'") or tweetCriteria.username.endswith("\"")):
			tweetCriteria.username = tweetCriteria.username[1:-1]

		active = True
		#results_file = codecs.open(cachefile+'.results', 'a')
		while active:

			json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar)
			if len(json['items_html'].strip()) == 0:
				break

			refreshCursor = json['min_position']
					
			tweets = PyQuery(json['items_html'])('div.js-stream-tweet')
			
			if len(tweets) == 0:
				break
			
			for tweetHTML in tweets:
				tweetPQ = PyQuery(tweetHTML)
				tweet = models.Tweet()

				usernameTweet = tweetPQ.attr('data-screen-name')

				
				soup = BeautifulSoup(tweetPQ("p.tweet-text").html(), "lxml")
				#txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'));
				txt = re.sub(r"\s+", " ", soup.get_text().replace('# ', '#').replace('@ ', '@').replace('"', ""));			


				retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
				favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
				dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"));
				id = tweetPQ.attr("data-tweet-id");
				permalink = tweetPQ.attr("data-permalink-path");
				
				geo = ''
				geoSpan = tweetPQ('span.Tweet-geo')
				if len(geoSpan) > 0:
					geo = geoSpan.attr('title')
				
				tweet.id = id
				tweet.permalink = 'https://twitter.com' + permalink
				tweet.username = usernameTweet
				tweet.text = txt
				tweet.date = datetime.datetime.fromtimestamp(dateSec)
				tweet.retweets = retweets
				tweet.favorites = favorites
				tweet.mentions = " ".join(re.compile('(@\\w*)').findall(txt))
				tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(txt))
				tweet.geo = geo
				
				results.append(tweet)
				resultsAux.append(tweet)
				#pickle.dump(tweet, results_file, pickle.HIGHEST_PROTOCOL)
				
				if receiveBuffer and len(resultsAux) >= bufferLength:
					receiveBuffer(resultsAux)
					resultsAux = []
					#os.remove(cachefile+'.results')

				
				if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
					active = False
					break

				
			"""resume_file = codecs.open(cachefile, "w+", "utf-8")
			resume_file.write("%s\n" % refreshCursor)
			resume_file.close()"""
			#sleep(randint(10,30))
					
		
		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux)
			"""if os.path.exists(cachefile+'.results'):
				os.remove(cachefile+'.results',)
			if os.path.exists(cachefile):
				os.remove(cachefile)"""
		
		return results

	
	@staticmethod
	def getJsonReponse(tweetCriteria, refreshCursor, cookieJar):
		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&max_position=%s"
		
		urlGetData = ''
		if hasattr(tweetCriteria, 'username'):
			urlGetData += ' from:' + tweetCriteria.username
			
		if hasattr(tweetCriteria, 'since'):
			urlGetData += ' since:' + tweetCriteria.since
			
		if hasattr(tweetCriteria, 'until'):
			urlGetData += ' until:' + tweetCriteria.until
			
		if hasattr(tweetCriteria, 'querySearch'):
			urlGetData += ' ' + tweetCriteria.querySearch

		if hasattr(tweetCriteria, 'topTweets'):
			if tweetCriteria.topTweets:
				url = "https://twitter.com/i/search/timeline?q=%s&src=typd&max_position=%s"

		url = url % (urllib.quote(urlGetData), refreshCursor)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		retries = 4
		count = 0
		for x in range(retries):
			try:
				response = opener.open(url)
				jsonResponse = response.read()
				break
			except urllib2.URLError, e:
				print (e)
				errorno = re.findall(r'\d+', str(e.reason))[0]
				if errorno == '104':
					if count == 1:
						cyberoam_login.login()
						count = 0
					else:
						count = count + 1
				else:
					sleep(randint(10, 20))

				if x == retries - 1:
					print "Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.quote(urlGetData)
					sys.exit()
					return
		
		"""try:
			response = opener.open(url)
			jsonResponse = response.read()
		except urllib2.URLError, e:
			print (e)
			errorno = re.findall(r'\d+', str(e.reason))[0]
			if errorno == '104':
				count = count + 1
			else:
				sleep(randint(10, 20))
			try:
				response = opener.open(url)
				jsonResponse = response.read()
			except urllib2.URLError, e1:
				print(e1)
				errorno1 = re.findall(r'\d+', str(e1.reason))[0]
				if count == 1 and errorno1 == '104':
					cyberoam_login.login()
					print 'Cyberoam login succesful'
					response = opener.open(url)
					jsonResponse = response.read()
					count = 0
				else:
					print "Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.quote(urlGetData)
					sys.exit()
					return"""
		
		dataJson = json.loads(jsonResponse)
		
		return dataJson		
