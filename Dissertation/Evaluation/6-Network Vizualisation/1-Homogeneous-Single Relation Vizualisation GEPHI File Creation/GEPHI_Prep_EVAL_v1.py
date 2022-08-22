#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:21:01 2020

Preparing Homogenous network graphs for Gephim for co-authorship and co-expertise networks.
@author: Liam Ephraims
"""
import pickle
import pandas as pd
import networkx as nx
import pandas as pd


#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/1-Preparing multitype nodes and edge dataset/Hetergenous_dataset_final.pickle",'rb')
unpickler = pickle.Unpickler(file)
Hetero_dataset = unpickler.load()

#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle",'rb')
unpickler = pickle.Unpickler(file)
Author_dataset = unpickler.load()

#Getting primary author names:
primary_authors = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
primary_authors_set = set(primary_authors.Name)

#Creating different node types:
org_nodes = pd.DataFrame(index=[org for org in set(Author_dataset["organization"]) if org != "NA"])

author_nodes = [author for author in set(Author_dataset["name"]) if author != "NA"]
author_nodes = set(author_nodes)
for coauthors in set(Author_dataset["coauthors"]):
    coauthors = coauthors.split(" ")
    for coauthor in coauthors:
        if not coauthor in author_nodes:
            author_nodes.add(coauthor)
author_nodes = pd.DataFrame(index=author_nodes)
            
topic_set = set()
for topic_list in Author_dataset["TOPICS"]:
    for topic, prop in topic_list:
        topic_set.add("T{}".format(topic))
topic_nodes =  pd.DataFrame(index=topic_set)

        
venue_nodes = pd.DataFrame(index=[jconf for jconf in set(Author_dataset["jconf"]) if jconf != "NA"])

#Creating homogenous networkx Author < TOPIC > Author network for Gephi vizualisation:
#author_topicNet = Hetero_dataset[Hetero_dataset.relation == "AUTHOR-(T)-AUTHOR"]
#author_topicNetG = nx.Graph()
#author_topicNetG.add_nodes_from(author_nodes.index)
#author_topicNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in author_topicNet.values if weight >= 1])
#nx.write_gexf(author_topicNetG, "author_topic_network.gexf")
#!NEED TO UDPATE FOR NEW RELATIONS!

import os
directory = "C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/1-Homogeneous-Single Relation Vizualisation GEPHI File Creation"
os.chdir(directory + "/GEPHI_network_files")



#Creating homogenous networkx Author < PAPER > Author network for Gephi vizualisation:
author_coauthorNet = Hetero_dataset[Hetero_dataset.relation == "AUTHOR-(P)-AUTHOR"]
author_coauthorNetG = nx.Graph()
author_coauthorNetG.add_nodes_from(author_nodes.index)
author_coauthorNetG.nodes()
author_coauthorNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in author_coauthorNet.values])
nx.write_gexf(author_coauthorNetG, "author_coauthor_network.gexf")


#Reformatting author nodes for primary authors only:
author_nodes = [author for author in set(Author_dataset["name"]) if author != "NA" and author in primary_authors_set]
author_nodes = set(author_nodes)
for coauthors in set(Author_dataset["coauthors"]):
    coauthors = coauthors.split(" ")
    for coauthor in coauthors:
        if not coauthor in author_nodes and coauthor in primary_authors_set:
            author_nodes.add(coauthor)
author_nodes = pd.DataFrame(index=author_nodes)


#Creating homogenous networkx ORG < AUTHOR > ORG network for Gephi vizualisation:
org_orgNet = Hetero_dataset[Hetero_dataset.relation == "ORG-(A)-ORG"]
org_orgNetG = nx.Graph()
org_orgNetG.add_nodes_from(org_nodes.index)
org_orgNetG.nodes()
org_orgNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in org_orgNet.values])
nx.write_gexf(org_orgNetG, "org_org_network.gexf")


#Creating homogenous networkx ORG < PAPER > VENUE network for Gephi vizualisation:
#org_venueNet = Hetero_dataset[Hetero_dataset.relation == "ORG-(P)-VENUE"]
#org_venueNetG = nx.Graph()
#org_venueNetG.add_nodes_from(org_nodes.index)
#org_venueNetG.add_nodes_from(venue_nodes.index)
#org_venueNetG.nodes()
#org_venueNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in org_venueNet.values])
#nx.write_gexf(org_venueNetG, "org_venue_network.gexf")

#Creating homogenous networkx AUTHOR < PAPER > VENUE network for Gephi vizualisation:
#author_venueNet = Hetero_dataset[Hetero_dataset.relation == "AUTHOR-(P)-VENUE"]
#author_venueNetG = nx.Graph()
#author_venueNetG.add_nodes_from(author_nodes.index)
#author_venueNetG.add_nodes_from(venue_nodes.index)
#author_venueNetG.nodes()
#author_venueNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in author_venueNet.values])
#nx.write_gexf(author_venueNetG, "author_venue_network.gexf")

#Creating homogenous networkx AUTHOR < PAPER > ORG network for Gephi vizualisation:
#author_orgNet = Hetero_dataset[Hetero_dataset.relation == "AUTHOR-(P)-ORG"]
#author_orgNetG = nx.Graph()
#author_orgNetG.add_nodes_from(org_nodes.index)
#author_orgNetG.add_nodes_from(author_nodes.index)
#author_orgNetG.nodes()
#author_orgNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in author_orgNet.values])
#nx.write_gexf(author_orgNetG, "author_org_network.gexf")

#Creating homogenous networkx AUTHOR < PAPER > TOPIC network for Gephi vizualisation:
#author_topicNet = Hetero_dataset[Hetero_dataset.relation == "AUTHOR-(P)-TOPIC"]
#author_topicNetG = nx.Graph()
#author_topicNetG.add_nodes_from(topic_nodes.index)
#author_topicNetG.add_nodes_from(author_nodes.index)
#author_topicNetG.nodes()
#author_topicNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in author_topicNet.values])
#nx.write_gexf(author_topicNetG, "author_topic_network.gexf")

#Creating homogenous networkx ORG < PAPER > TOPIC network for Gephi vizualisation:
#org_topicNet = Hetero_dataset[Hetero_dataset.relation == "ORG-(P)-TOPIC"]
#org_topicNetG = nx.Graph()
#org_topicNetG.add_nodes_from(org_nodes.index)
#org_topicNetG.add_nodes_from(topic_nodes.index)
#org_topicNetG.nodes()
#org_topicNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in org_topicNet.values])
#nx.write_gexf(org_topicNetG, "author_topic_network.gexf")

#Creating homogenous networkx ORG < PAPER > VENUE network for Gephi vizualisation:
#org_venueNet = Hetero_dataset[Hetero_dataset.relation == "ORG-(P)-VENUE"]
#org_venueNetG = nx.Graph()
#org_venueNetG.add_nodes_from(org_nodes.index)
#org_venueNetG.add_nodes_from(venue_nodes.index)
#org_venueNetG.nodes()
#org_venueNetG.add_edges_from([(source,target,{"weight": weight}) for source, target, relation, weight in org_venueNet.values])
#nx.write_gexf(org_venueNetG, "org_venue_network.gexf")



