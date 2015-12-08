import csv


class FeatureExtractor:
  def transitionFeatures(self, target, source):
    '''
    -Target and source langs need to be iso codes from ethnologue
    -KeepIndexes can be varied to include different features.
    -Output: {languageCode : {'FEATURE_NAME': 1, 'FEATURE_NAME': 0.5, 'FEATURE_NAME': 0}}
    -0.5 means that the URIEL group is unsure about the feature in that language.
    '''
    walsDirectory = "URIEL/wals.csv"
    keepIndexes = [3,7,8,9,10,11,12,16,22,24,26,27,29,33,34,35,36,40,42,45,57,59,60,72,75,83,84,85,89,90,91,97]
    wals = {}
    with open(walsDirectory,"rb") as infile:
      reader = csv.reader(infile)
      header = reader.next()
      for row in reader:
      	languageCode = row[0]
        if (languageCode in source) or (languageCode in target):
          wals[languageCode] = {}
          for i in keepIndexes:
            wals[languageCode][header[i]] = row[i]
    return wals