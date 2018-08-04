# First things first: we just do a sentence tokenizer on both the English
# and German versions and see if there are different numbers of sentences
# (which would imply that they're not being translated sentence->sentence,
# one-to-one)

import codecs
import re
import os
import glob

import tr_globals

import nltk.data

# Note: the german edition has page numbers like <123>, so we'll need to remove
# these with a regex
pagenum_reg_de = r'<[0-9]+>'
footnote_reg_de = r'\([0-9]+\)'
# The English edition has footnotes plopped at the end of sentences, so we'll
# also have to remove those with a regex
# The first one picks up footnotes at end of sentence. The second picks up
# footnotes at end of sentence but with a trailing space. 
end_footnote_reg_en = r'\.[0-9]+\s|\. [0-9]+\s'
# This one picks up footnotes in the *middle* of sentences (in these cases
# we have to keep track of the word the footnote is on so we don't remove it)
sent_footnote_reg_en = r'(([^ \n\t\r\.0-9]+)[0-9]+)\s'
# This detects strings that NLTK thinks are sentences but which are actually
# just section numbers/footnotes.
# The first one picks up "sentences" which are just footnotes "(3)",
# the second picks up section numbers "7."
nonsent_reg_de = r'^\([0-9\.]+\)$|^[0-9]+\.$'
nonsent_reg_en = r''

english_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
german_tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')

def tokenizeChapter(fulltext, lang):
    # Use the right tokenizer for the language
    if lang == "de":
        tokenizer = german_tokenizer
        ## Also remove page numbers + footnotes for German text
        #print(re.findall(pagenum_reg_de, fulltext))
        fulltext = re.sub(pagenum_reg_de, " ", fulltext)
        #print(re.findall(footnote_reg_de, fulltext))
        fulltext = re.sub(footnote_reg_de, " ", fulltext)
    elif lang == "en":
        tokenizer = english_tokenizer
        ## Remove footnotes for English text
        #print(re.findall(end_footnote_reg_en, fulltext))
        fulltext = re.sub(end_footnote_reg_en, '. ', fulltext)
        #print(re.findall(sent_footnote_reg_en, fulltext))
        fulltext = re.sub(sent_footnote_reg_en, r'\2 ', fulltext)
    else:
        raise ValueError("Invalid language code. Needs to be 'en' or 'de'")

    # Tokenize
    tokenized = tokenizer.tokenize(fulltext)

    # There's one issue where it thinks some footnotes and section numbers are
    # sentences. So remove these.
    if lang == "de":
        nonsent_reg = nonsent_reg_de
    else:
        nonsent_reg = nonsent_reg_en

    clean_tokenized = [sent for sent in tokenized if not re.match(nonsent_reg, sent)]
    return tokenized


def loadChapter(filepath):
    with codecs.open(filepath, "r", "utf-8") as f:
        file_text = f.read().replace('\n',' ')
        file_text = file_text.replace('\r', ' ')
    return file_text

def outputCleaned(tokens, output_filename):
    with codecs.open(output_filename, "w", "utf-8") as g:
        g.write(" ".join(tokens))

def cleanDirectory(input_dir):
    cleaned_dir = os.path.join(input_dir,"cleaned")
    print("cleaned_dir")
    print(cleaned_dir)
    ## Get all the files in that dir
    all_paths = glob.glob(os.path.join(input_dir,"*.txt"))
    #print(all_paths)
    ## Or just a single file, for debugging
    #all_paths = [input_dir + "\\ch02.de.txt"]
    for path_num, cur_path in enumerate(all_paths):
        cur_filename, file_prefix, file_lang, ch_num = tr_globals.getFileInfo(cur_path)
        print("Processing file #" + str(path_num) + ": " + cur_filename)

        ## Load chapter
        chapter_text = loadChapter(cur_path)

        ## Tokenize sentences
        tokens = tokenizeChapter(chapter_text, file_lang)
        print("Num tokens: " + str(len(tokens)))

        ## Output cleaned versions
        # First we create a "cleaned" subdirectory within the original directory
        if not os.path.isdir(cleaned_dir):
            os.makedirs(cleaned_dir)
        output_path = os.path.join(cleaned_dir, file_prefix + "_clean." + file_lang +  ".txt")
        print("Outputting to " + output_path)
        outputCleaned(tokens, output_path)

def main():
    #en_dir = os.path.join("..","Texts","FirstEnglishEdition")
    en_dir = os.path.join("..","Texts","Fowkes")
    de_dir = os.path.join("..","Texts","ThirdGermanEdition")
    cleanDirectory(en_dir)
    cleanDirectory(de_dir)
    

if __name__ == "__main__":
    main()