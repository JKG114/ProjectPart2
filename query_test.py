import QueryClass as QC
import json

file = open('small_index.json', 'r')
inverted = json.load(file)
file.close()

file=open('small_title.json','r')
titleDict = json.load(file)
file.close()

file=open("tf_index.json",'r')
tf_index=json.load(file)
file.close()

file=open("idf_index.json",'r')
idf_index=json.load(file)
file.close()

def test_filter_and_stem():
    #tests the parsing
    assert QC.filter_and_stem('the a','stopwords.dat')==[]
    assert QC.filter_and_stem(['2001','space','odyessy'],'stopwords.dat')==['2001','space','odyessi']
    assert QC.filter_and_stem(['Nemo','BOB','hEllO'],'stopwords.dat')==['nemo','bob','hello']

def test_clean():
    #tests the parsing for bool queries
    boolexp=QC.bool_expr_ast('nemo AND fish')
    assert boolexp==('AND',['nemo','fish'])
    assert QC.clean(boolexp,'stopwords.dat')==('AND', ['nemo', 'fish'])

    boolexp2=QC.bool_expr_ast('(nemo AND Odyessy) OR meeting')
    assert boolexp2==('OR',[('AND', ['nemo', 'Odyessy']), 'meeting'])
    assert QC.clean(boolexp2,'stopwords.dat')==('OR',[('AND', ['nemo', 'odyessi']), 'meet'])

def test_sequential_words():
    dict1={0:[1],1:[10,20],2:[7,8,10]}
    dict2={0:[2],2:[6,8,9,11]}
    assert QC.sequential_words(dict1,dict2)=={0: [2], 2: [8, 9, 11]}

    dict1={0:[0,3,6]}
    dict2={0:[1,4,7]}
    assert QC.sequential_words(dict1,dict2)=={0: [1, 4, 7]}

def test_phrase_words():
    dict1={0:[1],1:[10,20],2:[7,8,10]}
    dict2={0:[2],2:[6,8,9,11]}
    temp=QC.sequential_words(dict1,dict2)
    assert temp=={0: [2], 2: [8, 9, 11]}
    assert QC.phrase_words([temp])==[0,2]
    assert QC.phrase_words([dict1])==[0,1,2]
    assert QC.phrase_words([temp,dict1,dict2])==[2]

def test_small_queries():
    query1 = QC.QueryFactory.create('space')
    results=query1.match(inverted,'stopwords.dat',titleDict,tf_index,idf_index)
    assert results==[(0, 1.0), (2, 1.0), (3, 1.0), (8, 1.0)]
    assert titleDict['0']=='2001 space odyssey'
    assert titleDict['2']=='yuri gagarin first man orbit space'
    assert titleDict['3']=='kubrik movi includ full metal jacket 2001 space odyssey'
    assert titleDict['8']=='recent nasa program space'

    query2 = QC.QueryFactory.create('clockwork OR orange')
    results=query2.match(inverted,'stopwords.dat',titleDict,tf_index,idf_index)
    assert results==[('10', 0.9751424258351848), ('9', 0.9751424258351848), ('11', 0.5328498146926454), ('12', 0.5328498146926454)]

    query3 = QC.QueryFactory.create('"killer kiss"')
    results=query3.match(inverted,'stopwords.dat',titleDict,tf_index,idf_index)
    assert results==[(4, 0.9927038337834337)]

    query4 = QC.QueryFactory.create('Space Odyssey')
    results=query4.match(inverted,'stopwords.dat',titleDict,tf_index,idf_index)
    assert results==[(0, 0.9941370743997096), (3, 0.9941370743997096), (12, 0.7794184970625834), (2, 0.6265036364113967), (8, 0.6265036364113967)]

def test_get_tokens():
    query1 = QC.QueryFactory.create('Space OR 2001')
    bool_exp=QC.clean(QC.bool_expr_ast('Space OR 2001'),'stopwords.dat')
    assert query1.getTokens(bool_exp)==['space','2001']

    query2 = QC.QueryFactory.create('(Space OR 2001) AND clockwork OR odyessy')
    bool_exp=QC.clean(QC.bool_expr_ast('(Space OR 2001) AND clockwork OR odyessy'),'stopwords.dat')
    assert query2.getTokens(bool_exp)==['space','2001','clockwork','odyessi']

def test_query_factory():
    query1 = QC.QueryFactory.create('SpACe.')
    assert isinstance(query1,QC.OneWordQuery)==True
    query2 = QC.QueryFactory.create('SpA.Ce')
    assert isinstance(query2,QC.OneWordQuery)==True
    query3 = QC.QueryFactory.create('Space Odyssey and the or orange')
    assert isinstance(query3,QC.FreeTextQuery)==True
    query4 = QC.QueryFactory.create('"abc"')
    assert isinstance(query4,QC.PhraseQuery)==True
    query5 = QC.QueryFactory.create('(space AND orange or)')
    assert isinstance(query5,QC.BooleanQuery)==True

def test_calc_doc_weight():
    file=open("tf_index.json",'r')
    tf_index=json.load(file)
    file.close()

    file=open("idf_index.json",'r')
    idf_index=json.load(file)
    file.close()
    query1 = QC.QueryFactory.create('"killer kiss"')
    tokens = QC.filter_and_stem(['killer','kiss'],'stopwords.dat')
    assert tokens==['killer','kiss']
    idf_vector=[float(idf_index[x]) for x in tokens]
    doc4_weight=query1.calcDocWeight(tokens,'4',tf_index,idf_vector)
    assert doc4_weight==0.9927038337834337
    doc5_weight=query1.calcDocWeight(tokens,'5',tf_index,idf_vector)
    assert doc5_weight==0.9927038337834337

    query2 = QC.QueryFactory.create('(2001 OR space) AND odyssey')
    bool_exp=QC.clean(QC.bool_expr_ast('(2001 OR space) AND odyssey'),'stopwords.dat')
    tokens2=query2.getTokens(bool_exp)
    assert tokens2==['2001','space','odyssey']
    idf_vector=[float(idf_index[x]) for x in tokens2]
    doc0_weight=query2.calcDocWeight(tokens2,'0',tf_index,idf_vector)
    assert doc0_weight==0.9826307737901492
    doc3_weight=query2.calcDocWeight(tokens2,'3',tf_index,idf_vector)
    assert doc3_weight==0.9826307737901492
