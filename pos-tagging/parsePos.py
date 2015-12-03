import re
from treetagger import TreeTagger
import sys

languages = ['en', 'nl', 'it', 'es', 'sl', 'de', 'pl', 'sk', 'fr']
englishWordPositions = {}
tagDictMap = {}
taggerMap = {}
def main():
	global tagDictMap, taggerMap

	parser = argparse.ArgumentParser(description='Parse POS data')
	parser.add_argument('--input-file', help='Files containing POS info')
	args = parser.parse_args()

	output = open('tagged.all','w')
  	errors = open('errors.txt','w')
	tagLang(languages)
	trainingInstances = []
	with open(args.input_file) as file:
		lines = file.readlines()
		lines = [line.replace('\n', '') for line in lines]
		i = 0
		englishLine = True
		words = {}
		for lang in languages:
			words[lang] = []
		while (i < len(lines)):
			print i/27
			probMap = {}
			if (lines[i] != '!@#$%^&*()'):
				for lang in languages:
					print lang
					sentence = lines[i]
					probString = tagWrite(sentence, tagDictMap[lang], taggerMap[lang], lang, output, errors)
	 				#print 'Sentence ' + sentence
					#print 'Prob ' + probString
					i = i + 2
					if (englishLine == False):
						alignmentString = lines[i]
						i = i + 1
						wordTuples = parseSource(sentence, probString, alignmentString)
						words[lang] = words[lang] + wordTuples
					else:
						wordTuples = parseEnglish(sentence, probString)
						words[lang] = words[lang] + wordTuples
						englishLine = False

			else:
				englishLine = True
				trainingInstances.append(words)
				for lang in languages:
					words[lang] = []
				i = i + 1
			sys.stdout.flush()
		print 'Done'

def tagWrite(line, tagDict, tagger, langCode, output, errors):
  tags = tagger.tag(line)
  words = line.split()
  probabilities = getProbabilitiesForWords(tags, words, tagDict)
  returnStr = ""
  for probString in probabilities:
  	returnStr += probString.encode('utf-8') + '\t'
  return returnStr

def getToken(tagElement):
	return tagElement[0].encode('utf-8')


def getProbabilitiesForWords(tags, words, tagDict):
	wordCounter = 0
	tagCounter = 0
	probabilities = ['' for i in range(len(words))]
	universalTags = []
	while (wordCounter < len(words) and tagCounter < len(tags)):
		if words[wordCounter] == getToken(tags[tagCounter]):
			probabilities[wordCounter] = getProbabilityString(tags, tagCounter, tagDict)
			wordCounter += 1
			tagCounter += 1
		else:
			if (len(getToken(tags[tagCounter]).split()) > 1):
				for token in getToken(tags[tagCounter]).split()[::-1]:
					arrrayToInsert = tags[tagCounter][1:]
					arrrayToInsert = [token.decode('utf-8')] + arrrayToInsert
					tags.insert(tagCounter + 1, arrrayToInsert)
				tagCounter += 1
			elif (getToken(tags[tagCounter]) in words[wordCounter]):
				probString = getProbabilityString(tags, tagCounter, tagDict)
				probabilities[wordCounter] = probString
				wordCounter += 1
				tagCounter += 1
				while(wordCounter < len(words) and tagCounter < len(tags) and getToken(tags[tagCounter]) != words[wordCounter]):
					tagCounter += 1
			else:
				print words[wordCounter], getToken(tags[tagCounter])
	return probabilities

def getProbabilityString(tags, tagCounter, tagDict):
	outputStr = ""
	for tag in tags[tagCounter][1:]:
		oldTag = tag.split()[0]
		prob = tag.split()[-1]
		try:
			universalTag = tagDict[oldTag]
		except KeyError:
			print oldTag+" not found in"+"tag dictionary.\n"
			universalTag = oldTag
		outputStr += universalTag+ " " + prob + " "
	return outputStr


def tagLang(langs):
  global tagDictMap, taggerMap
  if "fr" in langs:
    frTagDict = convertTags('fr-treetagger.map')
    frTagger = TreeTagger(encoding='utf-8',language='french')
    tagDictMap['fr'] = frTagDict
    taggerMap['fr'] = frTagger
  if "sl" in langs:
    slTagDict = convertTags('sl-treetagger.map')
    slTagger = TreeTagger(encoding='utf-8',language='slovenian')
    tagDictMap['sl'] = slTagDict
    taggerMap['sl'] = slTagger
  if "de" in langs:
    deTagDict = convertTags('de-tiger.map')
    deTagger = TreeTagger(encoding='utf-8',language='german')
    tagDictMap['de'] = deTagDict
    taggerMap['de'] = deTagger
  if "it" in langs:
    itTagDict = convertTags('it-treetagger.map')
    itTagger = TreeTagger(encoding='utf-8',language='italian')
    tagDictMap['it'] = itTagDict
    taggerMap['it'] = itTagger
  if "pl" in langs:
    plTagDict = convertTags('pl-treetagger.map')
    plTagger = TreeTagger(encoding='utf-8',language='polish')
    tagDictMap['pl'] = plTagDict
    taggerMap['pl'] = plTagger
  if "sk" in langs:
    skTagDict = convertTags('sk-treetagger.map')
    skTagger = TreeTagger(encoding='utf-8',language='slovak')
    tagDictMap['sk'] = skTagDict
    taggerMap['sk'] = skTagger
  if "es" in langs:
    esTagDict = convertTags('es-treetagger.map')
    esTagger = TreeTagger(encoding='utf-8',language='spanish')
    tagDictMap['es'] = esTagDict
    taggerMap['es'] = esTagger
  if "nl" in langs:
    nlTagDict = convertTags('nl-treetagger.map')
    nlTagger = TreeTagger(encoding='utf-8',language='dutch')
    tagDictMap['nl'] = nlTagDict
    taggerMap['nl'] = nlTagger
  engTagger = TreeTagger(encoding='utf-8',language='english')
  taggerMap['en'] = engTagger
  engTagDict = convertTags('en-ptb.map')
  tagDictMap['en'] = engTagDict
  output = open('tagged.all','w')
  errors = open('errors.txt','w')
  numLines = 0

def convertTags(filename):
  posConvert = open("../universal-tags/"+filename,"r")
  tagDict = {}
  for line in posConvert:
    oldTag, newTag = line.split("\t")
    tagDict[oldTag] = newTag.strip()
  return tagDict


def parseSource(sentence, probString, alignmentString):
	global englishWordPositions
	words = re.split(r'\t', sentence)
	#print 'sourceWords coming up'
	#print words
	#print len(words)
	alignments = [re.split('~', x) for x in re.split(r'\t', alignmentString)]
	alignments = alignments[0:len(alignments)-1]
	tuples = []
	i = 1
	probStrings = re.split('\t', probString)
	probStrings = probStrings[0:len(probStrings) - 1]
	#print 'probStrings coming up'
	#print probStrings
	#print len(probStrings)
	for probDist in probStrings:
		if (len(probDist) == 0):
			continue
		probMap = getProbMapFromString(probDist)
		englishPosition = 0
		englishWord = []
		for alignment in alignments:
			if str(i) in alignment:
				englishWord = englishWord + [englishWordPositions[englishPosition]]
			englishPosition = englishPosition + 1
		
		tuples = tuples + [tuple([words[i-1], probMap, englishWord])]	
		i = i + 1
	return tuples

def parseEnglish(sentence, probString):
	global englishWordPositions
	words = re.split(r'\t', sentence)
	#print 'englishWords coming up'
	#print words
	#print len(words)
	englishWordPositions = {}
	tuples = []
	for i in range(len(words)):
		englishWordPositions[i] = words[i]
	i = 0
	for probDist in re.split('\t', probString):
		if (len(probDist) == 0 or probDist[len(probDist) - 1] == '\n'):
			continue
		probMap = getProbMapFromString(probDist)
		englishWord = [words[i]]
		tuples = tuples + [tuple([words[i], probMap, englishWord])]
		i = i + 1
	return tuples

def getProbMapFromString(probString):
	distElems = re.split(' ', probString)
	distElems = distElems[0:len(distElems)-1]
	j = 0
	probMap = {}
	while (j < len(distElems)):
		if (distElems[j] == '\n'):
			j = j + 2
			continue
		if (distElems[j] in probMap):
			probMap[distElems[j]] = probMap[distElems[j]] + (float)(distElems[j+1])
		else:
			probMap[distElems[j]] = (float)(distElems[j+1])
		j = j + 2
	return probMap;

if __name__ == "__main__": main()