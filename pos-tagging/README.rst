Treetagger + Probabilities
=================

Parses the alignment aggregator output, tags each line, and converts the tags to the universal POS tags. The output is a tsv.

Dependencies
------------
-  `TreeTagger <http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/>`__
-  `TreeTagger-Python <https://github.com/miotto/treetagger-python/>`__
-  `NLTK <http://nltk.org/>`__

Installation
------------
Make sure that Treetagger is setup correctly. Download all parameter files for languages that you expect to tag. Modify all of the cmd/tree-tagger-language files so that the options are as follows:
::

    OPTIONS="-token -lemma -sgml -prob -threshold .000000000001 -no-unknown"

This ensures that the tagger will output several tag probabilities per word. 

Additionally, correct the paths to bin, cmd and lib specified in tree-tagger-polish (and possibly other language taggers) within the cmd folder.

For Treetagger-Python: In the ``treetagger.py`` file, add the path to these cmd/tree-tagger-language files. Pip install Treetagger-Python (upgrade if necessary).

Usage
------------
::

    python parse-common.py -i common.txt
