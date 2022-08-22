#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:40:30 2020

Preparation of .txt and .edge files for using Muxviz interactive-multi-level graph viz tool through RShiny.

@author: Liam Ephraims

"""
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from math import isclose
import os


#Getting primary author names:
primary_authors = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
primary_authors_set = set(primary_authors.Name)

#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/1-Preparing multitype nodes and edge dataset/Hetergenous_dataset_final.pickle",'rb')
unpickler = pickle.Unpickler(file)
Hetero_dataset = unpickler.load()
Hetero_dataset = Hetero_dataset.loc[Hetero_dataset.weight > 1]


#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/2-Assignment of Topic Labels using Modelled Topics/Inferred_topic_label_dict.pickle",'rb')
unpickler = pickle.Unpickler(file)
Inferred_topic_label_dict = unpickler.load()

#Hetero_dataset = Hetero_dataset.loc[(Hetero_dataset.relation != "ORG-(A)-ORG") & (Hetero_dataset.relation != "TOPIC-(A)-TOPIC")
#                                    & (Hetero_dataset.relation != "VENUE-(A)-VENUE")]
#{'AUTHOR-(P)-AUTHOR',
# 'AUTHOR-(P)-ORG',
# 'AUTHOR-(P)-TOPIC',
# 'AUTHOR-(P)-VENUE',
# 'ORG-(A)-ORG',
# 'ORG-(P)-TOPIC',
# 'ORG-(P)-VENUE',
# 'TOPIC-(A)-TOPIC',
## 'TOPIC-(P)-VENUE',
# 'VENUE-(A)-VENUE'}
 
 
#Loading in Link Prediction results for recommendations:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/2-Implementation of Metapath embedding and Link Prediction/Hetergenous_Recommendations.pickle",'rb')
unpickler = pickle.Unpickler(file)
Recommendations_dts = unpickler.load()

#1. Looking for recommendations where, co-authors had NOT previously collaborated (no AUTHOR<-PAPER->AUTHOR EDGE)
 #, both of these authors is a primary organisation author (or if not available secondly just one is primary author
 # and thirdly, the predicted label/probability for the label is 1 and preferably greater then 80% likelihood of
 #authors collaborating.


#2. NOTE: THIS IS ONLY A PRACTICE PIPELINE AS IT IS USING THE TEST DATA RESULTS, instead of results of developed model.
#Extracted time variable for papers published, can be used in future for train/test on years prior saving latest dataset year
#(current) for recommendations! - using dynamic rather than static graph.


#3.  + will need to do metapath embedding for dev_network_dataset.

#Removing recommendations where label predicted is negative (not recommended to collaborate):
Recommendations_dts = Recommendations_dts[Recommendations_dts.Predicted_Label == 1]

#Looking for any matching coauthor pair who have been recommended to collaborate in the development network dataset 
#and do not yet share a co-author edge (i.e. have no coauthored a paper together and therefore will not be in hetero-edge
#dataset).


#Building coauthor set for hetergenous dataset to check against for new collaboration pairs:
coauthor_set = set()
for source, target, relation, weight in Hetero_dataset[Hetero_dataset.relation == 'AUTHOR-(P)-AUTHOR'].values:
    if tuple((source, target)) not in coauthor_set:
        coauthor_set.add(tuple((source, target)))
print(len(coauthor_set), "unique coauthor pairs")
#note: will remove true label in final version as there will be no true label for current pub year only predicted labels.
raw_cnt = 0
prob_filtered_cnt = 0
primary_recommendations = 0
secondary_recommendations = 0

primary_secondary_recommendations_list = []
for pred_label, pred_prob, true_label, author1, author2 in Recommendations_dts.values:
    if (not tuple((author1,author2)) in coauthor_set) and (not tuple((author2,author1)) in coauthor_set):
        raw_cnt += 1
        #print(pred_prob)
        if pred_prob > 0:
            prob_filtered_cnt += 1
            if ((author1 in primary_authors_set) or (author2 in primary_authors_set)) and not ((author1 in primary_authors_set) and (author2 in primary_authors_set)):
                secondary_recommendations += 1
                primary_secondary_recommendations_list.append([pred_prob, author1, author2, "secondary"])
            elif (author1 in primary_authors_set) and (author2 in primary_authors_set):
                    primary_recommendations += 1
                    primary_secondary_recommendations_list.append([pred_prob, author1, author2, "primary"])

#NOTE: This is only an example! When have dev dataset and pub years, this will be using the current year so probabilite
#will be used as cut-off decision threshold. At the moment, these are likely the false positives with AUC of 95% 
#the 5%. Although using this to finish assembly of pipeline before returning to rerun and hopefully extract pub years
#to create train/val, test and deployment datasets.
print("There were", raw_cnt,"instances of two authors being recommended (predicted) to collaborate in this current year.")
print("\n")
print("Meanwhile, there were", prob_filtered_cnt,"instances of two authors being recommended (predicted) to \
      collaborate in this current year with a high predicted probability of greater than 80%")
print("\n")
print("Of this", prob_filtered_cnt, "there was", secondary_recommendations, "secondary recommendations (recommendations\
 between a primary author and a secondary author) and there was", primary_recommendations, "primary recommendations\
(recommendations between two primary authors)")


                                
#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle",'rb')
#Final_dataset = pickle.load(file)
unpickler = pickle.Unpickler(file)
Author_dataset = unpickler.load()
#Creating different node types:

#!!!!!!!!WITH NAS INCLUDED IN VIZUALIZATION!!!!!!
#org_nodes = pd.DataFrame(index=[org for org in set(Author_dataset["organization"]) if org != "NA"])   #removing venue node from org nodes (bug needs fixing)
org_nodes = pd.DataFrame(index=[org.replace(" ", "_") for org in set(Author_dataset["organization"]) if org != "palliative medicine"])

#author_nodes = [author for author in set(Author_dataset["name"]) if author != "NA"]
author_nodes = [author.replace(" ", "_") for author in set(Author_dataset["name"]) ]

author_nodes = set(author_nodes)
for coauthors in set(Author_dataset["coauthors"]):
    coauthors = coauthors.split(" ")
    for coauthor in coauthors:
        if not coauthor in author_nodes:
            author_nodes.add(coauthor)
author_nodes = pd.DataFrame(index=author_nodes)
#
#venue_nodes = pd.DataFrame(index=[jconf for jconf in set(Author_dataset["jconf"]) if jconf != "NA"])
venue_nodes = pd.DataFrame(index=[jconf.replace(" ", "_") for jconf in set(Author_dataset["jconf"]) if not jconf in org_nodes.index])

topic_set = set()
for topic_list in Author_dataset["TOPICS"]:
    for topic, prop in topic_list:
        topic_set.add("T{}".format(str(int(topic) + 1)))
topic_nodes =  pd.DataFrame(index=topic_set)


    

import os
directory = "C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/2-Heterogeneous-Multiplex Vizualizations MuxVix File Creation"
os.chdir(directory + "/muxViz_network_files")



relations = {"Topics","Organisations","Authors", "Venues(Journal/Conferences)"} 
 

layer_dict = dict()
cnt = 0
for relation in relations:
    cnt += 1
    layer_dict[relation] = cnt

with open("./muxViz-master/MultiGraph_Layers.txt", "w", encoding="utf-8") as file:
    file.write("layerID layerLabel\n")
    for layer in layer_dict.keys():
        row_str = "{} {}\n".format(layer_dict[layer], layer)
        print(row_str)
        file.write(row_str)
    file.close()
    

#layerID layerLabel
#1 L1
#2 L2
#3 L3
#4 L4
#5 L5
#6 L6



#CHANGE THIS!
#Extended edges list
#An extended edges list is a new format that allows to specify all possible types of links, 
#intra- and inter-layer. Each line specifies the source node (first column) and 
#the source layer (second column), the destination node (third column) and 
#the destination layer (fourth column), possibly weighted by an integer or floating number (fifth column).

#Creating node density dictionaries to calculate standardised degree for each node- default 0 (no edges):
author_density_dict = dict()
org_density_dict = dict()
venue_density_dict = dict()
topic_density_dict = dict()


#Automatic-cleaning list (rather than user-input for cleaning below shared orgs names)
Correct_primary_org_name = "University_of_New_South_Wales"
#Creating UNSW dictionary to clean UNSW organisation names on user-request:
UNSW_dict = {"cnr":"Consiglio_Nazionale_delle_Ricerche-NRC","ingham_inst_appl_med_res":"ingham_institute_for_applied_medical_research","harvard_med_sch":"harvard_univ","sydney_childrens_hosp_network":"sydney_childrens_hosp","liverpool_hlth_serv":"liverpool_hosp","univ_western_sydney":"western_sydney_univ","university_of_western_sydney_-_campbelltown_campus":"western_sydney_univ","unsw_sydney":Correct_primary_org_name,"unsw_australia":Correct_primary_org_name,"unsw":Correct_primary_org_name,
             "univ_new_south_wales":Correct_primary_org_name,"university_of_new_south_wales_(unsw)_australia":Correct_primary_org_name,
             "univ_new_s_wales":Correct_primary_org_name, "univ_nsw":Correct_primary_org_name, "univ new south wales sydney":Correct_primary_org_name}
user_clean = False
while user_clean == True:
    request = input("Do you want to clean and merge orgs to single name, type (yes/no)\n")
    if request.lower() == "yes":
        clean = input("Type incorrect org name instance to remove (include _ instead of spaces\n")
        merge = input("Type correct org name to merge incorrect name instance with (include _ instead of spaces\n")
        UNSW_dict[clean] = merge
    elif request.lower() == "no":
        user_clean = False
#Automatic-cleaning list (rather than user-input for cleaning below shared venue names)
#Creating Venue cleaning dictionary to clean venue names on user-request:
Venue_clean_dict = {"clinical_oncology":"journal_of_clinical_oncology",
                    "palliative_medicine":"journal_of_palliative_medicine",
                    "radiotherapy_and_oncology":"international_journal_of_radiation_oncology_biology_physics"}
user_clean = False
while user_clean == True:
    request = input("Do you want to clean and merge venues to single name, type (yes/no)\n")
    if request.lower() == "yes":
        clean = input("Type incorrect venue name instance to remove (include _ instead of spaces\n")
        merge = input("Type correct venue name to merge incorrect name instance with (include _ instead of spaces\n")
        Venue_clean_dict[clean] = merge
    elif request.lower() == "no":
        user_clean = False


        
        

for author in author_nodes.index:
    author_density_dict[author] = 0
for org in org_nodes.index:
    if not org in UNSW_dict:
        org_density_dict[org] = 0
    if org in UNSW_dict and not UNSW_dict[org] in org_density_dict:
        org_density_dict[UNSW_dict[org]] = 0
for venue in venue_nodes.index:
    if not venue in Venue_clean_dict:
        venue_density_dict[venue] = 0
    if venue in Venue_clean_dict and not Venue_clean_dict[venue] in venue_density_dict:
        venue_density_dict[Venue_clean_dict[venue]] = 0
for topic in topic_nodes.index:
    topic_density_dict[topic] = 0
for source, target, relation, weight in Hetero_dataset.values:
    if source.replace(" ", "_") in author_density_dict:
        author_density_dict[source.replace(" ", "_")] += 1
    elif source.replace(" ", "_") in org_density_dict or source.replace(" ", "_") in UNSW_dict:
        if source.replace(" ", "_") in org_density_dict :
            org_density_dict[source.replace(" ", "_")] += 1
        elif source.replace(" ", "_") in UNSW_dict:
            #manual fix for org <-> venue error:
            #if org_density_dict[UNSW_dict[source.replace(" ", "_")]] == "journal_of_palliative_medicine":
            #    continue
            #aggregating all UNSW org names to same org. 
            #manual fix for org <-> venue error:
            #elif not org_density_dict[UNSW_dict[source.replace(" ", "_")]] == "journal_of_palliative_medicine":
            org_density_dict[UNSW_dict[source.replace(" ", "_")]]+= 1
    elif source.replace(" ", "_") in venue_density_dict  or source.replace(" ", "_") in Venue_clean_dict:
        if source.replace(" ", "_") in venue_density_dict :
            venue_density_dict[source.replace(" ", "_")] += 1
        elif source.replace(" ", "_") in Venue_clean_dict:
            #aggregating all venue names to same correct venue name. 
             venue_density_dict[Venue_clean_dict[source.replace(" ", "_")]]+= 1   
    
    elif source.replace(" ", "_") in topic_density_dict:
        topic_density_dict[source.replace(" ", "_")] += 1
        
    if target.replace(" ", "_") in author_density_dict:
        author_density_dict[target.replace(" ", "_")] += 1
    elif target.replace(" ", "_") in org_density_dict or target.replace(" ", "_") in UNSW_dict:
        if target.replace(" ", "_") in org_density_dict :
            org_density_dict[target.replace(" ", "_")] += 1
        elif target.replace(" ", "_") in UNSW_dict:
            #aggregating all UNSW org names to same org. 
             org_density_dict[UNSW_dict[target.replace(" ", "_")]]+= 1
    elif target.replace(" ", "_") in venue_density_dict or target.replace(" ", "_") in Venue_clean_dict:
        if target.replace(" ", "_") in venue_density_dict :
            venue_density_dict[target.replace(" ", "_")] += 1
        elif target.replace(" ", "_") in Venue_clean_dict:
            #aggregating all venue names to same correct venue name. 
             venue_density_dict[Venue_clean_dict[target.replace(" ", "_")]]+= 1   
    elif target.replace(" ", "_") in topic_density_dict:
        topic_density_dict[target.replace(" ", "_")] += 1      
#manually correcting an error in orgs and venues - where pallative care journal is both a org and venue!
        
#Prior to normalizing node denstities, creating greatest infuencers/nodes table for Vizualisation section:
author_list = []
for author in author_density_dict:
    author_list.append([author, author_density_dict[author]])
#Creating author dataframe to sort authors by:
author_df = pd.DataFrame(author_list, columns = ["Researcher","Unnormalized Density"])      
author_df.sort_values(by=["Unnormalized Density"], ascending=False, inplace=True)
#Taking top-50 Venues and saving as csv file:
author_df = author_df[:50]
author_df.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/Top-50-Influential-Researchers.csv")


#Prior to normalizing node denstities, creating greatest infuencers/nodes table for Vizualisation section:
venue_list = []
for venue in venue_density_dict:
    venue_list.append([venue.replace("_", " "), venue_density_dict[venue]])
#Creating venue dataframe to sort venues by:
venue_df = pd.DataFrame(venue_list, columns = ["Venue","Unnormalized Density"])      
venue_df.sort_values(by=["Unnormalized Density"], ascending=False, inplace=True)    
#Taking top-50 Venues and saving as csv file:
venue_df = venue_df[:50]
venue_df.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/Top-50-Influential-Venues.csv")



#Prior to normalizing node denstities, creating greatest infuencers/nodes table for Vizualisation section:
topic_list = []
for topic in topic_density_dict:
    topic_list.append([Inferred_topic_label_dict[topic], topic_density_dict[topic]])
#Creating venue dataframe to sort venues by:
topic_df = pd.DataFrame(topic_list, columns = ["Topic","Unnormalized Density"])      
topic_df.sort_values(by=["Unnormalized Density"], ascending=False, inplace=True) 
#Taking Topics ordered by most influencial network topics and saving as csv file:
topic_df = topic_df[:len(topic_df)]
topic_df.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/Top-50-Influential-Topics.csv")



#Prior to normalizing node denstities, creating greatest infuencers/nodes table for Vizualisation section:
org_list = []
for org in org_density_dict:
    org_list.append([org.replace("_", " "), org_density_dict[org]])
#Creating org dataframe to sort orgs by:
org_df = pd.DataFrame(org_list, columns = ["Organisation","Unnormalized Density"])      
org_df.sort_values(by=["Unnormalized Density"], ascending=False, inplace=True)   
#Taking top-50 Organisations and saving as csv file:
org_df = org_df[:50]
org_df.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/Top-50-Influential-Organisations.csv")




        


author_node_length = len(author_nodes.index) 
org_node_length = len(org_nodes.index)
venue_node_length = len(venue_nodes.index)
topic_node_length = len(topic_nodes.index)
total_node_length = author_node_length+org_node_length+venue_node_length+topic_node_length
#Standardizing each node type degree, seperately by node type:
for author in author_density_dict:
    author_density_dict[author] = round(author_density_dict[author]/(total_node_length-1),4)
for org in org_density_dict:
    org_density_dict[org] = round(org_density_dict[org]/(total_node_length-1),4)
for venue in venue_density_dict:
    venue_density_dict[venue] = round(venue_density_dict[venue]/(total_node_length-1),4)
for topic in topic_density_dict:
    topic_density_dict[topic] = round(topic_density_dict[topic]/(total_node_length-1),4)

#Checking for best cut-off for showing non-primary author nodes in vizualisation:
#from matplotlib import pyplot as plt
plt.hist(author_density_dict.values()) #0.05 * 100
plt.hist(venue_density_dict.values()) #>  #0.01  *100
plt.hist(org_density_dict.values())  #> 0.005  *100
plt.hist(topic_density_dict.values())  #> 0.02  *100

import numpy as np

#Taking 30% percentile as threshold cut-off value:
venue_density_threshold = np.percentile(list(venue_density_dict.values()), 96)
org_density_threshold = np.percentile(list(org_density_dict.values()), 97)
author_density_threshold = np.percentile(list(author_density_dict.values()), 80)
topic_density_threshold = np.percentile(list(topic_density_dict.values()), 0)  #include all topic nodes.


#Checking threshold for keeping edges:
plt.hist(list(Hetero_dataset["weight"]))  #10
max_weight = max(list(Hetero_dataset["weight"]))
#Normalizing edge weights:
Hetero_dataset["weight"] = Hetero_dataset["weight"]/max_weight
edge_weight_threshold = np.percentile(list(Hetero_dataset["weight"]), 50)

Primary_venue_dict = dict()
Primary_org_dict = dict()
Primary_author_dict = dict()
Primary_topic_dict = dict()

Hetero_primary_flag_dts = []
for source, target, relation, weight in Hetero_dataset.values:
    primary_edge = False
    for org in org_nodes.index:
        if ((org == source.replace(" ", "_") or org == target.replace(" ", "_")) and
            ((source in primary_authors_set ) or (target in primary_authors_set))):
            if not org in UNSW_dict:
                Primary_org_dict[org] = True
                primary_edge = True
                #print("TRUE")
            elif org in UNSW_dict:
                Primary_org_dict[UNSW_dict[org]] = True
                primary_edge = True
    for venue in venue_nodes.index:
        if ((venue == source.replace(" ", "_") or venue == target.replace(" ", "_")) and
            ((source in primary_authors_set ) or (target in primary_authors_set))):
            if not venue in Venue_clean_dict:
                Primary_venue_dict[venue] = True
                primary_edge = True
                #print("TRUE")
            elif venue in Venue_clean_dict:
                Primary_venue_dict[Venue_clean_dict[venue]] = True
                primary_edge = True

    for topic in topic_nodes.index:
        if ((topic == source.replace(" ", "_") or topic == target.replace(" ", "_")) and
            ((source in primary_authors_set ) or (target in primary_authors_set))):
            Primary_topic_dict[topic] = True
            #print("TRUE")
            primary_edge = True

    for author in author_nodes.index:
        if ((author == source.replace(" ", "_") or author == target.replace(" ", "_")) and
            ((source in primary_authors_set ) or (target in primary_authors_set))):
            if author_density_dict[author] > 0: #NOTE: INCLUDING THIS TO REMOVE RECOMMENDED & VIZUALISED 0 edge (isolated nodes) which should not exist due to co-author relations, implying a bug.
                Primary_author_dict[author] = True
                #print("TRUE")
                primary_edge = True
    if primary_edge == True:
        Hetero_primary_flag_dts.append([source, target,relation, weight, True])
    elif primary_edge == False:  #Not a primary edge, however, checking if above threshold for non-primary nodes:
        #trying to capture relationships between organisations.
        if relation == 'ORG-(A)-ORG':
            if weight >= 0.03:
                Hetero_primary_flag_dts.append([source, target,relation, weight, False])
        elif weight >= 0.1:
            Hetero_primary_flag_dts.append([source, target,relation, weight, False])
#Not including non-primary edges or non-primary nodes.

for author in author_nodes.index:
    if author not in Primary_author_dict:
        Primary_author_dict[author] = False
for topic in topic_nodes.index:
    if topic not in Primary_topic_dict:
        Primary_topic_dict[topic] = False
for venue in venue_nodes.index:
    if not venue  in Primary_venue_dict and not venue in Venue_clean_dict:
        Primary_venue_dict[venue] = False     
    elif venue in Venue_clean_dict:
        if not Venue_clean_dict[venue] in Primary_venue_dict:
            Primary_venue_dict[Venue_clean_dict[venue]] = False
for org in org_nodes.index:
    if not org  in Primary_org_dict and not org in UNSW_dict:
        Primary_org_dict[org] = False     
    elif org in UNSW_dict:
        if not UNSW_dict[org] in Primary_org_dict:
            Primary_org_dict[UNSW_dict[org]] = False
        
global_primary_dict = dict()
for author in Primary_author_dict:
    global_primary_dict[author] = Primary_author_dict[author]
for topic in Primary_topic_dict:
    global_primary_dict[topic] = Primary_topic_dict[topic]
for venue in Primary_venue_dict:
    global_primary_dict[venue] = Primary_venue_dict[venue]    
for org in Primary_org_dict:
    global_primary_dict[org] = Primary_org_dict[org]  
    
    
#Creating recomm set for checking authors:
auth_recommended_dict = dict()
auth_recommended_dict["primary"] = set()
auth_recommended_dict["secondary"] = set()
auth_recommended_dict["primary_pairs"] = set()
auth_recommended_dict["secondary_pairs"] = set()
auth_recommended_dict["general_pairs"] = set()


for prob, author1, author2, rec_type in primary_secondary_recommendations_list:
    if author_density_dict[author1] > 0 and author_density_dict[author2] > 0: # i.e. 21-10-2020 neither is an isolated node (BUG NEEDS FIXING & INVESTIGATION)!
        if rec_type == "primary":
            auth_recommended_dict["primary"].add(author1)
            auth_recommended_dict["primary"].add(author2)
            auth_recommended_dict["primary_pairs"].add(tuple((author1, author2)))
            auth_recommended_dict["general_pairs"].add(tuple((prob,author1, author2,rec_type)))
    
        elif rec_type == "secondary":
            auth_recommended_dict["secondary"].add(author1)
            auth_recommended_dict["secondary"].add(author2)
            auth_recommended_dict["secondary_pairs"].add(tuple((author1, author2)))
            auth_recommended_dict["general_pairs"].add(tuple((prob,author1, author2,rec_type)))

#Creating Recommendations table for recommendation output:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/1-Preparing multitype nodes and edge dataset/Hetergenous_dataset_final.pickle",'rb')
unpickler = pickle.Unpickler(file)
Hetero_dataset = unpickler.load()
#Creating node density dictionaries to calculate standardised degree for each node- default 0 (no edges):
general_density_dict = dict()
for author in author_nodes.index:
    general_density_dict[author] = 0
for org in org_density_dict:
    general_density_dict[org] = 0
for venue in venue_nodes.index:
    general_density_dict[venue] = 0
for topic in topic_nodes.index:
    general_density_dict[topic] = 0
for source, target, relation, weight in Hetero_dataset.values:
    if source.replace(" ", "_") in general_density_dict:
        general_density_dict[source.replace(" ", "_")] += 1  
    elif source.replace(" ", "_") in UNSW_dict:
        if UNSW_dict[source.replace(" ", "_")] in general_density_dict:
            general_density_dict[UNSW_dict[source.replace(" ", "_")]] += 1 
        else:
            general_density_dict[UNSW_dict[source.replace(" ", "_")]] = 1 
    elif source.replace(" ", "_") in Venue_clean_dict:
        if Venue_clean_dict[source.replace(" ", "_")] in general_density_dict:
            general_density_dict[Venue_clean_dict[source.replace(" ", "_")]] += 1 
        else:
            general_density_dict[Venue_clean_dict[source.replace(" ", "_")]] = 1 
    else:
        general_density_dict[source.replace(" ", "_")] = 0
    if target.replace(" ", "_") in general_density_dict:
        general_density_dict[target.replace(" ", "_")] += 1
        
    elif target.replace(" ", "_") in UNSW_dict:
        if UNSW_dict[target.replace(" ", "_")] in general_density_dict:
            general_density_dict[UNSW_dict[target.replace(" ", "_")]] += 1 
        else:
            general_density_dict[UNSW_dict[target.replace(" ", "_")]] = 1
    
    elif target.replace(" ", "_") in Venue_clean_dict:
        if Venue_clean_dict[target.replace(" ", "_")] in general_density_dict:
            general_density_dict[Venue_clean_dict[target.replace(" ", "_")]] += 1 
        else:
            general_density_dict[Venue_clean_dict[target.replace(" ", "_")]] = 1 
            
    else:
        general_density_dict[target.replace(" ", "_")] = 0


author_coauthors = {}
author_orgs = {}
author_venues = {}
author_topics = {}
for _, prob,_, author1, author2 in Recommendations_dts.values:
    if (author1 in primary_authors_set or author2 in primary_authors_set) and (prob > 0) and \
    (not tuple((author1,author2)) in coauthor_set) and (not tuple((author2,author1)) in coauthor_set) and\
        (general_density_dict[author1] > 0 and general_density_dict[author2] > 0): #NOTE: This is filtering out bug for 
            # 0 edge nodes (isolated) to be included in recommendations (need to investigate this to see
            #why these are being predicted for edges and if some nodes etc missing)

        print("Beginning",author1,author2)
        for source, target, relation, weight in Hetero_dataset.values:
            entity_org1 = None
            general_density_org1 = None
            entity_venue1 = None
            general_density_venue1 = None
            entity_topic1 = None
            general_density_topic1 = None
            entity_org2 = None
            general_density_org2 = None
            entity_venue2 = None
            general_density_venue2 = None
            entity_topic2 = None
            general_density_topic2 = None
            entity_coauthor1 = None
            entity_coauthor2 = None
            general_density_coauthor1 = None
            general_density_coauthor2 = None
            cnt_coauthor1 = None
            cnt_coauthor2 = None
            cnt_org1 = None
            cnt_venue1 = None
            cnt_topic1 = None
            cnt_org2 = None
            cnt_venue2 = None
            cnt_topic2 = None
            if (source == author1 or target == author1) and relation == 'AUTHOR-(P)-ORG':
                if source != author1:
                    if source.replace(" ", "_") in UNSW_dict:
                        entity_org1 = UNSW_dict[source.replace(" ", "_")] 
                        general_density_org1 = general_density_dict[UNSW_dict[source.replace(" ", "_")]]
                        cnt_org1 =  weight
                    elif source.replace(" ","_") in Venue_clean_dict:
                        entity_org1 = Venue_clean_dict[source.replace(" ", "_")] 
                        general_density_org1 = general_density_dict[Venue_clean_dict[source.replace(" ", "_")]]
                        cnt_org1 =  weight                        
                    elif not source.replace(" ", "_") in UNSW_dict and not source.replace(" ", "_") in Venue_clean_dict:
                        entity_org1 = source.replace(" ", "_") 
                        general_density_org1 = general_density_dict[source.replace(" ", "_")]
                        cnt_org1 =  weight 

                elif target != author1:
                    if target.replace(" ", "_") in UNSW_dict:
                        entity_org1 = UNSW_dict[target.replace(" ", "_")] 
                        general_density_org1 = general_density_dict[UNSW_dict[target.replace(" ", "_")]]
                        cnt_org1 =  weight
                    elif target.replace(" ","_") in Venue_clean_dict:
                        entity_org1 = Venue_clean_dict[target.replace(" ", "_")] 
                        general_density_org1 = general_density_dict[Venue_clean_dict[target.replace(" ", "_")]]
                        cnt_org1 =  weight                        
                    elif not target.replace(" ", "_") in UNSW_dict and not target.replace(" ", "_") in Venue_clean_dict:
                        entity_org1 = target.replace(" ", "_") 
                        general_density_org1 = general_density_dict[target.replace(" ", "_")]
                        cnt_org1 =  weight  
            if (source == author2 or target == author2) and relation == 'AUTHOR-(P)-ORG':
                if source != author2:
                    if source.replace(" ", "_") in UNSW_dict:
                        entity_org2 = UNSW_dict[source.replace(" ", "_")]
                        general_density_org2 = general_density_dict[UNSW_dict[source.replace(" ", "_")]] 
                        cnt_org2 = weight
                    elif source.replace(" ", "_") in Venue_clean_dict:
                        entity_org2 = Venue_clean_dict[source.replace(" ", "_")]
                        general_density_org2 = general_density_dict[Venue_clean_dict[source.replace(" ", "_")]] 
                        cnt_org2 = weight
                    elif not source.replace(" ", "_") in UNSW_dict and not source.replace(" ","_") in Venue_clean_dict:
                        entity_org2 = source.replace(" ", "_")
                        general_density_org2 = general_density_dict[source.replace(" ", "_")] 
                        cnt_org2 = weight                        
                elif target != author2:
                    if target.replace(" ", "_") in UNSW_dict:
                        entity_org2 = UNSW_dict[target.replace(" ", "_")]
                        general_density_org2 = general_density_dict[UNSW_dict[target.replace(" ", "_")]] 
                        cnt_org2 = weight
                    elif target.replace(" ", "_") in Venue_clean_dict:
                        entity_org2 = Venue_clean_dict[target.replace(" ", "_")]
                        general_density_org2 = general_density_dict[Venue_clean_dict[target.replace(" ", "_")]] 
                        cnt_org2 = weight
                    elif not target.replace(" ", "_") in UNSW_dict and not target.replace(" ","_") in Venue_clean_dict:
                        entity_org2 = target.replace(" ", "_")
                        general_density_org2 = general_density_dict[target.replace(" ", "_")] 
                        cnt_org2 = weight  
            if (source == author1 or target == author1) and relation ==  'AUTHOR-(P)-VENUE' :
                if source != author1:
                    entity_venue1 = source
                    general_density_venue1 = general_density_dict[source.replace(" ", "_")]
                    cnt_venue1 = weight
                elif target != author1:
                    entity_venue1 = target
                    general_density_venue1 = general_density_dict[target.replace(" ", "_")]
                    cnt_venue1 = weight
            if (source == author2 or target == author2) and relation ==  'AUTHOR-(P)-VENUE' :
                if source != author2:
                    entity_venue2 = source
                    general_density_venue2 = general_density_dict[source.replace(" ", "_")] 
                    cnt_venue2 = weight
                elif target != author2:
                    entity_venue2 = target
                    general_density_venue2 = general_density_dict[target.replace(" ", "_")]
                    cnt_venue2 = weight
            
            if (source == author1 or target == author1) and relation ==  'AUTHOR-(P)-TOPIC' :
                if source != author1:
                    entity_topic1 = source
                    general_density_topic1 = general_density_dict[source.replace(" ", "_")]
                    cnt_topic1 = weight
                elif target != author1:
                    entity_topic1 = target
                    general_density_topic1 = general_density_dict[target.replace(" ", "_")]
                    cnt_topic1 = weight
            if (source == author2 or target == author2) and relation ==  'AUTHOR-(P)-TOPIC' :
                if source != author2:
                    entity_topic2 = source
                    general_density_topic2 = general_density_dict[source.replace(" ", "_")] 
                    cnt_topic2 = weight
                elif target != author2:
                    entity_topic2 = target
                    general_density_topic2 = general_density_dict[target.replace(" ", "_")]  
                    cnt_topic2 = weight
            if (source == author1 or target == author1) and relation ==  'AUTHOR-(P)-AUTHOR' :
                if source != author1:
                    entity_coauthor1 = source
                    general_density_coauthor1 = general_density_dict[source.replace(" ", "_")] 
                    cnt_topic1 = weight
                elif target != author1:
                    entity_coauthor1 = target
                    general_density_coauthor1 = general_density_dict[target.replace(" ", "_")]  
                    cnt_coauthor1 = weight     
            if (source == author2 or target == author2) and relation ==  'AUTHOR-(P)-AUTHOR' :
                if source != author2:
                    entity_coauthor2 = source
                    general_density_coauthor2 = general_density_dict[source.replace(" ", "_")] 
                    cnt_topic2 = weight
                elif target != author2:
                    entity_coauthor2 = target
                    general_density_coauthor2 = general_density_dict[target.replace(" ", "_")]  
                    cnt_coauthor2 = weight
            if (entity_coauthor1 != None):
                if author1 in author_coauthors:
                    author_coauthors[author1].append((entity_coauthor1,general_density_coauthor1,weight ))
                else:
                    author_coauthors[author1]=[(entity_coauthor1,general_density_coauthor1,cnt_coauthor1)]
                    
            if (entity_org1!= None):
                if author1 in author_orgs:
                    author_orgs[author1].append((entity_org1,general_density_org1,weight ))
                else:
                    author_orgs[author1]=[(entity_org1,general_density_org1,cnt_org1)]
            if (entity_venue1!=  None):
                if author1 in author_venues:
                    author_venues[author1].append((entity_venue1,general_density_venue1,cnt_venue1 ))
                else:
                    author_venues[author1]= [(entity_venue1,general_density_venue1,cnt_venue1)]
                    
            if (entity_topic1 != None):    
                if author1 in author_topics:
                    author_topics[author1].append((entity_topic1,general_density_topic1,cnt_topic1 ))
                else:
                    author_topics[author1] = [(entity_topic1,general_density_topic1,cnt_topic1) ]
            if (entity_org2 !=None):
                if author2 in author_orgs:
                    author_orgs[author2].append((entity_org2,general_density_org2,cnt_org2 ))
                else:
                    author_orgs[author2] = [(entity_org2,general_density_org2,cnt_org2)]
            if (entity_venue2 != None):
                if author2 in author_venues:
                    author_venues[author2].append((entity_venue2,general_density_venue2,cnt_venue2 ))
                else:
                    author_venues[author2] = [(entity_venue2,general_density_venue2,cnt_venue2) ]
            if (entity_topic2 != None):    
                if author2 in author_topics:
                    author_topics[author2].append((entity_topic2,general_density_topic2,cnt_topic2 ))
                else:
                    author_topics[author2] = [(entity_topic2,general_density_topic2,cnt_topic2) ]
            if (entity_coauthor2 != None):
                if author2 in author_coauthors:
                    author_coauthors[author2].append((entity_coauthor2,general_density_coauthor2,weight ))
                else:
                    author_coauthors[author2]=[(entity_coauthor2,general_density_coauthor2,cnt_coauthor2)]
                
# author1   author2   
#org   author1-degree   author2-degree   general-degree


Indirect_relationship_recommendation_pairs = set()                
recommendation_intersection_pair_set = set()        
recommendation_table = []
for _, prob,_, author1, author2 in Recommendations_dts.values:
    if (author1 in primary_authors_set or author2 in primary_authors_set) and (prob > 0) and \
    (not tuple((author1,author2)) in coauthor_set) and (not tuple((author2,author1)) in coauthor_set):
        if author1 in primary_authors_set and author2 in primary_authors_set:
            Recommendation_Type = "Primary Recommendation"
        elif (author1 in primary_authors_set or author2 in primary_authors_set) and not (author1 in primary_authors_set and author2 in primary_authors_set):
            Recommendation_Type = "Secondary Recommendation"
        author1_topic_set = set()
        author2_topic_set = set()
        intersection = set()
        if author1 in author_topics and author2 in author_topics:
           for entity, general, specific in author_topics[author1]:
               author1_topic_set.add(entity)
           for entity, general, specific in author_topics[author2]:
               author2_topic_set.add(entity)
           intersection = author1_topic_set.intersection(author2_topic_set)
           print(intersection)
           if len(intersection) >= 1:
              for entity_int in intersection:
                   for entity, general, specific in author_topics[author1]:
                       if entity == entity_int:
                           auth1_spec = specific
                           general_int = general
                   for entity, general, specific in author_topics[author2]:
                       if entity == entity_int:
                           auth2_spec = specific
                           general_int = general
                   #if entity_int in topic_label_dict:
                   #    entity_int = topic_label_dict[topic]
                   if entity_int in Inferred_topic_label_dict:
                       entity_int = Inferred_topic_label_dict[entity_int]
                   recommendation_intersection_pair_set.add(tuple((author1, author2)))
                   Indirect_relationship_recommendation_pairs.add(tuple((author1,author2)))
                   recommendation_table.append([Recommendation_Type,author1, author2,"Topic",entity_int,auth1_spec, auth2_spec,general_int,prob])
        author1_org_set = set()
        author2_org_set = set()
        intersection = set()
        if author1 in author_orgs and author2 in author_orgs:
           for entity, general, specific in author_orgs[author1]:
               author1_org_set.add(entity)
           for entity, general, specific in author_orgs[author2]:
               author2_org_set.add(entity)
           intersection = author1_org_set.intersection(author2_org_set)
           print(intersection)
           if len(intersection) >= 1:
              for entity_int in intersection:
                   for entity, general, specific in author_orgs[author1]:
                       if entity == entity_int:
                           auth1_spec = specific
                           general_int = general
                   for entity, general, specific in author_orgs[author2]:
                       if entity == entity_int:
                           auth2_spec = specific
                           general_int = general
                   recommendation_intersection_pair_set.add(tuple((author1, author2)))
                   Indirect_relationship_recommendation_pairs.add(tuple((author1,author2)))
                   recommendation_table.append([Recommendation_Type,author1, author2,"Organisation",entity_int,auth1_spec, auth2_spec,general_int,prob])
        author1_venue_set = set()
        author2_venue_set = set()
        intersection = set()
        if author1 in author_venues and author2 in author_venues:
           for entity, general, specific in author_venues[author1]:
               author1_venue_set.add(entity)
           for entity, general, specific in author_venues[author2]:
               author2_venue_set.add(entity)
           intersection = author1_venue_set.intersection(author2_venue_set)
           print(intersection)
           if len(intersection) >= 1:
              for entity_int in intersection:
                   for entity, general, specific in author_venues[author1]:
                       if entity == entity_int:
                           auth1_spec = specific
                           general_int = general
                   for entity, general, specific in author_venues[author2]:
                       if entity == entity_int:
                           auth2_spec = specific
                           general_int = general
                   recommendation_intersection_pair_set.add(tuple((author1, author2)))
                   Indirect_relationship_recommendation_pairs.add(tuple((author1,author2)))
                   recommendation_table.append([Recommendation_Type,author1, author2,"Venue",entity_int,auth1_spec, auth2_spec,general_int,prob]) 
        author1_coauthor_set = set()
        author2_coauthor_set = set()
        intersection = set()
        if author1 in author_coauthors and author2 in author_coauthors:
           for entity, general, specific in author_coauthors[author1]:
               author1_coauthor_set.add(entity)
           for entity, general, specific in author_coauthors[author2]:
               author2_coauthor_set.add(entity)
           intersection = author1_coauthor_set.intersection(author2_coauthor_set)
           print(intersection)
           if len(intersection) >= 1:
              for entity_int in intersection:
                   for entity, general, specific in author_coauthors[author1]:
                       if entity == entity_int:
                           auth1_spec = specific
                           general_int = general
                   for entity, general, specific in author_coauthors[author2]:
                       if entity == entity_int:
                           auth2_spec = specific
                           general_int = general
                   recommendation_intersection_pair_set.add(tuple((author1, author2)))
                   Indirect_relationship_recommendation_pairs.add(tuple((author1,author2)))
                   recommendation_table.append([Recommendation_Type,author1, author2,"Coauthor",entity_int,auth1_spec, auth2_spec,general_int,prob]) 
                
       

#Checking to see if recommendation pairs are NOT in final recommendation summary due to finding no DIRECT relationships shared between recommended researchers:
for prob, author1, author2, rec_type in auth_recommended_dict["general_pairs"]:
    if not tuple((author1,author2)) in recommendation_intersection_pair_set:
        if author1 in primary_authors_set and author2 in primary_authors_set:
            Recommendation_Type = "Primary Recommendation"
        elif (author1 in primary_authors_set or author2 in primary_authors_set) and not (author1 in primary_authors_set and author2 in primary_authors_set):
            Recommendation_Type = "Secondary Recommendation"
        recommendation_table.append([Recommendation_Type,author1, author2,"No-Direct-Entity-Intersection","Use Pair Indirect Co-authorship Relationship-Network Vizualisation file","in", "'MuxViz Indirect-Network-Recommendation-Vizualisation' Folder","File: {},{}".format(author1,author2),prob]) 
        Indirect_relationship_recommendation_pairs.add(tuple((author1,author2)))
#Converting and pickling recommendation summary dataset into a dataframe containing each relation, edge set and weight instance between the networks.
recommendation_table_df = pd.DataFrame(recommendation_table, columns = ["Recommendation Type","Researcher1", "Researcher2", "Intersection","Entity","Researcher1-Entity-Weight","Researcher2-Entity-Weight","Entity-Network-Weight", "Research Collaboration Probability"])      
recommendation_table_df.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/Recommendation_Summary.csv")

#Writing researcher pairs without direct relation intersections to name txt file for creating later co-authorship vizualisations targeting these two authors only:
with open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/Indirect-Network-Recommendation-Vizualisations/Indirect-relationship-recommendation-pairs.txt","w") as file:
    for author1, author2 in Indirect_relationship_recommendation_pairs:
        file.write("{}|{}\n".format(author1,author2)) 
file.close() 
         
                
            
            
        
        
        
        
      
        
        
        
        
    
index_count = 0
index_dict = dict()    
node_keep_dict = dict()
with open("./muxViz-master/MultiGraph_node_layout.txt", "w", encoding="utf-8") as file:
    file.write("nodeID nodeLabel\n")
    for author in author_density_dict:
        if author in Primary_author_dict:
            if (Primary_author_dict[author] == True and author in primary_authors_set):
               #   or (author in auth_recommended_dict["primary"]) or  (author in auth_recommended_dict["secondary"]):
                index_count += 1
                index_dict[author] = index_count
                row_str = "{} {}\n".format(index_dict[author], author)
                print(row_str)
                node_keep_dict[author] = True
                file.write(row_str)
            #Not interested in non-primary authors.
            #elif (author in auth_recommended_dict["primary"]) or  (author in auth_recommended_dict["secondary"]) :
            #    index_count += 1
            #    index_dict[author] = index_count
            #    row_str = "{} {}\n".format(index_dict[author], author)
            #    print(row_str)
            #    node_keep_dict[author] = True
            #    #recording in node for recommendation.
            else:
                node_keep_dict[author] = False
    for org in org_density_dict:
        if org in Primary_org_dict and not org in UNSW_dict:
            if (Primary_org_dict[org] == True and org_density_dict[org] >= org_density_threshold): #or (org_density_dict[org] >= org_density_threshold):
                index_count += 1
                index_dict[org] = index_count
                row_str = "{} {}\n".format(index_dict[org], org)
                print(row_str)
                file.write(row_str)
                node_keep_dict[org] = True
            else:
                node_keep_dict[org] = False
        elif org in Primary_org_dict and org in UNSW_dict: 
            if (Primary_org_dict[UNSW_dict[org]] == True and org_density_dict[UNSW_dict[org]] >= org_density_threshold): #or (org_density_dict[org] >= org_density_threshold):
                if UNSW_dict[org] in index_dict:
                    continue
                    #want a unique id for just the one primary org name - not each error org name
                if not UNSW_dict[org] in index_dict:  
                    index_count += 1
                    index_dict[UNSW_dict[org]] = index_count
                row_str = "{} {}\n".format(index_dict[UNSW_dict[org]], UNSW_dict[org])
                print(row_str)
                file.write(row_str)
                node_keep_dict[UNSW_dict[org]] = True
            #else:
                #node_keep_dict[UNSW_dict[org]] = False
    for venue in venue_density_dict:
        if venue in Primary_venue_dict and not venue in Venue_clean_dict:
            if (Primary_venue_dict[venue] == True and venue_density_dict[venue] >= venue_density_threshold): #or (venue_density_dict[venue] >= venue_density_threshold):
                index_count += 1
                index_dict[venue] = index_count
                row_str = "{} {}\n".format(index_dict[venue], venue)
                print(row_str)
                file.write(row_str)
                node_keep_dict[venue] = True
            else:
                node_keep_dict[venue] = False
        elif venue in Primary_venue_dict and venue in Venue_clean_dict: 
            if (Primary_venue_dict[Venue_clean_dict[venue]] == True and venue_density_dict[Venue_clean_dict[venue]] >= venue_density_threshold): #or (org_density_dict[org] >= org_density_threshold):
                if Venue_clean_dict[venue] in index_dict:
                    continue
                    #want a unique id for just the one correct name - not each error venue name
                if not Venue_clean_dict[venue] in index_dict:  
                    index_count += 1
                    index_dict[Venue_clean_dict[venue]] = index_count
                row_str = "{} {}\n".format(index_dict[Venue_clean_dict[venue]], Venue_clean_dict[venue])
                print(row_str)
                file.write(row_str)
                node_keep_dict[Venue_clean_dict[venue]] = True
            else:
                node_keep_dict[Venue_clean_dict[venue]] = False
    for topic in topic_density_dict:
        if topic in Primary_topic_dict:
            if (Primary_topic_dict[topic] == True and topic_density_dict[topic] >= topic_density_threshold): #or (topic_density_dict[topic] >= topic_density_threshold):
                index_count += 1
                #if topic in Inferred_topic_label_dict:
                topic_label = Inferred_topic_label_dict[topic]
                topic_label = topic_label.replace(" ", "_")
                index_dict[topic] = index_count
                row_str = "{} {}\n".format(index_dict[topic], topic_label)
                print(row_str)
                file.write(row_str)
                node_keep_dict[topic] = True
                #else:
                #    print(topic, "NOT IN Inferrred topic label dict")
                #    topic_label = Inferred_topic_label_dict[topic_label_dict[topic]]
                #    index_dict[topic] = index_count
                #    row_str = "{} {}\n".format(index_dict[topic], topic_label_dict[topic])
                #    print(row_str)
                #    file.write(row_str)
                #    node_keep_dict[topic] = True
                    
            else:
                node_keep_dict[topic] = False
    
    file.close()
print(index_count)

    
    
#Creating node colour and size file - NEW version only primary nodes and non-primary nodes above threshold for degree:
cnt = 0
recom_author_cnt = 0
with open("./muxViz-master/MultiGraph_node_colour_size.txt", "w", encoding="utf-8") as file:
    file.write("nodeID layerID color size\n")
    for node in node_keep_dict:
        #Primary node: ORANGE
        if node_keep_dict[node] == True and node in Primary_org_dict:
                    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Organisations"], "green",org_density_dict[node]*100)
                    print(row_str)
                    cnt += 1
                    file.write(row_str)
        elif node_keep_dict[node] == True and node in Primary_author_dict:
            if Primary_author_dict[node] == True:
                if (node in primary_authors_set) and not ((node in auth_recommended_dict["primary"]) or  (node in auth_recommended_dict["secondary"])) :
                    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "orange",author_density_dict[node]*20)
                    print(row_str)
                    cnt += 1
                    file.write(row_str)        
                elif (node in primary_authors_set) and ((node in auth_recommended_dict["primary"]) or  (node in auth_recommended_dict["secondary"])) :
                    print("Recommended author node is", node, "as primary node will not amend node colour or size!")
                    recom_author_cnt += 1
                    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "purple",author_density_dict[node]*20)
                    print(row_str) 
                    cnt += 1
                    file.write(row_str) 
               #elif (not node in primary_authors_set) and ((node in auth_recommended_dict["primary"]) or  (node in auth_recommended_dict["secondary"])) :
               #     print("Recommended author node is", node, "and not primary node will amend colour to red!") 
               #     recom_author_cnt += 1
               #     row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "red",author_density_dict[node]*100)
        #!HERE AMENDED WILL NEED FIXING!!!!!!!!!!!!!!!!! for recommended authors!
        
                    #row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "purple",1)                    
                    
        elif node in Primary_venue_dict and node_keep_dict[node] == True:
                    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Venues(Journal/Conferences)"], "blue",venue_density_dict[node]*20)
                    print(row_str)
                    cnt += 1
                    file.write(row_str)
        elif node in Primary_topic_dict and node_keep_dict[node] == True:              
                    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Topics"], "red",topic_density_dict[node]*20)
                    print(row_str)
                    cnt += 1
                    file.write(row_str)
        #NON-PRIMARY NODE - although keep node - meets filtering criteria (standardized node degree threshold for node type):
        #if node_keep_dict[node] == True and global_primary_dict[node] == False and node in org_nodes.index:
        #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Organisations"], "green",org_density_dict[node]*100)
        #    print(row_str)
        #    cnt += 1
        #    file.write(row_str)
        #elif node_keep_dict[node] == True and global_primary_dict[node] == False and node in author_nodes.index \
        #         and not ((node in auth_recommended_dict["primary"]) or  (node in auth_recommended_dict["secondary"])):      
        #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "gray",0)
        #    print(row_str)
        #    cnt += 1
        #    file.write(row_str)
            
        #elif node_keep_dict[node] == True and global_primary_dict[node] == False and node in author_nodes.index \
        #         and ((node in auth_recommended_dict["primary"]) or  (node in auth_recommended_dict["secondary"])):      
        #!HERE AMENDED WILL NEED FIXING!!!!!!!!!!!!!!!!! for recommended authors!
                     #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "purple",author_density_dict[node]*100)
        #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "purple",1)
        
        #    print(row_str)
        #    recom_author_cnt += 1
        #    cnt += 1
        #    file.write(row_str)
        #    
        #elif node_keep_dict[node] == True and global_primary_dict[node] == False and node in venue_nodes.index:
        #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Venues(Journal/Conferences)"], "blue",venue_density_dict[node]*100)
        #    print(row_str)
        #    cnt += 1
        #    file.write(row_str)
        #elif node_keep_dict[node] == True and global_primary_dict[node] == False and node in topic_nodes.index:
        #    row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Topics"], "red",topic_density_dict[node]*100)
        #    print(row_str)
        #    cnt += 1
        #    file.write(row_str)

#print(cnt)
#Pruning non-primary edges to/from excluded nodes:
included_relations_set = set()
Hetero_primary_flag_dts_pruned = []
for source, target, relation, weight, primary_flag in Hetero_primary_flag_dts:
   if primary_flag == True:
       Hetero_primary_flag_dts_pruned.append([source, target, relation, weight, primary_flag])
   if primary_flag == False:
        #note: non-primary edge weight <= 50th percentile (half of edges) already removed.
        #Make sure source or target are not excluded nodes:
        if source.replace(" ", "_") in node_keep_dict and target.replace(" ", "_") in node_keep_dict:
            included_relations_set.add(relation)
            if node_keep_dict[source.replace(" ", "_")] == True and node_keep_dict[target.replace(" ", "_")] == True:
                Hetero_primary_flag_dts_pruned.append([source, target, relation, weight, primary_flag])
        #Otherwise, if not a primary author edge is the edge a primary organisation (UNSW) edge?
        elif source.replace(" ", "_") in UNSW_dict or target.replace(" ", "_") in UNSW_dict:
            primary_org = False
            if source.replace(" ", "_")  in UNSW_dict:
                if  UNSW_dict[source.replace(" ", "_")] == Correct_primary_org_name:
                    primary_org = True
            elif target.replace(" ", "_")  in UNSW_dict:
                if  UNSW_dict[target.replace(" ", "_")] == Correct_primary_org_name:
                    primary_org = True 
            if primary_org == True:
                Hetero_primary_flag_dts_pruned.append([source, target, relation, weight, primary_flag])
        



#Creating edge size and colour file:
#FORMAT: nodeID.from layerID.from nodeID.to layerID.to color size
cnt = 0
with open("./muxViz-master/MultiGraph_edge_colour_size.txt", "w", encoding="utf-8") as file:
    file.write("nodeID.from layerID.from nodeID.to layerID.to color size\n")
    for source, target, relation, weight, primary_flag in Hetero_primary_flag_dts_pruned:
       # if ((source in auth_recommended_dict["primary"]) or (target in auth_recommended_dict["secondary"])):
       #     if source.replace(" ", "_") in org_nodes.index:
       #         layerID_from = layer_dict["Organisations"]
       #         
       #     elif source.replace(" ", "_") in venue_nodes.index:
       #         layerID_from = layer_dict["Venues(Journal/Conferences)"]
       #     elif source.replace(" ", "_") in topic_nodes.index:
       #         layerID_from = layer_dict["Topics"]
       #     elif source.replace(" ", "_") in author_nodes.index:
       #         layerID_from = layer_dict["Authors"]
       #     else:
       #         print("EXCEPTION!!!", source)
       #     if target.replace(" ", "_") in org_nodes.index:
        #        layerID_to = layer_dict["Organisations"]
        #    elif target.replace(" ", "_") in venue_nodes.index:
        #        layerID_to = layer_dict["Venues(Journal/Conferences)"]
        #    elif target.replace(" ", "_") in topic_nodes.index:
        ##        layerID_to = layer_dict["Topics"]
         #   elif target.replace(" ", "_") in author_nodes.index:
         #       layerID_to = layer_dict["Authors"]
         #   else:
         #       print("EXCEPTION!!!", target)
         #   row_str = "{} {} {} {} {} {}\n".format(index_dict[source.replace(" ", "_")],layerID_from,
         #                                          index_dict[target.replace(" ", "_")], layerID_to,
         #                                          "purple", round(weight,4)*10)
        
        #Giving emphasis in primary author edges in Vizualisation making them orange and of significantly higher weight:                
        #Looking for primary author edge instances:
        if  ((source in primary_authors_set) or (target in primary_authors_set)): #and ((not source in auth_recommended_dict["primary"]) and (not target in auth_recommended_dict["secondary"])):
            if source.replace(" ", "_") in org_nodes.index:
                layerID_from = layer_dict["Organisations"]
                
            elif source.replace(" ", "_") in venue_nodes.index:
                layerID_from = layer_dict["Venues(Journal/Conferences)"]
            elif source.replace(" ", "_") in topic_nodes.index:
                layerID_from = layer_dict["Topics"]
            elif source.replace(" ", "_") in author_nodes.index:
                layerID_from = layer_dict["Authors"]
            else:
                print("EXCEPTION!!!", source)
            if target.replace(" ", "_") in org_nodes.index:
                layerID_to = layer_dict["Organisations"]
            elif target.replace(" ", "_") in venue_nodes.index:
                layerID_to = layer_dict["Venues(Journal/Conferences)"]
            elif target.replace(" ", "_") in topic_nodes.index:
                layerID_to = layer_dict["Topics"]
            elif target.replace(" ", "_") in author_nodes.index:
                layerID_to = layer_dict["Authors"]
            else:
                print("EXCEPTION!!!", target)
            
            if source.replace(" ", "_") in UNSW_dict:
                source = UNSW_dict[source.replace(" ", "_")]
            else:
                source = source.replace(" ", "_")
            if target.replace(" ", "_") in UNSW_dict:
                target = UNSW_dict[target.replace(" ", "_")]
            else:
                target = target.replace(" ", "_")
                
            if source.replace(" ", "_") in Venue_clean_dict:
                source = Venue_clean_dict[source.replace(" ", "_")]
            else:
                source = source.replace(" ", "_")
            if target.replace(" ", "_") in Venue_clean_dict:
                target = Venue_clean_dict[target.replace(" ", "_")]
            else:
                target = target.replace(" ", "_")
            #Giving emphasis to primary author edges by increasing weight of primary author edges by multiple of 4.   
            if source in index_dict and target in index_dict:
                row_str = "{} {} {} {} {} {}\n".format(index_dict[source],layerID_from,
                                                   index_dict[target], layerID_to,
                                                   "orange", round(weight*4,4))
                
            
                file.write(row_str)   
                cnt += 1
        #Creating green edges for primary organisation connections.
        # No extra emphasis is given to weights of primary organisation (UNSW):
        #Now looking for secondary case, primary organisation edge instances:
        elif  ((source.replace(" ", "_") in UNSW_dict or target.replace(" ", "_") in UNSW_dict)):
            primary_org_edge = False
            #print(source, target, "PRIMARY ORG EDGE")
            if source.replace(" ", "_") in UNSW_dict:
                if UNSW_dict[source.replace(" ", "_")] == Correct_primary_org_name:
                    primary_org_edge = True
            if target.replace(" ", "_") in UNSW_dict:
                if UNSW_dict[target.replace(" ", "_")] == Correct_primary_org_name:
                    primary_org_edge = True
            if primary_org_edge == True:    
                if source.replace(" ", "_") in org_nodes.index:
                    layerID_from = layer_dict["Organisations"]
                    
                elif source.replace(" ", "_") in venue_nodes.index:
                    layerID_from = layer_dict["Venues(Journal/Conferences)"]
                elif source.replace(" ", "_") in topic_nodes.index:
                    layerID_from = layer_dict["Topics"]
                elif source.replace(" ", "_") in author_nodes.index:
                    layerID_from = layer_dict["Authors"]
                else:
                    print("EXCEPTION!!!", source)
                if target.replace(" ", "_") in org_nodes.index:
                    layerID_to = layer_dict["Organisations"]
                elif target.replace(" ", "_") in venue_nodes.index:
                    layerID_to = layer_dict["Venues(Journal/Conferences)"]
                elif target.replace(" ", "_") in topic_nodes.index:
                    layerID_to = layer_dict["Topics"]
                elif target.replace(" ", "_") in author_nodes.index:
                    layerID_to = layer_dict["Authors"]
                else:
                    print("EXCEPTION!!!", target)
                
                if source.replace(" ", "_") in UNSW_dict:
                    source = UNSW_dict[source.replace(" ", "_")]
                else:
                    source = source.replace(" ", "_")
                if target.replace(" ", "_") in UNSW_dict:
                    target = UNSW_dict[target.replace(" ", "_")]
                else:
                    target = target.replace(" ", "_")
                    
                if source.replace(" ", "_") in Venue_clean_dict:
                    source = Venue_clean_dict[source.replace(" ", "_")]
                else:
                    source = source.replace(" ", "_")
                if target.replace(" ", "_") in Venue_clean_dict:
                    target = Venue_clean_dict[target.replace(" ", "_")]
                else:
                    target = target.replace(" ", "_")
                    
                if source in index_dict and target in index_dict:
                    row_str = "{} {} {} {} {} {}\n".format(index_dict[source],layerID_from,
                                                       index_dict[target], layerID_to,
                                                       "green", round(weight*2,4))
                    
                
                    file.write(row_str)   
                    cnt += 1
        #elif primary_flag == True:
        #    if source.replace(" ", "_") in org_nodes.index:
        #        layerID_from = layer_dict["Organisations"]
        #        
        #    elif source.replace(" ", "_") in venue_nodes.index:
        #        layerID_from = layer_dict["Venues(Journal/Conferences)"]
        #    elif source.replace(" ", "_") in topic_nodes.index:
        ##        layerID_from = layer_dict["Topics"]
         #   elif source.replace(" ", "_") in author_nodes.index:
         #       layerID_from = layer_dict["Authors"]
         #   else:
         #       print("EXCEPTION!!!", source)
         #   if target.replace(" ", "_") in org_nodes.index:
          #      layerID_to = layer_dict["Organisations"]
         #   elif target.replace(" ", "_") in venue_nodes.index:
          #      layerID_to = layer_dict["Venues(Journal/Conferences)"]
          #  elif target.replace(" ", "_") in topic_nodes.index:
          #      layerID_to = layer_dict["Topics"]
          #  elif target.replace(" ", "_") in author_nodes.index:
          #      layerID_to = layer_dict["Authors"]
           # else:
           #     print("EXCEPTION!!!", target)
           # if source.replace(" ", "_") in index_dict and target.replace(" ", "_") in index_dict:
           #     row_str = "{} {} {} {} {} {}\n".format(index_dict[source.replace(" ", "_")],layerID_from,
            #                                       index_dict[target.replace(" ", "_")], layerID_to,
            #                                       "gray", round(weight,4))
            #    file.write(row_str)   
            #    cnt += 1
        #elif primary_flag == False:
        #    if source.replace(" ", "_") in org_nodes.index:
        #        layerID_from = layer_dict["Organisations"]
        #    elif source.replace(" ", "_") in venue_nodes.index:
        ##        layerID_from = layer_dict["Venues(Journal/Conferences)"]
        #    elif source.replace(" ", "_") in topic_nodes.index:
        #       layerID_from = layer_dict["Topics"]
        #    elif source.replace(" ", "_") in author_nodes.index:
        #        layerID_from = layer_dict["Authors"]
        #    else:
        #        print("EXCEPTION!!!", source)
        #    if target.replace(" ", "_") in org_nodes.index:
        #        layerID_to = layer_dict["Organisations"]
        #    elif target.replace(" ", "_") in venue_nodes.index:
        #        layerID_to = layer_dict["Venues(Journal/Conferences)"]
        #    elif target.replace(" ", "_") in topic_nodes.index:
        #        layerID_to = layer_dict["Topics"]
        #    elif target.replace(" ", "_") in author_nodes.index:
        #        layerID_to = layer_dict["Authors"]
        ##    else:
         #       print("EXCEPTION!!!", target)
         #   if source.replace(" ", "_") in index_dict and target.replace(" ", "_") in index_dict:
         #       row_str = "{} {} {} {} {} {}\n".format(index_dict[source.replace(" ", "_")],layerID_from,
         #                                         index_dict[target.replace(" ", "_")], layerID_to,
         #                                          "gray", round(weight,4))
         #       file.write(row_str)   
         #       cnt += 1
    #Writing in format for recommendation edges:
    #for prob, author1,author2, rec_type in primary_secondary_recommendations_list:  
    #    row_str = "{} {} {} {} {} {}\n".format(index_dict[author1.replace(" ", "_")],layer_dict["Authors"],
    #                                           index_dict[author2.replace(" ", "_")], layer_dict["Authors"],
    #                                           "purple", 1*10)
    #    file.write(row_str)   
    #    cnt += 1
    #    print("RECOMMENDATION EDGE STR",row_str)
        
        
    file.close()
print("{} edges".format(cnt))


 #Extended edge list format - NEW ONLY PRIMARY AUTHOR AND edges with >= 10 EDGES and from non-excluded nodes:
#[source node] [source layer][target[target layer] [weight] 
#for relation in relations:
edge_cnt = 0
file_name = "./muxViz-master/MultiGraph_Layer_edges_extended.edges"
with open(file_name, "w", encoding="utf-8") as file:
    for source, target, relation, weight, primary_flag in Hetero_primary_flag_dts_pruned:
        if source.replace(" ", "_") in venue_nodes.index:
            slayer = "Venues(Journal/Conferences)"
        elif source.replace(" ", "_")  in org_nodes.index:
            slayer = "Organisations"
        elif source.replace(" ", "_")  in author_nodes.index:
            slayer = "Authors"
        elif source.replace(" ", "_")  in topic_nodes.index:
            slayer="Topics"
        if target.replace(" ", "_") in venue_nodes.index:
            tlayer = "Venues(Journal/Conferences)"
        elif target.replace(" ", "_") in org_nodes.index:
            tlayer = "Organisations"
        elif target.replace(" ", "_") in author_nodes.index:
            tlayer = "Authors"
        elif target.replace(" ", "_") in topic_nodes.index:
            tlayer="Topics"
        edge_cnt += 1
        
        if source.replace(" ", "_") in UNSW_dict:
            source = UNSW_dict[source.replace(" ", "_")]
        else:
            source = source.replace(" ", "_")
        if target.replace(" ", "_") in UNSW_dict:
            target = UNSW_dict[target.replace(" ", "_")]
        else:
            target = target.replace(" ", "_")
            
        if source.replace(" ", "_") in Venue_clean_dict:
            source = Venue_clean_dict[source.replace(" ", "_")]
        else:
            source = source.replace(" ", "_")
        if target.replace(" ", "_") in Venue_clean_dict:
            target = Venue_clean_dict[target.replace(" ", "_")]
        else:
            target = target.replace(" ", "_")
                
        if source in index_dict and target in index_dict:
            row_str = "{} {} {} {} {}\n".format(index_dict[source],layer_dict[slayer],
                                            index_dict[target], layer_dict[tlayer],
                                            round(weight, 4))
            file.write(row_str) 
        else:
            print(source,target,"not in index dict" )
    #Writing in format for recommendation edges:
    #for prob, author1,author2, rec_type in primary_secondary_recommendations_list:  
    #    row_str = "{} {} {} {} {}\n".format(index_dict[author1.replace(" ", "_")],layer_dict["Authors"],
    #                                           index_dict[author2.replace(" ", "_")], layer_dict["Authors"],1)
    #    file.write(row_str)   
    #    cnt += 1
    #    print("RECOMMENDATION EDGE STR",row_str)    
    file.close()    
print(edge_cnt)
#Configuration file to be imported to Muxnet as assembly file.
with open("./muxViz-master/MultiGraph_node_CONFIG.txt", "w", encoding="utf-8") as file:
    edge_file = "MultiGraph_Layer_edges_extended.edges"
    layer_file = "MultiGraph_Layers.txt"
    node_layout = "MultiGraph_node_layout.txt"
    row_str = "{};{};{}\n".format(edge_file,layer_file, node_layout)
    file.write(row_str)
    file.close()



 #Extended edge list format - OLD ALL EDGES:
#[source node] [source layer][target[target layer] [weight] 
#for relation in relations:
#edge_cnt = 0
#file_name = "MultiGraph_Layer_edges_extended.edges"
#with open(file_name, "w", encoding="utf-8") as file:
#    for source, target, relation, weight in Hetero_dataset.values:
#        if source.replace(" ", "_") in venue_nodes.index:
#            slayer = "Venues(Journal/Conferences)"
#        elif source.replace(" ", "_")  in org_nodes.index:
#            slayer = "Organisations"
#        elif source.replace(" ", "_")  in author_nodes.index:
#            slayer = "Authors"
#        elif source.replace(" ", "_")  in topic_nodes.index:
#            slayer="Topics"
#        if target.replace(" ", "_") in venue_nodes.index:
#            tlayer = "Venues(Journal/Conferences)"
#        elif target.replace(" ", "_") in org_nodes.index:
#            tlayer = "Organisations"
#        elif target.replace(" ", "_") in author_nodes.index:
#            tlayer = "Authors"
#        elif target.replace(" ", "_") in topic_nodes.index:
#            tlayer="Topics"
#        edge_cnt += 1
#        row_str = "{} {} {} {} {}\n".format(index_dict[source.replace(" ", "_")],layer_dict[slayer],
#                                            index_dict[target.replace(" ", "_")], layer_dict[tlayer],
#                                            weight)
##        file.write(row_str) 
#    file.close()
#print(edge_cnt)
##Configuration file to be imported to Muxnet as assembly file.
#with open("MultiGraph_node_CONFIG.txt", "w", encoding="utf-8") as file:
#    edge_file = "MultiGraph_Layer_edges_extended.edges"
#    layer_file = "MultiGraph_Layers.txt"
#    node_layout = "MultiGraph_node_layout.txt"
#    row_str = "{};{};{}\n".format(edge_file,layer_file, node_layout)
#    file.write(row_str)
##    file.close()
   
    
#TONIGHT
#Need to fix intra-edges formatting coauthor-coauthor, topic-topic, org-org and venue-venue etc!

#Need to fix formatting and filtering of primary author nodes (orange), topic, org, etc differerent colours, keeping
#only author, org, etc nodes that have high degree!
    
    

#Attempt using community algorithms/colouring and sizing by centrality.

#Fix exporting of graphs (can consider coming back to this later stage.)














