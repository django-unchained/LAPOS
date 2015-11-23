import re 
import json
import string
import argparse
import os

def getAlignments(str):
	alignmentString = re.findall(r'\({[0-9 ]*}\)', str)
	alignments = []
	for alignment in alignmentString:
		positions = []
		for delim in ['{','}','(',')']:
			alignment = alignment.replace(delim, '')
		for number in alignment.strip().split(' '):
			if (number!=''):
				positions.append(int(number))
			else:
				positions.append(-1)
		alignments.append(positions)
	return alignments

def getWords(str):	
	return [str.strip() for str in re.split(r'\({[0-9 ]*}\)', str) if str.strip() != 'NULL']

def encodeAlignments(arr):
	s = ""
	for elem in arr:
		s = s + ','
		for i in range(0,len(elem)-2):
			s = s + str(elem[i]) + '~'
		s = s + str(elem[len(elem)-1])
	return s[1:len(s)]

def main():
	#print 'Compiling common sentences'
	parser = argparse.ArgumentParser(description='Aggregate language data')
	parser.add_argument('--input-datapath', help='Path where input files with the specified extension can be found')
	parser.add_argument('--output-file', help='File where output is stored')
	parser.add_argument('--all-sentences', action='store_true',
		default=False, help='Use all sentences in the corpus. Default is False')
	parser.add_argument('--input-file-extension', default=".final", help='Default extension is .final')
	args = parser.parse_args()

	europarl_files = [file for file in os.listdir(args.input_datapath) if file.endswith(args.input_file_extension)]
	if len(europarl_files) == 0:
		print 'No input files found'
		return

	corpusSentences = set()

	language_file = open(args.input_datapath+'/'+europarl_files[0], 'r')
	lines = language_file.readlines()
	for i in range(0, len(lines), 3):
		corpusSentences.add(tuple(getWords(lines[i+2])))
	for file in europarl_files:
		language_file = open(args.input_datapath+'/'+file, 'r')
		lines = language_file.readlines()
		sentences = set()
		for i in range(0, len(lines), 3):
			sentences.add(tuple(getWords(lines[i+2])))
		if args.all_sentences:
			corpusSentences = corpusSentences.union(sentences)
		else:
			corpusSentences = corpusSentences.intersection(sentences)
	print 'Finished compiling ' + str(len(corpusSentences)) + ' sentences'

	print 'Populating data'
	data = {}
	for file in europarl_files:
		language_file = open(args.input_datapath+'/'+file, 'r')
		lines = language_file.readlines()
		print file
		for i in range(0, len(lines), 3):
			words = getWords(lines[i+2])
			if (tuple(words) in corpusSentences):
				metadata = lines[i]
				sentence = lines[i+1]
				alignments = getAlignments(lines[i+2])
				language = file[3:5]
				if (tuple(words) in data.keys()):
					entryArray = data[tuple(words)]
					#entryArray.append(tuple([metadata, sentence, alignments]))
					entryArray.append(tuple([language, sentence, alignments]))
					data[tuple(words)] = entryArray
				else:
					#data[tuple(words)] = [tuple([metadata, sentence, alignments, words])]
					data[tuple(words)] = [tuple([language, sentence, alignments])]

	outFile = open(args.output_file, 'w')
	print 'Writing output'
	for key in data.keys():
		languageSet = set()
		outFile.write(string.join(key))
		outFile.write('\n')
		for entry in data[key]:
			if (entry[0] not in languageSet):
				outFile.write("<"+ entry[0] + "> " + entry[1])
				outFile.write(encodeAlignments(entry[2]))
				outFile.write('\n')
				languageSet.add(entry[0])
		outFile.write('!@#$%^&*()')
		outFile.write('\n')
	outFile.close()

if __name__ == '__main__' : main()
