#Copyright © 2020 Liamephraims


import os
import re
import nltk 
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import multiprocessing as mp
import pandas as pd
#NOTE: Need to install ged4py with - C:\WINDOWS\system32>pip install git+https://github.com/Jacobe2169/ged4py.git#egg=ged4py
#To install latest version and fixes directly from Github.
from ged4py.algorithm import graph_edit_dist
from statistics import mean
import os.path
#################################################<START>Dataset extraction and network construction!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import networkx as nx
print(nx.__version__)



#Must be using networkx < VERSION 2:
#!pip uninstall networkx -y

#!pip install networkx==1.11

from jieba import analyse

def check_ref_count():
        ref_counts = open('PRIMARY_AUTHORS_XML/author_total_ref.txt','r')
        ref_counts_dict = {}
        for line in ref_counts.readlines():
            #Getting document of titles and abstracts divided by <>
            if "<>" in line:
                arr=line.split("<>")
                #print(line)
                #print(arr)
                count = arr[1].strip().split(" \n")[0]
                #print(count)
                if len(arr)>1 and arr[1].strip() != "NA":
                    ref_counts_dict[arr[0].strip()]=int(count)
                    #print("arr length > 1", ref_counts_dict[arr[0].strip()])
                    #print("Key", arr[0])
                else:
                    ref_counts_dict[arr[0].strip()]=0
        return ref_counts_dict             
                    
def check_main_count():
        main_counts = open('PRIMARY_AUTHORS_XML/author_total_main.txt','r')
        main_counts_dict = {}
        for line in main_counts.readlines():
            #Getting document of titles and abstracts divided by <>
            if "<>" in line:
                arr=line.split("<>")
                #print(line)
                #print(arr)
                count = arr[1].strip().split(" \n")[0]
                #print(count)
                if len(arr)>1 and arr[1].strip() != "NA":
                    main_counts_dict[arr[0].strip()]= int(count)
                   # print("arr length > 1", main_counts_dict[arr[0].strip()])
                    #print("Key", arr[0])
                else:
                    main_counts_dict[arr[0].strip()]=0
        return main_counts_dict

def disambiguated_author_XMLconvertion(filename,file_path, x,ego,predict_label_dict_fin, final_cluster_index):
    #Now saving cluster index papers for primary author to XML file:
    xmlFileName = file_path + "disambiguated_main/" + str(x)
    with open(filename, "r",encoding='utf-8') as filetoread, open(xmlFileName, 'w',encoding='utf-8') as xmlFile:
    # 这里是一行一行读取的文件
        print("Author ego is", ego, "extracting disambiguated author papers to XML:") 
        disambiguated_author_profile = []                   
        xmlFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xmlFile.write('<author_set>\n')
        paper_index = 0
        n_extraction = 0
        title_doi_list = []
        doi_list = []
        title_list = []
        for line in filetoread:
            line = line.strip()
            #print("Stripped line",line)
            if "<publication>" in line:
                #INCREMENT PAPER COUNTER - index
                pub_start_XML = line
                #print(pub_start_XML)
                paper_index += 1
                #print("paper_index incremented from", paper_index-1,"to",paper_index)
                if paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                    xmlFile.write(pub_start_XML + "\n")
                    n_extraction += 1
            elif "</publication>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                pub_end_XML=line
                titlex = title_XML[title_XML.find('>')+1: title_XML.rfind('<')].strip()
                orgx = organization_XML[organization_XML.find('>')+1: organization_XML.rfind('<')].strip()
                jconfx = jconf_XML[jconf_XML.find('>')+1: jconf_XML.rfind('<')].strip()
                authorsx = authors_XML[authors_XML.find('>')+1: authors_XML.rfind('<')].strip()
                yearx = year_XML[year_XML.find('>')+1: year_XML.rfind('<')].strip()
                DOIx = DOI[DOI.find('>')+1: DOI.rfind('<')].strip()
                #print(DOIx, len(DOIx))
                #print(titlex,len(titlex))
                title_list.append(titlex)
                doi_list.append(DOIx)
                #print("title_doi_instance",title_doi_instance)
                #print(title_doi_list)
                disambiguated_author_profile.append([authorsx,titlex,yearx,orgx,jconfx,DOIx])
                xmlFile.write(pub_end_XML  + "\n")
            elif "<title>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                title_XML = line
                xmlFile.write(title_XML  + "\n")
            elif "<abstract>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                abstract_XML = line
                xmlFile.write(abstract_XML  +  "\n")
                #Note: need to add abstracts to ambiguious author XMLs?
            elif "<organization>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                organization_XML = line
                xmlFile.write(organization_XML  + "\n")
                #print(organization_XML)
            elif "<jconf>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                jconf_XML = line
                #print(jconf_XML)
                xmlFile.write(jconf_XML  + "\n")
            elif "<label>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                label_XML = line
                xmlFile.write(label_XML  + "\n")
                #print(label_XML)
            elif "<pub_count>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                pub_count_XML = line
                xmlFile.write(pub_count_XML  + "\n")
                #print(pub_count_XML)
                
            elif "<authors>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                authors_XML = line
                xmlFile.write(authors_XML  + "\n")
                #print(authors_XML)
            elif "<year>" in line and paper_index -1 in predict_label_dict_fin[final_cluster_index]:
                year_XML = line
                xmlFile.write(year_XML  + "\n")
                #print(year_XML)
            elif "<total_cnt>" in line:
                total_XML = line
                xmlFile.write(total_XML  + "\n")
            elif "<DOI>" in line:
                DOI = line
                xmlFile.write(DOI  + "\n")
            elif "<FullName>" in line:
                fullname_XML = line
                xmlFile.write(fullname_XML  + "\n")
                print("!!!!!EGO TAG IS",fullname_XML,"ego from Rdata XML file is", ego )                     
        #write the footer
        #Checking if primary author has an ORCID paper set file to write into Disambiguation XML as non-duplicate validated papers:
        title_set = set(title_list)
        doi_set = set(doi_list)
        ego = ego.replace(",",".")
        filepath_ORCID = "{}ORCID/{}_PRIMARY_ORCID.xml".format(file_path,ego)
        print("!NEW FILEPATH IS", filepath_ORCID)
        if os.path.isfile(filepath_ORCID):
            with open(filepath_ORCID, "r",encoding='utf-8') as filetoreadORCID:
                title_doi_instance = []
                for line in filetoreadORCID:
                    print(line)
                    line = line.strip()
                    #print("Stripped line",line)
                    if "<publication>" in line:
                        #INCREMENT PAPER COUNTER - index
                        pub_start_XML = line
                        #print(pub_start_XML)
                        #print("paper_index incremented from", paper_index-1,"to",paper_index)
                        xmlFile.write(pub_start_XML + "\n")                        
                    elif "</publication>" in line:
                        pub_end_XML=line
                        titlex = title_XML[title_XML.find('>')+1: title_XML.rfind('<')].strip()
                        orgx = organization_XML[organization_XML.find('>')+1: organization_XML.rfind('<')].strip()
                        jconfx = jconf_XML[jconf_XML.find('>')+1: jconf_XML.rfind('<')].strip()
                        authorsx = authors_XML[authors_XML.find('>')+1: authors_XML.rfind('<')].strip()
                        yearx = year_XML[year_XML.find('>')+1: year_XML.rfind('<')].strip()
                        DOIx = DOI[DOI.find('>')+1: DOI.rfind('<')].strip()
                        if (not DOIx in doi_set) and (not titlex in title_set):
                            print("ORCID PAPER", DOIx, "is not in main papers will add to",ego,"disambiguated paper set")
                            n_extraction += 1
                            paper_index += 1
                            disambiguated_author_profile.append([authorsx,titlex,yearx,orgx,jconfx,DOIx])
                            xmlFile.write(pub_end_XML  + "\n")
                        else:
                            print("ORCID PAPER", DOIx, "IS in main papers will NOT add to",ego,"disambiguated paper set")
                    elif "<title>" in line:
                        title_XML = line
                        xmlFile.write(title_XML  + "\n")
                    elif "<abstract>" in line:
                        abstract_XML = line
                        xmlFile.write(abstract_XML  +  "\n")
                        #Note: need to add abstracts to ambiguious author XMLs?
                    elif "<organization>" in line:
                        organization_XML = line
                        xmlFile.write(organization_XML  + "\n")
                        #print(organization_XML)
                    elif "<jconf>" in line:
                        jconf_XML = line
                        #print(jconf_XML)
                        xmlFile.write(jconf_XML  + "\n")
                    elif "<label>" in line:
                        label_XML = line
                        xmlFile.write(label_XML  + "\n")
                        #print(label_XML)
                    elif "<pub_count>" in line:
                        pub_count_XML = line
                        xmlFile.write(pub_count_XML  + "\n")
                        #print(pub_count_XML)
                
                    elif "<authors>" in line:
                        authors_XML = line
                        xmlFile.write(authors_XML  + "\n")
                        #print(authors_XML)
                    elif "<year>" in line:
                        year_XML = line
                        xmlFile.write(year_XML  + "\n")
                        #print(year_XML)
                    elif "<total_cnt>" in line:
                        total_XML = line
                        xmlFile.write(total_XML  + "\n")
                    elif "<DOI>" in line:
                        DOI = line
                        xmlFile.write(DOI  + "\n")
        #Addition of missing validated ORCID papers to researcher disambiguated papers finished.
        xmlFile.write('</author_set>/n')
        
        
        print("finished conversion of disambiguated author cluster and addition of valdiated missing ORCID papers to XML")
        print("Publications converted is",n_extraction, "compared with", len(predict_label_dict_fin[final_cluster_index]), "papers in final cluster", 
               "and a final cluster of:", predict_label_dict_fin[final_cluster_index])   
        print("FINISHED XML CONVERSION OF DISAMBIGUATED AUTHOR", ego)
    disambiguated_author_profile = pd.DataFrame(disambiguated_author_profile, columns = ["Coauthors","Title", "Year","Organisation","Venue","DOI"])   
    return n_extraction, disambiguated_author_profile
def default_XMLconvertion(file_path,x,ref_path,author_type,ego):
    #Now saving cluster index papers for primary author to XML file:
    xmlFileName = file_path + "disambiguated_main/" + str(x)
    filename_ref_default = ref_path  + str(x)
    filename_ref_default = filename_ref_default.split("_" + author_type + "_MAIN.xml")[0] + '_' + author_type + '_REF.xml'
     
    with open(filename_ref_default, "r",encoding='utf-8') as filetoread, open(xmlFileName, 'w',encoding='utf-8') as xmlFile:
        # 这里是一行一行读取的文件
        print("Author ego is", ego, "extracting default reference author papers to XML:")                    
        xmlFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xmlFile.write('<author_set>\n')
        paper_index = 0
        n_extraction = 0
        for line in filetoread:
            line = line.strip()
            #print("Stripped line",line)
            if "<publication>" in line:
                #INCREMENT PAPER COUNTER - index
                pub_start_XML = line
                #print(pub_start_XML)
                paper_index += 1
                #print("paper_index incremented from", paper_index,"to",paper_index+1)
                xmlFile.write(pub_start_XML + "\n")
                n_extraction += 1
            elif "</publication>" in line:
                pub_end_XML=line
                xmlFile.write(pub_end_XML  + "\n")
            elif "<title>" in line:
                title_XML = line
                xmlFile.write(title_XML  + "\n")
            elif "<abstract>" in line:
                abstract_XML = line
                xmlFile.write(abstract_XML  +  "\n")
            #Note: need to add abstracts to ambiguious author XMLs?
            elif "<organization>" in line:
                organization_XML = line
                xmlFile.write(organization_XML  + "\n")
                #print(organization_XML)
            elif "<jconf>" in line:
                jconf_XML = line
                #print(jconf_XML)
                xmlFile.write(jconf_XML  + "\n")
            elif "<label>" in line:
                label_XML = line
                xmlFile.write(label_XML  + "\n")
                #print(label_XML)
            elif "<pub_count>" in line:
                pub_count_XML = line
                xmlFile.write(pub_count_XML  + "\n")
                #print(pub_count_XML)
                
            elif "<authors>" in line:
                authors_XML = line
                xmlFile.write(authors_XML  + "\n")
                #print(authors_XML)
            elif "<year>" in line:
                year_XML = line
                xmlFile.write(year_XML  + "\n")
                #print(year_XML)
            elif "<total_cnt>" in line:
                total_XML = line
                xmlFile.write(total_XML  + "\n")
            elif "<DOI>" in line:
                DOI = line
                xmlFile.write(DOI  + "\n")
            elif "<FullName>" in line:
                fullname_XML = line
                xmlFile.write(fullname_XML  + "\n")
                print("!!!!!EGO TAG IS",fullname_XML,"ego from Rdata XML file is", ego )                     
                #write the footer
        xmlFile.write('</author_set>/n')
        print("finished conversion of default reference author cluster to XML")
        print("Publications converted is",n_extraction) 
        print("FINISHED XML CONVERSION OF DISAMBIGUATED AUTHOR", ego)
    return n_extraction



class DataSet():
    """
pipeline for representation learning for all papers for a given name reference
"""

    def __init__(self, file_path, predicted_cluster_dict=None, cluster_index=None):
        if cluster_index != None:
            self.cluster_index=cluster_index
        else:
            self.cluster_index=False
        if predicted_cluster_dict != None:
            self.predicted_cluster_list = predicted_cluster_dict[cluster_index]
 #           print(self.predicted_cluster_list)
            for i in range(0,len(self.predicted_cluster_list)):
#                print(i)
                self.predicted_cluster_list[i] = self.predicted_cluster_list[i] + 1
  #          print("Cleaned",self.predicted_cluster_list)
            
                
                
        else:
            self.predicted_cluster_list = False    
        print("predicted_cluster_dict is",predicted_cluster_dict )
        print("cluster_index is",cluster_index )
        self.file_path = file_path 
        self.paper_authorlist_dict = {}
        self.paper_list = []
        self.coauthor_list = []
        self.paper_title=[]
        self.paper_jconf=[]
        self.paper_org = []
        self.paper_year = []
        self.paper_abstract = []
        self.paper_jconf_dict={}
        self.paper_title_dict = {}
        self.paper_org_dict = {}
        self.paper_year_dict = {}
        self.paper_abstract_dict = {}
        # 如果label相同，那么一定是同一个人
        self.label_list = []
        self.C_Graph = nx.Graph()
        self.D_Graph = nx.Graph()
        self.T_Graph = nx.Graph()
        self.Jconf_Graph = nx.Graph()
        self.Org_Graph = nx.Graph()
        self.Year_Graph = nx.Graph()
        self.Abstract_Graph = nx.Graph()
        # 整个图中总的边数
        self.num_nnz = 0
        
    
    def reader_arnetminer(self, title_abstract_dict_original=False):
        #if title_abstract_dict_original == False:
        file_title_abstract = open('PRIMARY_AUTHORS_XML/title_abstract_disseration_test.txt','r')
        #NOTE: A BUG IF encoding='utf-8'
        
        #print(file_title_abstract)
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
        #else:
         #   title_abstract_dict = title_abstract_dict_original
        #print(title_abstract_dict)
        paper_index = 0
       # print("FINAL TITLE_ABSTRACT_DICT", title_abstract_dict)

        #Counter for paper indexes?
        coauthor_set = set()
        #Opening author XML file: Has title, author names, affilation etc in XML <>
       
        with open(self.file_path, "r",encoding='utf-8') as filetoread:

            # 这里是一行一行读取的文件
            for line in filetoread:
                #print("!!!!!!!!!!!!!!!NEW LINE!!!!!!!!!!!!!!!")
                #print("original Line",line)
                line = line.strip()
                #print("new line",line)
                #print("Stripped line",line)
                if "FullName" in line:
                    
                    ego_name = line[line.find('>')+1:line.rfind('<')].strip()
                    print("Full line with FullName", line, sep="\n")
                    #print(line.find('>')+1, line.rfind('<'), sep="\n")
                    #print(line[line.find('>')+1:line.rfind('<')], sep="\n")
                    
                    
                #If it is a title header then firstly obtain abstract using title as key
                #for abstract dict and secondly prep title with lemmetization and stemming.
                elif ("<title>" in line and  self.predicted_cluster_list==False) or ("<title>" in line and paper_index in self.predicted_cluster_list):
                    #Taking title from XML  
                    text = line[line.find('>')+1: line.rfind('<')].strip()
                    #print(text)
                    # 从这里找出对应的摘要
                    abstract = ""
                    #!!!!!BUG IN ABSTRACT EXTRACTION!!!!
                    #Now moving to processing abstracts:
                    #print("Before", self.paper_abstract)
                    self.paper_abstract.append(paper_index)
                    #print("After", self.paper_abstract)
                    #print("HEREEEEEEEEEE",text)
                   #print(text in title_abstract_dict)
                    if text in title_abstract_dict:
                 #       print("if text in title_abstract_dict - true!!!!")
                        #if title is in the title_abstract dict as key
                        abstract = title_abstract_dict.get(text)
                        
                        
                        #then collect the abstract
                    if abstract=="":
                        abstract = text
                    #print( "hereeeeeeeeeeeeeee",abstract)
                    abstract = re.sub("[:()'.,?`]", "",abstract)
                    abstract_list = []
                    #print(abstract)
                    #print(abstract.split())
                    #Abstract processed either as "" empty string or as abstract if title_abstract_dict[text] not empty
                    if (len(abstract.split())>25):
                        #Taking the top five words from abstract with largest Term Frequency-Inverse Document Frequency
                        # main idea of TF-IDF is: if a word appears frequently in a document, that is, TF is high, and it rarely appears in other documents in the corpus, 
                        #that is, the low of DF, that is, if the IDF is high, the term is considered to have good classification capabilities.
                        abstract_list = analyse.extract_tags(abstract,topK=25)
                        #print(abstract_list)
                        #creating keyword tags for clustering
                    else:
                        #Otherwise, there is less than 25 words and we take them all.
                        abstract_list = abstract.split()
                    
                    self.paper_abstract_dict[paper_index] = []                    
                    #Resetting for next iteration
                    for w in abstract_list:
                        #print("Considering w from abstract list")
                        #print(w)
                        #print(abstract_list)
                        #print(w not in stopwords.words("english"))
                        try:
                            if w not in stopwords.words("english"):
                                #print("Entered if")
                                #Making sure word w IS NOT a stopword as we do not want these.
                                #Stop words are those words in natural language that have a very little meaning, such as "is", "an", "the", etc. 
                                #Search engines and other enterprise indexing platforms often filter the stop words while fetching results from the database against
                                #the user queries. - e.g. An, the, has it, etc
                                #Stop words are often removed from the text before training deep learning and machine learning models since stop words occur in abundance, hence providing little to no unique information that can be used for classification or clustering.
                                # 将每个单词转换为原型
                                #initalizing
                                #print(w)
                                lemmatizer = WordNetLemmatizer()
                                #Lemmatization is the process of grouping together the different inflected forms of a word so they can be analysed as a single item. 
                                #Lemmatization is similar to stemming but it brings context to the words. So it links words with similar meaning to one word.
                                #Examples of lemmatization:
                                #-> rocks : rock
                                #-> corpora : corpus
                                #-> better : good
                                yx = lemmatizer.lemmatize(w.lower())
                                #print("yx",yx)
                                self.paper_abstract_dict[paper_index].append(yx)
                                
                        except:
                            #print("Entered except")
                            continue
                    #Lemmetized abstract of k =<=25 words 
                   #print(self.paper_abstract_dict[paper_index],paper_index)
#                   Substiute
                    text = re.sub("[:()'.,?`]", "",text)
                    disease_List = text.split()
                    
                    #TITLES
                    #Now moving to processing titles
                    self.paper_title.append(paper_index)
                    self.paper_title_dict[paper_index]=[]
                    for w in disease_List:
                        try:
                            if w not in stopwords.words("english"):
                                #NOT a stopword as we do not want as,in,the etc
                                #Stop words are those words in natural language that have a very little meaning, such as "is", "an", "the", etc. 
                                #Search engines and other enterprise indexing platforms often filter the stop words while fetching results from the database against the user queries.
                                #Stop words are often removed from the text before training deep learning and machine learning models since stop words occur in abundance, hence providing little to no unique information that can be used for classification or clustering.
                                # 将每个单词转换为原型
                                lemmatizer = WordNetLemmatizer()
                                #Lemmatization is the process of grouping together the different inflected forms of a word so they can be analysed 
                                #as a single item. Lemmatization is similar to stemming but it brings 
                                #context to the words. So it links words with similar meaning to one word.
                                yx = lemmatizer.lemmatize(w.lower())
                                self.paper_title_dict[paper_index].append(yx)
                        except:
                            continue
                    #print(self.paper_title_dict[paper_index])
                elif ("<jconf>" in line and self.predicted_cluster_list==False) or ("<jconf>" in line and paper_index in self.predicted_cluster_list):
                    #print("Beginnning processing of conferences")
                    text = line[line.find('>') + 1: line.rfind('<')].strip()
                    text = re.sub("[:()'.,?`]", "", text)
                    disease_List = text.split()
                    self.paper_jconf.append(paper_index)
                    self.paper_jconf_dict[paper_index] = []
                    for w in disease_List:
                        if w not in stopwords.words("english"):
                            self.paper_jconf_dict[paper_index].append(w)
                        try:
                            if w not in stopwords.words("english"):
                                # 将每个单词转换为原型
                                lemmatizer = WordNetLemmatizer()
                                yx = lemmatizer.lemmatize(w.lower())
                                self.paper_jconf_dict[paper_index].append(yx)
                        except:
                            continue

# IF PUBLICATION XML HEADER THEN SIGNIFIES NEW PUBLICATION:
                elif "<publication>" in line:
                    #INCREMENT COUNTER
                    paper_index += 1
                  #  print("paper_index incremented from", paper_index-1,"to",paper_index)

 #                   # 加入第几篇文章
                    if self.predicted_cluster_list==False:
                        self.paper_list.append(paper_index) #List of papers indexs
                    elif self.predicted_cluster_list!=False and paper_index in self.predicted_cluster_list:
                        self.paper_list.append(paper_index) #List of papers indexs
                        
# BEGINNING YEAR PROCESSING:
                elif ("<year>" in line and self.predicted_cluster_list==False) or ("<year>" in line and paper_index in self.predicted_cluster_list):
                    self.paper_year.append(paper_index)
                    self.paper_year_dict[paper_index] = []
                    text = line[line.find('>') + 1: line.rfind('<')].strip()
                    if text != "null":
                        self.paper_year_dict[paper_index].append(text)
# BEGINNING organization PROCESSING: 
                elif ("<organization>" in line and self.predicted_cluster_list==False) or ("<organization>" in line and paper_index in self.predicted_cluster_list):
                    text = line[line.find('>') + 1: line.rfind('<')].strip()
                    text = re.sub("[:()'.,?`]", "", text)
                    disease_List = text.split()
                    self.paper_org.append(paper_index)
                    self.paper_org_dict[paper_index] = []
                    for w in disease_List:
                        try:
                            if w not in stopwords.words("english"):
                                # 将每个单词转换为原型
                                lemmatizer = WordNetLemmatizer()
                                yx = lemmatizer.lemmatize(w.lower())
                                self.paper_org_dict[paper_index].append(yx)
                        except:
                            continue
                elif ("<authors>" in line and self.predicted_cluster_list==False) or ("<authors>" in line and paper_index in self.predicted_cluster_list):
#                    # 加入的是所有的作者
                    author_list = line[line.find('>')+1: line.rfind('<')].strip().split(' ')
                    if len(author_list) > 1:
                        if ego_name in author_list:
#                            # 这里删除了文章的作者
                            author_list.remove(ego_name)
#                           #Show the list of collaborators in the first article
                            self.paper_authorlist_dict[paper_index] = author_list
                        else:
                            self.paper_authorlist_dict[paper_index] = author_list
#
                        for co_author in author_list:
                            coauthor_set.add(co_author)
                       # print("author_list",author_list)
#                        # Build a collaborator graph, only for the author collection of each article
                        for pos in range(0, len(author_list) - 1):
                            for inpos in range(pos+1, len(author_list)):
                            #    print("pos", pos, "inpos", inpos)
#                                # The result is a one-way partnership
                                
                                src_node = author_list[pos]
                           #     print(src_node, "src_node")
                                dest_node = author_list[inpos]
                          #      print("dest_node", dest_node)
                                #Returns True if the edge (u, v) is in the graph.
                               # print(self.C_Graph.has_edge(src_node, dest_node))
                                if not self.C_Graph.has_edge(src_node, dest_node):
                                    #If edge not yet made create edge with weight equal to 1
                                    self.C_Graph.add_edge(src_node, dest_node, weight = 1)
                                else:
                                    #Already an edge between authors - add 1 to weight of collabs between two authors
                                    edge_weight = self.C_Graph[src_node][dest_node]['weight']
#                                    # The more collaborations, the greater the weight of joining
                                    edge_weight += 1
                                    self.C_Graph[src_node][dest_node]['weight'] = edge_weight
                    else:
                        self.paper_authorlist_dict[paper_index] = []
                elif ("<label>" in line and self.predicted_cluster_list==False) or ("<label>" in line and paper_index in self.predicted_cluster_list):
                    label = int(line[line.find('>')+1: line.rfind('<')].strip())
                    self.label_list.append(label)
                    #print(label) - <label>29</label> captures integer label for pub.

        self.coauthor_list = list(coauthor_set)
        print("Paper list indexs are:", self.paper_list)
        """
        compute the 2-extension coauthorship for each paper
        generate doc-doc network
        edge weight is based on 2-coauthorship relation
        edge weight details are in paper definition 3.3
        """
        paper_2hop_dict = {}
      #  print(self.paper_list)
      #  print(self.paper_authorlist_dict)
        for paper_idx in self.paper_list:
            temp = set()
            if self.paper_authorlist_dict[paper_idx] != []:
                for first_hop in self.paper_authorlist_dict[paper_idx]:
                    temp.add(first_hop)
                    if self.C_Graph.has_node(first_hop):
                        for snd_hop in self.C_Graph.neighbors(first_hop):
                            temp.add(snd_hop)
            paper_2hop_dict[paper_idx] = temp
        for i in self.paper_title:
            for j in self.paper_title:
                if i != j:
                    title_set1 = self.paper_title_dict[i]
                    title_set2 = self.paper_title_dict[j]
                    title_edge_weight = len((set(title_set1)).intersection(set(title_set2)))
                    #print(title_edge_weight,"weight")
                    if title_edge_weight != 0:
                        self.T_Graph.add_edge(i,j,weight=title_edge_weight)

        for i in self.paper_jconf:
            for j in self.paper_jconf:
                if i != j:
                    jconf1 = self.paper_title_dict[i]
                    jconf2 = self.paper_title_dict[j]
                    jconf_edge_weight = len((set(jconf1)).intersection(set(jconf2)))
                    #print(title_edge_weight,"weight")
                    if jconf_edge_weight != 0:
                        self.Jconf_Graph.add_edge(i,j,weight=jconf_edge_weight)
        for i in self.paper_org:
            for j in self.paper_org:
                if i != j:
                    org1 = self.paper_org_dict[i]
                    org2 = self.paper_org_dict[j]
                    org_edge_weight = len((set(org1)).intersection(set(org2)))
                    #print(title_edge_weight,"weight")
                    if org_edge_weight != 0:
                        self.Org_Graph.add_edge(i,j,weight=org_edge_weight)
        for i in self.paper_year:
            for j in self.paper_year:
                if i != j:
                    year1 = self.paper_year_dict[i]
                    year2 = self.paper_year_dict[j]
                    year_edge_weight = 0
                    #co-authored in less than 20 years requirement
                    if not year1[0] == 'NA' and not year2[0] == 'NA':
                        if abs(int(year1[0])-int(year2[0]))<20:
                            year_edge_weight = 1
                        else:
                            year_edge_weight = 0
                            
                    #print(title_edge_weight,"weight")
                    if year_edge_weight != 0:
                        self.Year_Graph.add_edge(i,j,weight=year_edge_weight)

        for i in self.paper_abstract:
            for j in self.paper_abstract:
                if i != j:
                    abstract1 = self.paper_abstract_dict[i]
                    abstract2 = self.paper_abstract_dict[j]
                    abstract_edge_weight = len((set(abstract1)).intersection(set(abstract2)))
                    #print(title_edge_weight,"weight")
                    if abstract_edge_weight != 0:
                        self.Abstract_Graph.add_edge(i, j, weight=abstract_edge_weight)

        for idx1 in range(0, len(self.paper_list) - 1):
            for idx2 in range(idx1 + 1, len(self.paper_list)):
                temp_set1 = paper_2hop_dict[self.paper_list[idx1]]
                temp_set2 = paper_2hop_dict[self.paper_list[idx2]]

                edge_weight = len(temp_set1.intersection(temp_set2))
                #print(edge_weight, "weight")
                if edge_weight != 0:

                    self.D_Graph.add_edge(self.paper_list[idx1],
                                          self.paper_list[idx2],
                                          weight = edge_weight)
        bipartite_num_edge = 0
        for key, val in list(self.paper_authorlist_dict.items()):
            if val != []:
                bipartite_num_edge += len(val)

        self.num_nnz = self.D_Graph.number_of_edges() + \
                        self.T_Graph.number_of_edges() + \
                        self.Abstract_Graph.number_of_edges()+\
                        self.Org_Graph.number_of_edges()+\
                        self.C_Graph.number_of_edges()+\
                        self.Jconf_Graph.number_of_edges()+\
                            self.Year_Graph.number_of_edges() +\
                        bipartite_num_edge
        print(self.num_nnz,"+++++++")
        self.num_nnz = self.C_Graph.number_of_edges()
        print("D_Graph edges", self.D_Graph.number_of_edges())
        print("Year_Graph edges", self.Year_Graph.number_of_edges())
        print("T_GRAPH edges",self.T_Graph.number_of_edges())
        print("ABSTRACT_GRAPH edges", self.Abstract_Graph.number_of_edges())
        print("Org_Graph edges",self.Org_Graph.number_of_edges())
        print("C_Graph", self.C_Graph.number_of_edges())
        print("Jconf_Graph_edges",self.Jconf_Graph.number_of_edges())
        print("bipartite_num_edge",bipartite_num_edge)
        print("END OF EDGES ++++++++++++")
        
        self.num_nnz=300
        print("predicted_cluster_list is",self.predicted_cluster_list )
        print("cluster_index is",self.cluster_index )
        #if self.predicted_cluster_list != False and self.cluster_index != False:
        print("Cluster rotation:", self.cluster_index,"finished returning cluster graphs (dataset cluster object)")
        return ego_name
        
        
        
#################################################<END>Dataset extraction and network construction!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#################################################<START> EMBEDDING OF NETWORKS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import math
# 自定义sigmoid函数
def sigmoid(x):
    # return max(0.0001,float(x))
    # return x
    # return float(x) /(1+math.exp(-x))

    return float(1) / (1 + math.exp(-x))


    # return (math.exp(x)-math.exp(-x))/(math.exp(x)+math.exp(-x))
#bpr_optimizer = embedding.BprOptimizer(latent_dimen, alpha, matrix_reg)
import numpy as np

class BprOptimizer():
    """
    use Bayesian Personalized Ranking for objective loss
    Bayesian personalized ranking(BPR) , one of the famous learning to rank algorithms used in recommender systems.
    latent_dimen: latent dimension
    alpha: learning rate
    matrix_reg: regularization parameter of matrix
    """
    def __init__(self, latent_dimen, alpha, matrix_reg):
        self.latent_dimen = latent_dimen
        self.alpha = alpha
        self.matrix_reg = matrix_reg

    def get_merge(self, dataset):
        node_dict = {}
        for node in dataset.Abstract_Graph.nodes():
            neighbors_list = dataset.Abstract_Graph.neighbors(node)
            if len(list(neighbors_list)) != 1:
                node_dict[node] = []
                for item in neighbors_list:
                    if len(dataset.Abstract_Graph.neighbors(item)) == 1:
                        node_dict[node].append(item)
        #print(node_dict)
        return node_dict

    def init_model(self, dataset):
        """
        initialize matrix using uniform [-0.2, 0.2]
        """
        self.paper_latent_matrix = {}
        self.author_latent_matrix = {}
        self.title_latent_matrix = {}
        self.jconf_latent_matrix = {}
        self.org_latent_matrix = {}
        self.year_latent_matrix = {}
        self.abstract_latent_matrix = {}
        # dd,dt,djconf,dorg,dyear,dabstract
        self.w=[1,1,0.1,0.1,0.1,1]
        node_dict = self.get_merge(dataset)
        in_list = []
        for key,val in node_dict.items():
            in_list=in_list+[key]
            in_list=in_list+val
            in_list=list(set(in_list))
        list_out = list(set(dataset.paper_list)-set(in_list))
        for item in list_out:
            self.paper_latent_matrix[item] = np.random.uniform(-0.5, 0.5,self.latent_dimen)
        for key ,val in node_dict.items():
            item_vec = np.random.uniform(-0.5, 0.5,self.latent_dimen)
            self.paper_latent_matrix[key] = item_vec
            for item in val:
                    self.paper_latent_matrix[item] = item_vec

        for paper_idx in dataset.paper_list:
            self.paper_latent_matrix[paper_idx] = np.random.uniform(-0.5, 0.5,
                                                                    self.latent_dimen)
        for author_idx in dataset.coauthor_list:
            self.author_latent_matrix[author_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)
        for title_idx in dataset.paper_title:
            self.title_latent_matrix[title_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)
        for jconf_idx in dataset.paper_jconf:
            self.jconf_latent_matrix[jconf_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)
        for org_idx in dataset.paper_org:
            self.org_latent_matrix[org_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)
        for year_idx in dataset.paper_year:
            self.year_latent_matrix[year_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)
        for abstract_idx in dataset.paper_abstract:
            self.abstract_latent_matrix[abstract_idx] = np.random.uniform(-0.5, 0.5,
                                                                      self.latent_dimen)

    def update_pp_gradient(self, fst, snd, third):
        """
        SGD inference
        """
        x = self.predict_score(fst, snd, "pp") - \
            self.predict_score(fst, third, "pp")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.author_latent_matrix[snd] - \
                                  self.author_latent_matrix[third]) + \
                    2 * self.matrix_reg * self.author_latent_matrix[fst]
        self.author_latent_matrix[fst] = self.author_latent_matrix[fst] - \
                                         self.alpha * grad_fst

        grad_snd = common_term * self.author_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.author_latent_matrix[snd]
        self.author_latent_matrix[snd]= self.author_latent_matrix[snd] - \
                                        self.alpha * grad_snd

        grad_third = -common_term * self.author_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.author_latent_matrix[third]
        self.author_latent_matrix[third] = self.author_latent_matrix[third] - \
                                           self.alpha * grad_third

    def update_pd_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "pd") - \
            self.predict_score(fst, third, "pd")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.author_latent_matrix[snd] - \
                                  self.author_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                         self.alpha * grad_fst

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.author_latent_matrix[snd]
        self.author_latent_matrix[snd]= self.author_latent_matrix[snd] - \
                                        self.alpha * grad_snd

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.author_latent_matrix[third]
        self.author_latent_matrix[third] = self.author_latent_matrix[third] - \
                                           self.alpha * grad_third

    def update_dd_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dd") - \
            self.predict_score(fst, third, "dd")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.paper_latent_matrix[snd] - \
                                  self.paper_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                         self.alpha * grad_fst * self.w[0]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.paper_latent_matrix[snd]
        self.paper_latent_matrix[snd]= self.paper_latent_matrix[snd] - \
                                       self.alpha * grad_snd* self.w[0]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.paper_latent_matrix[third]
        self.paper_latent_matrix[third] = self.paper_latent_matrix[third] - \
                                          self.alpha * grad_third* self.w[0]
    def update_dt_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dt") - \
            self.predict_score(fst, third, "dt")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.title_latent_matrix[snd] - \
                                  self.title_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                         self.alpha * grad_fst* self.w[1]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.title_latent_matrix[snd]
        self.title_latent_matrix[snd]= self.title_latent_matrix[snd] - \
                                       self.alpha * grad_snd* self.w[1]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.title_latent_matrix[third]
        self.title_latent_matrix[third] = self.title_latent_matrix[third] - \
                                          self.alpha * grad_third* self.w[1]

    def update_djconf_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "djconf") - \
            self.predict_score(fst, third, "djconf")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.jconf_latent_matrix[snd] - \
                                  self.jconf_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                         self.alpha * grad_fst* self.w[2]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.jconf_latent_matrix[snd]
        self.jconf_latent_matrix[snd]= self.jconf_latent_matrix[snd] - \
                                       self.alpha * grad_snd* self.w[2]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.jconf_latent_matrix[third]
        self.jconf_latent_matrix[third] = self.jconf_latent_matrix[third] - \
                                          self.alpha * grad_third* self.w[2]

    def update_dorg_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dorg") - \
            self.predict_score(fst, third, "dorg")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.org_latent_matrix[snd] - \
                                  self.org_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                        self.alpha * grad_fst* self.w[3]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.org_latent_matrix[snd]
        self.org_latent_matrix[snd] = self.org_latent_matrix[snd] - \
                                        self.alpha * grad_snd* self.w[3]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.org_latent_matrix[third]
        self.org_latent_matrix[third] = self.org_latent_matrix[third] - \
                                          self.alpha * grad_third* self.w[3]

    def update_dyear_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dyear") - \
            self.predict_score(fst, third, "dyear")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.year_latent_matrix[snd] - \
                                  self.year_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                        self.alpha * grad_fst* self.w[4]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.year_latent_matrix[snd]
        self.year_latent_matrix[snd] = self.year_latent_matrix[snd] - \
                                      self.alpha * grad_snd* self.w[4]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.year_latent_matrix[third]
        self.year_latent_matrix[third] = self.year_latent_matrix[third] - \
                                        self.alpha * grad_third* self.w[4]
    def update_dabstract_gradient(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dabstract") - \
            self.predict_score(fst, third, "dabstract")
        common_term = sigmoid(x) - 1

        grad_fst = common_term * (self.abstract_latent_matrix[snd] - \
                                  self.abstract_latent_matrix[third]) + \
                   2 * self.matrix_reg * self.paper_latent_matrix[fst]
        self.paper_latent_matrix[fst] = self.paper_latent_matrix[fst] - \
                                        self.alpha * grad_fst* self.w[5]

        grad_snd = common_term * self.paper_latent_matrix[fst] + \
                   2 * self.matrix_reg * self.abstract_latent_matrix[snd]
        self.abstract_latent_matrix[snd] = self.abstract_latent_matrix[snd] - \
                                        self.alpha * grad_snd* self.w[5]

        grad_third = -common_term * self.paper_latent_matrix[fst] + \
                     2 * self.matrix_reg * self.abstract_latent_matrix[third]
        self.abstract_latent_matrix[third] = self.abstract_latent_matrix[third] - \
                                          self.alpha * grad_third* self.w[5]

    def compute_pp_loss(self, fst, snd, third):
        """
        loss includes ranking loss and model complexity
        """
        x = self.predict_score(fst, snd, "pp") - \
             self.predict_score(fst, third, "pp")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.author_latent_matrix[fst],
                                               self.author_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.author_latent_matrix[snd],
                                               self.author_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.author_latent_matrix[third],
                                               self.author_latent_matrix[third])
        return ranking_loss + complexity

    def compute_pd_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "pd") - \
            self.predict_score(fst, third, "pd")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.author_latent_matrix[snd],
                                               self.author_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.author_latent_matrix[third],
                                               self.author_latent_matrix[third])
        return ranking_loss + complexity

    def compute_dd_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dd") - \
            self.predict_score(fst, third, "dd")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[snd],
                                               self.paper_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[third],
                                               self.paper_latent_matrix[third])
        return ranking_loss + complexity

    def compute_dt_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dt") - \
            self.predict_score(fst, third, "dt")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.title_latent_matrix[snd],
                                               self.title_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.title_latent_matrix[third],
                                               self.title_latent_matrix[third])
        return ranking_loss + complexity

    def compute_djconf_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "djconf") - \
            self.predict_score(fst, third, "djconf")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.jconf_latent_matrix[snd],
                                               self.jconf_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.jconf_latent_matrix[third],
                                               self.jconf_latent_matrix[third])
        return ranking_loss + complexity

    def compute_dorg_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dt") - \
            self.predict_score(fst, third, "dt")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.org_latent_matrix[snd],
                                               self.org_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.org_latent_matrix[third],
                                               self.org_latent_matrix[third])
        return ranking_loss + complexity

    def compute_dyear_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dyear") - \
            self.predict_score(fst, third, "dyear")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.year_latent_matrix[snd],
                                               self.year_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.year_latent_matrix[third],
                                               self.year_latent_matrix[third])
        return ranking_loss + complexity

    def compute_dabstract_loss(self, fst, snd, third):
        x = self.predict_score(fst, snd, "dabstract") - \
            self.predict_score(fst, third, "dabstract")
        ranking_loss = -np.log(sigmoid(x))

        complexity = 0.0
        complexity += self.matrix_reg * np.dot(self.paper_latent_matrix[fst],
                                               self.paper_latent_matrix[fst])
        complexity += self.matrix_reg * np.dot(self.abstract_latent_matrix[snd],
                                               self.abstract_latent_matrix[snd])
        complexity += self.matrix_reg * np.dot(self.abstract_latent_matrix[third],
                                               self.abstract_latent_matrix[third])
        return ranking_loss + complexity

    def predict_score(self, fst, snd, graph_type):
        """
        pp: person-person network
        pd: person-document bipartite network
        dd: doc-doc network
        detailed notation is inside paper
        """
        if graph_type == "pp":
            return np.dot(self.author_latent_matrix[fst],
                          self.author_latent_matrix[snd])
            # a = self.author_latent_matrix[fst]
            # b = self.author_latent_matrix[snd]
            # return np.dot(a,b)/float(np.sqrt(a.dot(a))*np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.author_latent_matrix[fst]
            #                                 - self.author_latent_matrix[snd])))
        elif graph_type == "pd":
            return np.dot(self.paper_latent_matrix[fst],
                          self.author_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.author_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.author_latent_matrix[snd])))
        elif graph_type == "dd":
            return np.dot(self.paper_latent_matrix[fst],
                          self.paper_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.paper_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.paper_latent_matrix[snd])))
        elif graph_type == "dt":
            return np.dot(self.paper_latent_matrix[fst],
                          self.title_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.title_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.title_latent_matrix[snd])))
        elif graph_type == "djconf":
            return np.dot(self.paper_latent_matrix[fst],
                          self.jconf_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.jconf_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.jconf_latent_matrix[snd])))
        elif graph_type == "dorg":
            return np.dot(self.paper_latent_matrix[fst],
                          self.org_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.org_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.org_latent_matrix[snd])))
        elif graph_type == "dyear":
            return np.dot(self.paper_latent_matrix[fst],
                          self.year_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.year_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.year_latent_matrix[snd])))
        elif graph_type == "dabstract":
            return np.dot(self.paper_latent_matrix[fst],
                          self.abstract_latent_matrix[snd])
            # a = self.paper_latent_matrix[fst]
            # b = self.abstract_latent_matrix[snd]
            # return np.dot(a, b) / float(np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            # return np.sqrt(np.sum(np.square(self.paper_latent_matrix[fst]
            #                                 - self.abstract_latent_matrix[snd])))
#################################################<END> ---LOSS FUNCTION-EMBEDDING--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#################################################<START> ---SAMPLER-EMBEDDING--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import random
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    if len(x)>0:
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)
    else:
        return 0.5


"""
(i, j) belongs positive sample set
(i, t) belongs negative sample set
notation details are in the paper
用于采样产生正负集合
"""

class CoauthorGraphSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        """
        sample negative instance uniformly
        """
        a_i = random.choice(list(dataset.C_Graph.nodes()))
        a_t = random.choice(dataset.coauthor_list)
        while True:
            neig_list = list(dataset.C_Graph.neighbors(a_i))
            if a_t not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.C_Graph[a_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                a_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield a_i, a_j, a_t
                break

            else:
                a_i = random.choice(dataset.C_Graph.nodes())
                a_t = random.choice(dataset.coauthor_list)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        a_i = random.choice(dataset.C_Graph.nodes())
        neg_pair = random.sample(dataset.coauthor_list, 2)

        while True:
            neig_list = dataset.C_Graph.neighbors(a_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.C_Graph[a_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                a_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(a_i, neg_pair[0], "pp")
                sc2 = bpr_optimizer.predict_score(a_i, neg_pair[1], "pp")
                a_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield a_i, a_j, a_t
                break

            else:
                a_i = random.choice(dataset.C_Graph.nodes())
                neg_pair = random.sample(dataset.coauthor_list, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        a_i = random.choice(dataset.C_Graph.nodes())
        neg_list = list(set(dataset.coauthor_list) - \
                   set(dataset.C_Graph.neighbors(a_i)) - set([a_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.C_Graph.neighbors(a_i)
        weight_list = [dataset.C_Graph[a_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        a_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        norm_soft = softmax([bpr_optimizer.predict_score(a_i, ne, "pp")
                             for ne in neg_list])
        a_t = np.random.choice(neg_list, 1, p = norm_soft)[0]
        yield a_i, a_j, a_t


class LinkedDocGraphSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        d_i = random.choice(dataset.D_Graph.nodes())
        d_t = random.choice(dataset.paper_list)

        while True:
            neig_list = dataset.D_Graph.neighbors(d_i)
            if d_t not in neig_list:
                # given d_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.D_Graph[d_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                d_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield d_i, d_j, d_t
                break

            else:
                d_i = random.choice(dataset.D_Graph.nodes())
                d_t = random.choice(dataset.paper_list)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        d_i = random.choice(dataset.D_Graph.nodes())
        neg_pair = random.sample(dataset.paper_list, 2)

        while True:
            neig_list = dataset.D_Graph.neighbors(d_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.D_Graph[d_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                d_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(d_i, neg_pair[0], "dd")
                sc2 = bpr_optimizer.predict_score(d_i, neg_pair[1], "dd")
                d_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield d_i, d_j, d_t
                break

            else:
                d_i = random.choice(dataset.D_Graph.nodes())
                neg_pair = random.sample(dataset.paper_list, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        d_i = random.choice(dataset.D_Graph.nodes())
        neg_list = list(set(dataset.paper_list) - \
                   set(dataset.D_Graph.neighbors(d_i)) - set([d_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.D_Graph.neighbors(d_i)
        weight_list = [dataset.D_Graph[d_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        d_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        norm_soft = softmax([bpr_optimizer.predict_score(d_i, ne, "dd")
                             for ne in neg_list])
        d_t = np.random.choice(neg_list, 1, p = norm_soft)[0]
        yield d_i, d_j, d_t

class DocumentTitleSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        t_i = random.choice(dataset.T_Graph.nodes())
        t_t = random.choice(dataset.paper_title)

        while True:
            neig_list = dataset.T_Graph.neighbors(t_i)
            if t_t not in neig_list:
                # given d_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.T_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.T_Graph.nodes())
                t_t = random.choice(dataset.paper_title)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        t_i = random.choice(dataset.T_Graph.nodes())
        neg_pair = random.sample(dataset.paper_title, 2)

        while True:
            neig_list = dataset.T_Graph.neighbors(t_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.T_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(t_i, neg_pair[0], "dt")
                sc2 = bpr_optimizer.predict_score(t_i, neg_pair[1], "dt")
                t_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.T_Graph.nodes())
                neg_pair = random.sample(dataset.paper_title, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        t_i = random.choice(dataset.T_Graph.nodes())
        neg_list = list(set(dataset.paper_title) - \
                   set(dataset.T_Graph.neighbors(t_i)) - set([t_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.T_Graph.neighbors(t_i)
        weight_list = [dataset.T_Graph[t_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        norm_soft = softmax([bpr_optimizer.predict_score(t_i, ne, "dt")
                             for ne in neg_list])
        t_t = np.random.choice(neg_list, 1, p = norm_soft)[0]
        yield t_i, t_j, t_t



class DocumentJConfSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        jconf_i = random.choice(dataset.Jconf_Graph.nodes())
        jconf_t = random.choice(dataset.paper_jconf)

        while True:
            neig_list = dataset.Jconf_Graph.neighbors(jconf_i)
            if jconf_t not in neig_list:
                weight_list = [dataset.Jconf_Graph[jconf_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                jconf_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield jconf_i, jconf_j, jconf_t
                break

            else:
                jconf_i = random.choice(dataset.Jconf_Graph.nodes())
                jconf_t = random.choice(dataset.paper_jconf)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        jconf_i = random.choice(dataset.Jconf_Graph.nodes())
        neg_pair = random.sample(dataset.paper_jconf, 2)
        cnt=0
        while True:
            neig_list = dataset.Jconf_Graph.neighbors(jconf_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Jconf_Graph[jconf_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                jconf_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(jconf_i, neg_pair[0], "djconf")
                sc2 = bpr_optimizer.predict_score(jconf_i, neg_pair[1], "djconf")
                jconf_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield jconf_i, jconf_j, jconf_t
                break

            else:
                cnt += 1
                if (cnt > 5):
                    neig_list = dataset.Jconf_Graph.neighbors(jconf_i)
                    weight_list = [dataset.Jconf_Graph[jconf_i][nbr]['weight']
                                   for nbr in neig_list]
                    norm_weight_list = [float(w) / sum(weight_list)
                                        for w in weight_list]
                    jconf_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                    jconf_t = random.choice(dataset.Jconf_Graph.nodes())
                    yield jconf_i, jconf_j, jconf_t
                    break

                jconf_i = random.choice(dataset.Jconf_Graph.nodes())
                neg_pair = random.sample(dataset.paper_jconf, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        jconf_i = random.choice(dataset.Jconf_Graph.nodes())
        neg_list = list(set(dataset.paper_jconf) - \
                   set(dataset.Jconf_Graph.neighbors(jconf_i)) - set([jconf_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.Jconf_Graph.neighbors(jconf_i)
        weight_list = [dataset.Jconf_Graph[jconf_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        jconf_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        jconf_t = 0
        if len(neg_list) > 0:
            norm_soft = softmax([bpr_optimizer.predict_score(jconf_i, ne, "djconf")
                                 for ne in neg_list])
            jconf_t = np.random.choice(neg_list, 1, p=norm_soft)[0]
        else:
            jconf_t = np.random.choice(neig_list)
        yield jconf_i, jconf_j, jconf_t


class BipartiteGraphSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        d_i = random.choice(dataset.paper_list)
        a_t = random.choice(dataset.coauthor_list)

        while True:
            if dataset.paper_authorlist_dict[d_i] != [] \
                and a_t not in dataset.paper_authorlist_dict[d_i]:
                a_j = random.choice(dataset.paper_authorlist_dict[d_i])
                yield d_i, a_j, a_t
                break

            else:
                d_i = random.choice(dataset.paper_list)
                a_t = random.choice(dataset.coauthor_list)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        d_i = random.choice(dataset.paper_list)
        neg_pair = random.sample(dataset.coauthor_list, 2)

        while True:
            if dataset.paper_authorlist_dict[d_i] != [] \
                and neg_pair[0] not in dataset.paper_authorlist_dict[d_i] \
                    and neg_pair[1] not in dataset.paper_authorlist_dict[d_i]:

                a_j = random.choice(dataset.paper_authorlist_dict[d_i])

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(d_i, neg_pair[0], "pd")
                sc2 = bpr_optimizer.predict_score(d_i, neg_pair[1], "pd")
                a_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield d_i, a_j, a_t
                break

            else:
                d_i = random.choice(dataset.paper_list)
                neg_pair = random.sample(dataset.coauthor_list, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        d_i = random.choice(dataset.paper_list)
        neg_list = list(set(dataset.coauthor_list) - \
                        set(dataset.paper_authorlist_dict[d_i]))

        while True:
            if dataset.paper_authorlist_dict[d_i] != []:
                a_j = random.choice(dataset.paper_authorlist_dict[d_i])

                # sample negative instance based on pre-defined exponential distribution
                norm_soft = softmax([bpr_optimizer.predict_score(d_i, ne, "pd")
                                     for ne in neg_list])
                a_t = np.random.choice(neg_list, 1, p = norm_soft)[0]
                yield d_i, a_j, a_t
                break

            else:
                d_i = random.choice(dataset.paper_list)
                neg_list = list(set(dataset.coauthor_list) - \
                                set(dataset.paper_authorlist_dict[d_i]))

class DocumentOrgSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        t_i = random.choice(dataset.Org_Graph.nodes())
        t_t = random.choice(dataset.paper_org)

        while True:
            neig_list = dataset.Org_Graph.neighbors(t_i)
            if t_t not in neig_list:
                # given d_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Org_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.Org_Graph.nodes())
                t_t = random.choice(dataset.paper_org)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        t_i = random.choice(dataset.Org_Graph.nodes())
        neg_pair = random.sample(dataset.paper_org, 2)
        cnt = 0
        while True:
            neig_list = dataset.Org_Graph.neighbors(t_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Org_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(t_i, neg_pair[0], "dorg")
                sc2 = bpr_optimizer.predict_score(t_i, neg_pair[1], "dorg")
                t_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield t_i, t_j, t_t
                break

            else:
                cnt += 1
                if (cnt > 5):
                    neig_list = dataset.Org_Graph.neighbors(t_i)
                    weight_list = [dataset.Org_Graph[t_i][nbr]['weight']
                                   for nbr in neig_list]
                    norm_weight_list = [float(w) / sum(weight_list)
                                        for w in weight_list]
                    t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                    t_t = random.choice(dataset.Org_Graph.nodes())
                    yield t_i, t_j, t_t
                    break
                t_i = random.choice(dataset.Org_Graph.nodes())
                neg_pair = random.sample(dataset.paper_org, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        t_i = random.choice(dataset.Org_Graph.nodes())
        neg_list = list(set(dataset.paper_org) - \
                   set(dataset.Org_Graph.neighbors(t_i)) - set([t_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.Org_Graph.neighbors(t_i)
        weight_list = [dataset.Org_Graph[t_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        t_t = 0
        if len(neg_list) > 0:
            norm_soft = softmax([bpr_optimizer.predict_score(t_i, ne, "dorg")
                                 for ne in neg_list])
            t_t = np.random.choice(neg_list, 1, p=norm_soft)[0]
        else:
            t_t = np.random.choice(neig_list)
        yield t_i, t_j, t_t

class DocumentYearSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        t_i = random.choice(dataset.Year_Graph.nodes())
        t_t = random.choice(dataset.paper_year)

        while True:
            neig_list = dataset.Year_Graph.neighbors(t_i)
            if t_t not in neig_list:
                # given d_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Year_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.Year_Graph.nodes())
                t_t = random.choice(dataset.paper_year)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        t_i = random.choice(dataset.Year_Graph.nodes())
        neg_pair = random.sample(dataset.paper_year, 2)

        while True:
            neig_list = dataset.Year_Graph.neighbors(t_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Year_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(t_i, neg_pair[0], "dyear")
                sc2 = bpr_optimizer.predict_score(t_i, neg_pair[1], "dyear")
                t_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.Year_Graph.nodes())
                neg_pair = random.sample(dataset.paper_year, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        t_i = random.choice(dataset.Year_Graph.nodes())
        neg_list = list(set(dataset.paper_year) - \
                   set(dataset.Year_Graph.neighbors(t_i)) - set([t_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.Year_Graph.neighbors(t_i)
        weight_list = [dataset.Year_Graph[t_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        norm_soft = softmax([bpr_optimizer.predict_score(t_i, ne, "dyear")
                             for ne in neg_list])
        t_t = np.random.choice(neg_list, 1, p = norm_soft)[0]
        yield t_i, t_j, t_t

class DocumentAbstractSampler():
    @staticmethod
    def generate_triplet_uniform(dataset):
        t_i = random.choice(dataset.Abstract_Graph.nodes())
        t_t = random.choice(dataset.paper_abstract)

        while True:
            neig_list = dataset.Abstract_Graph.neighbors(t_i)
            if t_t not in neig_list:
                # given d_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Abstract_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                yield t_i, t_j, t_t
                break

            else:
                t_i = random.choice(dataset.Abstract_Graph.nodes())
                t_t = random.choice(dataset.paper_abstract)

    @staticmethod
    def generate_triplet_reject(dataset, bpr_optimizer):
        """
        generate negative instance using ranking-aware rejection sampler
        consider linear case
        """
        t_i = random.choice(dataset.Abstract_Graph.nodes())
        neg_pair = random.sample(dataset.paper_abstract, 2)
        cnt = 0
        while True:
            neig_list = dataset.Abstract_Graph.neighbors(t_i)
            if neg_pair[0] not in neig_list and neg_pair[1] not in neig_list:
                # given a_i, sample its neighbor based on its weight value
                # idea of edge sampling
                weight_list = [dataset.Abstract_Graph[t_i][nbr]['weight']
                               for nbr in neig_list]
                norm_weight_list = [float(w) / sum(weight_list)
                                    for w in weight_list]
                t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

                # sample negative instance using ranking-aware rejection sampler
                sc1 = bpr_optimizer.predict_score(t_i, neg_pair[0], "dabstract")
                sc2 = bpr_optimizer.predict_score(t_i, neg_pair[1], "dabstract")
                t_t = neg_pair[0] if sc1 <= sc2 else neg_pair[1]
                yield t_i, t_j, t_t
                break
            else:
                cnt+=1
                if(cnt>5):
                    neig_list = dataset.Abstract_Graph.neighbors(t_i)
                    weight_list = [dataset.Abstract_Graph[t_i][nbr]['weight']
                                   for nbr in neig_list]
                    norm_weight_list = [float(w) / sum(weight_list)
                                        for w in weight_list]
                    t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]
                    t_t = random.choice(dataset.Abstract_Graph.nodes())
                    yield t_i, t_j, t_t
                    break
                t_i = random.choice(dataset.Abstract_Graph.nodes())
                neg_pair = random.sample(dataset.paper_abstract, 2)

    @staticmethod
    def generate_triplet_adaptive(dataset, bpr_optimizer):
        """
        generate negative instance using adaptive sampling
        sample from a pre-defined exponential distribution
        """
        t_i = random.choice(dataset.Abstract_Graph.nodes())
        neg_list = list(set(dataset.paper_abstract) - \
                        set(dataset.Abstract_Graph.neighbors(t_i)) - set([t_i]))

        # given a_i, sample its neighbor based on its weight value
        # idea of edge sampling
        neig_list = dataset.Abstract_Graph.neighbors(t_i)
        weight_list = [dataset.Abstract_Graph[t_i][nbr]['weight']
                       for nbr in neig_list]
        norm_weight_list = [float(w) / sum(weight_list)
                            for w in weight_list]
        t_j = np.random.choice(neig_list, 1, p=norm_weight_list)[0]

        # sample negative instance based on pre-defined exponential distribution
        t_t = 0
        if len(neg_list) > 0:
            norm_soft = softmax([bpr_optimizer.predict_score(t_i, ne, "dabstract")
                                 for ne in neg_list])
            t_t = np.random.choice(neg_list, 1, p=norm_soft)[0]
        else:
            t_t = np.random.choice(neig_list)
        yield t_i, t_j, t_t

#################################################<END> ---SAMPLER--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



def save_embedding(dict, paper_list, num_dimen,filename):
    """
    save the final embedding results for each document
    """
    fn = filename.split('/')[-1]
    embedding_file = open('C:\\Users\\Liam Ephraims\\Author_Disambiguation\\emb'+fn+'.txt','w')
    # embedding_file.write(str(len(paper_list)) + ' ' + str(num_dimen) + os.linesep)
    D_matrix = dict[paper_list[0]]
    for idx in range(1, len(paper_list)):
        D_matrix = np.vstack((D_matrix, dict[paper_list[idx]]))
    D_matrix = np.hstack((np.array([list(range(1, len(paper_list)+1))]).T, D_matrix))
    np.savetxt(embedding_file, D_matrix[:,1:],
               fmt = ' '.join(['%1.5f'] * num_dimen))
#################################################<TRAINER> ---TRAINER HELPER--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class TrainHelper():
    @staticmethod
    def helper(num_epoch, dataset, bpr_optimizer,eval_f1, sampler_method,filename,
               pp_sampler=False,
               pd_sampler=False,
               dd_sampler=False,
               dt_sampler=False,
               djconf_sampler=False,
               dorg_sampler=False,
              dyear_sampler=False,
               dabstract_sampler=False, network_comparison=False,affinity_prop=False):

        bpr_optimizer.init_model(dataset)
        if sampler_method == "uniform":
            for _ in range(0, num_epoch):
                bpr_loss = 0.0
                for _ in range(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                 #           self.num_nnz = self.D_Graph.number_of_edges() + \
                 #       self.T_Graph.number_of_edges() + \
                 #       self.Abstract_Graph.number_of_edges()+\
                  #      self.Org_Graph.number_of_edges()+\
                   #     self.C_Graph.number_of_edges()+\
                    #    self.Jconf_Graph.number_of_edges()+\
                     #   bipartite_num_edge
                        
                    if not pp_sampler == False and dataset.C_Graph.number_of_edges() > 0:
                        for i, j, t in pp_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_pp_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)
                            
                    if not pd_sampler==False: #NOTE: NO GRAPH OBJECT USING PAPER LIST AND CO AUTHOR LIST.
                        for i, j, t in pd_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_pd_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)
                    #print(" if not dd_sampler == False and dataset.D_Graph.number_of_edges() > 0:")
                    #print(not dd_sampler == False and dataset.D_Graph.number_of_edges() > 0)
                    if not dd_sampler == False and dataset.D_Graph.number_of_edges() > 0:
                        for i, j, t in dd_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_dd_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)
                    if not dt_sampler == False:
                        for i, j, t in dt_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_dt_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_dt_loss(i, j, t)
                   # print(" if not dd_sampler == False and dataset.Jconf_Graph.number_of_edges() > 0:")
                    #print(not dd_sampler == False and dataset.Jconf_Graph.number_of_edges() > 0)
                    if not djconf_sampler==False and dataset.Jconf_Graph.number_of_edges() > 0:
                       for i, j, t in djconf_sampler.generate_triplet_uniform(dataset):
                           bpr_optimizer.update_djconf_gradient(i, j, t)
                           bpr_loss += bpr_optimizer.compute_djconf_loss(i, j, t)
                    if not dorg_sampler == False and dataset.Org_Graph.number_of_edges() > 0:
                        for i, j, t in dorg_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_dorg_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_dorg_loss(i, j, t)
                    if not dyear_sampler == False and dataset.Year_Graph.number_of_edges() > 0:
                        for i, j, t in dyear_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_dyear_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_dyear_loss(i, j, t)
                    #print(" if not dd_sampler == False and dataset.Abstract_Graph.number_of_edges() > 0:")
                    #print(not dd_sampler == False and dataset.Abstract_Graph.number_of_edges() > 0)
                    if not dabstract_sampler == False and dataset.Abstract_Graph.number_of_edges() > 0:
                        for i, j, t in dabstract_sampler.generate_triplet_uniform(dataset):
                            bpr_optimizer.update_dabstract_gradient(i, j, t)
                            bpr_loss += bpr_optimizer.compute_dabstract_loss(i, j, t)

                average_loss = float(bpr_loss) / dataset.num_nnz
                # print "average bpr loss is " + str(average_loss)

                #average_loss = float(bpr_loss) / dataset.num_nnz
                #print "average bpr loss is " + str(average_loss)
            average_f1,average_pre,average_rec, predict_label_dict,disambig_alg = eval_f1.compute_f1(dataset, bpr_optimizer,network_comparison,affinity_prop)
                #print 'f1 is ' + str(average_f1)
            save_embedding(bpr_optimizer.paper_latent_matrix,
                           dataset.paper_list, bpr_optimizer.latent_dimen, filename)
            return average_f1,average_pre,average_rec, predict_label_dict, dataset,disambig_alg,network_comparison,affinity_prop
        elif sampler_method == "reject":
            for _ in range(0, num_epoch):
                bpr_loss = 0.0
                for _ in range(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                    for i, j, t in pp_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_pp_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)
                    #
                    for i, j, t in pd_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_pd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)

                    for i, j, t in dd_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_dd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)

                    for i, j, t in dt_sampler.generate_triplet_reject(dataset,bpr_optimizer):
                        bpr_optimizer.update_dt_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dt_loss(i, j, t)

                    for i, j, t in djconf_sampler.generate_triplet_reject(dataset,bpr_optimizer):
                        bpr_optimizer.update_djconf_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_djconf_loss(i, j, t)
                    #
                    for i, j, t in dorg_sampler.generate_triplet_reject(dataset,bpr_optimizer):
                        bpr_optimizer.update_dorg_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dorg_loss(i, j, t)

                    for i, j, t in dyear_sampler.generate_triplet_reject(dataset,bpr_optimizer):
                        bpr_optimizer.update_dyear_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dyear_loss(i, j, t)

                    for i, j, t in dabstract_sampler.generate_triplet_reject(dataset,bpr_optimizer):
                        bpr_optimizer.update_dabstract_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dabstract_loss(i, j, t)

            average_f1, average_pre, average_rec = eval_f1.compute_f1(dataset, bpr_optimizer,network_comparison,affinity_prop)
            # print 'f1 is ' + str(average_f1)
            return average_f1,average_pre,average_rec
        elif sampler_method == "adaptive":
            for _ in range(0, num_epoch):
                bpr_loss = 0.0
                for _ in range(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                    for i, j, t in pp_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_pp_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)
                    #
                    for i, j, t in pd_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_pd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)

                    for i, j, t in dd_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_dd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)
                    for i, j, t in dt_sampler.generate_triplet_adaptive(dataset,bpr_optimizer):
                        bpr_optimizer.update_dt_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dt_loss(i, j, t)

                    for i, j, t in djconf_sampler.generate_triplet_adaptive(dataset,bpr_optimizer):
                        bpr_optimizer.update_djconf_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_djconf_loss(i, j, t)
                    
                    for i, j, t in dorg_sampler.generate_triplet_adaptive(dataset,bpr_optimizer):
                        bpr_optimizer.update_dorg_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dorg_loss(i, j, t)

                    for i, j, t in dyear_sampler.generate_triplet_adaptive(dataset,bpr_optimizer):
                       bpr_optimizer.update_dyear_gradient(i, j, t)
                       bpr_loss += bpr_optimizer.compute_dyear_loss(i, j, t)

                    for i, j, t in dabstract_sampler.generate_triplet_adaptive(dataset,bpr_optimizer):
                        bpr_optimizer.update_dabstract_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dabstract_loss(i, j, t)

            average_f1, average_pre, average_rec = eval_f1.compute_f1(dataset, bpr_optimizer,network_comparison,affinity_prop)
            # print 'f1 is ' + str(average_f1)
            return average_f1,average_pre,average_rec
        save_embedding(bpr_optimizer.paper_latent_matrix,
                       dataset.paper_list, bpr_optimizer.latent_dimen,filename)
#################################################<TRAINER END> ---TRAINER HELPER--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#################################################<START> ---K-MEANS--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from sklearn.cluster import *
from sklearn.decomposition import *
from sklearn.externals import joblib

# 构建关于文章的矩阵
def construct_doc_matrix(dict, paper_list):
    """
    construct the learned embedding for document clustering
    dict: {paper_index, numpy_array}
    """
    D_matrix = dict[paper_list[0]]
    for idx in range(1, len(paper_list)):
        D_matrix = np.vstack((D_matrix, dict[paper_list[idx]]))
    return D_matrix

from scipy import stats
from sklearn.cluster import KMeans

class XMeans(KMeans):

    def __init__(self, k_init = 1, **k_means_args):
        self.k_init = k_init
        self.k_means_args = k_means_args

    def fit(self, X):
        km = KMeans(self.k_init, **self.k_means_args).fit(X)
        self.cluster_centers_ = list(km.cluster_centers_)
        self.labels_, _ = self.__recrucive_clustering(X, km.labels_, np.unique(km.labels_), np.max(km.labels_))
        self.cluster_centers_ = np.array(self.cluster_centers_)
        return self

    def __recrucive_clustering(self, X, labels, labelset, splits):
        for label in labelset:
            cluster = X[labels == label]
            if len(cluster) <= 3: continue
            km = KMeans(2, **self.k_means_args).fit(cluster)
            if self.__recrucive_decision(cluster, km.labels_, km.cluster_centers_):
                self.cluster_centers_[label] = km.cluster_centers_[0]
                self.cluster_centers_.append(km.cluster_centers_[1])
                km.labels_[km.labels_ == 1] += splits
                km.labels_[km.labels_ == 0] += label
                labels[labels == label], splits = self.__recrucive_clustering(cluster, km.labels_, [label, splits+1], splits+1)
        return labels, splits

    def __recrucive_decision(self, cluster, labels, centers):
        samples = cluster.shape[0]
        parameters = cluster.shape[1] * (cluster.shape[1] + 3) / 2
        bic = self.__bic(cluster, None, samples, parameters)
        new_bic = self.__bic(cluster[labels == 0], cluster[labels == 1], samples, parameters*2)
        return bic > new_bic

    def __bic(self, cluster_0, cluster_1, samples, parameters):
        if cluster_1 is not None:
            alpha = self.__model_likelihood(cluster_0, cluster_1)
            return -2.0 * (samples * np.log(alpha) + self.__log_likelihood(cluster_0) + self.__log_likelihood(cluster_1)) + parameters * np.log(samples)
        else:
            return -2.0 * self.__log_likelihood(cluster_0) + parameters * np.log(samples)

    def __model_likelihood(self, cluster_0, cluster_1):
        mu_0, mu_1 = np.mean(cluster_0, axis=0), np.mean(cluster_1, axis=0)
        sigma_0, sigma_1 = np.cov(cluster_0.T) , np.cov(cluster_1.T)
        det_0 = np.linalg.det(sigma_0) if len(cluster_0) > 1 else 0.0
        det_1 = np.linalg.det(sigma_1)if len(cluster_1) > 1 else 0.0
        beta = np.linalg.norm(mu_0 - mu_1) / np.sqrt(det_0 + det_1+0.00001)
        return 0.5 / stats.norm.cdf(beta)

    def __log_likelihood(self, cluster):
        if len(cluster) == 1: return np.log(1.0)
        mu = np.mean(cluster, axis=0)
        sigma = np.cov(cluster.T)
        if not str(sigma[0][0]).isdigit():
            return np.log(1.0)
        try:
            log_likehood = np.sum(stats.multivariate_normal.logpdf(x, mu, sigma) for x in cluster)
        except:
            sigma = sigma * np.identity(sigma.shape[0])
            log_likehood = np.sum(stats.multivariate_normal.logpdf(x, mu, sigma) for x in cluster)
        return log_likehood

    def predict(self):
        return self.labels_

    def fit_predict(self, X):
        self.fit(X)
        return self.labels_

#################################################<END> ---K-MEANS--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#################################################<END> ---K-MEANS--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################<START> ---MODEL READER--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

from joblib import load

class Token:
    __slots__ = ('text', 'span')

    def __init__(self, text, span):
        self.text = text
        self.span = span

    def __repr__(self):
        return '<Token %s>' % self.text.encode('utf-8')

    def __reduce__(self):
        return (self.__class__, (self.text, self.span))


class RegexpTokenizer(object):
    __slots__ = ('_rule',)

    def __init__(self, rule=r'[\w\d]+'):
        self._rule = re.compile(rule, re.UNICODE)

    def tokenize(self, text):
        return [Token(text[o.start():o.end()], o.span()) for o in self._rule.finditer(text)]

class ModelReader(object):
    def __init__(self, model_file):
        model = load(model_file, mmap_mode='r')
        self._word_embedding = model['word_embedding']
        self._entity_embedding = model['entity_embedding']
        self._W = model.get('W')
        self._b = model.get('b')
        self._vocab = model.get('vocab')

        self._tokenizer = RegexpTokenizer()

    @property
    def vocab(self):
        return self._vocab

    @property
    def word_embedding(self):
        return self._word_embedding

    @property
    def entity_embedding(self):
        return self._entity_embedding

    @property
    def W(self):
        return self._W

    @property
    def b(self):
        return self._b

    def get_word_vector(self, word, default=None):
        index = self._vocab.get_word_index(word)
        if index:
            return self.word_embedding[index]
        else:
            # 不返回default，返回默认值
            return self.word_embedding[0]
    def get_entity_vector(self, title, default=None):
        index = self._vocab.get_entity_index(title)
        if index:
            return self.entity_embedding[index]
        else:
            return default

    def get_text_vector(self, text):
        vectors = [self.get_word_vector(t.text.lower())
                   for t in self._tokenizer.tokenize(text)]
        vectors = [v for v in vectors if v is not None]
        if not vectors:
            return None

        ret = np.mean(vectors, axis=0)
        ret = np.dot(ret, self._W)
        ret += self._b

        ret /= np.linalg.norm(ret, 2)

        return ret

#################################################<END> ---MODEL READER--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################<start> ---EVAL_METRIC--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def hdbscan(D_matrix):
    return HDBSCAN(min_cluster_size=1).fit_predict(D_matrix)
def dbscan(D_matrix):
    return DBSCAN(eps=1.5, min_samples=2).fit_predict(D_matrix)
def ap(D_matrix):
    return AffinityPropagation(damping=0.6).fit_predict(D_matrix)
def xmeans(D_matrix):
    return XMeans(random_state=1).fit_predict(D_matrix)
def meanshift(D_matrix):
    # bandwidth=estimate_bandwidth(D_matrix,quantile=0.4)
    return MeanShift().fit_predict(D_matrix)
def kmeans(D_matrix,true_cluster_size):
    return KMeans(n_clusters=true_cluster_size,init="k-means++").fit_predict(D_matrix)
def hac(D_matrix,true_cluster_size):
    return AgglomerativeClustering(n_clusters = true_cluster_size,linkage = "average",affinity = "cosine").fit_predict(D_matrix)
def compute_distance(D_matrix,predict_label_dict):
    avg_distance = 0
    sum_list = []
    for key, value in predict_label_dict.items():
        list_item = []
        for j in value:
            list_item.append(D_matrix[j])
        D_itme_array = np.array(list_item)
        for i in range(D_itme_array.shape[0]):
            sum_distance = 0
            for j in range(D_itme_array.shape[0]):
                dist = np.sqrt(np.sum(np.square(D_itme_array[i] - D_itme_array[j])))
                sum_distance += dist
            sum_list.append(sum_distance)
        avg_distance = float(np.median(sum_list)) / D_itme_array.shape[0]
        break
    return avg_distance
def compute_sd(D_matrix,predict_label_dict):
    D_matrix = D_matrix
    dstd = np.std(D_matrix)
    dvar = D_matrix.shape[0]*dstd*dstd
    sum_ci_var = 0.0
    center = []
    for key ,val in predict_label_dict.items():
        C_i_matrix = D_matrix[0]
        for i in val:
            C_i_matrix=np.row_stack((C_i_matrix,D_matrix[i-1]))
        np.delete(C_i_matrix,0,axis=0)
        c_i_std = np.std(C_i_matrix)
        c_i_var = C_i_matrix.shape[0]*c_i_std*c_i_std
        sum_ci_var+=c_i_std
        center.append(np.sum(C_i_matrix,axis=0)/float(C_i_matrix.shape[0]))
    scat = sum_ci_var/float(len(predict_label_dict)*dvar)
    return scat

class Evaluator():
    @staticmethod
    def compute_f1(dataset, bpr_optimizer, network_comparison, affinity_prop):
        D_matrix = construct_doc_matrix(bpr_optimizer.paper_latent_matrix,dataset.paper_list)
       #print(D_matrix)
        X_embedded = TSNE(n_components=2).fit_transform(D_matrix)
        x = []
        y = []
        for i in range(X_embedded.shape[0]):
            x.append(X_embedded[i][0])
            y.append(X_embedded[i][1])
        plt.scatter(x, y)
        plt.show()
        #print(x)
        #print(y)
        true_cluster_size = len(set(dataset.label_list))
        
        true_label_dict = {}
        for idx, true_lbl in enumerate(dataset.label_list):
            if true_lbl not in true_label_dict:
                true_label_dict[true_lbl] = [idx]
            else:
                true_label_dict[true_lbl].append(idx)
        predict_label_dict = {}
        y_pred = dbscan(D_matrix)
        print("Y_pred", y_pred)
        for idx, pred_lbl in enumerate(y_pred):
            if pred_lbl not in predict_label_dict:
                predict_label_dict[pred_lbl] = [idx]
            else:
                predict_label_dict[pred_lbl].append(idx)

        y_pred1 = ap(D_matrix)
        print("Y_pred1", y_pred1)
        predict_label_dict1 = {}
        for idx, pred_lbl in enumerate(y_pred1):
            if pred_lbl not in predict_label_dict1:
                predict_label_dict1[pred_lbl] = [idx]
            else:
                predict_label_dict1[pred_lbl].append(idx)
        avg_distance1 = compute_distance(D_matrix,predict_label_dict1)
        sd1 = compute_sd(D_matrix,predict_label_dict1)
        #print(sd1, "dbscan 距离")
        #print(avg_distance1,"距离")
    
        y_pred2 = xmeans(D_matrix)
        print("Y_pred2", y_pred2)
        predict_label_dict2={}
        for idx, pred_lbl in enumerate(y_pred2):
            if pred_lbl not in predict_label_dict2:
                predict_label_dict2[pred_lbl] = [idx]
            else:
                predict_label_dict2[pred_lbl].append(idx)
        sd2 = compute_sd(D_matrix, predict_label_dict2)
        #print(sd2, "ap 距离")
        #!!!!!!!!note NOW ONLY USING THE DBSCAN CLUSTERING ALGORITHM!!!!!!!!
        #predict_label_dict={}
        #if avg_distance1>1.75: #increased average distance so to increase requirements for affinity prop alg.
        if np.all(y_pred==y_pred2):
        #then x-means and DBSCAN are both in agreeance
             predict_label_dict = predict_label_dict
             print("...Using DBSCAN clustering result...XMEANS=DBSCAN!")
             disambig_alg = "DBSCAN"
        elif sd2>sd1 and avg_distance1>1.75 and network_comparison == True and affinity_prop == True:
             predict_label_dict=predict_label_dict2
             print("...Using affinity prop clustering result...")
             disambig_alg = "Affinity Propagation"
        else:
             predict_label_dict = predict_label_dict
             print("...Using DBSCAN clustering result...Default!")
             disambig_alg = "DBSCAN"

   #NOTE: NOW ONLY USING DBSCAN as clustering algorithm instead of afinity propogation and xmeans.     
        print(predict_label_dict, "predict_label_dict")
        print(true_label_dict, "true_label_dict")
        print(true_cluster_size, "True cluster size")
        # compute cluster-level F1
        # let's denote C(r) as clustering result and T(k) as partition (ground-truth)
        # construct r * k contingency table for clustering purpose
        r_k_table = []
        for v1 in predict_label_dict.values():
            k_list = []
            
            for v2 in true_label_dict.values():
                
                N_ij = len(set(v1).intersection(v2))
                k_list.append(N_ij)
            r_k_table.append(k_list)
        r_k_matrix = np.array(r_k_table)
        r_num = int(r_k_matrix.shape[0])
        # compute F1 for each row C_i
        #print(r_k_table)
        
        sum_f1 = 0.0
        sum_pre = 0.0
        sum_rec = 0.0
        for row in range(0, r_num):
            row_sum = np.sum(r_k_matrix[row,:])
            if row_sum != 0:
                max_col_index = np.argmax(r_k_matrix[row,:])
                row_max_value = r_k_matrix[row, max_col_index]
                prec = float(row_max_value) / row_sum
                col_sum = np.sum(r_k_matrix[:, max_col_index])
                rec = float(row_max_value) / col_sum
                row_f1 = float(2 * prec * rec) / (prec + rec)
                sum_f1 += row_f1
                sum_pre += prec
                sum_rec += rec
        # print len(y_pred)
        average_f1 =float(sum_f1) / r_num
        #average_f1 = float(sum_f1)
        average_pre = float(sum_pre) /r_num
        average_rec = float(sum_rec) /r_num
        return average_f1,average_pre,average_rec, predict_label_dict,disambig_alg

#################################################<END> ---EVAL_METRIC--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!







#################################################<START> ---MAIN--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#nltk.download('wordnet')

#if __name__ == "__main__":

#Getting list of author xml files from sample_data folder, using os.walk, returns a nested list, which
#is then collected using file_list[0] to obtain list unnested.

def get_median(data):
        data = sorted(data)
        size = len(data)
        if size % 2 == 0:   # 判断列表长度为偶数
            median = (data[size//2]+data[size//2-1])/2
            data[0] = median
        if size % 2 == 1:   # 判断列表长度为奇数
            median = data[(size-1)//2]
            data[0] = median
        return data[0]
    
F1_List = []
F1_Max_List = []
F1_Max_List_pre =[]
F1_Max_List_rec = []
f1_name = {}
def get_file_list(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        file_list.append(files)
    return file_list[0]
#file_list = get_file_list("../sampled_data/")
import time


def primary_or_secondary_main(file_path, ref_path,author_type,network_comparison=False, affinity_prop=False):
    place_holder = 0
    author_summary_dataframe = []
    failed_authors = 0
    disambiguated_authors = 0
    defaulted_reference_authors = 0
    main_count_dict = check_main_count()
    ref_count_dict = check_ref_count()
    file_path_list = file_path + "MAIN/"
    file_list = get_file_list(file_path_list)

    #print(file_list)

    #Sorting file list alphabetically
    file_list = sorted(file_list)
    #Unsure of exact purpose
    file_list = file_list[:]
    
    
    
    #counter
    cnt = 0
    copy_f1_list = []

    #Begins iteration for each author file going into main function.

    #Extracting primary authors:
    for x in file_list:
        final_count = 0
        cnt += 1
        filename = file_path + "MAIN/" + str(x)
        print(filename)
        print("count:" + str(cnt))
        print(time.strftime('%H:%M:%S', time.localtime(time.time())))
        F1_Max_List = []
        #for i in range(1):
            #main()
        #def main()
        #Disambiugation rule set and status reports:
        
        #Create a author_total_cnt_dict which records authors n papers for ref and main.
        #Condition where ref(n) > main(n) ? what to do there?
        #Disambiguation Rule 1: main(n) > 1 & ref(n) > 1 (Can attempt disambiguation) Status: Disambiguated (k clusters)|Disambiguated (1 cluster)
        #Disambiguation Rule 2: main(n) > 1 & ref(n) <= 1 & cluster(n) == 1 (Will take whole cluster - network comparison to ref not undertaken) Status: Disambiguated (1 cluster)
        #Else: Take reference network as authors paper set - provided by uni and verified ORCID profiles Status: Default Reference Network
        #If no main papers for author return: None Status: No author main network file
        #If no reference papers file for author: Status: No author reference file

        latent_dimen = 40
        alpha = 0.1  
        matrix_reg = 0.1
        num_epoch = 10
        sampler_method = 'uniform'
        dataset = DataSet(filename)
        #title_abstract_dict_original = dataset.reader_arnetminer()
        ego = dataset.reader_arnetminer()
        if ego in main_count_dict:
            main_counts = main_count_dict[ego]
        else:
            print(ego, "NOT IN main_count_dict - ?No main author file?")
            main_counts = 0
        if ego in ref_count_dict:
            ref_counts = ref_count_dict[ego]
        else:
            print(ego, "NOT IN ref_count_dict - ?No ref author file?")
            ref_counts = 0
            
        print("Main paper number for author", ego, "is",main_counts)
        print("Ref paper number for author", ego, "is",ref_counts)
        if main_counts > 1:
            bpr_optimizer = BprOptimizer(latent_dimen, alpha, matrix_reg)
            dd_sampler = LinkedDocGraphSampler()
            dt_sampler = DocumentTitleSampler()
            djconf_sampler = DocumentJConfSampler()
            pp_sampler = CoauthorGraphSampler()
            pd_sampler = BipartiteGraphSampler()
            dyear_sampler = DocumentYearSampler()
            dorg_sampler = DocumentOrgSampler()
            dabstract_sampler = DocumentAbstractSampler()
            eval_f1 = Evaluator()
            run_helper = TrainHelper()
            avg_f1,avg_pre,avg_rec,predict_label_dict_fin, graph,disambig_alg,network_comparison,affinity_prop = run_helper.helper(num_epoch, dataset, bpr_optimizer,
                eval_f1, sampler_method,filename, pp_sampler,pd_sampler,dd_sampler,
                dt_sampler,
               djconf_sampler,dorg_sampler,
              dyear_sampler,
               dabstract_sampler,network_comparison=False,affinity_prop=False)
            inexact_graph_edit_dist_cluster_dict = {}
            print(predict_label_dict_fin)
            cluster_count = len(predict_label_dict_fin)
            print(cluster_count,"cluster count")
        else:
            print("Disambiguation aborted: Main paper error - count is",main_counts)
            cluster_count = 0
        
            #Extracting primary authors reference networks:
            print("Attempting network comparison; reference network setup")
        if author_type == "PRIMARY" and ((main_counts>1 and ref_counts>1) or (cluster_count==1 and main_counts>1 and ref_counts<=1)) :
            print("Passed network comparison requirements:", "main count:",main_counts,"ref_count:",ref_counts,"cluster_count",cluster_count)
            reference_network_filename = ref_path  + str(x)
            reference_network_filename = reference_network_filename.split("_" + author_type + "_MAIN.xml")[0] + '_' + author_type + '_REF.xml'
            reference_network = DataSet(reference_network_filename)
            #reference_network.reader_arnetminer(title_abstract_dict_original)
            reference_network.reader_arnetminer()
            #Undertaking inexact graph edit distance against each cluster for most representative cluster for disambiugated author:
            print("TEST HERE!!!!!!!")
            print(set(predict_label_dict_fin.keys()))
            if (network_comparison == True) and len(predict_label_dict_fin) > 1 and ((not set(predict_label_dict_fin.keys()) == set([0,-1])) or (not set(predict_label_dict_fin.keys()) == set([-1,0]))):
                disambiguated_authors += 1
                for i in predict_label_dict_fin:
                    cluster = DataSet(filename, predicted_cluster_dict=predict_label_dict_fin, cluster_index=i)
                    cluster.reader_arnetminer()
                    #cluster.reader_arnetminer(title_abstract_dict_original)
                    inexact_graph_edit_dist_cluster_dict[i] = []
                  #  print("AT inexact_graph_edit_dist_cluster_dict[i] = []")
                  #  print(i, "i")
                    print(len(predict_label_dict_fin[i]))
                    inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.C_Graph,cluster.C_Graph))
                    inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.T_Graph,cluster.T_Graph))
                    inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.Jconf_Graph,cluster.Jconf_Graph))
    #Year graph instead of org graph as no ref orgs - inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.Org_Graph,cluster.Org_Graph))
                    inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.Year_Graph,cluster.Year_Graph))
                    inexact_graph_edit_dist_cluster_dict[i].append(graph_edit_dist.compare(reference_network.Abstract_Graph,cluster.Abstract_Graph))
                    print("Cluster GIED list created:", inexact_graph_edit_dist_cluster_dict[i])
                    print("FINAL inexact_graph_edit_dist_cluster_dict is!", inexact_graph_edit_dist_cluster_dict)
                    GED_cluster_avgs = [(i,mean(inexact_graph_edit_dist_cluster_dict[i])) for i in inexact_graph_edit_dist_cluster_dict]
                    print("Average GED for clusters is",GED_cluster_avgs)
                    best_average_GED_cluster = [999,999]
                    for cluster in inexact_graph_edit_dist_cluster_dict:
                        clust_avg = mean(inexact_graph_edit_dist_cluster_dict[cluster])
                        print("Cluster",cluster, "has average GED of",clust_avg)
                        if clust_avg < best_average_GED_cluster[1]:
                            best_average_GED_cluster = [cluster,clust_avg]
                            print("New best_average_GED_cluster is:",best_average_GED_cluster )
                    #Note: May need to add in a random.choice for when all GED avgs are the same - e.g. 2.0
                final_cluster_index = best_average_GED_cluster[0]
                print("final cluster for author is",final_cluster_index)
                final_count,disambiguated_author_profile= disambiguated_author_XMLconvertion(filename,file_path, x,ego,predict_label_dict_fin, final_cluster_index)
                disambiguated_authors += 1
                disambiguated_author_profile.to_excel("./DISAMBIGUATED_AUTHOR_PROFILES/"+ ego + "_AUTHOR_DISAMBIG_PROFILE.xls")
                #adding status to summary dataframe:
                author_summary_dataframe.append([ego,"Disambiguated (k clusters)",main_counts,ref_counts,cluster_count, final_count,disambig_alg,place_holder,"None"])
                    
            else:
                cluster_size_dict = dict()
                for index in set(predict_label_dict_fin.keys()):
                    print(index)
                    print(predict_label_dict_fin[index])
                    print(len(predict_label_dict_fin[index]))
                    cluster_size_dict[index] = len(predict_label_dict_fin[index])
                max_size = 0
                biggest_cluster = 0
                for cluster in cluster_size_dict.keys():
                    print(cluster)
                    if cluster_size_dict[cluster] > max_size:
                        print("cluster", cluster, "bigger then max_size:", max_size, "with length of", cluster_size_dict[cluster])
                        biggest_cluster = cluster
                        max_size = cluster_size_dict[cluster]
                    elif cluster_size_dict[cluster] >= max_size:
                        print("!TWO LARGE CLUSTERS THE SAME SIZE!")
                final_cluster_index = biggest_cluster
                
                # only 2 clusters or not wanting to use timely network comparison
                #non-optimized method, likely 2nd cluster is very small e.g. 2 papers - with
                #default being to choose the biggest cluster from DBSCAN as author representation and one most likely to be closest
                #to reference author dataset.

                print("Only one cluster for author, cluster index is", final_cluster_index)
                print("Final/biggest cluster is", final_cluster_index, "with paper indexes:",predict_label_dict_fin[final_cluster_index] )
                #Now saving cluster index papers for primary author to XML file:
                final_count, disambiguated_author_profile= disambiguated_author_XMLconvertion(filename,file_path, x,ego,predict_label_dict_fin, final_cluster_index)
                disambiguated_authors += 1
                print("SAVING DISAMBIGUATED AUTHOR PROFILE EXCEL")
                disambiguated_author_profile.to_excel("./DISAMBIGUATED_AUTHOR_PROFILES/"+ ego + "_AUTHOR_DISAMBIG_PROFILE.xls")
                #adding status to summary dataframe
                author_summary_dataframe.append([ego,"Disambiguated (1 cluster)",main_counts,ref_counts,cluster_count, final_count,disambig_alg,place_holder,"None"])
        else:
            print("Failed disambig comparison requirements defaulting to reference network:", "main count:",main_counts,"ref_count:",ref_counts,"cluster_count",cluster_count)
            if ref_counts > 0: #author has reference papers
                #Then take reference network as XML authors publciations.
                final_count = default_XMLconvertion(file_path,x,ref_path,author_type,ego)
                defaulted_reference_authors += 1
                #adding status to summary dataframe
                author_summary_dataframe.append([ego,"Default Reference Network",main_counts,ref_counts,cluster_count, final_count, "None",place_holder,"None"])
            else: #author has no reference papers
                print("Author failed disambiguation/network comparison and also failed default to reference network")
                print("Likely main count and ref count are both 0: Main:",main_counts,"Ref:",ref_counts)
                #add status to summary dataframe
                author_summary_dataframe.append([ego,"Failed",main_counts,ref_counts,cluster_count, final_count,"None",place_holder,"None"])
                failed_authors += 1
                '{} {}'.format(1, 2)
        #CONSIDER: Corrective - That way if disambiguation cuts out authors papers that were actually correct and that exist in uni database or ORCID profile these can be readded to add these back in?
       # if ref_counts>main_counts:
            #additionally if there are more reference papers then main papers will either add or prioritise exclusively reference papers.
            #though speak to Tim about this as to whether it would be a good idea to ta
    author_summary_dataframe = pd.DataFrame(author_summary_dataframe, columns = ['Name', 'Status', 'Main Count','Reference Count', 'Cluster Count', 'Final_count',"Unsupervised Clustering Method",'Read_Count',"Read_status"])                   
    return author_summary_dataframe, cnt, failed_authors, defaulted_reference_authors, disambiguated_authors        
                       
            
            #Concludes disambiugation.
#Notes, to-dos and considerations:
            #Note: included agreeance between xmeans and ABDSCAN algorithm - and increased distance for ap.
#                  or further consider using ABSDCAN only due to nature of author dataset-i.e using ids low lvl ambiguaty
#as opposed to direct name search approach without author ids provided~need to wait for test data (ground truth).
           #Note: One more author to correct: Slow bug
            #!!Note: Need to consider whether reference papers will be readded to final disambiguated at end!!
            #Could serve as a way to correct for any authors that had a significant amount of author papers removed.
#Consider moving to SQlite database instead of XML files.
            
#Author disambiguation and network comparison for primaru authors 
primary_path = "./PRIMARY_AUTHORS_XML/"
primary_ref = "./PRIMARY_AUTHORS_XML//REF/"
summary, cnt, failed_authors, defaulted_reference_authors, disambiguated_authors = primary_or_secondary_main(file_path=primary_path,ref_path=primary_ref, author_type="PRIMARY",network_comparison=False,affinity_prop=False)
display(summary.loc[0])

summary.to_csv("C:/Users/Liam Ephraims/Desktop/LiamDissertation/Evaluation/2-3 - Disambiguation and Network Comparison (IGM)/Disambiguation_summary.csv")
#################################################<END> ---MAIN--- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
print("...Disambiguation Complete...")
print("Of",cnt,"total author(s):")
print(failed_authors,"failed disambiguation and default reference author representation")
print(defaulted_reference_authors, "defaulted to reference network as author representation")
print(disambiguated_authors, " successfully disambiguated")



















    
