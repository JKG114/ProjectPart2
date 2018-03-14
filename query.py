from QueryClass import Query
from QueryClass import QueryFactory
from QueryClass import OneWordQuery
from QueryClass import PhraseQuery
from QueryClass import BooleanQuery
from QueryClass import FreeTextQuery
import json
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('stopwords')
parser.add_argument('index')
parser.add_argument('title')
parser.add_argument('-t',action='store_true')
parser.add_argument('-v',action='store_true')

args = parser.parse_args()

stopwords = args.stopwords
inverted_index = args.index
title = args.title


def query(stopwords, inverted_index, title):
    #Open inverted index and create corresponding dictionary
    file = open(inverted_index, 'r')
    inverted = json.load(file)
    file.close()

    file=open(title,'r')
    titleDict = json.load(file)
    file.close()

    file=open("tf_index.json",'r')
    tf_index=json.load(file)
    file.close()

    #while this is true (it's always true)
    while 1:
        try:
            #Take Query input
            query = input( )
            query = QueryFactory.create(query)
            #Ouery Output
            id_list=query.match(inverted, stopwords,titleDict,tf_index)
            if args.t is True:
                #just titles
                id_list=[f'"{titleDict[str(x[0])]}"' for x in id_list]
                print(*id_list)
            elif args.v is True:
                #title,weight pairs
                for pair in id_list:
                    pageTitle=f'"{titleDict[str(pair[0])]}"'
                    print(pageTitle, end=' ')
                    print(pair[1])
            else:
                #ids
                id_list=[x[0] for x in id_list]
                print(*id_list)

        except EOFError:  # Catch the Ctrl-D
            print ('\n')
            break
        except:  # Trap all other errors
            print('')

query(stopwords, inverted_index, title)
