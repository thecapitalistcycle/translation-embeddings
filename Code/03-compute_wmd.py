# Compute the Word Mover's Distance between each pair of aligned sentences
import logging
logger = logging.getLogger(__name__)
import csv
import codecs
import string
import os
import glob
import joblib

from numpy import dot, zeros, dtype, float32 as REAL,\
    double, array, vstack, fromstring, sqrt, newaxis,\
    ndarray, sum as np_sum, prod, ascontiguousarray,\
    argmax
import numpy as np
import nltk
import gensim
from gensim.corpora.dictionary import Dictionary

en_emb_loc = os.path.join("..","Embeddings","unsup.256.en")
de_emb_loc = os.path.join("..","Embeddings","unsup.256.de")

aligned_loc = os.path.join("..","Texts","AlignedFowkes")

output_prefix = "fowkes"
output_loc = os.path.join("..","Texts","WMD")
pickle_loc = os.path.join("..","Output")

punct_remover = str.maketrans('', '', string.punctuation)
# Additional unicode punctuation that needs to be removed
unicode_punct = "“”"

def gensimTest():
    # Testing to see if gensim can auto-load the cross-lingual embedding files
    en_model = gensim.models.KeyedVectors.load_word2vec_format(en_emb_loc, binary=False)
    print(en_model['the'])
    # Success!

def loadEmbeddings():
    en_model = gensim.models.KeyedVectors.load_word2vec_format(en_emb_loc, binary=False)
    de_model = gensim.models.KeyedVectors.load_word2vec_format(de_emb_loc, binary=False)
    return en_model, de_model

def loadChapter(ch_loc):
    statements = []
    row_counter = 0
    with codecs.open(ch_loc, "r", "utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) > 0:
                statements.append((row_counter,row[0],row[1]))
                row_counter = row_counter + 1
    return statements

def tokenizeDoc(doc_text):
    tokenized = nltk.word_tokenize(doc_text)
    tokenized = [token.lower() for token in tokenized]
    # Remove tokens which are just punctuation
    tokenized = [token.translate(punct_remover) for token in tokenized]
    # Remove unicode punctuation
    for punct_char in unicode_punct:
        tokenized = [token.replace(punct_char, "") for token in tokenized]
    tokenized = [token for token in tokenized if len(token) > 0]
    return tokenized

# If pyemd C extension is available, import it.
# If pyemd is attempted to be used, but isn't installed, ImportError will be raised in wmdistance
try:
    from pyemd import emd
    PYEMD_EXT = True
except ImportError:
    PYEMD_EXT = False

def biling_wmd(en_model, de_model, en_doc, de_doc):
    # ADAPTED FROM THE ORIGINAL keyedvectors.py FILE FROM GENSIM
    if not PYEMD_EXT:
        raise ImportError("Please install pyemd Python package to compute WMD.")

    # Remove out-of-vocabulary words.
    len_pre_oov_en = len(en_doc)
    len_pre_oov_de = len(de_doc)
    en_doc = [token for token in en_doc if token in en_model]
    de_doc = [token for token in de_doc if token in de_model]
    diff_en = len_pre_oov_en - len(en_doc)
    diff_de = len_pre_oov_de - len(de_doc)
    if diff_en > 0 or diff_de > 0:
        logger.info('Removed %d and %d OOV words from en_doc and de_doc (respectively).', diff_en, diff_de)

    if len(en_doc) == 0 or len(de_doc) == 0:
        logger.info(
            "At least one of the documents had no words that were in the vocabulary. "
            "Aborting (returning inf)."
        )
        return float('inf')

    # NOW we need to do an annoying thing: prepending "de__" or "en__" to
    # the tokens to ensure that no cognates mess up the system (i.e., so that
    # the *only* distances ever computed are between en and de words)
    en_doc_tags = ["en__" + token for token in en_doc]
    de_doc_tags = ["de__" + token for token in de_doc]

    # Now that we've tagged the two languages, we can combine into one
    # dictionary without fear of cognates only being counted once
    # ("de__wit" and "en__wit" will be different entries in the dict)
    dictionary = Dictionary(documents=[en_doc_tags, de_doc_tags])
    vocab_len = len(dictionary)

    if vocab_len == 1:
        # Both documents are composed by a single unique token
        return 0.0

    # Sets for faster look-up.
    docset_en = set(en_doc_tags)
    docset_de = set(de_doc_tags)

    # Compute distance matrix.
    distance_matrix = zeros((vocab_len, vocab_len), dtype=double)
    for i, t1 in dictionary.items():
        for j, t2 in dictionary.items():
            if t1 not in docset_en or t2 not in docset_de:
                continue
            # Compute Euclidean distance between word vectors.
            # (this is where we use the prefix to ensure correct vector is used)
            t1_tag = t1[:4]
            t1_word = t1[4:]
            t1_vec = en_model[t1_word] if t1_tag == "en__" else de_model[t1_word]
            t2_tag = t2[:4]
            t2_word = t2[4:]
            t2_vec = en_model[t2_word] if t2_tag == "en__" else de_model[t2_word]
            distance_matrix[i, j] = sqrt(np_sum((t1_vec - t2_vec)**2))

    if np_sum(distance_matrix) == 0.0:
        # `emd` gets stuck if the distance matrix contains only zeros.
        logger.info('The distance matrix is all zeros. Aborting (returning inf).')
        return float('inf')

    def nbow(document):
        d = zeros(vocab_len, dtype=double)
        nbow = dictionary.doc2bow(document)  # Word frequencies.
        doc_len = len(document)
        for idx, freq in nbow:
            d[idx] = freq / float(doc_len)  # Normalized word frequencies.
        return d

    # Compute nBOW representation of documents.
    d1 = nbow(en_doc_tags)
    d2 = nbow(de_doc_tags)

    # Compute WMD.
    return emd(d1, d2, distance_matrix)

def computeWMDs(ch_pairs, en_model, de_model):
    ## Compute wmds
    wmd_rows = []
    for cur_pair in ch_pairs:
        pair_id = cur_pair[0]
        en_doc = cur_pair[1]
        de_doc = cur_pair[2]
        en_tokenized = tokenizeDoc(en_doc)
        de_tokenized = tokenizeDoc(de_doc)
        print("****** Aligning en:")
        print(en_tokenized)
        print("****** With de:")
        print(de_tokenized)
        wmd = biling_wmd(en_model, de_model, en_tokenized, de_tokenized)
        wmd_rows.append([pair_id,en_doc,de_doc,wmd])
    return wmd_rows

def getChapterInfo(chap_loc):
    # Takes the filepath for the chapter and parses the chapter information
    # (name, language) from it
    filename = chap_loc.split(os.sep)[-1]
    # Extract just the name of the chapter
    file_elts = filename.split(".")
    ch_name = file_elts[0]
    return ch_name

def outputWMDs(ch_name, wmd_rows):
    output_filename = ch_name + ".wmd.txt"
    with codecs.open(os.path.join(output_loc,output_filename), 'w', 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(wmd_rows)

def outputPickle(ch_data):
    pickle_filename = output_prefix + ".pkl"
    joblib.dump(ch_data, os.path.join(pickle_loc, pickle_filename))

def main():
    # Activate gensim logging to console
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    #gensimTest()
    ## Load the embeddings
    en_model, de_model = loadEmbeddings()
    ## Load the chapters
    all_chapters = sorted(glob.glob(os.path.join(aligned_loc,"*.txt")))
    # all_rows will eventually hold a list of lists of translation pair data
    ch_data = []
    for cur_ch_loc in all_chapters:
        ch_name = getChapterInfo(cur_ch_loc)
        print("****** Processing " + ch_name)
        ch_pairs = loadChapter(cur_ch_loc)
        # Computation
        cur_rows = computeWMDs(ch_pairs, en_model, de_model)
        ch_data.append(cur_rows)
        # Output current chapter file
        outputWMDs(ch_name, cur_rows)
    # Output pickle (for the viewer)
    outputPickle(ch_data)

if __name__ == "__main__":
    main()