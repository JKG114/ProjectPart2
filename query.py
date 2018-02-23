from QueryClass import Query
from QueryClass import QueryFactory
from QueryClass import OneWordQuery
from QueryClass import PhraseQuery
from QueryClass import BooleanQuery
from QueryClass import FreeTextQuery
import json
import re
import sys

stopwords = sys.argv[1]
inverted_index = sys.argv[2]
title = sys.argv[3]
def query(stopwords, inverted_index, title):
    #Open inverted index and create corresponding dictionary
    file = open(inverted_index, 'r')
    inverted = json.load(file)
    file.close()

    #while this is true (it's always true)
    while 1:
        try:

            #Take Query input
            query = input( )
            query = QueryFactory.create(query)
            #Ouery Output
            print(*query.match(inverted, stopwords))

        except EOFError:  # Catch the Ctrl-D
            print ('\n')
            break
        except:  # Trap all other errors
            print('')

query(stopwords, inverted_index, title)
