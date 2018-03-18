# Part 2 of DATA 2040 Building a Search Engine Project

### Authors: Jesse Geman (@JKG114) and Ken Noh (@SquareDorito)

### To create inverted index:
```
python3 create.py stopwords collection index title
```
* stopwords: location of stopwords file
* collection: location of .xml collection
* index: location to write inverted index to
* title: location to write title index to

### To query from inverted index:
```
python3 query.py stopwords index title [-t] [-v]
```
* stopwords: location of stopwords file
* index: location of inverted index
* title: location of title index
* -t: optional title flag, will print titles instead of id's
* -v: optional verbose flag, will print (title, score) pairs instead of id's

### Running tets:
To run tests for create.py:
```
pytest test_create.py
```

To run tests for query.py, first need to run create.py for the small dataset.
```
python create.py stopwords.dat small.xml small_index.json small_title.json
pytest query_test.py
```
All the tests are for QueryClass.py where the majority of the program is handled. There are no actual tests for query.py because query.py only contains the REPL.
