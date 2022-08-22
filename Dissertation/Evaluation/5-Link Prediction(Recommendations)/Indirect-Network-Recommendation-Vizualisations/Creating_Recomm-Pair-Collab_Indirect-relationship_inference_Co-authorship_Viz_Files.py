#Copyright © 2020 Liamephraims
"""
Created on Wed Oct 21 13:26:03 2020

Creating Researcher Recommendation Collaboration Indirect-relationship inference pairs Co-authorship Vizualisation Files:

@author: Liam Ephraims
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
from math import isclose
import os

#Getting primary author names:
primary_authors = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
primary_authors = set(primary_authors.Name)

#Getting two recommendation author names:
pair_list = []
with open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/Indirect-Network-Recommendation-Vizualisations/Indirect-relationship-recommendation-pairs.txt", "r") as file:
    for line in file.readlines():
        print(line)
        pair_list.append(line[:-1])
    
for pair in pair_list:
    primary_authors_set = set()
    author1,author2 = pair.split("|")
    if author1 in primary_authors:
        primary_authors_set.add(author1)
    if author2 in primary_authors:
        primary_authors_set.add(author2)
    
   
    #Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
    file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/1-Preparing multitype nodes and edge dataset/Hetergenous_dataset_final.pickle",'rb')
    unpickler = pickle.Unpickler(file)
    Hetero_dataset = unpickler.load()
    Hetero_dataset = Hetero_dataset.loc[Hetero_dataset.weight > 1]
    Hetero_dataset = Hetero_dataset[Hetero_dataset.relation == 'AUTHOR-(P)-AUTHOR']
    
    
    #Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
    file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle",'rb')
    #Final_dataset = pickle.load(file)
    unpickler = pickle.Unpickler(file)
    Author_dataset = unpickler.load()
    #Creating different node types:
    
    #author_nodes = [author for author in set(Author_dataset["name"]) if author != "NA"]
    author_nodes = [author.replace(" ", "_") for author in set(Author_dataset["name"]) ]
    
    author_nodes = set(author_nodes)
    for coauthors in set(Author_dataset["coauthors"]):
        coauthors = coauthors.split(" ")
        for coauthor in coauthors:
            if not coauthor in author_nodes:
                author_nodes.add(coauthor)
    author_nodes = pd.DataFrame(index=author_nodes)
    
    
    import os
    directory = "C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/6-Network Vizualisation/2-Heterogeneous-Multiplex Vizualizations MuxVix File Creation"
    os.chdir(directory + "/muxViz_network_files")
    
    relations = {"Authors"}
    
    layer_dict = dict()
    cnt = 0
    for relation in relations:
        cnt += 1
        layer_dict[relation] = cnt
    
    with open("./muxViz-master/MultiGraph_Layers_{}-{}.txt".format(author1,author2), "w", encoding="utf-8") as file:
        file.write("layerID layerLabel\n")
        for layer in layer_dict.keys():
            row_str = "{} {}\n".format(layer_dict[layer], layer)
            print(row_str)
            file.write(row_str)
        file.close()
        
        
    #Loading in Link Prediction results for recommendations:
    file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/2-Implementation of Metapath embedding and Link Prediction/Hetergenous_Recommendations.pickle",'rb')
    unpickler = pickle.Unpickler(file)
    Recommendations_dts = unpickler.load()
    
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
    for pred_label, pred_prob, true_label, author_1, author_2 in Recommendations_dts.values:
        if ((author_1 == author1) and (author_2 == author2)) or ((author_2 == author1) and (author_1 == author2)):
            if (not tuple((author_1,author_2)) in coauthor_set) and (not tuple((author_2,author_1)) in coauthor_set):
                raw_cnt += 1
                #print(pred_prob)
                if pred_prob > 0.00:
                    prob_filtered_cnt += 1
                    if ((author_1 in primary_authors_set) or (author_2 in primary_authors_set)) and not ((author_1 in primary_authors_set) and (author_2 in primary_authors_set)):
                        secondary_recommendations += 1
                        primary_secondary_recommendations_list.append([pred_prob, author_1, author_2, "secondary"])
                    elif (author_1 in primary_authors_set) and (author_2 in primary_authors_set):
                            primary_recommendations += 1
                            primary_secondary_recommendations_list.append([pred_prob, author_1, author_2, "primary"])
    
        
    #Creating node density dictionaries to calculate standardised degree for each node- default 0 (no edges):
    author_density_dict = dict()    
        
        
    
    for author in author_nodes.index:
        author_density_dict[author] = 0
        
    
    for source, target, relation, weight in Hetero_dataset.values:
        if source.replace(" ", "_") in author_density_dict:
            author_density_dict[source.replace(" ", "_")] += 1
        if target.replace(" ", "_") in author_density_dict:
            author_density_dict[target.replace(" ", "_")] += 1
    
            
    author_node_length = len(author_nodes.index) 
    
    #Standardizing each node type degree, seperately by node type:
    for author in author_density_dict:
        author_density_dict[author] = author_density_dict[author]/(author_node_length-1)
            
            
    import numpy as np
    
    percentile = 99
    #Taking {percentile} as threshold cut-off value for network nodes and edges:
    author_density_threshold = np.percentile(list(author_density_dict.values()), percentile)
    
    max_weight = max(list(Hetero_dataset["weight"]))
    #Normalizing edge weights:
    Hetero_dataset["weight"] = Hetero_dataset["weight"]/max_weight
    average_edge_weight = np.mean(Hetero_dataset["weight"])
    edge_weight_threshold = np.percentile(list(Hetero_dataset["weight"]),percentile)
    max_weight_normalized = max(list(Hetero_dataset["weight"]))
    
    
    #Creating recomm set for checking authors:
    auth_recommended_dict = dict()
    auth_recommended_dict["primary"] = set()
    auth_recommended_dict["secondary"] = set()
    auth_recommended_dict["primary_pairs"] = set()
    auth_recommended_dict["secondary_pairs"] = set()
    
    
    for prob, author_1, author_2, rec_type in primary_secondary_recommendations_list:
        if ((author_1 == author1) and (author_2 == author2)) or ((author_2 == author1) and (author_1 == author2)):
            if rec_type == "primary":
                auth_recommended_dict["primary"].add(author1)
                auth_recommended_dict["primary"].add(author2)
                auth_recommended_dict["primary_pairs"].add(tuple((author1, author2)))
                
            elif rec_type == "secondary":
                auth_recommended_dict["secondary"].add(author1)
                auth_recommended_dict["secondary"].add(author2)
                auth_recommended_dict["secondary_pairs"].add(tuple((author1, author2)))
    
    Primary_author_dict = dict()
    Primary_edge_dict = dict()
    for source, target, relation, weight in Hetero_dataset.values:    
            if ((source in primary_authors_set ) or (target in primary_authors_set)):
                #Checking if author is a primary researcher or not:
                if source in primary_authors_set and not source in Primary_author_dict:
                    Primary_author_dict[source] = True
                elif not source in primary_authors_set and not source in Primary_author_dict:
                    Primary_author_dict[author] = False
                if target in primary_authors_set and not target in Primary_author_dict:
                    Primary_author_dict[target] = True
                elif not target in primary_authors_set and not target in Primary_author_dict:
                    Primary_author_dict[target] = False
                #Checking if a primary edge or not:    
                if not tuple((source, target)) in Primary_edge_dict and not tuple((target, source)) in Primary_edge_dict:
                    Primary_edge_dict[tuple((source, target))] = (True,weight,False)
                else:
                    print("EXCEPTION-4",(tuple((source, target)) in Primary_edge_dict or tuple((target, source)) in Primary_edge_dict ))
            elif ((not source in primary_authors_set) and (not target in primary_authors_set)):
                Primary_author_dict[source] = False
                Primary_author_dict[target] = False            
                if not tuple((source, target)) in Primary_edge_dict and not tuple((target, source)) in Primary_edge_dict:
                    Primary_edge_dict[tuple((source, target))] = (False,weight, False)    
            else:
                print("EXCEPTION5",source, target, relation, weight)
    for author_1,author_2 in auth_recommended_dict["primary_pairs"]:
        #Primary authors already put into dictionary, thereby can assume if not in Primary dict than is a secondary author.
        if not author_1 in Primary_author_dict:
            Primary_author_dict[author_1] = False
        if not author_2 in Primary_author_dict:
            Primary_author_dict[author_2] = False
        if not tuple((author_1,author_2)) in Primary_edge_dict and not tuple((author_2,author_1)) in Primary_edge_dict:
            Primary_edge_dict[tuple((author_1,author_2))] = (True, edge_weight_threshold, "primary_pairs")
            
    for author_1,author_2 in auth_recommended_dict["secondary_pairs"]: 
        #All authors in secondary pair are secondary authors.
        if not author_1 in Primary_author_dict:
            Primary_author_dict[author_1] = False
        if not author_2 in Primary_author_dict:
            Primary_author_dict[author_2] = False
        if not tuple((author_1,author_2)) in Primary_edge_dict and not tuple((author_2,author_1)) in Primary_edge_dict:
            Primary_edge_dict[tuple((author_1,author_2))] = (True, edge_weight_threshold, "secondary_pairs")
            
      
            
            
            
            
    
            
    index_count = 0
    index_dict = dict()    
    with open("./muxViz-master/MultiGraph_node_layout_{}-{}.txt".format(author1,author2), "w", encoding="utf-8") as file:
        file.write("nodeID nodeLabel\n")
        for author in Primary_author_dict:
                #if (Primary_author_dict[author] == True and author in primary_authors_set):
                   #   or (author in auth_recommended_dict["primary"]) or  (author in auth_recommended_dict["secondary"]):
                index_count += 1
                index_dict[author] = index_count
                row_str = "{} {}\n".format(index_dict[author], author)
                print(row_str)
                file.write(row_str)
        file.close()
    print(index_count)
    
    
    
    #Creating node colour and size file - NEW version only primary nodes and non-primary nodes above threshold for degree:
    cnt = 0
    recom_author_cnt = 0
    with open("./muxViz-master/MultiGraph_node_colour_size_{}-{}.txt".format(author1,author2), "w", encoding="utf-8") as file:
        file.write("nodeID layerID color size\n")
        for node in Primary_author_dict:
    
            if (node in primary_authors_set) and (not (node in auth_recommended_dict["secondary"])) and (not (node in auth_recommended_dict["primary"])):
                        row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "orange",author_density_dict[node]*5)
                       # print(row_str)
                        cnt += 1
                        file.write(row_str)  
            elif (node in primary_authors_set) and ((node in auth_recommended_dict["secondary"]) or ( node in auth_recommended_dict["primary"])):
                        print("Recommendation primary node:", node)
                        row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "red",author_density_dict[node]*5)
                        #print(row_str)
                        cnt += 1
                        file.write(row_str)  
            elif (not node in primary_authors_set) and ((node in auth_recommended_dict["secondary"]) or (node in auth_recommended_dict["primary"])):
                        print("Recommendation secondary node:", node)
                        row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "purple",(author_density_dict[node] + author_density_threshold)*5)
                        #print(row_str)
                        cnt += 1
                        file.write(row_str)  
            else:
                        row_str = "{} {} {} {}\n".format(index_dict[node], layer_dict["Authors"], "green",author_density_dict[node]*5)
                        #print(row_str)
                        cnt += 1
                        file.write(row_str) 
            
        file.close()
        
    
    
    #Creating edge size and colour file:
    #FORMAT: nodeID.from layerID.from nodeID.to layerID.to color size
    cnt = 0
    with open("./muxViz-master/MultiGraph_edge_colour_size_{}-{}.txt".format(author1,author2), "w", encoding="utf-8") as file:
        file.write("nodeID.from layerID.from nodeID.to layerID.to color size\n")
        for author_1, author_2 in Primary_edge_dict:
            primary_flag, weight, pair_bool = Primary_edge_dict[tuple((author_1, author_2))]
            #Giving emphasis in primary author edges in Vizualisation making edges different colours and of significantly higher weight:                
            #Looking for primary author edge instances:
            if  primary_flag == True: 
                if pair_bool == "primary_pairs":
                    #This is a primary recommendation pair edge between two primary authors (Blue):
                    layerID_from = layer_dict["Authors"]
                    layerID_to = layer_dict["Authors"]
                    row_str = "{} {} {} {} {} {}\n".format(index_dict[author_1],layerID_from,
                                                           index_dict[author_2], layerID_to,
                                                           "blue", weight)
                    file.write(row_str)   
                    cnt += 1
                    print("primary_pair edge")
                elif pair_bool == "secondary_pairs":
                    #This is a secondary recommendation pair edge with a primary author (Purple):
                    layerID_from = layer_dict["Authors"]
                    layerID_to = layer_dict["Authors"]
                    row_str = "{} {} {} {} {} {}\n".format(index_dict[author_1],layerID_from,
                                                           index_dict[author_2], layerID_to,
                                                           "red", weight)
                    file.write(row_str)   
                    cnt += 1
                    print("secondary_pair edge")
                else: #pair_bool == False NOT a recommendation edge, although IS a normal primary edge:
                    #This is a normal primary edge (ORANGE):
                    layerID_from = layer_dict["Authors"]
                    layerID_to = layer_dict["Authors"]
                    row_str = "{} {} {} {} {} {}\n".format(index_dict[author_1],layerID_from,
                                                           index_dict[author_2], layerID_to,
                                                           "orange", weight)
                    file.write(row_str)   
                    cnt += 1
                    
            elif  primary_flag == False: 
                cnt += 1 #Not a primary edge, thereby edge will take on default secondary colour set in MuxViz.
            else:
                print("EXCEPTION: Edge Colour & Size")
                
                
                
        file.close()
    print("{} edges".format(cnt))
    
    
    #[source node] [source layer][target node][target layer] [weight] 
    edge_cnt = 0
    file_name = "./muxViz-master/MultiGraph_Layer_edges_extended_{}-{}.edges".format(author1,author2)
    with open(file_name, "w", encoding="utf-8") as file:
        for author_1, author_2 in Primary_edge_dict:
            _, weight, _ = Primary_edge_dict[tuple((author_1, author_2))]
    
            layerID_from = layer_dict["Authors"]
            layerID_to = layer_dict["Authors"]
            #Giving emphasis to primary author edges by increasing weight of primary author edges by multiple of 4.   
            row_str = "{} {} {} {} {}\n".format(index_dict[author_1],layerID_from,
                                                       index_dict[author_2], layerID_to, weight)
            file.write(row_str)   
            edge_cnt += 1    
        file.close()    
    print(edge_cnt)
    
    print(edge_cnt, cnt)
    
    #Configuration file to be imported to Muxnet as assembly file.
    with open("./muxViz-master/MultiGraph_node_CONFIG_{}-{}.txt".format(author1,author2), "w", encoding="utf-8") as file:
        edge_file = "MultiGraph_Layer_edges_extended_{}-{}.edges".format(author1,author2)
        layer_file = "MultiGraph_Layers_{}-{}.txt".format(author1,author2)
        node_layout = "MultiGraph_node_layout_{}-{}.txt".format(author1,author2)
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

























