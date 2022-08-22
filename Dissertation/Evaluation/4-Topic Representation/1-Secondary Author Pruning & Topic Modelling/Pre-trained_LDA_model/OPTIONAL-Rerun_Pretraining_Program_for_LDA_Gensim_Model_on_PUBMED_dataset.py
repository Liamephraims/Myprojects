#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 15:14:59 2020

File for PRE-TRAINING for Latent Dirichlet allocation (LDA) classification of cancer researcher interests

****BASED ON GENSIM LDA DOCUMENTATION***

@author: Liam Ephraims
"""

import re
import os
import numpy as np
import pandas as pd
from pprint import pprint

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# spacy for lemmatization
import spacy

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

#Importing Biomedical PUBMED publication dataset for training LDA model adding these to the orgs title abstract collection:
def get_file_list(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        file_list.append(files)
    return file_list[0]
filedir = 'C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/cancer_PUBMED_dataset/'
PUBMED_papers = get_file_list(filedir)
paper_cnt = 0
PUBMED_title_abstract_dict = dict()
for file in PUBMED_papers:
    print("...",paper_cnt, "of", len(PUBMED_papers), "PUBMED papers remaining...")
    filename = filedir + file
    #print(filename)
    publication_data =  open(filename,"r",encoding='utf-8')
    pub_list = []
    cnt = 0
    for line in publication_data.readlines():
        if cnt % 2 != 0:
            pub_list.append(line)
            #print(line)
        cnt += 1
        # first index == title, second index == abstract, third index == keywords
        #print(pub_list)
    PUBMED_title_abstract_dict[pub_list[0]] = pub_list[1]
    paper_cnt += 1
print(paper_cnt, "files added to the PUBMED title_abstract_dict from PUBMED Biomedical and Health Science Dataset as a training dataset for LDA.")


#Cleaning training dataset - based on PUBMED Cancer-related papers:
title_abstract_text_list = []
count = 0
for i in PUBMED_title_abstract_dict:
    count += 1
    abstract = PUBMED_title_abstract_dict[i]
    #adding in title with abstract:
    abstract = abstract + " " + i
    title_abstract_text_list.append(abstract)
data = title_abstract_text_list
print("EXTRACTED", len(title_abstract_text_list),"PUBLICATIONS FROM PUBMED-TRAINING TITLE-ABSTRACT DICT")
# Remove new line characters
data = [re.sub('\s+', ' ', sent) for sent in data]

# Remove distracting single quotes
data = [re.sub("\'", "", sent) for sent in data]

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

data_words = list(sent_to_words(data))

# Build the bigram and trigram models
bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)

# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
#python3 -m spacy download en
nlp = spacy.load('en', disable=['parser', 'ner'])

# Define functions for stopwords, bigrams, trigrams and lemmatization
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

# Remove Stop Words
data_words_nostops = remove_stopwords(data_words)

# Form Bigrams
data_words_bigrams = make_bigrams(data_words_nostops)

# Do lemmatization keeping only noun, adj, vb, adv
data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized)

# Create Corpus
texts = data_lemmatized

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

def compute_coherence_values(corpus, dictionary, texts,limit, start=2, step=3):
    """
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    perplexity_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        print("Training LDA for", num_topics, "topics")
        model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=num_topics, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
        perplexity_values.append(model.log_perplexity(corpus))
    return model_list, coherence_values, perplexity_values
model_list, coherence_values,perplexity_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=1, limit=51, step=5)

    
# Coherence graph:
x = range(1, 51, 5)
plt.plot(x, coherence_values)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E4-Topic Figures/Global_Coherence")
plt.show()

#Perplexity Graph:
x = range(1, 51, 5)
plt.plot(x, perplexity_values)
plt.xlabel("Num Topics")
plt.ylabel("Perplexity score")
plt.legend(("Perplexity_values"), loc='best')
plt.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E4-Topic Figures/Global_Perplexity")
plt.show()

# Print the coherence scores
print("FIRST GLOBAL RUN:")
for m, cv, pv in zip(x, coherence_values,perplexity_values):
    print("Num Topics =", m, " has Coherence Value of", round(cv, 4), "and Perplexity Value of",round(pv,4))
    

limit=51; start=1; step=5;
topic_range = [num for num in range(start, limit, step)]
#Selecting best model to retrain for local topic range:
max_coherence = 0
best_model = ''
topic_num_final = 0
for model, coherence, perplexity, topic_num in zip(model_list, coherence_values,perplexity_values, topic_range):
    if coherence > max_coherence:
        max_coherence = coherence
        best_model = model
        topic_num_final = topic_num
if topic_num_final - 5 < 1:
    topic_num_start = 1
elif not topic_num_final - 5 < 1:
    topic_num_start = topic_num_final - 5

#retraining for best model:
model_list, coherence_values,perplexity_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=topic_num_start, limit=topic_num_final + 5, step=1)

# Print the coherence scores
print("SECOND LOCAL RUN:")
for m, cv, pv in zip(x, coherence_values,perplexity_values):
    print("Num Topics =", m, " has Coherence Value of", round(cv, 4), "and Perplexity Value of",round(pv,4))
    
# Coherence graph:
limit=topic_num_final + 5; start=topic_num_start; step=1;
x = range(start, limit, step)
plt.plot(x, coherence_values)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E4-Topic Figures/Local_range_Coherence")
plt.show()

#Perplexity Graph:
limit=topic_num_final + 5; start=topic_num_start; step=1;
x = range(start, limit, step)
plt.plot(x, perplexity_values)
plt.xlabel("Num Topics")
plt.ylabel("Perplexity score")
plt.legend(("Perplexity_values"), loc='best')
plt.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E4-Topic Figures/Local_range_Perplexity")
plt.show()

topic_range = [num for num in range(start, limit, step)]
max_coherence = 0
best_model = ''
topic_num_final = 0
for model, coherence, perplexity, topic_num in zip(model_list, coherence_values,perplexity_values, topic_range):
    if coherence > max_coherence:
        max_coherence = coherence
        best_model = model
        topic_num_final = topic_num

# Saving visualization of topics as html for users to vizualise LDA model topic distributions:
vis = pyLDAvis.gensim.prepare(best_model, corpus, id2word)
pyLDAvis.save_html(vis, 'C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/2-Assignment of Topic Labels using Modelled Topics/trained_LDA_topics.html')

# Saving model to disk.
from gensim.test.utils import datapath
temp_file = datapath("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Pre-trained_LDA_model/trained_LDA")
best_model.save(temp_file)



