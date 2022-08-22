#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
https://www.aclweb.org/anthology/D11-1024.pdf - coherence
https://www.jstage.jst.go.jp/article/transinf/E99.D/4/E99.D_2015DAP0031/_pdf/-char/en - topic mod/representations
PUBMED training dataset - https://ieee-dataport.org/open-access/biomedical-keyphrase-extraction-dataset
PUBMED training dataset paper -file:///C:/Users/Liam%20Ephraims/Downloads/Keyphrase_Generation_with_CopyNet_and_Semantic_Web.pdf


Created on Tue Jun 23 15:36:35 2020

@author: Liam Ephraims
Context:
Secondary Pruning Protocol for Secondary Authors whos papers were removing in primary author disambiguation
and further only taking secondary author papers which are co-authored with primary authors:
Secondary Author Pruning Protocol and Final disambiguated Dataset Construction: 
1. Will extract a dataset from all disambig primary author XMLS
2. Create a dictionary of title: primary author list
3. Read in secondary author papers iff paper title is in title: primary author list dictionary
4. Iff after reading secondary authors papers, secondary author no longer has any papers then remove the author
   from the final dataset
   
Following Author pruning, pre-trained LDA topic model imported and used to infere topics of all cancer researhers.

Then using topic vectors for each researcher over their set of papers, we calculate their topic vector centroids
and use this to vizualise their topic expertise network based on cosin similarity matrix between researchers centroids (using this as edge weight for subsequent vizualisations - instead of individual edge topic links)

"""

import pickle
import pandas as pd
import os
#Getting primary author names:
primary_authors = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
primary_authors_set = set(primary_authors.Name)



def get_title_abstract_dict():
    file_title_abstract = open('C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/2-Running Disambiugation and Cluster Comparison/PRIMARY_AUTHORS_XML/title_abstract_disseration_test.txt','r',encoding="utf-8", errors='replace')
    title_abstract_dict = {}
    for line in file_title_abstract.readlines():
        #Getting document of titles and abstracts divided by <>
        if "<>" in line:
            arr=line.split("<>")
            #splits by key and value - title/abstract - returning as [title - arr[0], abstract arr[1]]
            #print(line)
            #print(arr)
            if len(arr)>1:
                title_abstract_dict[arr[0].strip()]=arr[1].strip()
                #print("arr length > 1", title_abstract_dict[arr[0]])
                #print("Key", arr[0])
            else:
                title_abstract_dict[arr[0].strip()]=""
            # if length of arr is not > 1 then only a title is present without abstract.
    return title_abstract_dict
    
title_abstract_dict = get_title_abstract_dict() 

def get_file_list(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        file_list.append(files)
    return file_list[0]

#Schema for primary dataset:
def primary_assemble(file_path,author_type):
    author_list = []
    file_path_list = file_path  + "disambiguated_main/" 
    print(file_path_list)
    file_list = get_file_list(file_path_list)

    #print(file_list)

    #Sorting file list alphabetically
    file_list = sorted(file_list)
    #Unsure of exact purpose
    file_list = file_list[:]
    #counter
    cnt = 0
    summary_final_primary_dict = {}
    #Begins iteration for each author file going into main function.
    #Extracting primary authors disambiguated files:
    for x in file_list:
        cnt += 1
        pub_cnt = 0
        read_status = "False"
        filename = file_path + "disambiguated_main/" + str(x)
       # print(filename)
        
        with open(filename, "r",encoding='utf-8') as filetoread:
            # 这里是一行一行读取的文件
            for line in filetoread:
                line = line.strip()
                #print(line)
                if "FullName" in line:
                    name = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<title>" in line:
                    title = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<DOI>" in line:
                    DOI = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<jconf>" in line:
                    jconf = line[line.find('>')+1: line.rfind('<')].strip()                      
                elif "<year>" in line:
                    year = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<organization>" in line: 
                    organization = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<authors>" in line:
                    authors = line[line.find('>')+1: line.rfind('<')].strip()                                        
 #              elif ("<label>" in line):  
 #              elif ("<year>" in line):
                elif ("<total_cnt>" in line):
                    total_cnt = line[line.find('>')+1: line.rfind('<')].strip() 
                elif "</publication>" in line:
                   ## print("ENTERED END PUB:", [name, title,jconf,organization,authors,DOI])
                    topic_place_holder = ''
                    topic_place_holder2 = ''
                    abstract_place_holder = ''
                    author_list.append([year,name, title,jconf,organization,authors,DOI,abstract_place_holder])
                    pub_cnt += 1
        print("Extracted", pub_cnt, "publications of", total_cnt, "total XML publications for author", str(x))
        read_status = "True"
        summary_final_primary_dict[name] = [pub_cnt,read_status]
    print("Read in",cnt, "primary authors to final dataset")
    return author_list,summary_final_primary_dict,cnt
       
def secondary_assemble(file_path,author_type):
    author_list = []
    file_path_list = file_path  + "MAIN/" 
    print(file_path_list)
    file_list = get_file_list(file_path_list)

    #print(file_list)

    #Sorting file list alphabetically
    file_list = sorted(file_list)
    #Unsure of exact purpose
    file_list = file_list[:]
    print("File list is",file_list)
    #counter
    cnt = 0
    #Begins iteration for each author file going into main function.
    #Extracting primary authors disambiguated files:
    for x in file_list:
        cnt+=1 
        pub_cnt = 0
        pruned_cnt = 0
        filename = file_path + "MAIN/" + str(x)
       # print(filename)
        
        with open(filename, "r",encoding='utf-8') as filetoread:
            # 这里是一行一行读取的文件
            for line in filetoread:
                line = line.strip()
                #print(line)
                if "FullName" in line:
                    name = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<title>" in line:
                    title = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<jconf>" in line:
                    jconf = line[line.find('>')+1: line.rfind('<')].strip()                      
                elif "<year>" in line:
                    year = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<organization>" in line: 
                    organization = line[line.find('>')+1: line.rfind('<')].strip()
                elif "<authors>" in line:
                    authors = line[line.find('>')+1: line.rfind('<')].strip() 
                elif "<DOI>" in line:
                    DOI = line[line.find('>')+1: line.rfind('<')].strip()                                       
 #              elif ("<label>" in line):  
                elif ("<total_cnt>" in line):
                    total_cnt = line[line.find('>')+1: line.rfind('<')].strip() 
                elif "</publication>" in line:
                    if (title in title_set) or (DOI in doi_set):
                        topic_place_holder = ''
                        topic_place_holder2 = ''
                        abstract_place_holder = ''
                        print("ENTERED END PUB and secondary authors pub in primary author dataset!", [name, title,jconf,organization,authors,DOI])
                        author_list.append([year, name, title,jconf,organization,authors,DOI,abstract_place_holder])
                        pub_cnt += 1
                    else:
                        print("publication", DOI, "not in primary dataset pruning secondary author publciation")
                        pruned_cnt += 1
                        
        print("Extracted", pub_cnt, "publications of", total_cnt, "total XML publications for author", str(x))
        print(pruned_cnt, "papers were pruned of a total",total_cnt,"for author", str(x))
    print("Read in", cnt, "secondary authors to final dataset")
    return author_list, cnt


#Beginning primary and secondary author extraction for final dataset:     
primary_disamb_path = "C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/2-Running Disambiugation and Cluster Comparison/PRIMARY_AUTHORS_XML/"

Primary_list,summary_primary_dict,primary_cnt = primary_assemble(file_path=primary_disamb_path,author_type="PRIMARY")
Primary_dataframe = pd.DataFrame(Primary_list, columns = ['year','name', 'title', 'jconf','organization', 'coauthors',"DOI", "TOPICS"])
title_set = set(Primary_dataframe['title'])
doi_set = set(Primary_dataframe['DOI'])
disambig_summary = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
for i in range(len(disambig_summary)):
    if disambig_summary['Name'][i] in summary_primary_dict:
        disambig_summary['Read_Count'][i] = summary_primary_dict[disambig_summary['Name'][i]][0]
        disambig_summary['Read_status'][i] = summary_primary_dict[disambig_summary['Name'][i]][1]
disambig_summary.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
#disambig_summary.loc[0]
Secondary_path = "C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/2-Running Disambiugation and Cluster Comparison/SECONDARY_AUTHORS_XML/"
Secondary_list, secondary_cnt = secondary_assemble(file_path=Secondary_path,author_type="SECONDARY")
Secondary_dataframe = pd.DataFrame(Secondary_list, columns = ['year','name', 'title', 'jconf','organization', 'coauthors',"DOI","TOPICS"])
#ADD dois to XML extractions
#For secondary author read lines
#Iff paper title OR DOI IN primary_Dataset then append to secondary dataset- else SKIP

#Combine primary and secondary datasets into final disambiguated dataset.
final_dataset = pd.concat([Primary_dataframe, Secondary_dataframe],ignore_index=True )
print("Final dataset created with:",primary_cnt,"primary authors read and",secondary_cnt,"secondary authors read into final dataset")

#Loading TRAINED GENSIM-LDA MODEL: Trained on 10000 PUBMED data mined/crawled Cancer-related publications (title and abstract):
from gensim.test.utils import datapath
import gensim

# Loading pretrained LDA model from disk.
temp_file = datapath("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Pre-trained_LDA_model/trained_LDA")
trained_LDA = gensim.models.ldamodel.LdaModel.load(temp_file)

#Beginning text cleaning pipeline for primary organisations researchers papers:

import re
import numpy as np
import pandas as pd

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess

# spacy for lemmatization
import spacy

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

#Cleaning training dataset - based on PUBMED Cancer-related papers:
title_abstract_text_list = []
count = 0
for i in title_abstract_dict:
    count += 1
    abstract = title_abstract_dict[i]
    #adding in title with abstract:
    abstract = abstract + " " + i
    title_abstract_text_list.append(abstract)
# Remove new line characters
abstract = [re.sub('\s+', ' ', sent) for sent in title_abstract_text_list]

# Remove distracting single quotes
abstract = [re.sub("\'", "", sent) for sent in title_abstract_text_list]
abstract_words = list(sent_to_words(title_abstract_text_list))
    
# Build the bigram and trigram models
bigram = gensim.models.Phrases(abstract_words, min_count=5, threshold=100) # higher threshold fewer phrases.
  
# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
    
# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
#python3 -m spacy download en
nlp = spacy.load('en', disable=['parser', 'ner'])

# Remove Stop Words
abstract_words_nostops = remove_stopwords(abstract_words)

# Form Bigrams
abstract_words_bigrams = make_bigrams(abstract_words_nostops)
    
# Lemmatization keeping only noun, adj, vb, adv
data_lemmatized = lemmatization(abstract_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

# Creating Dictionary
id2word = corpora.Dictionary(data_lemmatized)

#Creating inverse value-key dict for later calcultion of topic researcher centroids:
id2word_inverse_dict = dict()
for key, value in zip(id2word.keys(), id2word.values()):
     id2word_inverse_dict[value] = key
     
# Creating Corpus - Term Document Frequency
new_corpus = [id2word.doc2bow(text) for text in data_lemmatized]
    
#Creating term-document frequency dictionary for later calculating researcher centroids:
doc_corpus_term_frequency = dict()
for title, corpus in zip(title_abstract_dict.keys(),new_corpus ):
    doc_corpus_term_frequency[title] = corpus
    
title_topic_dict = dict()

#Training/Updating with new or unseen researchers papers in addition to pre-trained PUBMED dataset:
#for title,doc in zip(title_abstract_dict,new_corpus):
#    trained_LDA.update([doc])

#Beginning inference phase for adding topic probabilities for each researchers unseen (test) publications:
for title,doc in zip(title_abstract_dict,new_corpus):
    vector = trained_LDA[doc]
    title_topic_dict[title] = dict()
    #for topic in vector:
    title_topic_dict[title] = vector[0]


#Creating set containing all the non-zero probability word ids for all words associated with all topic distributions:
wordid_set = set()
topic_str = trained_LDA.show_topics(-1, len(id2word))
for topic, topstr in topic_str:
    topre = re.findall("(\d*\d.\d\d\d)\*\"(\w+)\"", topstr)
    for prob, word in topre:
        if float(prob) > 0.000:
            if word in id2word_inverse_dict:
                wordid_set.add(id2word_inverse_dict[word])

#Creating dictionary for each researcher, capturing the word tf (raw term frequency) across all
#topic distributions of the total corpus. Using this as a way of calculating the topic centroid for each
#author over these topic word distributions. Summing each tf for all researchers papers and dividing each by
#the number of abstracts.
researcher_topic_centroid_dict = dict()
researcher_topics_vector_centroid_dict = dict()
#Using ALL authors - primary author dataset to add topic labels for each author
#Creating an expertise dictionary for authors:
researcher_topic_representation_dict = dict()
author_paperscnt_dict = {}
author_expertise_dict = {}
author_topiccnt_dict = {}
unique_authors = set(final_dataset.name)
count = 0
for author in unique_authors:
    count += 1
    topic_set = set()
    topic_prop =set()
    print("...Beginning author {} - {} of {}".format(author, count, len(unique_authors)))
    researcher_topic_representation_dict[author] = dict()
    researcher_topic_centroid_dict[author] = dict()
    #Creating a topic word distribution vector over all words with a default count of zero for each author
    for wordid in wordid_set:
        researcher_topic_centroid_dict[author][wordid] = 0
    for num in range(len(wordid_set)): #number of topics from topic model
        researcher_topic_representation_dict[author][num] = 0
    paper_count = 0
   # print(final_dataset.iloc[row]['name'], author)
    for row in range(len(final_dataset)):
        if final_dataset.iloc[row]['name'] == author:
            paper_count += 1
            instance = final_dataset.iloc[row]
            if instance['title'] in doc_corpus_term_frequency:
                for wordid, freq in doc_corpus_term_frequency[title]:
                    if wordid in researcher_topic_centroid_dict[author]: 
                        researcher_topic_centroid_dict[author][wordid] +=freq
                    if not wordid in researcher_topic_centroid_dict[author]:   
                        researcher_topic_centroid_dict[author][wordid] = freq
                for topic, proportion in title_topic_dict[instance['title']]:
                    researcher_topic_representation_dict[author][topic] += proportion
                    topic_set.add(topic)
    
    author_paperscnt_dict[author] = paper_count
    author_topiccnt_dict[author] = topic_set
    #Now dividing each topic word frequency count by the number of papers and adding to vector of
    ##each researchers topic word centroid or topic representation:
    researcher_topic_vector = []
    for wordindex in researcher_topic_centroid_dict[author]:
        researcher_topic_centroid_dict[author][wordid] = int(researcher_topic_centroid_dict[author][wordid]/ author_paperscnt_dict[author])
        researcher_topic_vector.append(researcher_topic_centroid_dict[author][wordid])
        researcher_topics_vector_centroid_dict[author] = np.array(researcher_topic_vector)
    
    for topic in researcher_topic_representation_dict[author]:
        #Creating final topic proportions for author:
        researcher_topic_representation_dict[author][topic] = researcher_topic_representation_dict[author][topic]/author_paperscnt_dict[author]
    author_expertise_dict[author] = researcher_topic_representation_dict[author]
#Creating the cosin similarity matrix for all researchers based on their topic representation vectors:
#import pandas as pd#

#import math
#def cosine_similarity(v1,v2):
#  # "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
#    sumxx, sumxy, sumyy = 0, 0, 0
#    for i in range(len(v1)):
#        x = v1[i]; y = v2[i]
#        sumxx += x*x
#        sumyy += y*y
#        sumxy += x*y
#    return sumxy/math.sqrt(sumxx*sumyy)
 
#Creating dictionary for sum of researchers topic vector counts
#researcher_topics_vector_truth_dict = dict()
#for researchers in researcher_topics_vector_centroid_dict:
#    running_total = 0.0
#    for count in researcher_topics_vector_centroid_dict[researchers]:
#        running_total += count
#    if running_total == 0:
#       researcher_topics_vector_truth_dict[researchers] = False
#researchers =[ researchers for researchers in researcher_topics_vector_centroid_dict.keys() if not researchers in researcher_topics_vector_truth_dict and researchers in primary_authors_set]

#This needs to be optimized - very slow.
#author_pairs_dict_topic = dict()
#def cossim_matrix(researchers):
#    for i in range(len(researchers)):
#        for j in range(len(researchers)):
##            if researchers[i] != researchers[j]:
#                if not ((researchers[i],researchers[j])) in author_pairs_dict_topic and not ((researchers[j],researchers[i])) in author_pairs_dict_topic:
#                    author_pairs_dict_topic[((researchers[i],researchers[j]))] = round(cosine_similarity(researcher_topics_vector_centroid_dict[researchers[i]],researcher_topics_vector_centroid_dict[researchers[j]]),2)
#cossim_matrix(researchers)

#pickling_on = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Researcher_cosine_distance_dict.pickle","wb")
#pickle.dump(author_pairs_dict_topic, pickling_on)
#pickling_on.close()


for row in range(len(final_dataset)):
    if final_dataset.iloc[row]['title'] in title_abstract_dict:  
        final_dataset.iloc[row]['abstract'] = title_abstract_dict[final_dataset.iloc[row]['title']]

    
for row in range(len(final_dataset)):
    #if final_dataset.iloc[row]['title'] in title_abstract_dict:  
       # final_dataset.iloc[row]['abstract'] = title_abstract_dict[final_dataset.iloc[row]['title']]
    if final_dataset.iloc[row]['title'] in title_topic_dict:
       # final_dataset.iloc[row]['Primary_topic_labels'] = author_expertise_dict_labels[final_dataset.iloc[row]['name']][0] 
        #final_dataset.iloc[row]['Secondary_topic_labels'] = author_expertise_dict_labels[final_dataset.iloc[row]['name']][1]
        topics_vec = []
        for topic, prop in title_topic_dict[final_dataset.iloc[row]['title']]:
            topics_vec.append((topic, prop))
        final_dataset.iloc[row]['TOPICS'] = topics_vec
 
    
#Creating a CSV file for capturing each researchers data:
dataset_list = []
for author in set(final_dataset['name']):
    Name = author
    Titles = set()
    Venues = set()
    Organizations = set()
    Coauthors = set()
    Number_Coauthors = -1 #not including author
    DOIs = set()
    if author in author_expertise_dict:
        Topics = author_expertise_dict[author]
    else:
        Topics = 'NA'   
    if author in author_paperscnt_dict:
        Paper_number = author_paperscnt_dict[author]
    else:
        Paper_number = 'NA'    
    Abstracts = set()
    for row in range(len(final_dataset)):
        if author == final_dataset.iloc[row]['name']:
            Titles.add(final_dataset.iloc[row]['title'])
            Venues.add(final_dataset.iloc[row]['jconf'])
            Organizations.add(final_dataset.iloc[row]['organization'])
            coauthor_list = final_dataset.iloc[row]['coauthors'].split(' ')
            for coauthor in coauthor_list:
                Coauthors.add(coauthor)
            DOIs.add(final_dataset.iloc[row]['DOI'])
    Number_Coauthors += len(Coauthors)
    dataset_list.append([Name,Titles,Paper_number,Venues,Organizations,Coauthors,Number_Coauthors,DOIs,Topics])

All_authors_tpc_modelled = pd.DataFrame(dataset_list, columns = ['Name', 'Titles','No. Papers', 'Venues','Organizations', 'Coauthors',"No. Coauthors", "DOIs","Topics"])
All_authors_tpc_modelled.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/final_dataset_TPC_Modelled_Summary.csv")
    

pickling_on = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle","wb")
pickle.dump(final_dataset, pickling_on)
pickling_on.close()

    
pickling_on = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset_author.pickle","wb")
pickle.dump(All_authors_tpc_modelled, pickling_on)
pickling_on.close()       

#Creating excel for primary authors only:
#Creating a CSV file for capturing each researchers data:
primary_dataset_list = []
for author in set(final_dataset['name']):
    if author in primary_authors_set:
        Name = author
        Titles = set()
        Venues = set()
        Organizations = set()
        Coauthors = set()
        Number_Coauthors = -1 #not including author
        DOIs = set()        
        if author in author_expertise_dict:
            Topics = author_expertise_dict[author]
        else:
            Topics = 'NA'
        if author in author_paperscnt_dict:
            Paper_number = author_paperscnt_dict[author]
        else:
            Paper_number = 'NA'
        Abstracts = set()
        for row in range(len(final_dataset)):
            if author == final_dataset.iloc[row]['name']:
                Titles.add(final_dataset.iloc[row]['title'])
                Venues.add(final_dataset.iloc[row]['jconf'])
                Organizations.add(final_dataset.iloc[row]['organization'])
                coauthor_list = final_dataset.iloc[row]['coauthors'].split(' ')
                for coauthor in coauthor_list:
                    Coauthors.add(coauthor)
                DOIs.add(final_dataset.iloc[row]['DOI'])
        Number_Coauthors += len(Coauthors)
        primary_dataset_list.append([Name,Titles,Paper_number,Venues,Organizations,Coauthors,Number_Coauthors,DOIs,Topics])

Primary_tpc_modelled = pd.DataFrame(primary_dataset_list, columns = ['Name', 'Titles','No. Papers', 'Venues','Organizations', 'Coauthors',"No. Coauthors", "DOIs","Topics"])
Primary_tpc_modelled.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/Primary_Author_TOPIC_Summary.csv")
    




                                                                    
        


    
