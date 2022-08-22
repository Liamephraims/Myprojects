#Copyright © 2020 Liamephraims
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 14:34:07 2020
Link Prediction  (Conversion of dataframe to Stellargraph and basic link prediction using
                   Metapath2Vec & Logistic Regression Classifer) based on Stellargraph link prediction tutorial/documentation
                   of static graph data - not utilising year temporal data so far - in future this will be extended
                   to a dynamic graph training on 4 years and testing on the subsequent 2 years,
                   with the most recent calender year being the development set for real-time recommendations.
                   
                   *REF: STELLARGRAPH TUT & PAPER.*
                   *REF:Hyperparameter tuning of Light GBM model - https://www.kaggle.com/mlisovyi/lightgbm-hyperparameter-optimisation-lb-0-761*
@author: Liam Ephraims
"""
import sys
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from math import isclose
from sklearn.decomposition import PCA
import os
import networkx as nx
import numpy as np
import pandas as pd
from stellargraph import StellarGraph, datasets
from stellargraph.data import EdgeSplitter
from collections import Counter
import multiprocessing
from IPython.display import display, HTML
from sklearn.model_selection import train_test_split

#Getting primary author names:
primary_authors = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
primary_authors_set = set(primary_authors.Name)

#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/5-Link Prediction(Recommendations)/1-Preparing multitype nodes and edge dataset/Hetergenous_dataset_final.pickle",'rb')
unpickler = pickle.Unpickler(file)
Hetero_dataset = unpickler.load()


#Loading in cleaned and topic-modelled researcher dataset by paper per researcher:
file = open("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/Final_dataset.pickle",'rb')
#Final_dataset = pickle.load(file)
unpickler = pickle.Unpickler(file)
Author_dataset = unpickler.load()


#Creating different node types:
org_nodes = pd.DataFrame(index=[org for org in set(Author_dataset["organization"]) if org != "NA" and org!='palliative medicine'])
#bug in extracted dataset - org!='palliative medicine' - duplicated venue in org - needs manually cleaning to be filtered out for stellargraph dataset creation.

author_nodes = [author for author in set(Author_dataset["name"]) if author != "NA"]
author_nodes = set(author_nodes)
for coauthors in set(Author_dataset["coauthors"]):
    coauthors = coauthors.split(" ")
    for coauthor in coauthors:
        if not coauthor in author_nodes:
            author_nodes.add(coauthor)
author_nodes = pd.DataFrame(index=author_nodes)
            

        
venue_nodes = pd.DataFrame(index=[jconf for jconf in set(Author_dataset["jconf"]) if jconf != "NA"])

topic_csv = pd.read_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/4-Topic Representation/1-Secondary Author Pruning & Topic Modelling/final_dataset_TPC_Modelled_Summary.csv")

topic_set = set()
for topic_list in Author_dataset["TOPICS"]:
    for topic, prop in topic_list:
        topic_set.add("T{}".format(str(int(topic) + 1)))
topic_nodes =  pd.DataFrame(index=topic_set)

#adding in missing topic nodes - need to fix this bug at some point!- some topics are being pruned out.


import re
try:
    #Creating the multi-node and edge Stellargraph (hetergenous graph):
    author_hetero_weighted = StellarGraph(
    {"author": author_nodes,"venue": venue_nodes, "org": org_nodes, "topic":topic_nodes},
    Hetero_dataset,
    edge_type_column="relation",
)
    
except:
    the_type, the_value, the_traceback = sys.exc_info()
    #Checking to see if this is the topic node bug - this will automatically pick up if so and add in neccessary topic nodes.
    if str(the_type) == "<class 'ValueError'>" and str(the_value).split(":")[1] ==  ' expected all source and target node IDs to be contained in `nodes`, found some missing':
        the_value = str(the_value)
        missing_topics = re.findall("T\d+",the_value)
        for topic in missing_topics:
            topic_set.add(topic)
            topic_nodes =  pd.DataFrame(index=topic_set)
            #Creating the multi-node and edge Stellargraph (hetergenous graph):
        author_hetero_weighted = StellarGraph(
                    {"author": author_nodes,"venue": venue_nodes, "org": org_nodes, "topic":topic_nodes},
                    Hetero_dataset,
                    edge_type_column="relation",
                    )   



print(author_hetero_weighted.info())
    


#We have to carefully split the data to avoid data leakage and evaluate the algorithms correctly:

#For computing node embeddings, a Train Graph (graph_train)

#For training classifiers, a classifier Training Set (examples_train) of positive and negative edges that weren’t used for computing node embeddings

#For choosing the best classifier, an Model Selection Test Set (examples_model_selection) of positive and negative edges that weren’t used for computing node embeddings or training the classifier

#For the final evaluation, a Test Graph (graph_test) to compute test node embeddings with more edges than the Train Graph, and a Test Set (examples_test) of positive and negative edges not used for neither computing the test node embeddings or for classifier training or model selection


#We begin with the full graph and use the EdgeSplitter class to produce Test Graph & Train Graph


#Splitting edges for testing data or the testing graph: --- TEST

#Test Graph - Test set of positive/negative link examples

#The Test Graph is the reduced graph we obtain from removing the test set of links from the full graph.
# Define an edge splitter on the original graph:
    
edge_splitter_test = EdgeSplitter(author_hetero_weighted)

# Randomly sample a fraction p=0.1 of all positive links, and same number of negative links, from graph, and obtain the
# reduced graph graph_test with the sampled paper links (indicating collaborations) removed:
    #Test Graph
    #examples_test: Test set of positive/negative link examples
graph_test, examples_test, labels_test = edge_splitter_test.train_test_split(
    p=0.08, method="global", edge_label="AUTHOR-(P)-AUTHOR"
)

print(graph_test.info())

#Train Graph  --  TRAIN
#This time, we use the EdgeSplitter on the Test Graph, and perform a train/test split on the examples to produce:
  #1. Training graph (train graph)
  #2. examples: Training set of link examples
  #3. labels: Set of link examples for model selection


#Splitting edges for testing data or the testing graph:
edge_splitter_train = EdgeSplitter(graph_test, author_hetero_weighted)
graph_train, examples, labels = edge_splitter_train.train_test_split(
    p=0.08, method="global", edge_label="AUTHOR-(P)-AUTHOR"
)

(
    examples_train,
    examples_model_selection,
    labels_train,
    labels_model_selection,
) = train_test_split(examples, labels, train_size=0.75, test_size=0.25)

print(graph_train.info())


# Do the same process to compute a training subset from within the test graph
edge_splitter_train = EdgeSplitter(graph_test, author_hetero_weighted)
graph_train, examples, labels = edge_splitter_train.train_test_split(
    p=0.08, method="global", edge_label="AUTHOR-(P)-AUTHOR"
)
(
    examples_train,
    examples_model_selection,
    labels_train,
    labels_model_selection,
) = train_test_split(examples, labels, train_size=0.75, test_size=0.25)

print(graph_train.info())


#Summary of training and testing sets created:
pd.DataFrame([
        (
            "Training Set",
            len(examples_train),
            "Train Graph",
            "Test Graph",
            "Train the Link Classifier",
        ),
        (
            "Model Selection",
            len(examples_model_selection),
            "Train Graph",
            "Test Graph",
            "Select the best Link Classifier model",
        ),
        (
            "Test set",
            len(examples_test),
            "Test Graph",
            "Full Graph",
            "Evaluate the best Link Classifier",
        ),
    ],
    columns=("Split", "Number of Examples", "Hidden from", "Picked from", "Use"),
).set_index("Split")
    
    
#Defining parameters for metapath2vec embeddings & defining metapaths:  
dimensions = 150
num_walks = 5
walk_length = 120
context_window_size = 15
num_iter = 3
workers = multiprocessing.cpu_count()

#Note: These need to be different node types - e.g. random walk embeddings from moving from one author (default) to
#another author. Possibly need to consider turning organisation, venue and topic into entities nodes?

user_metapaths = [
    #Adding in metapaths for each node-type pathway:
    ["author","org","author"], #co-organisation
    ["author","author"], #co-authorship 
    ["author","topic","author"], #co-topic
    ["author","venue","author"], #co-venue
    ["author","org","venue","topic","venue","org","author"], #global topic meta-path
    ["org","author","author","org"],  #  organisation/author co-author interactions
    ["venue","author","author","venue"] #  organisation/author topic interactions
]

#Training the graph:
from stellargraph.data import UniformRandomMetaPathWalk
from gensim.models import Word2Vec


def metapath2vec_embedding(graph, name):
    rw = UniformRandomMetaPathWalk(graph)
    walks = rw.run(
        graph.nodes(), n=num_walks, length=walk_length, metapaths=user_metapaths
    )
    print(f"Number of random walks for '{name}': {len(walks)}")

    model = Word2Vec(
        walks,
        size=dimensions,
        window=context_window_size,
        min_count=0,
        sg=1,
        workers=workers,
        iter=num_iter,
    )

    def get_embedding(u):
        return model.wv[u]

    return get_embedding



embedding_train = metapath2vec_embedding(graph_train, "Train Graph")

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import lightgbm as lgbm
from sklearn.preprocessing import StandardScaler


# 1. link embeddings
def link_examples_to_features(link_examples, transform_node, binary_operator):
    return [
        binary_operator(transform_node(src), transform_node(dst))
        for src, dst in link_examples
    ]


# 2. training classifier
def train_link_prediction_model(
    link_examples, link_labels, get_embedding, binary_operator
):
    clf = link_prediction_classifier()
    link_features = link_examples_to_features(
        link_examples, get_embedding, binary_operator
    )
    clf.fit(link_features, link_labels)
    return clf


def link_prediction_classifier(max_iter=2000):
    lr_clf = LogisticRegressionCV(Cs=10, cv=10, scoring="roc_auc", max_iter=max_iter)
    return Pipeline(steps=[("sc", StandardScaler()), ("clf", lr_clf)])


# 3. and 4. evaluate classifier
def evaluate_link_prediction_model(
    clf, link_examples_test, link_labels_test, get_embedding, binary_operator
):
    link_features_test = link_examples_to_features(
        link_examples_test, get_embedding, binary_operator
    )
    score = evaluate_roc_auc(clf, link_features_test, link_labels_test)
    lr_fpr, lr_tpr, _ = create_roc_curve(clf, link_features_test, link_labels_test)
    return score,lr_fpr, lr_tpr


def evaluate_roc_auc(clf, link_features, link_labels):
    predicted = clf.predict_proba(link_features)

    # check which class corresponds to positive links
    positive_column = list(clf.classes_).index(1)
    return roc_auc_score(link_labels, predicted[:, positive_column])

def create_roc_curve(clf, link_features, link_labels):
    predicted = clf.predict_proba(link_features)
    # check which class corresponds to positive links
    positive_column = list(clf.classes_).index(1)
    return roc_curve(link_labels, predicted[:, positive_column])

def operator_L1(u, v):
    return np.abs(u - v)


def operator_L2(u, v):
    return (u - v) ** 2


def run_link_prediction(binary_operator):
    clf = train_link_prediction_model(
        examples_train, labels_train, embedding_train, binary_operator
    )
    score,lr_fpr, lr_tpr = evaluate_link_prediction_model(
        clf,
        examples_model_selection,
        labels_model_selection,
        embedding_train,
        binary_operator,
    )

    return {
        "lr_fpr":lr_fpr,
        "lr_tpr":lr_tpr,
        "classifier": clf,
        "binary_operator": binary_operator,
        "score": score,
    }

binary_operators = [operator_L1, operator_L2]

results = [run_link_prediction(op) for op in binary_operators]
best_result = max(results, key=lambda result: result["score"])

print(f"Best result from '{best_result['binary_operator'].__name__}'")

pd.DataFrame(
    [(result["binary_operator"].__name__, result["score"]) for result in results],
    columns=("name", "ROC AUC score"),
).set_index("name")



embedding_test = metapath2vec_embedding(graph_test, "Test Graph")

#REF: LightGBM  hyperparameter testing taken from LightGBM Kaggle Tutorial: *REF*
#Formatting for training and testing of a Gradient-boosted light model:
# Feature Scaling for light gradient boosted models:

sc = StandardScaler()
train_features_best = np.array(link_examples_to_features(examples_train, embedding_train, best_result['binary_operator']))
train_features_best = sc.fit_transform(train_features_best)

test_features_best = np.array(link_examples_to_features(examples_test, embedding_test, best_result['binary_operator']))
test_features_best = sc.fit_transform(test_features_best)


def learning_rate_010_decay_power_0995(current_iter):
    base_learning_rate = 0.1
    lr = base_learning_rate  * np.power(.995, current_iter)
    return lr if lr > 1e-3 else 1e-3

import lightgbm as lgb
fit_params={"early_stopping_rounds":30, 
            "eval_metric" : 'auc', 
            "eval_set" : [(test_features_best,labels_test)],
            'eval_names': ['valid'],
            #'callbacks': [lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_099)],
            'verbose': 100,
            'categorical_feature': 'auto'}

from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform
param_test ={'num_leaves': sp_randint(6, 50), 
             'min_child_samples': sp_randint(100, 500), 
             'min_child_weight': [1e-5, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4],
             'subsample': sp_uniform(loc=0.2, scale=0.8), 
             'colsample_bytree': sp_uniform(loc=0.4, scale=0.6),
             'reg_alpha': [0, 1e-1, 1, 2, 5, 7, 10, 50, 100],
             'reg_lambda': [0, 1e-1, 1, 5, 10, 20, 50, 100]}

#This parameter defines the number of HP points to be tested
n_HP_points_to_test = 100

from sklearn.model_selection import RandomizedSearchCV, GridSearchCV

#n_estimators is set to a "large value". The actual number of trees build will depend on early stopping and 5000 define only the absolute maximum
clf = lgb.LGBMClassifier(max_depth=-1, random_state=314, silent=True, metric='None', n_jobs=4, n_estimators=5000)
gs = RandomizedSearchCV(
    estimator=clf, param_distributions=param_test, 
    n_iter=n_HP_points_to_test,
    scoring='roc_auc',
    cv=3,
    refit=True,
    random_state=314,
    verbose=True)

gs.fit(train_features_best, labels_train, **fit_params)
print('Best score reached: {} with params: {} '.format(gs.best_score_, gs.best_params_))
clf_sw = lgb.LGBMClassifier(**clf.get_params())
#set optimal parameters
clf_sw.set_params(**gs.best_params_)

gs_sample_weight = GridSearchCV(estimator=clf_sw, 
                                param_grid={'scale_pos_weight':[1,2,6,12]},
                                scoring='roc_auc',
                                cv=5,
                                refit=True,
                                verbose=True)

gs_sample_weight.fit(train_features_best, labels_train, **fit_params)
print('Best score reached: {} with params: {} '.format(gs_sample_weight.best_score_, gs_sample_weight.best_params_))

    
#Configure from the HP optimisation
clf_final = lgb.LGBMClassifier(**gs.best_estimator_.get_params())
#Train the final model with learning rate decay
clf_final.fit(train_features_best, labels_train, **fit_params, callbacks=[lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_0995)])

#Predictions for light gradient boosted model for embeddings as L1 and L2 regularization:
y_pred_hyp=clf_final.predict_proba(test_features_best)
# check which class corresponds to positive links
positive_column = list(clf_final.classes_).index(1)
y_pred_hyp = y_pred_hyp[:, positive_column]

gbhyp_fpr, gbhyp_tpr, _ = roc_curve(labels_test, y_pred_hyp)
gbhyp_auc = roc_auc_score(labels_test, y_pred_hyp)


# generating a no skill prediction (majority class)
ns_probs = [0 for _ in range(len(labels_test))]
ns_fpr, ns_tpr, _ = roc_curve(labels_test, ns_probs)
ns_auc = roc_auc_score(labels_test, ns_probs)
#auc_curves = {"No Skill":[ns_fpr, ns_tpr], "Light Gradient Boosted-L1":[gbl1_fpr, gbl1_tpr],
#             "Light Gradient Boosted-mean":[gbmean_fpr, gbmean_tpr], "Light Gradient Boosted-L2":[gbl2_fpr, gbl2_tpr],
#             "Light Gradient Boosted-sum":[gbsum_fpr, gbsum_tpr]
#             }
lr_name = "Logistic Regression -" + " " + best_result['binary_operator'].__name__.split("_")[1] + " regularization"
gb_name = "Light Gradient Boosting Machine(LightGBM) -" + " " + best_result['binary_operator'].__name__.split("_")[1] + " regularization"
auc_curves = {"No Skill":[ns_fpr, ns_tpr], 
              gb_name:[gbhyp_fpr, gbhyp_tpr]                                           
             }


#Evaluating both models on test dataset for plotting RUC Curve:
test_scores = dict()
print("Beginning evaluation on test dataset for", best_result['binary_operator'].__name__)
score,lr_fpr, lr_tpr = evaluate_link_prediction_model(best_result["classifier"],
                                                examples_test,
                                                labels_test,
                                                embedding_test,
                                               best_result['binary_operator'])
auc_curves[lr_name] = [lr_fpr, lr_tpr]
test_scores[lr_name] = score
    

#Adding score of no-skill model and gradient boosted model:
test_scores["No Skill"] = ns_auc
test_scores[gb_name] = gbhyp_auc


for classifier in test_scores:
    print("{}: ROC AUC={}".format(classifier,test_scores[classifier]))




from matplotlib import pyplot
#Plotting ROC Curves for both logistic regression models and no-skill baseline:
pyplot.plot(auc_curves['No Skill'][0], auc_curves['No Skill'][1], 
            linestyle='--', label= 'No Skill')
pyplot.plot(auc_curves[lr_name][0], auc_curves[lr_name][1], marker='.', label=lr_name)
pyplot.plot(auc_curves[gb_name][0], auc_curves[gb_name][1], marker='.', label=gb_name)


#check this - 
# axis labels
pyplot.xlabel('False Positive Rate (1 - Specificity)')
pyplot.ylabel('True Positive Rate (Sensitivity)')
# show the legend
pyplot.legend()
# show the plot
pyplot.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E2-Link Prediction(Recommendations) Results/OUTPUT-ROC_Curve_Comparison",
               dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None, metadata=None)
pyplot.show()    


#Pulling out recommendations dataframe using best model :
max_score = 0
best_classifier = ''
for classifier in test_scores:
    if test_scores[classifier] > max_score:
        max_score = test_scores[classifier]
        best_classifier = classifier
if best_classifier == lr_name:
    # Calculate edge features for test data using best model:
    link_features = link_examples_to_features(
    examples_test, embedding_test, best_result["binary_operator"])
    predicted_link_labels = best_result["classifier"].predict(link_features)
    predicted_link_prob = best_result["classifier"].predict_proba(link_features)
    positive_column = list(best_result["classifier"].classes_).index(1)
    print("Using logistic regression model for link prediction/recommendations")
else:
    if best_classifier == gb_name:
         # Calculate edge features for test data using best model:
        link_features = link_examples_to_features(
        examples_test, embedding_test, best_result["binary_operator"])
        predicted_link_labels = clf_final.predict(link_features)
        predicted_link_prob = clf_final.predict_proba(link_features)
        positive_column = list(clf_final.classes_).index(1)
        print("Using Light Gradient Boosting Machine (LightGBM) model for link prediction/recommendations")
    
    
#labels_test: Labels for each node-pair
predicted_link_prob = predicted_link_prob[:, positive_column]
#examples_test: author-pair names (examples)

def recommendations_to_df(predicted_labels, pos_predicted_probabilities, true_label, author_pair_names):
    recommendation_list_of_lists = []
    if (len(predicted_labels) == len(author_pair_names) and len(pos_predicted_probabilities) == len(author_pair_names) 
                              and len(true_label) == len(author_pair_names) ):
        for index in range(len(author_pair_names)):
            if (author_pair_names[index][0] in primary_authors_set or author_pair_names[index][1] in primary_authors_set):
                recommendation_list = []
                recommendation_list.append(predicted_labels[index])
                recommendation_list.append(pos_predicted_probabilities[index])
                recommendation_list.append(true_label[index])
                recommendation_list.append(author_pair_names[index][0])
                recommendation_list.append(author_pair_names[index][1])
                recommendation_list_of_lists.append(recommendation_list)
        return recommendation_list_of_lists
    else:
        raise NameError('Vectors are not of equal length!')

recommendations_list = recommendations_to_df(predicted_link_labels, predicted_link_prob, labels_test,examples_test)
recommendations_df = pd.DataFrame(recommendations_list, columns = ["Predicted_Label", "Pos_Pred_Prob", "True_Link_label","Coauthor1", "Coauthor2"])   

#Saving Primary Organisation Recommendations dataset as pickle for later usage:    
pickling_on = open("Hetergenous_Recommendations.pickle","wb")
pickle.dump(recommendations_df, pickling_on)
pickling_on.close()      
    
#Creating PCA Visualisation as diagnostic output:

# Learn a projection from 128 dimensions to 2
pca = PCA(n_components=2)
X_transformed = pca.fit_transform(link_features)

# plot the 2-dimensional points
plt.figure(figsize=(16, 12))
plt.scatter(
    X_transformed[:, 0],
    X_transformed[:, 1],
    c=np.where(labels_test == 1, "b", "r"),
    alpha=0.5,
)
plt.savefig("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/Evaluation Results and Tables/E2-Link Prediction(Recommendations) Results/OUTPUT-PCA_NODES_EDGES_LINK_PRED", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None, metadata=None)



