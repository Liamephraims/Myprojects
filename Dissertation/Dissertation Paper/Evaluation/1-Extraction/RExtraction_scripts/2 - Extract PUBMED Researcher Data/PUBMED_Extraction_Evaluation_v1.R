#Copyright © 2020 Liamephraims

library(easyPubMed)
library(dplyr)
library(ggplot2)
library(skimr)
library(rorcid)
library(dplyr)
library(igraph)
library(visNetwork)
library(stringr)
library(rorcid)
library(rscopus)

#install.packages("wosr")
library(wosr)
# Get session ID using IP-Address (Note: Wifi-IP needs to be at any institution who has access to Web of Science account- university)
sid <- auth(NULL, NULL)

#Using this SPHERE UTS-UNSW Based Dataset from the Department of Medicine UNSW, we will apply our recommendation collaboration methdology
#focused on this cohort of researchers and with this dataset and additionally associated papers and grants datasets for these researchers
#allowing for valdiation - thus this dataset will be named 'Valdiation dataset' and UTS_researchers interchangeably.
Extraction_summary_df <- data.frame(Name=NA, PUBMED_Total=NA,PUBMED_ORCID_Successful=NA, OVERALL_PUBMED_STATUS=NA)


#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\University_Input_datasets"
setwd(dir)
getwd()
dir()
#Loading in the SPHERE Researchers Dataset:
UTS_researchers <- read.csv("TEST_10_SAMPLE_data_RESEARCHERS.csv", 
                            header = TRUE, 
                            quote="\"", 
                            stringsAsFactors= TRUE, 
                            strip.white = TRUE)


UTS_researchers$name_clean <- sapply(1:nrow(UTS_researchers),function(y){
  
  lname <- str_to_upper(str_trim(UTS_researchers$SURNAME[y]))
  lname_clean <- str_split(lname, " |-|'")
  lname_clean <- paste(lname_clean[[1]], sep="",collapse="")
  print(lname_clean)
  fname <-str_sub(str_to_upper(str_trim(UTS_researchers$FIRST_NAME[y])),1,1)
  print(fname)
  return(paste(lname_clean,fname,sep=",",collapse=","))
})



#Loading in Validation Dataset:
UTS_PUBLICATIONS <- read.csv("TEST_10_SAMPLE_data_PUBS_MASTER.csv", 
                             header = TRUE, 
                             quote="\"", 
                             stringsAsFactors= TRUE, 
                             strip.white = TRUE)

#View(UTS_PUBLICATIONS)
#cleaning for publications valdiation:
for (row in 1:nrow(UTS_PUBLICATIONS))
  
{
  if (UTS_PUBLICATIONS$RE_flag[row] != "no"){
    re_key = UTS_PUBLICATIONS$RE_flag[row]
    #UTS_PUBLICATIONS$ALL_AUTHORS[row] <- str_replace(as.character(UTS_PUBLICATIONS$ALL_AUTHORS[row]), "-|'","")
    test <- str_trim(str_replace(as.character(UTS_PUBLICATIONS$ALL_AUTHORS[row]), "-|'|\\*",""))
    
    authors = str_extract_all(as.character(test), "\\w+, \\w+")
    print(authors)
  }
  #Koh, E-S
  if (UTS_PUBLICATIONS$RE_flag[row] == "no"){
    test <- str_trim(str_replace(as.character(UTS_PUBLICATIONS$ALL_AUTHORS[row]), "-|'|\\*",""))
    between_split_key = as.character(UTS_PUBLICATIONS$ALL_COAUTHORS_KEY[row])
    authors = str_split(as.character(test), between_split_key)
    print(authors)
  }
  #authors <- "Crotty, M; Gnanamanickam, ES; Cameron, I;Agar, M; Ratcliffe, J ; Laver, K"
  
  #3 authors = str_split(authors, ";")
  #  within_AUTH_key = ","
  #  class(authors)
  
  within_AUTH_key = UTS_PUBLICATIONS$within_AUTH_key[row]
  if (within_AUTH_key == ""){
    within_AUTH_key = " "
  }
  print('within_AUTH_key')
  print(within_AUTH_key)
  name_schema <- as.character(UTS_PUBLICATIONS$name_schema[row])
  print("name_schema")
  print(name_schema)
  list_index <- 0
  cleaned_author_list <- list()
  cleaned_author_list[1] = ""
  for (i in 1:length(authors[[1]])){
    
    
    
    name = str_split(authors[[1]][i], as.character(within_AUTH_key))
    index <- 0
    cleaned_name <- list()
    cleaned_name[[1]] = " "
    for (j in 1:length(name[[1]])){
      # j <- 1
      
      print(name[[1]][j])
      
      if (name[[1]][j] != ""){
        index <- index + 1
        cleaned_name[[1]][index] <- name[[1]][j]
      }
    }
    name <-  cleaned_name
    
    print("name")
    print(name)
    if (name_schema == "last,first"){
      lname <- name[[1]][1]
      fname <-  substr(name[[1]][length(name[[1]])],1,1)
      print(lname)
      print(fname)
      cleaned <- paste(str_to_upper(str_trim(lname)),str_to_upper(str_trim(fname)), collapse=",", sep=",")
    }
    if (name_schema == "first,last")
    { lname <- name[[1]][length(name[[1]])]
    fname <- substr(name[[1]][1],1,1)
    print(lname)
    print(fname)
    cleaned <- paste(str_to_upper(str_trim(lname)),str_to_upper(str_trim(fname)), collapse=",", sep=",")
    }
    list_index <- list_index + 1
    cleaned_author_list[[1]][list_index] = cleaned
  }
  cleaned_author_list <- paste(unlist(cleaned_author_list), collapse="; ")
  UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED[row] <- cleaned_author_list
}


#REMOVED:Subsetting for Researchers at UTS Cohort who have an ORCID ID (inclusive of duplicates):
#UNSW_ORCID_SUBSET <- UTS_researchers[(UTS_researchers$ORCID.ID != '')&(!is.na(UTS_researchers$ORCID.ID)),]

#Now taking all researchers.
UNSW_ORCID_SUBSET <- UTS_researchers
UNSW_ORCID_SUBSET$ORCID.ID <- as.character(UNSW_ORCID_SUBSET$ORCID.ID)
print(paste("Initial amount of UTS researchers in validation dataset is",length(UTS_researchers$ORCID.ID)))
#41 out of 46 researchers with ORCID ids

#Here is a character vector of all researcher of the UTS cohort with ORCID IDS
ORCID_COLUMN <- UNSW_ORCID_SUBSET$ORCID.ID
NAME_vector <-  UNSW_ORCID_SUBSET$SURNAME
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!GET_PAPERS FUNC FOR PUBMED API!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Getting paper dois for author:
get_doi <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$doi
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    if(is.na(x)){data.frame(value=NA)}
    else
    {data.frame(value = x)}}
  ))
}

#Getting pubmed ids for later PubMed data extraction for author based on papers
get_pubid <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$pmid
  if (is.null(list.x)){list.x <-  rep(NA, length(x$title))}
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    
    if(is.na(x)){
      data.frame(value=NA)}
    
    else
      
    {data.frame(value = x)}}
  ))}


get_papers <- function(x){
  
  papers <- data.frame(title = x$title,
                       doi   = get_doi(x),
                       pubmedid = get_pubid(x))
  
  paper.doi <- lapply(1:nrow(papers), function(y){
    if(length(papers!=0)){
      if(!is.na(papers[y,2]) & !(papers[y,2] == '')) 
      {return(as.character(check_dois(papers[y,2][1])$good))}
      
      else if ((is.na(papers[y,2])|(papers[y,2] == '')) & (!is.na(papers[y,3]) & !(papers[y,3] == '') ))
      {return(list(as.character(papers[y,3])))}
      
      else
      {return(NA)}}})
  
  your.papers <- lapply(1:length(paper.doi), function(y){
    if(length(paper.doi[[y]]) == 0 | is.na(paper.doi[[y]])){
      data.frame(doi=NA, surname=NA, firstname=NA, pubmedid = NA, venue=NA, affil=NA,title=NA,abstract=NA,month=NA,year=NA)
    } else {
      #NOTE this is likely buggy
      data.frame(doi = paper.doi[[y]][[1]],
                 surname = x$lastname,
                 firstname = x$firstname,
                 pubmedid = as.character(papers[y,3]),
                 venue = x$journal, #Journal
                 affil = x$address, #affil
                 title = x$title, #title
                 abstract = x$abstract, 
                 month = x$month,
                 year = x$year,
                 #UNSURE IF CAN GET CITY/COUNTRY - IN ADDRESS?
                 stringsAsFactors = FALSE)}})
  do.call(rbind.data.frame, your.papers)
  
}

#i <- 1
#myQuery <- str_c(unlist(str_split(ORCID_COLUMN[i], '-')), collapse='')
#myIdList <- get_pubmed_ids(myQuery)
#t <- fetch_pubmed_data(pubmed_id_list = myIdList, retmax =myIdList$RetMax, retstart = myIdList$RetStart)
#t2 <- table_articles_byAuth(t, included_authors = "all", getKeywords = TRUE)  




#Extracting co-authors of each researcher and concatenating into a list of coauthors for each primary author+DOI+scopus_id - this will thereby get all first-order networks of each researcher.
all.coauthors_first_order_PUBMED_DISAMB_v1 <- list()
for (i in 1:length(ORCID_COLUMN))
{ cat(i, "of", length(ORCID_COLUMN), "ORCID=", ORCID_COLUMN[i], "\n")
  if (!is.na(ORCID_COLUMN[i]) & (nchar(ORCID_COLUMN[i]) == 19) & !ORCID_COLUMN[i] == "\"\""){
    myQuery <- str_c(unlist(str_split(ORCID_COLUMN[i], '-')), collapse='')
    myIdList <- get_pubmed_ids(myQuery)
    if (myIdList$Count > 0)
    {
      t <- fetch_pubmed_data(pubmed_id_list = myIdList, retmax =myIdList$RetMax, retstart = myIdList$RetStart)
      t2 <- table_articles_byAuth(t, included_authors = "all", getKeywords = TRUE)  
      all.coauthors_first_order_PUBMED_DISAMB_v1[i] <- list(get_papers(t2))
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order_PUBMED_DISAMB_v1[i][[1]]$doi)),"SUCCESSFUL","SUCCESSFUL")
    }
    else {
          print(paste(i, "- Empty myIdList$IdList for", ORCID_COLUMN[i], "with Idlist value of", myIdList$IdList, "& query string of:", myQuery))
          #print("Attempting to extract coauthors and papers using ORCID input into Web-of-Science as alternative measure")
          #ID <- ORCID_COLUMN[i]
          #Preparing W-O-S specific ResearcherIDs - AI= Author Identifiers
          #query1 <- paste0('AI=(\"',ID,'\")')
          # Download data for Researcher ID query for get papers function
          #test <- pull_wos(query1, sid = sid)
        #if (nrow(test$publication) > 0)
        #  {
        #    print("Web-of-Science extraction successful")
        #    all.coauthors_first_order[i] <- list(get_papers_WOS(pull_wos(query1, sid = sid)))}
        #else if (nrow(test$publication) == 0)
         #       {
          #HERE TO
          
          #  print("WOS ORCID ID UNSUCCESSFUL, attempting to use SCOPUS WITH ORCID ID as substitute")
            #test <- author_data(au_id=ORCID_COLUMN[i], searcher='ORCID')
            #if (length(test$entries) > 1)
            #{all.coauthors_first_order[i] <- list(get_papers_SCOPUS(test))
            #print("Successfully extracted using SCOPUS WITH ORCID ID")}
            #else if (length(test$entries)==1) 
            #{print(paste("ORCID ID SCOPUS extraction unsuccessful making", i, "NA dataframe"))
        print("ORCID Unsuccessful, returning empty list for researcher")    
        all.coauthors_first_order_PUBMED_DISAMB_v1[i] <- list(data.frame(doi=NA, surname=NA, firstname=NA,  pubmedid = NA, venue=NA, affil=NA,title=NA,abstract=NA,month=NA,year=NA))
        y <- y + 1
        Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"UNSUCCESSFUL","UNSUCCESSFUL")
        
            #}
        
            
            
            
        #}
          
          
          
          
          #END
          }
  }
  else
  {print("ORCID ID Unsuccessful, returning empty list for researcher")    
    all.coauthors_first_order_PUBMED_DISAMB_v1[i] <- list(data.frame(doi=NA, surname=NA, firstname=NA,  pubmedid = NA, venue=NA, affil=NA,title=NA,abstract=NA,month=NA,year=NA))
    Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","UNSUCCESSFUL")
    y <- y + 1}}
#print(paste("Overall, there were", y, "ORCID queries that were rejected or did not return matching PUBMED IDs AND alternatively could not use Web-of-Science/ORCID query"))
print(paste("Overall, there were", y, "ORCID queries that were rejected"))

all.coauthors_first_order_EVAL_v1 <- all.coauthors_first_order_PUBMED_DISAMB_v1
View(all.coauthors_first_order_EVAL_v1)


#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data"
setwd(dir)
getwd()
dir()

Extraction_summary_df_PUBMED <- Extraction_summary_df
save(Extraction_summary_df_PUBMED, file = "Extraction_summary_df_PUBMED_v1.Rdata")


save(all.coauthors_first_order_EVAL_v1, file = "all.coauthors_first_order_PUBMED_EVAL_v1.Rdata")
View(all.coauthors_first_order_EVAL_v1)









