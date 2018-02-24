# Create an AST from a boolean expression. AST is a tuple
# consisting of an operator and a list of operands.
#
# Note: NOT is not supported.

# Example:
#   given a AND b
#   returns ('AND', ['a','b'])
#
# Copyright 2006, by Paul McGuir
# Modified: 02/2011 for csci1580
# Modified: 02/2018 for data2040

from typing import Union

import pyparsing


class BoolOperand(object):
    reprsymbol = None

    def __init__(self, t):
        self.args = t[0][0::2]

    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str, self.args)) + ")"

    def eval_expr(self):
        raise NotImplementedError


class BoolAnd(BoolOperand):
    reprsymbol = 'AND'

    def eval_expr(self):
        lst = []
        for arg in self.args:
            if not isinstance(arg, BoolOperand):
                elem = arg
            else:
                elem = arg.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst


class BoolOr(BoolOperand):
    reprsymbol = 'OR'

    def eval_expr(self):
        lst = []
        for arg in self.args:
            if not isinstance(arg, BoolOperand):
                elem = arg
            else:
                elem = arg.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst

BOOL_OPERAND = pyparsing.Word(pyparsing.alphanums +
                              "!#$%&'*+,-./:;<=>?@[]^_`{|}~\\")
OP_LIST = [("AND", 2, pyparsing.opAssoc.LEFT, BoolAnd),
           ("OR", 2, pyparsing.opAssoc.LEFT, BoolOr)]
BOOL_EXPR = pyparsing.operatorPrecedence(BOOL_OPERAND, OP_LIST)

def bool_expr_ast(expr: str) -> Union[str, tuple]:
    expr = expr.strip()
    parsed_expr = BOOL_EXPR.parseString(expr)[0]
    if not isinstance(parsed_expr, BoolOperand):
        return expr
    return parsed_expr.eval_expr()

import itertools
import json
import re
from nltk.stem.porter import *
import numpy as np


# Query variable's used
pattern = re.compile('[\W_]+')
stemmer = PorterStemmer()



def filter_and_stem(queries, stopwords):
    '''Takes a list of query words and a stop word document and filters/stems the query words,
    removing empty spaces along the way'''
    stemmer = PorterStemmer()
    alpha_pattern = re.compile('[\W_]+')
    stop_words = ''
    with open(stopwords, 'r') as stop:
        for line in stop:
            word = line.replace('\n', '|')
            stop_words = stop_words + word
    stop.close()
    stop_words = stop_words[:-1]
    stop_pattern = re.compile("\\b(%s)\\b" %stop_words, re.I)

    queries = [alpha_pattern.sub('',query_word) for query_word in queries]
    queries = [stop_pattern.sub('', query_word) for query_word in queries]

    queries = [x.strip(' ') for x in queries]
    queries = list(filter(None, queries))
    queries = [stemmer.stem(query_word) for query_word in queries]
    return(queries)


def clean(bool_exp, stopwords):
    '''cleans a boolean AST expression removing nonalpha's, stopwords, and stemming'''
    # Get the stop words
    stop_words = ''
    with open(stopwords, 'r') as stop:
        for line in stop:
            word = line.replace('\n', '|')
            stop_words = stop_words + word
    stop.close()
    stop_words = stop_words[:-1]
    stop_pattern = re.compile("\\b(%s)\\b" % stop_words, re.I)
    pattern = re.compile('[\W_]+')
    stemmer = PorterStemmer()

    # Clean/Filter/Stem
    for i in range(len(bool_exp[1])):
        if type(bool_exp[1][i]) == tuple:
            clean(bool_exp[1][i], stopwords)
        else:
            bool_exp[1][i] = pattern.sub('', bool_exp[1][i])
            bool_exp[1][i] = stop_pattern.sub('', bool_exp[1][i])
            bool_exp[1][i] = stemmer.stem(bool_exp[1][i])
        #print("clean print:", bool_exp[1][i])
    return bool_exp


def sequential_words(dict1, dict2):
    # takes two dictionaries as arguments, corresponding to sequential words in a query phrase: If the words
    # corresponding to dict1 and dict2 occur sequentially in the same pages returns a dictionary with those
    # page ids as keys and a list of locations (where the second word was located after the first)

    # get the number of shared pages for the two dictionaries
    page_intersect = list(set(dict1.keys() & set(dict2.keys())))
    new_dict = {}
    # for each page in page_intesect check which ones have the sequential word ordering
    # by adding one to the locations in dict1 and seeing if they equal the locations in the corresponding page
    # for dict2
    for page_id in page_intersect:
        a_locs = np.array(dict1[page_id]) + 1
        b_locs = np.array(dict2[page_id])
        if bool(set(a_locs) & set(b_locs)):
            locs_list = list(set(a_locs) & set(b_locs))
            locs_list.sort()
            new_dict[page_id] = locs_list
    return new_dict


# takes ordered list of dictionaries (index[query_word])
def phrase_words(dicts):
    # if there is only one word in the phrase: return the list of pages the word is in
    if len(dicts) == 1:
        ids = list(dicts[0].keys())
        ids = list(map(int, ids))
        ids.sort()
        return list(dicts[0].keys())

    # case where there are only two words in phrase
    if len(dicts) == 2:
        ids = sequential_words(dicts[0], dicts[1])
        ids = list(ids.keys())
        ids = list(map(int, ids))
        ids.sort()
        return ids

    # Case where there are more than two words:
    else:
        # get the shared dictionary for first two words
        shared_dict = sequential_words(dicts[0], dicts[1])
        counter = 2
        while counter < len(dicts) and (bool(shared_dict) == True):
            shared_dict = sequential_words(shared_dict, dicts[counter])
            counter += 1
        if bool(shared_dict):
            ids = list(shared_dict.keys())
            ids = list(map(int, ids))
            ids.sort()
            return ids
        else:
            return ''


def match_bool(bool_exp, index):
    '''Takes an AST expression and an index and returns the page ids that meet the bool criteria'''
    ids = []

    for i in range(len(bool_exp[1])):
       #print(bool_exp[1][i])

        if type(bool_exp[1][i]) == tuple:
            #print('tuple', bool_exp[1][i])
            if bool_exp[0] == 'AND':
                if len(ids) == 0:
                    ids = match_bool(bool_exp[1][i], index)
                else:
                    ids = list(set(ids) & set(match_bool(bool_exp[1][i], index)))
            if bool_exp[0] == 'OR':
                if len(ids) == 0:
                    ids = match_bool(bool_exp[1][i], index)
                else:
                    ids = list(set(ids) | set(match_bool(bool_exp[1][i], index)))
        else:
            #print('hello')
            if bool_exp[0] == 'AND':
                #print('hi')
                # if bool[1][i] empty or not in index keys(words) return empty string
                if (bool_exp[1][i] == '') or (bool_exp[1][i] not in index.keys()):
                    return []
                elif len(ids) == 0:
                    ids = list(index[bool_exp[1][i]].keys())
                else:
                    ids = list(set(ids) & set(index[bool_exp[1][i]].keys()))
            if bool_exp[0] == 'OR':
                if (bool_exp[1][i] == '') or (bool_exp[1][i] not in index.keys()):
                    ids = ids
                elif len(ids) == 0:
                    ids = list(index[bool_exp[1][i]].keys())
                else:
                    ids = list(set(ids) | set(index[bool_exp[1][i]].keys()))

    ids = ids = list(map(int, ids))
    ids.sort()
    return ids


# YOUR QUERY CLASS BELOW
class Query:
    def __init__(self, query):
        self.query = query

    def print_query(self):
        print("Find: " + self.query)


# YOUR ONEWORDQUERY CLASS BELOW
class OneWordQuery(Query):
    def __init__(self, query):
        super().__init__(query)
        # finds list of page ids for pages that contain query

    def match(self, index, stopwords):
        # Make query lowercase
        query_string = self.query.lower()

        # Remove non-alphanumeric characters
        query_string = filter_and_stem([query_string],stopwords)[0]

        if query_string == '':
            return ''
        else:
            query_ids = list(index[query_string].keys())
            query_ids = list(map(int, query_ids))
            query_ids.sort()
            return query_ids


class FreeTextQuery(Query):
    def __init__(self, query):
        super().__init__(query)

    def match(self, index, stopwords):
        # Make qery lowercase
        query_string = self.query.lower()

        # identify tokens and create list of tokens
        queries = query_string.split(' ')

        # filter stop words and stem
        queries = filter_and_stem(queries, stopwords)
        # take the query words in the index and get the set of corresponding page ids
        queries = [query_word for query_word in queries if query_word in index.keys()]
        ids = [list(index[query_word].keys()) for query_word in queries]
        ids = list(itertools.chain.from_iterable(ids))
        ids = set(ids)
        ids = list(ids)
        ids = list(map(int, ids))
        ids.sort()
        return ids


# YOUR PHRASEQUERY CLASS BELOW

class PhraseQuery(Query):
    def __init__(self, query):
        super().__init__(query)

    def match(self, index, stopwords):
        # remove double quotes, convert to lowercase, obtain tokens
        query_string = self.query[1:]
        query_string = query_string[:-1]
        query_string = query_string.lower()
        queries = query_string.split(' ')

        # filter stop words and stem
        queries = filter_and_stem(queries, stopwords)

        dicts = [index[query_word] for query_word in queries]

        if len(dicts) == len(queries):
            ids = phrase_words(dicts)
            return ids
        else:
            #will never enter this else statement, but you know...compulsion.
            return ''



# YOUR BOOLEANQUERY CLASS BELOW
class BooleanQuery(Query):
    def __init__(self, query):
        super().__init__(query)

    def match(self, index, stopwords):

        # Converty the Query to AST
        bool_exp = bool_expr_ast(self.query)

        # Clean the query (remove stopwords, stem, etc.)
        bool_exp = clean(bool_exp, stopwords)
        ids = match_bool(bool_exp, index)
        ids.sort()
        return ids


#YOUR QUERYFACTORY BELOW

class QueryFactory:
    @staticmethod
    def create(query_string: str):
        if not query_string:
            return None
        if query_string[0] == '"' and query_string[-1] == '"':
            return PhraseQuery(query_string)
        if any([t in query_string for t in ('(', ')', 'AND', 'OR')]):
            return BooleanQuery(query_string)
        words = query_string.split()
        if len(words) == 1:
            return OneWordQuery(query_string)
        elif len(words) > 1:
            return FreeTextQuery(query_string)
        else:
            raise ValueError('This query string is not supported.')
