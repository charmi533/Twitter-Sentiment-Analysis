# -*- coding: utf-8 -*-

import sys,getopt,got,datetime,codecs, os

def main(argv):
  
  if len(argv) == 0:
    print 'You must pass some parameters. Use \"-h\" to help.'
    return
    
  if len(argv) == 1 and argv[0] == '-h':
    print """\nTo use this jar, you can pass the folowing attributes:
    username: Username of a specific twitter account (without @)
       since: The lower bound date (yyyy-mm-aa)
       until: The upper bound date (yyyy-mm-aa)
 querysearch: A query text to be matched
   maxtweets: The maximum number of tweets to retrieve

 \nExamples:
 # Example 1 - Get tweets by username [barackobama]
 python Exporter.py --username "barackobama" --maxtweets 1\n

 # Example 2 - Get tweets by query search [europe refugees]
 python Exporter.py --querysearch "europe refugees" --maxtweets 1\n

 # Example 3 - Get tweets by username and bound dates [barackobama, '2015-09-10', '2015-09-12']
 python Exporter.py --username "barackobama" --since 2015-09-10 --until 2015-09-12 --maxtweets 1\n
 
 # Example 4 - Get the last 10 top tweets by username
 python Exporter.py --username "barackobama" --maxtweets 10 --toptweets\n"""
    return

  filename = ''
  try:
    #print argv
    opts, args = getopt.getopt(argv, "", ("username=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=", "outputfile="))
    
    tweetCriteria = got.manager.TweetCriteria()
    
    for opt,arg in opts:
          
      if opt == '--username':
        tweetCriteria.username = arg
        
      elif opt == '--since':
        tweetCriteria.since = arg

      elif opt == '--until':
        tweetCriteria.until = arg
        
      elif opt == '--querysearch':
        tweetCriteria.querySearch = arg
        
      elif opt == '--toptweets':
        tweetCriteria.topTweets = True
        
      elif opt == '--maxtweets':
        tweetCriteria.maxTweets = int(arg)
                
      elif opt == '--outputfile':
        filename = arg
    
    if filename == '':
      print '\nEnter the filename with one or more characters'
      return


    if not os.path.exists(filename):
      outputFile = codecs.open(filename, "w+", "utf-8")
      outputFile.write('"username"\t"date"\t"retweets"\t"favorites"\t"text"\t"geo"\t"mentions"\t"hashtags"\t"id"\t"permalink"')
    else:
      outputFile = codecs.open(filename, "a", "utf-8")
    print 'Searching...\n'
    
    def receiveBuffer(tweets):
      for t in tweets:
        outputFile.write(('\n"%s"\t"%s"\t%d\t%d\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink)))
      outputFile.flush();
      print 'More %d saved on file...\n' % len(tweets)

    cachefile_path = '/home/charmi533/Desktop/Btp/code/GetOldTweets-python/'+filename+'.cache'
    got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, cachefile=cachefile_path)
    """if not os.path.exists(cachefile_path):
      got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, cachefile=cachefile_path)
    else:
      cachefile = codecs.open(cachefile_path, 'r')
      refreshCursor = cachefile.read()
      got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, refreshCursor=refreshCursor, cachefile=cachefile_path)"""
    
  except arg:
    print 'Arguments parser error, try -h' + arg
  finally:
    outputFile.close()
    print 'Done. Output file generated "%s".'%filename

if __name__ == '__main__':
  if len(sys.argv) > 1:
  	main(sys.argv[1:])