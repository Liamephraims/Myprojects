#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 16:20:33 2020
Title: Heterograph Link Prediction Version 1.
@author: Liam Ephraims
"""

from stellargraph import StellarGraph
import pickle
import networkx as nx
import pandas as pd 
from jieba import analyse
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
#%matplotlib inline
#import matplotlib.pyplot as plt


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

#PICKLE THE OTHER DATASET BELOW INSTEAD:
unique_authors = set(Author_dataset.name)


#Extracting source-target edges for homogenous dataframes representations of PAPER-relation network:
#edge_set_YEAR = set()
#edge_set_COUNTRY = set()
edge_weight_dict = dict()
nodes_edge_list_of_lists = []
edge_set_author_P_ORG = set()
edge_set_author_P_author = set()
edge_set_author_P_venue = set()
edge_set_author_P_topic = set()
#edge_set_author_T_author = set()
edge_set_org_A_org = set()
edge_set_venue_A_venue = set()
author_expertise_dict = {}
org_author_dict = {}
venue_author_dict = {}
venue_title_dict = {}
org_title_dict = {}
topic_author_dict = dict()
topic_title_dict = dict()


for index in range(len(Author_dataset)):
    #ADDING IN YEAR FOR TRAIN/TEST/DEV SPLITS IN LINK PRED as temporal dataset:
    print("Beginning AUTHOR -> PAPER -> AUTHOR -relation extraction - {} of {}".format(index, len(Author_dataset)))
    author1 = Author_dataset["name"][index]
    author1_topic = Author_dataset["TOPICS"][index]
    
    #Building author expertise dictionary for later extraction of Author <-> TOPIC <-> Author edges:
   # if author1 in author_expertise_dict:
   #     for topic, prop in author1_topic:
   #         if prop >20:
   #             if topic in author_expertise_dict[author1]:
   #                 author_expertise_dict[author1][topic] += round(prop/100,2)
   #             elif topic not in author_expertise_dict[author1]:
   #                 author_expertise_dict[author1][topic] = round(prop/100,2)
   # elif author1 not in author_expertise_dict:
   #     for topic, prop in author1_topic:
   #         if prop >20:
   #             author_expertise_dict[author1] = dict()
   #             author_expertise_dict[author1][topic] = round(prop/100,2)
                        
                
    
    #Extracting author <(P)> author CO-AUTHOR edges:
    coauthor_list = Author_dataset["coauthors"][index].split(" ")
    for coauthor in coauthor_list:
        if not coauthor == author1:
            if (not tuple((author1,coauthor)) in edge_set_author_P_author) and (not tuple((coauthor,author1)) in edge_set_author_P_author): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                edge_set_author_P_author.add(tuple((author1,coauthor)))
            if not (tuple((author1,coauthor)) in edge_weight_dict) and (not tuple((coauthor,author1)) in edge_weight_dict):
                edge_weight_dict[tuple((author1,coauthor))] = {"AUTHOR-(P)-AUTHOR": 1}      
            elif tuple((author1,coauthor)) in edge_weight_dict:
                if "AUTHOR-(P)-AUTHOR" in edge_weight_dict[tuple((author1,coauthor))]:
                    edge_weight_dict[tuple((author1,coauthor))]["AUTHOR-(P)-AUTHOR"] += 1
                else:
                    edge_weight_dict[tuple((author1,coauthor))]["AUTHOR-(P)-AUTHOR"] = 1 
            elif tuple((coauthor,author1)) in edge_weight_dict:
                if "AUTHOR-(P)-AUTHOR" in edge_weight_dict[tuple((coauthor,author1))]:
                    edge_weight_dict[tuple((coauthor,author1))]["AUTHOR-(P)-AUTHOR"] += 1
                else:
                    edge_weight_dict[tuple((coauthor,author1))]["AUTHOR-(P)-AUTHOR"] = 1 
            else:
                print("None (else) condition entered for coauthor-papers!")
        else:
            print("Skipping edge: Coauthor == Author")
      
    #Extracting AUTHOR <-> (PAPER) <-> ORGANISATION edges:   Belongs:  note: CO-ORG = AUTHOR <-> ORG <-> AUTHOR
    org = Author_dataset["organization"][index]
    if org != "NA":
        if (not tuple((author1,org)) in edge_set_author_P_ORG): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
            edge_set_author_P_ORG.add(tuple((author1,org)))
        if not (tuple((author1,org)) in edge_weight_dict):
            edge_weight_dict[tuple((author1,org))] = {"AUTHOR-(P)-ORG": 1}                    
        elif tuple((author1,org)) in edge_weight_dict:
            if "AUTHOR-(P)-ORG" in edge_weight_dict[tuple((author1,org))]:
                edge_weight_dict[tuple((author1,org))]["AUTHOR-(P)-ORG"] += 1
            else:
                edge_weight_dict[tuple((author1,org))]["AUTHOR-(P)-ORG"] = 1
        else:
            print("None (else) condition entered for AUTHOR-(P)-ORG!") 

        #Building author organisation dictionary for later extraction of ORG <-> AUTHOR <-> ORG edges:
        if org != "NA":
            if org in org_author_dict:
                if author1 in org_author_dict[org]:
                    org_author_dict[org][author1] += 1
                elif author1 not in org_author_dict[org]:
                    org_author_dict[org][author1] = 1
            elif not org in org_author_dict:
                org_author_dict[org] = dict()
                org_author_dict[org][author1] = 1
                    
    #Extracting AUTHOR <-> (PAPER) <-> VENUE edges:   Belongs:  note: CO-VENUE = AUTHOR <-> VENUE <-> AUTHOR
    venue = Author_dataset["jconf"][index]
    if venue != "NA":
        if (not tuple((author1,venue)) in edge_set_author_P_venue): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
            edge_set_author_P_venue.add(tuple((author1,venue)))
        if not (tuple((author1,venue)) in edge_weight_dict):
            edge_weight_dict[tuple((author1,venue))] = {"AUTHOR-(P)-VENUE": 1}   
        elif tuple((author1,venue)) in edge_weight_dict:  
            if "AUTHOR-(P)-VENUE" in edge_weight_dict[tuple((author1,venue))]:
                edge_weight_dict[tuple((author1,venue))]["AUTHOR-(P)-VENUE"] += 1
            else:
                edge_weight_dict[tuple((author1,venue))]["AUTHOR-(P)-VENUE"] = 1
        else:
            print("None (else) condition entered for AUTHOR-(P)-VENUE!")

        
        #Building author-venue dictionary for later extraction of VENUE <-> AUTHOR <-> VENUE (co-publishers) edges:
        if venue != "NA":
            if venue in venue_author_dict:
                if author1 in venue_author_dict[venue]:
                    venue_author_dict[venue][author1] += 1
                elif author1 not in venue_author_dict[venue]:
                    venue_author_dict[venue][author1] = 1
            elif not venue in venue_author_dict:
                venue_author_dict[venue] = dict()
                venue_author_dict[venue][author1] = 1
            
    #Extracting AUTHOR <- (PAPER) -> TOPIC edges:
    topic_list = Author_dataset["TOPICS"][index]
    if topic_list != []:
        for topic, prop in topic_list:
            topic = "T{}".format(topic)
            if prop > 0.20:
                if (not tuple((author1,topic)) in edge_set_author_P_topic): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_author_P_topic.add(tuple((author1,topic)))
                if not (tuple((author1,topic)) in edge_weight_dict):
                    edge_weight_dict[tuple((author1,topic))] = {"AUTHOR-(P)-TOPIC": round(prop,2)}   
                elif tuple((author1,topic)) in edge_weight_dict:  
                    if "AUTHOR-(P)-TOPIC" in edge_weight_dict[tuple((author1,topic))]:
                        edge_weight_dict[tuple((author1,topic))]["AUTHOR-(P)-TOPIC"] += round(prop,2)
                    else:
                        edge_weight_dict[tuple((author1,topic))]["AUTHOR-(P)-TOPIC"] = round(prop,2)
                else:
                    print("None (else) condition entered for AUTHOR-(P)-TOPIC!")
                    
        #Building author-topic dictionary for later extraction of TOPIC <-> AUTHOR <-> TOPIC (co-publishers) edges:
        if topic_list != []:
            for topic, prop in topic_list:
                if prop >0.20:
                    topic = "T{}".format(topic)
                    if topic in topic_author_dict:
                       if author1 in topic_author_dict[topic]:
                           topic_author_dict[topic][author1] += round(prop,2)
                       elif author1 not in topic_author_dict[topic]:
                           topic_author_dict[topic][author1] = round(prop,2)
                    elif not topic in topic_author_dict:
                        topic_author_dict[topic] = dict()
                        topic_author_dict[topic][author1] = round(prop,2)
                 
                    
                 
#FIX REMOVE FROM ITERATION - MAKE SEPERATE!
#FIX: !!MAJOR ERROR IN THIS AS GOES EVER PAPERS MORE THAN ONCE DEPENDING ON CO-AUTHORS!!!!!
#SOLVED: THE REASON IS ITS USING AUTHOR as a relation not paper, so each author is being 
#considered. Problematic as means weighting is more dependant on co-author amount, rather then papers.

#PAPER ONLY EDGES:
Paper_dataset = Author_dataset.iloc[:,1:]
Paper_dataset.drop_duplicates(subset=["title"])
for index in range(len(Paper_dataset)):

   #Extracting seperate topic, organisation and venue title dictionaries for TOPIC <P> ORG, TOPIC <P> VENUE and  VENUE <-> PAPER <-> ORGANISATION (co-publishers) edges:
    title = Author_dataset["title"][index]
    venue = Author_dataset["jconf"][index]
    org = Author_dataset["organization"][index]
    topic_list = Author_dataset["TOPICS"][index]
    if title != "NA" and venue != "NA":
        if venue in venue_title_dict:
            if title in venue_title_dict[venue]:
                venue_title_dict[venue][title] += 1
            elif title not in venue_title_dict[venue]:
                venue_title_dict[venue][title] = 1
        elif not venue in venue_title_dict:
            venue_title_dict[venue] = dict()
            venue_title_dict[venue][title] = 1   
    if title != "NA" and org != "NA":
        if org in org_title_dict:
            if title in org_title_dict[org]:
                org_title_dict[org][title] += 1
            elif title not in org_title_dict[org]:
                org_title_dict[org][title] = 1
        elif not org in org_title_dict:
            org_title_dict[org] = dict()
            org_title_dict[org][title] = 1  
    if topic_list != [] and title != "NA":
        for topic, prop in topic_list:
            topic = "T{}".format(topic)
            if topic in topic_title_dict:
                if title in topic_title_dict[topic]:
                    topic_title_dict[topic][title] += round(prop,2)
                elif title not in topic_title_dict[topic]:
                    topic_title_dict[topic][title] = round(prop,2)
            elif not topic in topic_title_dict:
                topic_title_dict[topic] = dict()
                topic_title_dict[topic][title] = round(prop,2)
                
            
        
        #FIXED TO PAPERS INSTEAD OF AUTHOR
#ORG <-> (PAPER) <-> VENUE Relation:  
edge_set_org_P_venue = set()
for org in org_title_dict:
    for venue in venue_title_dict:
        if (org != "NA") and (venue != "NA") and (not tuple((org,venue)) in edge_set_org_P_venue) and (not tuple((venue, org)) in edge_set_org_P_venue) and (not venue == "NA") and (not org == "NA"):
            paper_intersection = set(org_title_dict[org].keys()).intersection(set(venue_title_dict[venue].keys()))
            ven_org_edge_weight = len(paper_intersection) 
            if ven_org_edge_weight != 0:
                if (not tuple((org,venue)) in edge_set_org_P_venue) and (not tuple((venue, org)) in edge_set_org_P_venue): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_org_P_venue.add(tuple((org,venue)))
                if not (tuple((org,venue)) in edge_weight_dict) and (not tuple((venue, org)) in edge_weight_dict):
                    edge_weight_dict[tuple((org,venue))] = {"ORG-(P)-VENUE": ven_org_edge_weight}                    
                elif tuple((org,venue)) in edge_weight_dict:
                    if "ORG-(P)-VENUE" in edge_weight_dict[tuple((org,venue))]:
                        edge_weight_dict[tuple((org,venue))]["ORG-(P)-VENUE"] += ven_org_edge_weight
                    else:
                        edge_weight_dict[tuple((org,venue))]["ORG-(P)-VENUE"] = ven_org_edge_weight
                elif tuple((venue,org)) in edge_weight_dict:
                    if "ORG-(P)-VENUE" in edge_weight_dict[tuple((venue,org))]:
                        edge_weight_dict[tuple((venue,org))]["ORG-(P)-VENUE"] += ven_org_edge_weight
                    else:
                        edge_weight_dict[tuple((venue,org))]["ORG-(P)-VENUE"] = ven_org_edge_weight
                else:
                    print("None (else) condition entered for ORG-(P)-VENUE edge!")          
#TOPIC <- (P) -> ORG
edge_set_org_P_topic = set()
for org in org_title_dict:
    for topic in topic_title_dict:
        if (org != "NA") and (topic != "NA") and (not tuple((org,topic)) in edge_set_org_P_topic) and (not tuple((topic, org)) in edge_set_org_P_topic) and (not topic == "NA") and (not org == "NA"):
            paper_intersection = set(org_title_dict[org].keys()).intersection(set(topic_title_dict[topic].keys()))
            topic_org_edge_weight = len(paper_intersection) 
            if topic_org_edge_weight != 0:
                if (not tuple((org,topic)) in edge_set_org_P_topic) and (not tuple((topic, org)) in edge_set_org_P_topic): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_org_P_topic.add(tuple((org,topic)))
                if not (tuple((org,topic)) in edge_weight_dict) and (not tuple((topic, org)) in edge_weight_dict):
                    edge_weight_dict[tuple((org,topic))] = {"ORG-(P)-TOPIC": topic_org_edge_weight}                    
                elif tuple((org,topic)) in edge_weight_dict:
                    if "ORG-(P)-TOPIC" in edge_weight_dict[tuple((org,topic))]:
                        edge_weight_dict[tuple((org,topic))]["ORG-(P)-TOPIC"] += topic_org_edge_weight
                    else:
                        edge_weight_dict[tuple((org,topic))]["ORG-(P)-TOPIC"] = topic_org_edge_weight
                elif tuple((topic,org)) in edge_weight_dict:
                    if "ORG-(P)-TOPIC" in edge_weight_dict[tuple((topic,org))]:
                        edge_weight_dict[tuple((topic,org))]["ORG-(P)-TOPIC"] += topic_org_edge_weight
                    else:
                        edge_weight_dict[tuple((topic,org))]["ORG-(P)-TOPIC"] = topic_org_edge_weight
                else:
                    print("None (else) condition entered for ORG-(P)-TOPIC edge!")    

#TOPIC <- (PAPER) - > VENUE     

edge_set_topic_P_venue = set()
for topic in topic_title_dict:
    for venue in venue_title_dict:
        print(venue)
        print(topic)
        if (topic != "NA") and (venue != "NA") and (not tuple((topic,venue)) in edge_set_topic_P_venue) and (not tuple((venue, topic)) in edge_set_topic_P_venue) and (not venue == "NA") and (not topic == "NA"):
            paper_intersection = set(topic_title_dict[topic].keys()).intersection(set(venue_title_dict[venue].keys()))
            ven_topic_edge_weight = len(paper_intersection) 
            if ven_topic_edge_weight != 0:
                if (not tuple((topic,venue)) in edge_set_topic_P_venue) and (not tuple((venue, topic)) in edge_set_topic_P_venue): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_topic_P_venue.add(tuple((topic,venue)))
                if not (tuple((topic,venue)) in edge_weight_dict) and (not tuple((venue, topic)) in edge_weight_dict):
                    edge_weight_dict[tuple((topic,venue))] = {"TOPIC-(P)-VENUE": ven_topic_edge_weight}                    
                elif tuple((topic,venue)) in edge_weight_dict:
                    if "TOPIC-(P)-VENUE" in edge_weight_dict[tuple((topic,venue))]:
                        edge_weight_dict[tuple((topic,venue))]["TOPIC-(P)-VENUE"] += ven_topic_edge_weight
                    else:
                        edge_weight_dict[tuple((topic,venue))]["TOPIC-(P)-VENUE"] = ven_topic_edge_weight
                elif tuple((venue,topic)) in edge_weight_dict:
                    if "TOPIC-(P)-VENUE" in edge_weight_dict[tuple((venue,topic))]:
                        edge_weight_dict[tuple((venue,topic))]["TOPIC-(P)-VENUE"] += ven_topic_edge_weight
                    else:
                        edge_weight_dict[tuple((venue,topic))]["TOPIC-(P)-VENUE"] = ven_topic_edge_weight
                else:
                    print("None (else) condition entered for TOPIC-(P)-VENUE edge!") 
        
     
                                   
#ORG <-> (AUTHOR) <-> ORG Relation:  CO-STAFF-ORG:     
for org1 in org_author_dict:
    for org2 in org_author_dict:
        if (org1 != "NA") and (org2 != "NA") and (org1 != org2) and (not tuple((org1,org2)) in edge_set_org_A_org) and (not tuple((org2,org1)) in edge_set_org_A_org):
            author_intersection = set(org_author_dict[org1].keys()).intersection(set(org_author_dict[org2].keys()))
            org_edge_weight = len(author_intersection) 
            if org_edge_weight != 0:
                if (not tuple((org1,org2)) in edge_set_org_A_org) and (not tuple((org2,org1)) in edge_set_org_A_org): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_org_A_org.add(tuple((org1,org2)))
                if not (tuple((org1,org2)) in edge_weight_dict) and (not tuple((org2,org1)) in edge_weight_dict):
                    edge_weight_dict[tuple((org1,org2))] = {"ORG-(A)-ORG": org_edge_weight}                    
                elif tuple((org1,org2)) in edge_weight_dict:
                    if "ORG-(A)-ORG" in edge_weight_dict[tuple((org1,org2))]:
                        edge_weight_dict[tuple((org1,org2))]["ORG-(A)-ORG"] += org_edge_weight
                    else:
                        edge_weight_dict[tuple((org1,org2))]["ORG-(A)-ORG"] = org_edge_weight
                elif tuple((org2,org1)) in edge_weight_dict:
                    if "ORG-(A)-ORG" in edge_weight_dict[tuple((org2,org1))]:
                        edge_weight_dict[tuple((org2,org1))]["ORG-(A)-ORG"] += org_edge_weight
                    else:
                        edge_weight_dict[tuple((org2,org1))]["ORG-(A)-ORG"] = org_edge_weight
                else:
                    print("None (else) condition entered for ORG-A_ORG edge!")  

#VENUE <-> (AUTHOR) <-> VENUE Relation:  CO-PUB VENUE:            
for venue1 in venue_author_dict:
    for venue2 in venue_author_dict:
        if (venue1 != "NA") and (venue2 != "NA") and (venue1 != venue2) and (not tuple((venue1,venue2)) in edge_set_venue_A_venue) and (not tuple((venue2,venue1)) in edge_set_venue_A_venue):
            author_intersection = set(venue_author_dict[venue1].keys()).intersection(set(venue_author_dict[venue2].keys()))
            venue_edge_weight = len(author_intersection)          
            if venue_edge_weight != 0:
                if (not tuple((venue1,venue2)) in edge_set_venue_A_venue) and (not tuple((venue2,venue1)) in edge_set_venue_A_venue): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_venue_A_venue.add(tuple((venue1,venue2)))
                if not (tuple((venue1,venue2)) in edge_weight_dict) and (not tuple((venue2,venue1)) in edge_weight_dict):
                    edge_weight_dict[tuple((venue1,venue2))] = {"VENUE-(A)-VENUE": venue_edge_weight}                    
                elif tuple((venue1,venue2)) in edge_weight_dict:
                    if "VENUE-(A)-VENUE" in edge_weight_dict[tuple((venue1,venue2))]:
                        edge_weight_dict[tuple((venue1,venue2))]["VENUE-(A)-VENUE"] += venue_edge_weight
                    else:
                        edge_weight_dict[tuple((venue1,venue2))]["VENUE-(A)-VENUE"] = venue_edge_weight
                elif tuple((venue2,venue1)) in edge_weight_dict:
                    if "VENUE-(A)-VENUE" in edge_weight_dict[tuple((venue2,venue1))]:
                        edge_weight_dict[tuple((venue2,venue1))]["VENUE-(A)-VENUE"] += venue_edge_weight
                    else:
                        edge_weight_dict[tuple((venue2,venue1))]["VENUE-(A)-VENUE"] = venue_edge_weight
                else:
                    print("None (else) condition entered for VENUE-A_VENUE edge!")  
                    
edge_set_topic_A_topic = set()                
#TOPIC <-> (AUTHOR) <-> TOPIC Relation:  CO-PUB TOPIC:            
for topic1 in topic_author_dict:
    for topic2 in topic_author_dict:
        if (topic1 != "NA") and (topic2 != "NA") and (topic1 != topic2) and (not tuple((topic1,topic2)) in edge_set_topic_A_topic) and (not tuple((topic2,topic1)) in edge_set_topic_A_topic):
            author_intersection = set(topic_author_dict[topic1].keys()).intersection(set(topic_author_dict[topic2].keys()))
            topic_edge_weight = len(author_intersection)          
            if topic_edge_weight != 0:
                if (not tuple((topic1,topic2)) in edge_set_topic_A_topic) and (not tuple((topic2,topic1)) in edge_set_topic_A_topic): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_topic_A_topic.add(tuple((topic1,topic2)))
                if not (tuple((topic1,topic2)) in edge_weight_dict) and (not tuple((topic2,topic1)) in edge_weight_dict):
                    edge_weight_dict[tuple((topic1,topic2))] = {"TOPIC-(A)-TOPIC": topic_edge_weight}                    
                elif tuple((topic1,topic2)) in edge_weight_dict:
                    if "TOPIC-(A)-TOPIC" in edge_weight_dict[tuple((topic1,topic2))]:
                        edge_weight_dict[tuple((topic1,topic2))]["TOPIC-(A)-TOPIC"] += topic_edge_weight
                    else:
                        edge_weight_dict[tuple((topic1,topic2))]["TOPIC-(A)-TOPIC"] = topic_edge_weight
                elif tuple((topic2,topic1)) in edge_weight_dict:
                    if "TOPIC-(A)-TOPIC" in edge_weight_dict[tuple((topic2,topic1))]:
                        edge_weight_dict[tuple((topic2,topic1))]["TOPIC-(A)-TOPIC"] += topic_edge_weight
                    else:
                        edge_weight_dict[tuple((topic2,topic1))]["TOPIC-(A)-TOPIC"] = topic_edge_weight
                else:
                    print("None (else) condition entered for TOPIC-(A)-TOPIC edge!")  

#TOPIC AS A NODE - TOPIC RELATIONSHIPS NO LONGER REQUIRED IN THIS FORMAT!:
    
#AUTHOR <-> TOPIC <-> AUTHOR CO-EXPERTISE Edges:
#edge_set_author_T_author = set()
#for author1 in author_expertise_dict:
#    for author2 in author_expertise_dict:
#        if (author1 != "NA") and (author2 != "NA") and (not author1 == author2) and (not tuple((author1,author2)) in edge_set_author_T_author) and (not tuple((author2,author1)) in edge_set_author_T_author):
#            topic_intersection = set(author_expertise_dict[author1].keys()).intersection(set(author_expertise_dict[author2].keys()))
#            total_prop_intersection_weight = 0
#            for topic in topic_intersection:
#                author1_top_prop = author_expertise_dict[author1][topic]
#                author2_top_prop = author_expertise_dict[author2][topic]
#                total_prop_intersection_weight += min([author1_top_prop,author2_top_prop])
##            if total_prop_intersection_weight != 0:
#                if (not tuple((author1,author2)) in edge_set_author_T_author) and (not tuple((author2,author1)) in edge_set_author_T_author): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
#                    edge_set_author_T_author.add(tuple((author1,author2)))
#                if not (tuple((author1,author2)) in edge_weight_dict) and (not tuple((author2,author1)) in edge_weight_dict):
#                    edge_weight_dict[tuple((author1,author2))] = {"AUTHOR-(T)-AUTHOR": total_prop_intersection_weight}                    
#                elif tuple((author1,author2)) in edge_weight_dict:
#                    if "AUTHOR-(T)-AUTHOR" in edge_weight_dict[tuple((author1,author2))]:
#                        edge_weight_dict[tuple((author1,author2))]["AUTHOR-(T)-AUTHOR"] += total_prop_intersection_weight
#                    else:
#                        edge_weight_dict[tuple((author1,author2))]["AUTHOR-(T)-AUTHOR"] = total_prop_intersection_weight
#                elif tuple((author2,author1)) in edge_weight_dict:
##                    if "AUTHOR-(T)-AUTHOR" in edge_weight_dict[tuple((author2,author1))]:
 #                       edge_weight_dict[tuple((author2,author1))]["AUTHOR-(T)-AUTHOR"] += total_prop_intersection_weight
 #                   else:
 #                       edge_weight_dict[tuple((author2,author1))]["AUTHOR-(T)-AUTHOR"] = total_prop_intersection_weight
 #               else:
 #                   print("None (else) condition entered for AUTHOR-T-AUTHOR edge!")

#VENUE <-> TOPIC <-> VENUE (co-topic)
venue_topic_dict = {}
venue_set = set(Author_dataset["jconf"])
cnt = 1
for venue in venue_set:
    if venue != "NA" and venue != " ":
        venue_topic_dict[venue] = dict()
        print("Beginning {} of {} unique venues in building venue-topic dictionary:".format(cnt,len(venue_set)))
        venue_topics = set()
        for index in range(len(Author_dataset)):
            topic_list = Author_dataset.iloc[index]["TOPICS"]
            author_venue = Author_dataset.iloc[index]["jconf"]
            if venue == author_venue:
                #add topics if proportion for topic is higher than 20%:
                for topic, prop in topic_list:
                    if prop > 0.20:
                        if topic in venue_topic_dict[venue]:
                            venue_topic_dict[venue][topic] += round(prop,2)
                        elif not topic in venue_topic_dict[venue]:
                            venue_topic_dict[venue][topic] = round(prop,2)
                        else:
                            print("FAILED DICT INCREMENT OF TOPIC",topic,"FOR VENUE",venue)
    cnt += 1
edge_set_venue_T_venue = set()
for venue1 in venue_topic_dict:
    for venue2 in venue_topic_dict:
        if (venue1 != "NA") and (venue2 != "NA") and (venue1 != venue2) and (not tuple((venue1,venue2)) in edge_set_venue_T_venue):
            topic_intersection = set(venue_topic_dict[venue1].keys()).intersection(set(venue_topic_dict[venue2].keys()))
            total_prop_intersection_weight = 0
            for topic in topic_intersection:
               venue1_top_prop = venue_topic_dict[venue1][topic]
               venue2_top_prop = venue_topic_dict[venue2][topic]
               total_prop_intersection_weight += min([venue1_top_prop,venue2_top_prop])
            if total_prop_intersection_weight != 0:
                if (not tuple((venue1,venue2)) in edge_set_venue_T_venue) and (not tuple((venue2,venue1)) in edge_set_venue_T_venue): #As graph is multi-graph and undirected so only need to represent edge between two - this would be a duplicate edge otherwise.
                    edge_set_venue_T_venue.add(tuple((venue1,venue2)))
                if not (tuple((venue1,venue2)) in edge_weight_dict) and (not tuple((venue2,venue1)) in edge_weight_dict):
                    edge_weight_dict[tuple((venue1,venue2))] = {"VENUE-(T)-VENUE": total_prop_intersection_weight}                    
                elif tuple((venue1,venue2)) in edge_weight_dict:
                    if "VENUE-(T)-VENUE" in edge_weight_dict[tuple((venue1,venue2))]:
                        edge_weight_dict[tuple((venue1,venue2))]["VENUE-(T)-VENUE"] += total_prop_intersection_weight
                    else:
                        edge_weight_dict[tuple((venue1,venue2))]["VENUE-(T)-VENUE"] = total_prop_intersection_weight
                elif tuple((venue2,venue1)) in edge_weight_dict:
                    if "VENUE-(T)-VENUE" in edge_weight_dict[tuple((venue2,venue1))]:
                        edge_weight_dict[tuple((venue2,venue1))]["VENUE-(T)-VENUE"] += total_prop_intersection_weight
                    else:
                        edge_weight_dict[tuple((venue2,venue1))]["VENUE-(T)-VENUE"] = total_prop_intersection_weight
                else:
                   print("None (else) condition entered for VENUE-T-VENUE edge!") 

edge_type = "VENUE-(T)-VENUE"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_venue_T_venue if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 
edge_type = "TOPIC-(A)-TOPIC"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_topic_A_topic if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 

edge_type = "VENUE-(A)-VENUE"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_venue_A_venue if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 


edge_type = "ORG-(A)-ORG"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_org_A_org if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row)  

edge_type = "ORG-(P)-VENUE"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_org_P_venue if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row)                         
 

edge_type = "TOPIC-(P)-VENUE"           
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_topic_P_venue if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row)                         

#THIS ONE!! org-topic
edge_type = "ORG-(P)-TOPIC"               
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_org_P_topic if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row)                         

edge_type = "AUTHOR-(P)-AUTHOR"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_author_P_author if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row)     
    
edge_type = "AUTHOR-(P)-VENUE"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_author_P_venue if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 
    
edge_type = "AUTHOR-(P)-ORG"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_author_P_ORG if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 
    
    
edge_type = "AUTHOR-(P)-TOPIC"                
for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_author_P_topic if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
    print(row)   
    nodes_edge_list_of_lists.append(row) 
               
##edge_type = "AUTHOR-(T)-AUTHOR"                
#for row in [[source,target,edge_type,edge_weight_dict[tuple((source,target))][edge_type]] for source, target in edge_set_author_T_author if tuple((source, target)) in edge_weight_dict and edge_type in edge_weight_dict[tuple((source,target))]]:
#    print(row)   
#    nodes_edge_list_of_lists.append(row) 


#Converting and pickling dataset into a dataframe containing each relation, edge set and weight instance between the networks.
nodes_edges_df = pd.DataFrame(nodes_edge_list_of_lists, columns = ["source", "target", "relation","weight"])      

set(nodes_edges_df.relation)
pickling_on = open("Hetergenous_dataset_final.pickle","wb")
pickle.dump(nodes_edges_df, pickling_on)
pickling_on.close()  
