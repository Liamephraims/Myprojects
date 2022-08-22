# -*- coding: utf-8 -*-
"""
ASSIGNMENT OF TOPIC LABELS TO MODELLED TOPICS:
    
Instructions:
    
1. To begin the assignment of topic labels, within the 2-Assignment of Topic Labels using Modelled Topics
   folder from 4-Topic Representation, open the html trained_LDA_topics file for a vizualisation
   of the trained research topic distributions for your research organisation.
   
   Using this vizualisation, run this python script and enter a topic label when requested for each topic where you are sure of the expertise label
   as inferred from the word distribution of the topic. 
   
   

"""
import pickle
import networkx as nx
import pandas as pd 
from jieba import analyse
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:

file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle",'rb')
#Final_dataset = pickle.load(file)
unpickler = pickle.Unpickler(file)
Author_dataset = unpickler.load()

#Loading in cleaned and topic-modelled researcher dataset by researcher paper sets:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset_author.pickle",'rb')
#Final_dataset = pickle.load(file)
unpickler = pickle.Unpickler(file)
Author_dataset_RESEARCHER = unpickler.load()

#Collecting topics:
Topics = set()
for topic_list in Author_dataset['TOPICS'].values:
    for topic, prop in topic_list:
        Topics.add(topic)
Topics = list(Topics)

#Requesting user to add a new topic label for each topic where possible:
Inferred_topic_label_dict = dict()
print("Using the topic vizualization file add topic labels where confident in the topic expertise")
for topic in Topics:
    print("\n")
    print("Topic is", str(int(topic) + 1))
    topic_request = input("Would you like to add a topic label to this topic? [yes|no]:\n")
    if topic_request.lower() == "yes":
        topic_label = input("Insert new topic label for topic distribution:\n")
    else:
        topic_label = "T" + str(int(topic) + 1)
    print("Topic Label is", topic_label)
    Inferred_topic_label_dict["T"+str(topic + 1)] = topic_label

pickling_on = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/2-Assignment of Topic Labels using Modelled Topics/Inferred_topic_label_dict.pickle","wb")
pickle.dump(Inferred_topic_label_dict, pickling_on)
pickling_on.close()
        
        
        
        
        

