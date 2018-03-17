import pytest
# from query import *
from create import *
import xml.etree.ElementTree as ET

stopwords = "stopwords.dat"

def test_get_namespace():
#test whether the get_namspace functions works on the two types of xml files
    try:
        tree = ET.parse('small.xml')
    except ET.ParseError:
        print("ERROR: Bad XML File encountered. Exiting...")
        exit()

    small_root = tree.getroot()

    try:
        tree = ET.parse('pixar_pages_current.xml')
    except ET.ParseError:
        print("ERROR: Bad XML File encountered. Exiting...")
        exit()

    pixar_root = tree.getroot()

    assert get_namespace(small_root) ==  ''
    assert get_namespace(pixar_root) == '{http://www.mediawiki.org/xml/export-0.6/}'


def test_page_small_list():
    #test the page_list function
    tree = ET.parse('small.xml')
    stopwords = "stopwords.dat"
    namespace = ''
    pages = page_list(namespace,tree, stopwords)
    #test page id
    assert pages[0][0] == [0]
    assert pages[2][0] == [2]
    #test parses words
    assert pages[2][2] == [['yuri', 'gagarin', 'first', 'man', 'orbit', 'space']]
    #test text
    assert pages[2][1] == ['yuri gagarin first man orbit space']

def test_create_small_dicts():
    #test the create_dicts function
    tree = ET.parse('small.xml')
    stopwords = "stopwords.dat"
    namespace = ''
    pages = page_list(namespace, tree, stopwords)
    dicts = create_dicts(pages)
    word_dict = dicts[0]
    title_dict = dicts[1]
    tf = dicts[2]
    idf = dicts[3]
    assert tf['2001'][3] == 1
    assert tf['odyssey'][12] == 1
    assert idf['odyssey'] == 0.6368220975871743
    assert word_dict["2001"][3] == [6]
    assert word_dict['murder'][5] == [1]
    assert title_dict[7] == "full metal jacket bullet hunt"


# The page_list function takes some time to run, if you are in a hurry we recommend you comment out the two
# tests below. They are similar to the previous two, only they are run using the pixar xml files

#create pixar_pages, required for the following functions
tree = ET.parse('pixar_pages_current.xml')
root = tree.getroot()
namespace = get_namespace(root)
pixar_pages = page_list(namespace, tree, stopwords)


def test_page_pixar_list():
#This test takes a while to run, you can comment it out if you want to.
    #test page id of bigger file
    assert pixar_pages[0][0] == [6]
    #check to make sure 'the' was removed from text ('the' is in the text of this page)
    assert ("the" in pixar_pages[0][2][0]) == False
    #check to make sure 'Formatting' was reformatted properly ('Formatting' is in the text of this page)
    assert ("Formatting" in pixar_pages[0][2][0]) == False
    assert ("formatting" in pixar_pages[0][2][0]) == False
    assert ("format" in pixar_pages[0][2][0]) == True


def test_create_pixar_dicts():
    dicts = create_dicts(pixar_pages)
    word_dict = dicts[0]
    title_dict = dicts[1]
    tf = dicts[2]
    idf = dicts[3]
    assert idf['nemo'] == 1.644899843709648
    assert idf['dory8'] == 4.042260406689452
    assert word_dict['findingdory3d'][25474] == [2274]
    assert len(word_dict['nemo']) == 749
    assert word_dict['nemo'][1461] == [191, 195, 198]
    assert ('the' in word_dict.keys()) == False
    assert ('formatting' in word_dict.keys()) == False
    assert len(tf['nemo']) == 749
    assert tf['nemo'][1461] == 3
    assert len(title_dict) == len(pixar_pages)
    assert title_dict[1461] == 'Pixar Wiki'
