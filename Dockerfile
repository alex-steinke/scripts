FROM python:2.7
RUN apt-get update
RUN apt-get -y remove ipython
RUN apt-get -y install less vim nano ipython npm
RUN pip install --user matplotlib jupyter pandas mock teamcity-nose django==1.10.6 django-bootstrap3==8.2.1 bs4 lxml requests nltk git+git://github.com/jkitchin/scopus
#RUN easy_install nose flake8
RUN npm install difflib
ADD ./ ./opt/sbml
RUN python -m nltk.downloader brown words wordnet punkt averaged_perceptron_tagger
RUN mkdir /root/.scopus
RUN echo 'MY_API_KEY = "cf180549a5478b7660313e3218e68093"' >> /root/.scopus/my_scopus.py
