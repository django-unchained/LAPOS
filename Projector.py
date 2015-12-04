import pickle
from os import walk


SENTENCE_KEY = 'sentence'
ALIGNMENT_KEY = 'alignment'
DISTRIBUTION_KEY = 'distribution'
ENGLISH = 'en'
ALIGNMENT_OVERLAP_THRESHOLD = 0.5

WORD_INDEX = 0
ALIGNMENT_INDEX = 2
PROBABILITY_LIST_INDEX = 1




def get_alignment_decision(lang1_eng_alignment_set, lang2_eng_alignment_set):
    if len(lang1_eng_alignment_set) == 0 or len(lang2_eng_alignment_set) == 0:
        return(False)
    if (len(set.intersection(lang1_eng_alignment_set, lang2_eng_alignment_set)) / (min(len(lang1_eng_alignment_set), len(lang2_eng_alignment_set)))) > ALIGNMENT_OVERLAP_THRESHOLD:
       return(True)
    else:
        return(False)

def get_source_alignments(instance, target_lang, source_langs, target_word_tuple):
    target_word_eng_alignments = set(target_word_tuple[ALIGNMENT_INDEX])
    alignment_dict = {}
    if len(target_word_eng_alignments == 0):
        return({})
    for source_lang in source_langs:
        source_lang_word_alignments = []
        source_sentence = instance[source_lang]
        for src_word_tuple in source_sentence:
            src_word_eng_alignments = set(src_word_tuple[ALIGNMENT_INDEX])
            if get_alignment_decision(target_word_eng_alignments, src_word_eng_alignments):
                source_lang_word_alignments.append(src_word_tuple)
        alignment_dict[source_lang] = source_lang_word_alignments
    return(alignment_dict)
"""
Returns
alignment for target word
map {-src_lang (for each source language)
        -[list of source word_tuples of source_words aligned to this target word]
    }
"""


def  conflate_distributions(source_lang_alignment):  #[input: list of source word_tuples of source words aligned to this target word]
    conflated_distribution = {}
    for source_word_tuple in source_lang_alignment:
        source_word_probability_map = source_word_tuple[PROBABILITY_LIST_INDEX]
        for pos in source_word_probability_map.keys():
            conflated_distribution[pos] = conflated_distribution.get(pos, 0) + source_word_probability_map[pos]
    normalizer_value = 0
    for pos in conflated_distribution.keys():
        normalizer_value += conflated_distribution.get(pos, 0)
    for pos in conflated_distribution.keys():
        conflated_distribution[pos] = conflated_distribution.get(pos, 0)/normalizer_value
    return(conflated_distribution)
#Returns a map from pos tag to normalized tag probability after simply adding all the probability values


def get_source_distributions(target_source_alignments):#Takes map{ source_lang: [list of source word tuples a target word is aligned to]}
    source_lang_distributions = {}
    for source_lang in target_source_alignments.keys():
        source_lang_alignment = target_source_alignments[source_lang]#List of word tuples
        conflated_distribution = conflate_distributions(source_lang_alignment)
        source_lang_distributions[source_lang] = conflated_distribution
    return(source_lang_distributions)
"""
Returns
{
    -src_lang
        -{distribution}
}
"""


"""
Process Corpus Procedure
For each instance in the corpus
    For each word in the target language
        Get all the words aligned to it from each source language
        Conflate the probability distributions asociated with all words aligned from each source language to get one distribution from each language
        Add to a list of projection instances within this sentence : tuple( target_word_tuple, source_distributions )
    Add sentence projection instances to the corpus list

returns:
list [

    (target_word_tuple, map of distributions from source languages)  ---> projection instance

]

"""
def process_corpus(corpus, target_lang, source_langs):
    sentence_level_projection_instances = []
    for instance in corpus:
        sentence_level_projection_instance = []#list of tuples of (target_word_tuple, map of distributions for source languages) for a target sentence
        target_sentence = instance[target_lang]
        for target_word_tuple in target_sentence:
            target_source_alignments = get_source_alignments(instance, target_lang, source_langs, target_word_tuple)#returns list of source language word tuples that this target word is aligned to
            if (len(target_source_alignments) == 0):#unaligned word, currently NOT considered in our accuracy calculations
                continue
            source_distributions = get_source_distributions(target_source_alignments)#conflates distributions of all source aligned words in this source language into one distribution
            sentence_level_projection_instance.append((target_word_tuple,source_distributions))
        sentence_level_projection_instances.append(sentence_level_projection_instance)
    return(sentence_level_projection_instances)

def get_actual_tags(word_projection_instance):# NEED TO DEAL WITH CASE WHEN MULTIPLE TAGS HAVE SAME PROBABILITY
    distribution = word_projection_instance[PROBABILITY_LIST_INDEX]
    max = -1
    actual_tags = []
    """
    Eventualy replace with itemgetter method. This implementation is just for readability and debugging
    """
    for pos in distribution.keys():
        if distribution[pos] > max:
            max = distribution[pos]
            actual_tags = [pos]
        elif distribution[pos] == max:
            actual_tags.append(pos)
    return(actual_tags)

def predict_tag(best_candidate_counts, best_candidate_max_probs):#Picks the highest probability tag among all those agreed upon by max no. of source languages
    tie_candidates = []
    tie_count = -1
    for pos_candidate in best_candidate_counts.keys():
        if best_candidate_counts[pos_candidate] > tie_count:
            tie_candidates = [pos_candidate]
        elif best_candidate_counts[pos_candidate] == tie_count:
            if best_candidate_max_probs[pos_candidate] > best_candidate_max_probs[tie_candidates[-1]]:
                tie_candidates = [pos_candidate]
            elif best_candidate_max_probs[pos_candidate] == best_candidate_max_probs[tie_candidates[-1]]:
                tie_candidates.append(pos_candidate)
    return(tie_candidates)

def get_predicted_tag(word_projection_instance):#Checks for pos tag with max agreement among all source languages
    source_distributions_dict = word_projection_instance[1]
    best_candidates_counts = {}
    best_candidate_max_probs = {}
    for source_lang in source_distributions_dict.keys():
        source_lang_distribution = source_distributions_dict[source_lang]
        max_prob = -1
        best_candidate = None
        for pos in source_lang_distribution.keys():
            if source_lang_distribution[pos] > max_prob:
                max_prob = source_lang_distribution[pos]
                best_candidate = pos
        best_candidates_counts[best_candidate] = best_candidates_counts.get(best_candidate, 0) + 1
        if best_candidate not in best_candidate_max_probs:
            best_candidate_max_probs[best_candidate] = max_prob
        else:
            current_max_prob = best_candidate_max_probs[best_candidate]
            if max_prob > current_max_prob:
                best_candidate_max_probs[best_candidate] = max_prob
    return(predict_tag(best_candidates_counts, best_candidate_max_probs))


def get_projection_score(sentence_level_projection_instance):
    tot_correct = 0
    tot = 0
    for word_projection_instance in sentence_level_projection_instance:
        actual_tag = get_actual_tags(word_projection_instance)
        predicted_tag = get_predicted_tag(word_projection_instance)
        if len(set.intersection(set(actual_tag) == set(predicted_tag))) > 0:#Correct tag is assumed to be recoverable ----> This is why weighting of languages is important
            tot_correct += 1
        tot += 1
    return ([tot_correct, tot])

def project_and_eval(corpus, target_lang, source_langs):
    sentence_level_projection_instances = process_corpus(corpus, target_lang, source_langs)
    dump_file = open(PROJECTION_INSTANCE_DUMP_FILE, 'wb')
    pickle.dump(sentence_level_projection_instances, dump_file)#writing out projection instances so that they can simply be read in once again
    dump_file.close()
    tot_correct = 0
    tot = 0
    for sentence_level_projection_instance in sentence_level_projection_instances:
        [instance_tot_correct, instance_tot] = get_projection_score(sentence_level_projection_instance)
        tot_correct += instance_tot_correct
        tot += instance_tot
    print("Projection score = " + str(tot_correct/tot))

def populate_data(pickle_data_folder):
    if pickle_data_folder[-1] != '/':
        pickle_data_folder += '/'
    aggregated_data = []
    for [path, dirs, files] in walk(pickle_data_folder):
        for file in files:
            print ('Reading file' + file)
            f = open(pickle_data_folder + file, 'rb')
            data_structure = pickle.load(f)
            aggregated_data.append(data_structure)
        break
    return(aggregated_data)

"""
############################################ M A I N   F U N C T I O N #################################################
"""


"""
            RE WRITE GET ACTUAL TAGS FUNCTON!!!
"""
PICKLE_PATH = "./pickle_files"
PROJECTION_INSTANCE_DUMP_FILE = './Projection_instances.pickle'
TARGET_LANGUAGE = 'es'

#ALL_LANGUAGES = ['en', 'nl', 'it', 'es', 'sl', 'de', 'pl', 'sk', 'fr']

SOURCE_LANGUAGES = ['en', 'nl', 'it', 'sl', 'de', 'pl', 'sk', 'fr']

corpus = populate_data(PICKLE_PATH)

project_and_eval(corpus, TARGET_LANGUAGE, SOURCE_LANGUAGES)