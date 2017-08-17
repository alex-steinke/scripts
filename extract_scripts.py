from bs4 import BeautifulSoup, Tag
from bs4 import Tag
from nltk.corpus import brown
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import FreqDist, Text
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
import operator
import requests
import time
from os import listdir
from os.path import isfile, join
from nltk.corpus import PlaintextCorpusReader
from nltk import ngrams
from math import log

def from_ont_list(oldfile, newfile):
    """ Extract entries from list that was exportet from ontology. Ech line might be surrounded by double quotes,
    multiple entries are separated by ;; and eaach is surrounded by single quotes. Entry is discarded if it appears in
    wordlist of the brown corpus with 'learned' category removed. (This condition should not be used on NMOBR list)

    :param oldfile: Old file
    :param newfile: New file
    :return:
    """
    with open(oldfile, "r") as ins:
        for line in ins:
            try:
                if len(line.encode('utf-8').strip()) > 0:
                    line = line.encode('utf-8').strip().strip('"')
                    for item in line.split(';;'):
                        item = item.strip("'")
                        if item not in (set(brown.words()) - set(
                                brown.words(categories=['learned']))):
                            with open(newfile, 'a') as the_file:
                                print item
                                the_file.write(item.lower() + '\n')
                        else:
                            print "NOP - " + str(item)
            except Exception, e:
                print str(e)


def get_nsd(newfile):
    """Crawls rarediseases.info.nih.gov and saves nervous system diseases including synonyms and short forms to a file.
    :param newfile: File
    :return:
    """
    r = requests.get('https://rarediseases.info.nih.gov/diseases/diseases-by-category/17/nervous-system-diseases')
    soup = BeautifulSoup(r.text, 'html.parser')
    soup.prettify()
    div = soup.findAll("div", {"class": "body-container"})
    x = set()
    for a in div[0].findAll('a'):
        try:
            y = set()
            time.sleep(5)
            y.add(str(a.get_text()).strip())
            print str(a.get_text()).strip()
            r2 = requests.get('https://rarediseases.info.nih.gov' + a.get('href'))
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            soup2.prettify()
            syn = soup2.findAll("div", {"id": "diseaseSynonyms"})[0].findAll("span", {"class": "complete"})[
                0].get_text()
            for s in syn.split(';'):
                y.add(str(s).strip())
            with open(newfile, 'a') as the_file:
                z = list(y - x)
                for i in range(len(z)):
                    x.add(z[i])
                    the_file.write(z[i] + '\n')
        except Exception, e:
            print str(e)


def get_brain_regions(newfile):
    """Saves lables from data.rdf file containg brain regions to a file.
    :param newfile: File
    :return:
    """
    with open("data.rdf", "r") as ins:
        x = list()
        for line in ins:
            try:
                if '<rdfs:label' in line:
                    text = BeautifulSoup(line).text.encode('utf-8').strip()
                    if text not in x and len(
                            text) > 3 and ',' not in text and ')' not in text and '(' not in text and 'and' not in text:
                        print text
                        x.add(text)
                        with open(newfile, 'a') as the_file:
                            the_file.write(text + '\n')
            except Exception:
                pass


def get_nn(newfile):
    """Extract concepts, and synonyms in English and Lating from NeuroNames nn.xml file.
    :param newfile: New file
    :return:
    """
    with open("nn.xml", "r") as ins:
        x = set()
        for line in ins:
            try:
                if '<concept ' in line:
                    soup = BeautifulSoup(line)
                    soup.prettify()
                    text = soup.concept.get('standardname')
                    if text not in x:
                        print text
                        x.add(text)
                        with open(newfile, 'a') as the_file:
                            the_file.write(text + '\n')
                if '<synonym synonymLanguage="English"' in line:
                    soup = BeautifulSoup(line)
                    soup.prettify()
                    text = soup.synonym.text
                    if text not in x:
                        print text
                        x.add(text)
                        with open(newfile, 'a') as the_file:
                            the_file.write(text + '\n')
                if '<synonym synonymLanguage="Latin"' in line:
                    soup = BeautifulSoup(line)
                    soup.prettify()
                    text = soup.synonym.text
                    if text not in x:
                        print text
                        x.add(text)
                        with open(newfile, 'a') as the_file:
                            the_file.write(text + '\n')
            except Exception:
                pass


def get_abs(old_folder, newfile):
    """Extracts abstracts from multiple .ris files.
    :param old_folder: Folder with .ris files
    :param newfile: New file
    :return:
    """
    onlyfiles = [f for f in listdir(old_folder) if isfile(join(old_folder, f))]
    for f in onlyfiles:
        with open("./" + old_folder+'/' + f, "r") as ins:
            print f
            for line in ins:
                if not len(line.strip()) == 0 and not line.startswith('N1  -') and not line.startswith(
                        'UR  -') and not line.startswith('ER  -'):
                    if line.startswith('AB  -'):
                        line = line[5:]
                    with open(newfile, 'a') as the_file:
                        the_file.write(line.strip() + '\n')


def get_tag_pos(data):
    """Identifies start and end positions of all BrainRegion tags
    :param data:    PubMed XML
    :return:        List of tupels describing positions of the tags
    """
    regions = []
    lens = [len(tag.string) for tag in data.contents]
    start_pos = [sum(lens[:ind]) for ind in xrange(0, len(lens))]
    end_pos = [sum(lens[:ind]) for ind in xrange(1, len(lens))]
    start_tag = [spot for tag, spot in zip(data.contents, start_pos) if
                 isinstance(tag, Tag) and tag.name == 'brainregion']
    end_tag = [spot for tag, spot in zip(data.contents, end_pos) if
               isinstance(tag, Tag) and tag.name == 'brainregion']
    for i in range(len(start_tag)):
        try:
            regions.append((start_tag[i], end_tag[i]))
        except IndexError:
            regions.append((start_tag[i], len(data.text)))
    return regions


def get_brain_regions():
    with open("bc.xml") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        soup.prettify()
        articles = soup.findAll('pubmedarticle')
        for art in articles:
            a1 = get_tag_pos(art.articletitle)
            a2 = get_tag_pos(art.abstracttext)
            print art.abstracttext
            for x in a2:
                print art.abstracttext.text[x[0]:x[1]]


def calc_cid(origin, new, c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient):
    """Calculates strict and lenient matches, insertions and deletions from from two sets of positions
    """
    for ner in new:
        if ner in origin:
            c_strict += 1
            c_lenient += 1
        else:
            i_strict += 1
            c_lenient_check = False
            for oner in origin:
                if oner[1] >= ner[0] >= oner[0] or oner[1] >= ner[1] >= oner[0]:
                    c_lenient_check = True
            if c_lenient_check:
                c_lenient += 1
            else:
                i_lenient += 1
    for ner in origin:
        if ner not in new:
            d_strict += 1
            d_lenient_check = False
            for nner in new:
                if nner[1] >= ner[0] >= nner[0] or nner[1] >= ner[1] >= nner[0]:
                    d_lenient_check = True
            if not d_lenient_check:
                d_lenient += 1
    return c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient


def eval_brain_regions(origin, new):
    """Evaluate the results of NER labeling"""
    c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient, error = 0, 0, 0, 0, 0, 0, 0
    with open(origin) as fp:
        osoup = BeautifulSoup(fp, 'html.parser')
    with open(new) as fp:
        nsoup = BeautifulSoup(fp, 'html.parser')
    osoup.prettify()
    nsoup.prettify()
    oart = osoup.findAll('pubmedarticle')
    nart = nsoup.findAll('pubmedarticle')
    for i in range(len(oart)):
        try :
            opostxt = get_tag_pos(oart[i].abstracttext)
            npostxt = get_tag_pos(nart[i].abstracttext)
            opostit = get_tag_pos(oart[i].articletitle)
            npostit = get_tag_pos(nart[i].articletitle)
        except:
            error +=1
        c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient = calc_cid(opostxt, npostxt, c_strict, i_strict,
                                                                                 d_strict, c_lenient, i_lenient, d_lenient)
        c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient = calc_cid(opostit, npostit, c_strict, i_strict,
                                                                                 d_strict, c_lenient, i_lenient, d_lenient)
    precision_strict = c_strict/(c_strict+i_strict+0.0)
    recall_strict = c_strict/(c_strict+d_strict+0.0)
    f_strict = 2*((precision_strict*recall_strict)/(precision_strict+recall_strict))
    precision_lenient = c_lenient / (c_lenient + i_lenient + 0.0)
    recall_lenient = c_lenient / (c_lenient + d_lenient + 0.0)
    f_lenient = 2 * ((precision_lenient * recall_lenient) / (precision_lenient + recall_lenient))
    print 'Error: {6} \nStrict: {0}-{1}-{2}\nLenient: {3}-{4}-{5}\n'.format(c_strict, i_strict, d_strict, c_lenient, i_lenient, d_lenient, error)
    print 'Strict\nPrecision: {0}\t\tRecall: {1}\t\tF: {2}\n'.format(precision_strict,recall_strict,f_strict)
    print 'Lenient\nPrecision: {0}\t\tRecall: {1}\t\tF: {2}'.format(precision_lenient, recall_lenient, f_lenient)


def art_lower(oldfile, newfile):
    """Save aricles in lower case"""
    with open(oldfile) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        soup.prettify()
        with open(newfile, 'a') as the_file:
            for art in soup.findAll('pubmedarticle'):
                try:
                    the_file.write(art.articletitle.text.strip().lower() + '\n')
                except:
                    pass
                try:
                    the_file.write(art.abstracttext.text.strip().lower() + '\n')
                except:
                    pass


def cal_frequ(folder, file, resultsfile, gram_length, v2=False):
    print "Calculating PMI for "+file
    counter_input = {}
    counter_brown = {}
    result = {}
    input = ''
    grams = []
    corpus = []
    pmi = {}
    npmi = {}
    lem_variations = {}
    with open(folder+'/'+file) as fp:
        if '.xml' in file:
            soup = BeautifulSoup(fp, 'html.parser')
            soup.prettify()
            art = soup.findAll('pubmedarticle')
            for i in range(len(art)):
                try:
                    for sent in sent_tokenize("".join([str(x).decode("utf-8", "ignore") for x in art[i].articletitle.contents])):
                        try:
                            get_tag_pos(art[i].articletitle)
                            if "<brainregion>" in sent:
                                innerhtml = BeautifulSoup(sent, 'html.parser')
                                innerhtml.prettify()
                                input += innerhtml.text + '\n'
                        except:
                            pass
                    for sent in sent_tokenize("".join([str(x) for x in art[i].abstracttext.contents])):
                        try:
                            get_tag_pos(art[i].abstracttext)
                            if "<brainregion>" in sent:
                                innerhtml = BeautifulSoup(sent, 'html.parser')
                                innerhtml.prettify()
                                input += innerhtml.text + '\n'
                        except:
                            pass
                except:
                    pass
        else:
            linecounter = 0
            for line in fp.readlines():
                    for sent in sent_tokenize(line.decode("utf-8", "ignore")):
                        try:
                            innerhtml = BeautifulSoup(sent, 'html.parser')
                            innerhtml.prettify()
                            if "<brainregion>" in sent.lower():
                                input += innerhtml.text + '\n'
                            tokens = word_tokenize("".join(['brainregionplaceholder' if type(c) == Tag else c for c in innerhtml.contents]))
                            corpus.extend([WordNetLemmatizer().lemmatize(i, pos='v') for i in tokens])
                            if gram_length != 0:
                                [grams.append(n) for n in ngrams([WordNetLemmatizer().lemmatize(i, pos='v') for i in tokens], gram_length)]
                            else:
                                grams.append([WordNetLemmatizer().lemmatize(i, pos='v') for i in tokens])
                        except Exception,e:
                            print str(e)
                            pass
                    linecounter += 1
                    if linecounter % 1000 == 0:
                        print str(linecounter) + " - " + str(len(grams))
    print 'Loading corpus done'
    tokens = word_tokenize(input.replace('\n', ' '))
    print 'Loading tokens done: '+str(len(tokens))
    bc = brown.tagged_words(categories=list(set(brown.categories()) - set('learned')))
    for v in [(wt[0][0], wt[1]) for wt in FreqDist(pos_tag(tokens)).most_common() if wt[0][1].startswith('V')]:
        lemma = WordNetLemmatizer().lemmatize(v[0], pos='v')
        if lemma in lem_variations.keys():
            if v[0] not in lem_variations[lemma].keys():
                lem_variations[lemma][v[0]] = 1
            else:
                lem_variations[lemma][v[0]] += 1
        else:
            lem_variations[lemma] = {v[0]: 1}
        counter_input[lemma] = counter_input[lemma] + v[1] if lemma in counter_input.keys() else v[1]
    print 'Calculating FreqDist of the corpus done'
    for v in [(wt[0][0], wt[1]) for wt in FreqDist(bc).most_common() if wt[0][1].startswith('V')]:
        lemma = WordNetLemmatizer().lemmatize(v[0], pos='v')
        counter_brown[lemma] = counter_brown[lemma] + v[1] if lemma in counter_brown.keys() else v[1]
    print 'Calculating FreqDist of brown done'
    for v in counter_input.keys():
        result[v] = operator.truediv(counter_input[v], len(tokens)) - operator.truediv(counter_brown[v],
                                                                                       len(bc)) \
            if v in counter_brown.keys() else operator.truediv(counter_input[v], len(tokens))
    print 'Calculating most common verbs done'
    flist = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    try:
        with open("FreqDist_"+resultsfile, 'a') as the_file:
            the_file.write(file + '\n')
            [the_file.write(str(x) + '\n') for x in flist[:100]]
            the_file.write('\n\n')
    except:
        pass
    if len(flist) < 1000:
        flen = len(flist)
    else:
        flen = 1000
    corpuslen = len(corpus)
    zzz = 0
    for z in flist[:flen]:
        try:
            gsum = sum('brainregionplaceholder' in i and z[0] in i for i in grams)
            if v2:
                pmi[z[0]] = log(operator.truediv(operator.truediv(gsum, len(grams)), operator.truediv(sum('brainregionplaceholder' in i for i in grams), len(grams)) * operator.truediv(sum(z[0] in i for i in grams), len(grams))))
                npmi[z[0]] = operator.truediv(pmi[z[0]], -log(operator.truediv(gsum, len(grams))))
            else:
                pmi[z[0]] = log(operator.truediv(corpuslen*gsum,
                                corpus.count('brainregionplaceholder')*corpus.count(z[0])))
                npmi[z[0]] = operator.truediv(pmi[z[0]], -log(operator.truediv(gsum, corpuslen)))
        except:
            pass
        zzz += 1
        if zzz % 10 == 0:
            print zzz
    print 'Calculating PMI done'
    print sorted(pmi.items(), key=operator.itemgetter(1), reverse=True)[:100]
    with open(resultsfile, 'a') as the_file:
        the_file.write(file + '\n')
        [the_file.write(str(x) + '\n' + str(sorted(lem_variations[x[0]].items(), key=operator.itemgetter(1), reverse=True)) + '\n') for x in sorted(pmi.items(), key=operator.itemgetter(1), reverse=True)]
        the_file.write('\n\n')
    with open("NPMI_"+resultsfile, 'a') as the_file:
        the_file.write(file + '\n')
        [the_file.write(str(x) + '\n' + str(sorted(lem_variations[x[0]].items(), key=operator.itemgetter(1), reverse=True)) + '\n') for x in sorted(npmi.items(), key=operator.itemgetter(1), reverse=True)]
        the_file.write('\n\n')


print "OK"
"""

for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS0T.txt', 0, v2=True)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)

for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS5T.txt', 5, v2=True)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)

for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS3T.txt', 3, v2=True)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)


for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS0F.txt', 0, v2=False)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)

for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS5F.txt', 5, v2=False)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)

for c in ['nsd','neuro','nmb']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS3F.txt', 3, v2=False)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)


for c in ['nn','cel','cno','dis','func','inv']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTST.txt', 0, v2=True)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)

for c in ['nn','cel','cno','dis','func','inv']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTST5.txt', 5, v2=True)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)


for c in ['nn','cel','cno','dis','func','inv']:
    try:
        cal_frequ('./tagged', c+'.txt', 'RESULTS.txt', 0)
    except Exception,e:
        with open('RESULTS.txt', 'a') as the_file:
            the_file.write('ERROR\n')
            print str(e)


with open("NMOBR_lower.txt", "r") as ins:
    with open("nmb.txt", 'a') as the_file:
        for line in ins:
            if len(line) > 5:
                the_file.write(line.lower())

with open("./added3_2/NMOBR_ext.txt", "r") as ins:
    with open("nmb.txt", 'a') as the_file:
        for line in ins:
            if len(line) > 5:
                the_file.write(line.lower())

            """
#eval_brain_regions('bc.xml', 'ner.xml')



"""
    tokens = word_tokenize(raw)
    text = Text(tokens)
    fdist1 = FreqDist(text)
    x = [EnglishStemmer().stem(i) for i in tokens]
    fdist2 = FreqDist(Text(x))
    fdist3 = FreqDist(pos_tag(tokens))
    print fdist1.most_common(50)
    print fdist2.most_common(50)
    z =[wt[0] for (wt, _) in fdist3.most_common() if wt[1].startswith('V')]
    print z

#cal_frequ()

for x in ['NSD']:
    with open(x+".txt", "r") as ins:
        with open('nerlist/'+x+".txt", 'a') as the_file:
            bro = (set(brown.words()) - set(
                        brown.words(categories=['learned'])))
            for line in ins:
                if len(line)>4:
                    the_file.write(line.lower())
                    """
#eval_brain_regions('bc.xml', 'ner.xml')