import json
import xml.etree.ElementTree as ET
import re
from nltk.stem.porter import *
import sys
from math import *
import time
import argparse

def get_namespace(root):
    #takes in a tree root of an xml and returns its namespace, if there is one.

    # default case
    namespace = ''
    # get the namespace from the xml
    if bool(root.attrib):
        start = root.tag.find('{')
        end = root.tag.find('}') + 1
        namespace = root.tag[start:end]
    return namespace

def page_list(namespace, tree, stopwords):
    # takes a namespace, a tree, and the stopwords file path
    # Returns a list, pages, that will contain tuples of ids,titles,texts from each page in the xml document

    # The stop words to remove from the titles/text of the xml files
    stop_words = ''
    with open(stopwords, 'r') as stop:
        for line in stop:
            word = line.replace('\n', '|')
            stop_words = stop_words + word
    stop.close()
    stop_words = stop_words[:-1]

    # Stop pattern, the set of stop-words to remove from the text of each page
    stop_pattern = re.compile("\\b(%s)\\b" % stop_words, re.I)

    # the non-alphanumeric characters that will be removed from all the text we get(we will sub anything
    # in the set defined by 'pattern' out with the empty string: '')
    pattern = re.compile('[\W_]+')
    #initiate the porter stemmer to be uses below
    stemmer = PorterStemmer()
    #Pages: a list that will contain tuples with Pageids, titles, and text
    pages = []
    if namespace != '':
        # get the title, id, and text for each page by iterating through
        # the page elements in the tree using the namespace obtained above.
        for page in tree.findall(namespace + 'page'):
            # initiate empty lists to contain the page title, page id, and page text for
            # each page
            titles = []
            ids = []
            texts = []
            # get the page title
            title = page.find(namespace + 'title').text
            titles.append(title)
            # get the page id(integer)
            ids.append(int(page.find(namespace + 'id').text))

            # the text element is always a child of the revision child of the wikia pages
            revision = page.find(namespace + 'revision')
            text = revision.find(namespace + 'text').text
            # if there is text, concat and then add the title and text to the text stream for the given page.
            # The text stream is a list of words that have been removed of stop words and stemmed
            if text != None:
                text = title.lower() + '\n' + text.lower()
                text = pattern.sub(' ', text)
                text = text.split(" ")
                text = [stop_pattern.sub("", word) for word in text]
                text = [x.strip(' ') for x in text]
                text = list(filter(None, text))
                text = [stemmer.stem(word) for word in text]
                texts.append(text)
            # if there is no text, do the same thing as above, except only add the title to the stream of text
            else:
                text = title.lower()
                text = pattern.sub(' ', text)
                text = text.split(" ")
                text = [stop_pattern.sub("", word) for word in text]
                text = [x.strip(' ') for x in text]
                text = list(filter(None, text))
                text = [stemmer.stem(word) for word in text]
                texts.append(text)
            # update the pages list with the tuple for the given page
            pages.append((ids, titles, texts))
        return pages

    # Same as above, only for case where there is no namespace (don't contend with revision tag)
    if namespace == '':
        for page in tree.findall('page'):
            # initiate empty lists to contain the page title, page id, and page text for
            # each page

            titles = []
            ids = []
            texts = []

            # get the page title
            title = page.find('title').text
            titles.append(title)

            # get the page id(integer)
            ids.append(int(page.find('id').text))

            # Get the text form the page
            text = page.find('text').text

            # if there is text, concat and then add the title and text to the text stream for the given page.
            # The text stream is a list of words that have been removed of stop words and stemmed
            if text != None:
                text = title.lower() + '\n' + text.lower()
                text = pattern.sub(' ', text)
                text = text.split(" ")
                text = [stop_pattern.sub("", word) for word in text]
                text = [x.strip(' ') for x in text]
                text = list(filter(None, text))
                text = [stemmer.stem(word) for word in text]
                texts.append(text)
            # if there is no text, do the same thing as above, except only add the title to the stream of text
            else:
                text = title.lower()
                text = pattern.sub(' ', text)
                text = text.split(" ")
                text = [stop_pattern.sub("", word) for word in text]
                text = [x.strip(' ') for x in text]
                text = list(filter(None, text))
                text = [stemmer.stem(word) for word in text]
                texts.append(text)
            # update the pages list with the tuple for the given page
            pages.append((ids, titles, texts))
        return pages

#start_time=time.time()

def create_dicts(pages):
    #create the dictionaries of titles, words(from text), adn term frequencies to be populated
    #with the elements of pages.

    #title_dict will have page ids as keys and corresponding page titles as values
    #word_dict (for the inverted index) will have filtered/stemmed words from page text as keys and
    # dictionaries as values these dictionaries will have page ids as keys and the words location in the
    #page as values. Finally, the tf, and idf dicts will have term frequencies and idf scores
    word_dict = {}
    title_dict = {}
    tf = {}

    for page in pages:
        words = page[2][0]
        id = page[0][0]
        # add id/title to title_dict
        title_dict[id] = page[1][0]
        for loc in range(len(words)):
            if words[loc] in word_dict.keys():
                if id in word_dict[words[loc]].keys():
                    word_dict[words[loc]][id].append(loc)
                    tf[words[loc]][id] += 1
                else:
                    word_dict[words[loc]][id] = [loc]
                    tf[words[loc]][id] = 1
            else:
                word_dict[words[loc]] = {id: [loc]}
                tf[words[loc]] = {id: 1}

    idf = {}
    N = len(title_dict)
    for word in word_dict.keys():
        idf[word] = log10(N / len(word_dict[word].keys()))
    dicts = [word_dict, title_dict, tf, idf]
    return dicts

def create(stopwords, collection, inverted_index, title_index):

    # initate the xml tree
    try:
        tree = ET.parse(collection)
    except ET.ParseError:
        print("ERROR: Bad XML File encountered. Exiting...")
        exit()

    root = tree.getroot()

    #get the namespace from the xml
    namespace = get_namespace(root)

    pages = page_list(namespace,tree, stopwords)


    dicts = create_dicts(pages)
    word_dict = dicts[0]
    title_dict = dicts[1]
    tf = dicts[2]
    idf = dicts[3]

    inverted = open(inverted_index, 'w')
    json.dump(word_dict, inverted)
    inverted.close()

    title_in = open(title_index, 'w')
    json.dump(title_dict, title_in)
    title_in.close()

    idf_in = open("idf_index.json", 'w')
    json.dump(idf,idf_in)
    idf_in.close()

    tf_in = open("tf_index.json","w")
    json.dump(tf,tf_in)
    tf_in.close()

#print("Took: %s seconds to run."% (time.time()-start_time))
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('stopwords')
    parser.add_argument('collection')
    parser.add_argument('index')
    parser.add_argument('title')

    args = parser.parse_args()

    stopwords = args.stopwords
    collection = args.collection
    inverted_index = args.index
    title_index = args.title
    create(stopwords, collection, inverted_index, title_index)
