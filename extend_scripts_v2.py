from nltk import ngrams
from nltk.corpus import wordnet as wn
from nltk.tokenize import TweetTokenizer
from nltk.corpus import brown
from itertools import chain
from itertools import product
from nltk.corpus import PlaintextCorpusReader
import re
import time


def extend_wordlists(absfile, wordlists, newfolder, drf=True, syn=True, perta=True, extend=True):
    """For each given wordlist create different varriations for each entry and save them if they are
    present in the abstract.

    :param absfile:     Corpus to check if terms ocure
    :param wordlists:   List of filenames of wordlists
    :param newfolder:   Folder to save generated terms
    :param drf:         Should derivationally related forms be used (Default: True)
    :param syn:         Should synonyms be used (Default: True)
    :param perta:       Should pertainyms be used (Default: True)
    :return:
    """

    # create a corpus from abstracts
    corpus = PlaintextCorpusReader('./', absfile)
    # list of new terms
    new = []
    # create a corpus from brown corpus without 'learned' category
    cat = brown.categories()
    cat.pop(brown.categories().index('learned'))
    bc = "".join([" ".join(list_of_words) for list_of_words in brown.sents(categories=cat)])
    # create a bigram set from abstract
    bg = set()
    old = []
    with open(absfile, "r") as ins:
        for line in ins:
            linebigrams = ngrams(line.lower().split(), 2)
            for grams in linebigrams:
                bg.add(grams)
    print 'Abstract Bigrams done: ' + str(len(list(bg)))
    # for each wordlist
    for txtfile in wordlists:
        bgwl = set()
        with open(txtfile+".txt", "r") as ins:
            for line in ins:
                old.append(line)
                linebigrams = ngrams(line.lower().split(), 2)
                for grams in linebigrams:
                    bgwl.add(grams)
        print 'Wordlist Bigrams done: ' + str(len(list(bgwl)))
        with open(txtfile+".txt", "r") as ins:
            linecount = 0
            for line in ins:
                #print 'Line: '+line
                linecount += 1
                if linecount % 100 == 0:
                    print 'Line: '+str(linecount)
                # create bigrams the line in the wordlist
                bigrams = ngrams(line.lower().split(), 2)
                bgl = set()
                for grams in bigrams:
                    bgl.add(grams)
                # terms containing a single word are ignored
                # if there is just one bigram
                if len(bgl) == 1:
                    # generate all variations
                    gen_list = gen_vars(bgl, 0, drf, syn, perta)
                    #print gen_list
                    # save the term if it is in the abstract but not in brown corpus
                    for i in gen_list:
                        if i in bg:
                            if str(i[0] + ' ' + i[1]).encode('utf-8').strip() not in bc.lower():
                                try:
                                    with open(newfolder+txtfile+'_ext.txt', 'a') as the_file:
                                        if extend:
                                            for newext in list(set(extend_term(bgwl, i[0]+' '+i[1], corpus))):
                                                print "- " + newext
                                                if newext not in new and newext not in old:

                                                    new.append(newext)
                                                    the_file.write(newext + '\n')
                                        else:
                                            if i[0] + ' ' + i[1] not in new and i[0] + ' ' + i[1] not in old:
                                                new.append(i[0] + ' ' + i[1])
                                                the_file.write(i[0] + ' ' + i[1] + '\n')
                                except Exception:
                                    pass
                # if a term has more then one bigram do the same for each
                # only concider new variations with the same token length as original
                if len(bgl) > 1:
                    y = []
                    ok = True
                    for num in range(len(bgl)):
                        y.append(set())
                        gen_list = gen_vars(bgl, num, drf, syn, perta)
                        for i in gen_list:
                            if i in bg:
                                y[num].add(i)
                    for num in range(len(bgl)):
                        if len(y[num]) == 0:
                            ok = False
                        if 0 < num < (len(bgl)-1):
                            if len(y[num]) < len(y[num+1]):
                                ok = False
                        y[num] = list(y[num])
                    if all(i == 1 for i in map(len, y)):
                        ok = False
                    if ok:
                        finall = list(product(*y))
                        filtered = []
                        for bgfl in finall:
                            count = {}
                            for eint in bgfl:
                                if eint[0] in count.keys():
                                    count[eint[0]] += 1
                                else:
                                    count[eint[0]] = 1
                                if eint[1] in count.keys():
                                    count[eint[1]] += 1
                                else:
                                    count[eint[1]] = 1
                            if count.values().count(1) == 2:
                                filtered.append(bgfl)
                        if len(filtered) > 1:
                            for v in filtered:
                                text = ''
                                for v2 in v:
                                    if v2[0] in text:
                                        text = text.replace(v2[0], v2[0]+' '+v2[1])
                                    if v2[1] in text:
                                        text = text.replace(v2[1], v2[0]+' '+v2[1])
                                    else:
                                        text = v2[0]+' '+v2[1]
                                if (len(list(ngrams(line.lower().split(), 2))) == len(list(ngrams(text.lower().split(), 2)))) and text.lower().split() != line.lower().split():
                                    myregex = re.compile('\W'+re.escape(text.encode('utf-8').lower().strip())+'\W')
                                    if len(myregex.findall(corpus.raw().encode('utf-8').lower())) > 0 and text.encode('utf-8').strip() not in bc.lower():
                                        try:
                                            with open(newfolder + txtfile + '_ext.txt', 'a') as the_file:
                                                #print text
                                                if extend:
                                                    for newext in list(
                                                            set(extend_term(bgwl, text.strip(), corpus))):
                                                        if newext not in new and newext not in old:
                                                            print "- "+newext
                                                            new.append(newext)
                                                            the_file.write(newext + '\n')
                                                else:
                                                    if text.strip() not in new and text.strip() not in old:
                                                        new.append(text.strip())
                                                        the_file.write(text.strip() + '\n')
                                        except Exception:
                                            pass


def gen_vars(bgl, num, drf, syn, perta):
    """Generate all possible variations for a given bigram
    :param bgl:         Bigram set of the term
    :param num:         Bigram number
    :param drf:         Should derivationally related forms be used (Default: True)
    :param syn:         Should synonyms be used (Default: True)
    :param perta:       Should pertainyms be used (Default: True)
    :return:            List of all possible variations
    """
    bg = list(bgl)[num]
    lemma1 = set()
    lemma2 = set()
    lemma1.add(bg[0])
    lemma2.add(bg[1])
    if drf:
        [lemma1.add(k.name().replace('_', ' ')) for k in chain(
            *[j.derivationally_related_forms() for j in
              chain(*[i.lemmas() for i in wn.synsets(bg[0])])])]
        [lemma2.add(k.name().replace('_', ' ')) for k in chain(
            *[j.derivationally_related_forms() for j in
              chain(*[i.lemmas() for i in wn.synsets(bg[1])])])]
    if syn:
        [lemma1.add(k.name().replace('_', ' ')) for k in chain(*[i.lemmas() for i in wn.synsets(bg[0])])]
        [lemma2.add(k.name().replace('_', ' ')) for k in chain(*[i.lemmas() for i in wn.synsets(bg[1])])]
    if perta:
        [lemma1.add(k.name().replace('_', ' ')) for k in chain(*[j.pertainyms() for j in
                                                             chain(*[i.lemmas() for i in
                                                                     wn.synsets(
                                                                         bg[0])])])]
        [lemma2.add(k.name().replace('_', ' ')) for k in chain(*[j.pertainyms() for j in
                                                             chain(*[i.lemmas() for i in
                                                                     wn.synsets(
                                                                         bg[1])])])]
    return list(product(lemma1, lemma2))


def extend_term(bgwl, term, corpus):
    """Extern the term based on bigrams in the wordlist and availabity of the extended form in the abstract
    :param bgwl:    Bigram list of the wordlist
    :param term:    Term to extend
    :param corpus:  Abstract corpus
    :return:        List with extended terms
    """
    tknzr = TweetTokenizer()
    tokens = tknzr.tokenize(term)
    newlist = []
    for i in [item[1] for item in bgwl if item[0] == tokens[len(tokens) - 1]]:
        #print re.escape((term + " " + i).encode('utf-8').lower().strip())
        myregex = re.compile('\W' + re.escape((term + " " + i).encode('utf-8').lower().strip()) + '\W')
        if len(myregex.findall(corpus.raw().encode('utf-8').lower())) > 0:
            #print term + " - " + i
            newlist.extend(extend_term(bgwl, (term + " " + i).lower(), corpus))
    for i in [item[0] for item in bgwl if item[1] == tokens[0]]:
        #print re.escape((term + " " + i).encode('utf-8').lower().strip())
        myregex = re.compile('\W' + re.escape((i + " " + term).encode('utf-8').lower().strip()) + '\W')
        if len(myregex.findall(corpus.raw().encode('utf-8').lower())) > 0:
            #print i + " - " + term
            newlist.extend(extend_term(bgwl, (i + " " + term).lower(), corpus))
    if len(newlist) == 0:
        newlist.append(term)
    #print 'LIST:'
    #print newlist
    return newlist

start = time.time()
extend_wordlists('abstract2.txt', ['cno','NMOBR','cel','inv','func','dis','mol','brain_nn'], './added3_2/', drf=True, syn=False, perta=True, extend=False)
#extend_wordlists('abstract.txt', ['cno','NMOBR','cel','inv','func','dis','mol','brain_nn','brain'], './added4_2/', drf=True, syn=True, perta=True, extend=False)

end2 = time.time()
hours, rem = divmod(end2-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))