import Agarwal

def write_files(infile):
	x = infile.split('.csv')
	tagged_filename = x[0]+'_tagged_tweets.txt'
	Agarwal.tag_tweets(infile, tagged_filename)

	features_filename = x[0]+'_features.csv'
	Agarwal.senti_features(infile, features_filename, tagged_filename)

def run_svm():
	