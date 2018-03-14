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
'''
python3 query.py stopwords index title [-t] [-v]
'''
* stopwords: location of stopwords file
* index: location of inverted index
* title: location of title index
* -t: optional title flag, will print titles instead of id's
* -v: optional verbose flag, will print (title, score) pairs instead of id's
