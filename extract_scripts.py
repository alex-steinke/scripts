from bs4 import BeautifulSoup
from nltk.corpus import brown
import requests
import time
from os import listdir
from os.path import isfile, join


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
                                the_file.write(item + '\n')
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




