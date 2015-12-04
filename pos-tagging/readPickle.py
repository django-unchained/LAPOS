import pickle
import argparse

def main():
	parser = argparse.ArgumentParser(description='Sample code to read pickle file')
	parser.add_argument('--pickle-file', help='Input pickle file', required=True)
	args = parser.parse_args()
	
	print 'Reading file'
	f = open(args.pickle_file, 'rb')
	dataStructure = pickle.load(f)
	print 'Printing data structure'
	print dataStructure
if __name__=="__main__":main()