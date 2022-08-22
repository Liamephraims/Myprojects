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

#Extraction Summary:
Extraction_summary_df <- data.frame(Name=NA, SCOPUS_Total=NA,SCOPUS_ID_Successful=NA,ORCID_ID_Successful=NA, OVERALL_SCOPUS_STATUS=NA)

#Using this SPHERE UTS-UNSW Based Dataset from the Department of Medicine UNSW, we will apply our recommendation collaboration methdology
#focused on this cohort of researchers and with this dataset and additionally associated papers and grants datasets for these researchers
#allowing for valdiation - thus this dataset will be named 'Valdiation dataset' and UTS_researchers interchangeably.


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
UTS_PUBLICATIONS$cleaned_author_list[row] <- cleaned_author_list
}


#Subsetting for Researchers at UTS Cohort who have a Scopus ID (inclusive of duplicates):
UNSW_SCOPUS_SUBSET <- UTS_researchers[((UTS_researchers$SCOPUS.ID != '')&(!is.na(UTS_researchers$SCOPUS.ID)))|((UTS_researchers$ORCID.ID != '')&(!is.na(UTS_researchers$ORCID.ID))),]
UNSW_SCOPUS_SUBSET$SCOPUS.ID <- as.character(UNSW_SCOPUS_SUBSET$SCOPUS.ID)
print(paste("Initial amount of UTS researchers in validation dataset is",length(UTS_researchers$SCOPUS.ID), 
            "With only", length(UNSW_SCOPUS_SUBSET$SCOPUS.ID), "of these researchers with Scopus IDs OR a supplementary ORCID ID"))
#10 SCOPUS IDS in total.
# 10 ORCID IDS total.
#Note above subset not being used in pipeline.


#This will be our vector of scopus ID researchers for data extraction and vizualisation:
SCOPUS_vector <- as.character(UTS_researchers$SCOPUS.ID)
NAME_vector <- UTS_researchers$SURNAME
ORCID_vector <- as.character(UTS_researchers$ORCID.ID)


#Having accessed Scopus website and requested API authorisation key, which we have saved and stored implicitly we will first test to ensure this key is present:

key = get_api_key()
if (have_api_key())
{print("Have API Key")} else {"Failed: No API Key detected"}




#########################GET PAPERS FOR SCOPUS API!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!BEGIN
#Getting paper dois for author:
get_doi <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$df$`prism:doi`
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    if(is.na(x)){data.frame(value=NA)}
    else
    {data.frame(value = x)}}
  ))
}
#Function to pull affiliations for authors in get_papers:
getaffil <- function(y, x){
  print(y)
  print("getaffil")
  auth_affil_ids <- as.array(x$full_data$author[x$full_data$author$entry_number==y,]$`afid.$`)
  print(paste(auth_affil_ids, "auth_affil_ids"))
  if (length(auth_affil_ids) != 0){
    
    for (i in 1:length(auth_affil_ids)){
      print(paste(auth_affil_ids[i], "auth_affil_ids[i]"))
      print(paste(x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids[i] & x$full_data$affiliation$entry_number == y,  "affilname"], "replacement"))
      
      if (is.na(auth_affil_ids[i]) | auth_affil_ids[i] == ''| auth_affil_ids[i] == ' ') {auth_affil_ids[i] <- NA}
      else{print("!PRINTING CHECK HERE!")
        print(x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids[i] & x$full_data$affiliation$entry_number == y,  "affilname"])
        check <- x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids[i] & x$full_data$affiliation$entry_number == y,  "affilname"]
      if (length(check) > 0){
        if (!check == ''& !check == ' ' &!is.na(check)) {auth_affil_ids[i]  <- check}}
      else {auth_affil_ids[i] <- NA}
      }}
    print("getaffil-end")
    return(auth_affil_ids)
  }
  else {return(NA)}}


#Function to pull countries for authors in get_papers:
getcountry <- function(y, x){
  print(y)
  print("getcountry")
  auth_affil_ids <- as.array(x$full_data$author[x$full_data$author$entry_number==y,]$`afid.$`)
  print(paste(auth_affil_ids, "auth_affil_ids"))
  if (length(auth_affil_ids) != 0){
    
    for (i in 1:length(auth_affil_ids)){
      print(paste(auth_affil_ids[i], "auth_affil_ids[i]"))
      print(paste(x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids[i] & x$full_data$affiliation$entry_number == y,  "affiliation-country"], "replacement"))
      
      if (is.na(auth_affil_ids[i]) | auth_affil_ids[i] == ''|auth_affil_ids[i] == ' ') {auth_affil_ids[i] <- NA}
      else{check <- x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids[i] & x$full_data$affiliation$entry_number == y,  "affiliation-country"]
      print(check)
      if (length(check) > 0){
        if (!check == ''& !check == ' ' &!is.na(check)) {auth_affil_ids[i]  <- check}}
      else {auth_affil_ids[i] <- NA}
      }}
    print("getcountry-end")
    return(auth_affil_ids)
    
  }
  else {return(NA)}}

#!!!!!!!!!!!!BUG IN SCOPUS ABSTRACT EXTRACTION - constant instead of indexer!!!!!!!1! 05/06/2020
getabstract <- function(y, paper.doi, papers){
  #print(y)
  #print(paper.doi[[y]][[1]])
  print("abstract")
  abstract = abstract_retrieval(paper.doi[[y]][[1]], identifier = "doi")
  print(abstract)
  if (length(abstract$content) != 0) {
  if (length(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts) != 0)
  {return(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)}
  else {abstract2 <- abstract_retrieval(papers[y,][4], identifier = "scopus_id") 
  if (length(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)!= 0){
    print("abstract-end")
    return(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)}
  
  else if ((length(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)== 0))
  {return(NA)}}}
  else {return(NA)}
  }


#Getting pubmed ids for later PubMed data extraction for author based on papers
get_pubid <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$df$`pubmed-id`
  if (is.null(list.x)){list.x <-  rep(NA, length(x$df$`dc:title`))}
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    
    if(is.na(x)){
      data.frame(value=NA)}
    
    else
      
    {data.frame(value = x)}}
  ))}

#Getting scopus identifier ids for documents in case DOI for papers are missing
#thus preventing co-authors and papers being missed.
get_dc_scop_id <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$df$`dc:identifier`
  if (is.null(list.x)){list.x <-  rep(NA, length(x$df$`dc:title`))}
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    
    if(is.na(x)){
      data.frame(value=NA)}
    
    else
      
    {data.frame(value = x)}}
  ))}

#TESTINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG-----------test <- author_data(au_id=SCOPUS_vector[1])
#Get an author's papers and all co-authors names and papers:

#x <- author_data(au_id=SCOPUS_vector[1])
#CLOSEST THING TO PUB DATE IN SCOPUS IS COVERDATE!
#str_split(x$full_data$df$`prism:coverDate`, "-")[[1]][1]


get_papers <- function(x){
  
  papers <- data.frame(title = x$df$`dc:title`,
                       doi   = get_doi(x),
                       pubmedid = get_pubid(x),
                       scop_dcID = get_dc_scop_id(x))
  # View(papers)
  
  paper.doi <- lapply(1:nrow(papers), function(y){
    if(length(papers!=0)){
      if(!is.na(papers[y,2])) 
      {return(as.character(check_dois(papers[y,2][1])$good))}
      
      else if (is.na(papers[y,2]) & !is.na(papers[y,4]))
      {return(list(as.character(papers[y,4])))}
      
      else
      {return(NA)}}})
  #View(paper.doi)
  
  your.papers <- lapply(1:length(paper.doi), function(y){
    if(length(paper.doi[[y]]) == 0 | is.na(paper.doi[[y]])){
      data.frame(doi=NA, title=NA,abstract =NA,Venue=NA,scopus=NA, firstname=NA,surname=NA ,initials=NA, pubmedid = NA,affil=NA, country = NA, year = NA)
    } else {
      
      #print(x$full_data$affiliation[x$full_data$affiliation$afid == auth_affil_ids & x$full_data$affiliation$entry_number == y,  "affilname"])
      
      
      #print(getcountry(y))
      #print(as.array(x$full_data$author[x$full_data$author$entry_number == y, c("initials")]))
      #print(y)
      #print(getaffil(y))
      #print(length(getaffil(y)))
      #print(nchar(getaffil(y)))
      #print(paste(paper.doi[[y]][[1]], "DOIIII"))
      #print(getabstract(y))
      
      #print(as.array(paste(x$full_data$author[x$full_data$author$entry_number == y, c("given-name")], x$full_data$author[x$full_data$author$entry_number == y, c("surname")])))
      data.frame(doi = paper.doi[[y]][[1]],
                 
                 title = as.character(x$df[x$df$entry_number == y, c("dc:title")]),
                 abstract = getabstract(y, paper.doi, papers),
                 Venue = as.character(x$df[x$df$entry_number == y, c("prism:publicationName")]),
                 scopus = as.array(x$full_data$author[x$full_data$author$entry_number == y, c("authid")]),
                 firstname = as.array(paste(x$full_data$author[x$full_data$author$entry_number == y, c("given-name")])),
                 surname = as.array(x$full_data$author[x$full_data$author$entry_number == y, c("surname")]),
                 initials = as.array(x$full_data$author[x$full_data$author$entry_number == y, c("initials")]),
                 pubmedid = as.character(papers[y,3]),
                 affil =  getaffil(y, x),                 
                 country = getcountry(y, x),
                 year =  as.character(x$df[x$df$entry_number == y, c("prism:coverDate")]),
                 stringsAsFactors = FALSE)
    }})
  
  
  do.call(rbind.data.frame, your.papers)
} 
#!!!!!!!!!!!!!!!!!!!!!!!SCOPUS GET PAPERS FINISHED~~~~~~~~~~~~~~~~~~~~~~~~~~



#Firstly, we will get the papers (get_papers) for all researchers that have UNIQUE scopus IDs from our scopus validation dataset vector.
print(paste("We have", length(SCOPUS_vector), "unique researchers with scopus IDs - commencing data extraction"))

#Extracting co-authors of each researcher and concatenating into a list of coauthors for each primary author+DOI+scopus_id - this will thereby get all first-order networks of each researcher.
all.coauthors_first_order <- list()
for (i in 1:length(UTS_researchers$SURNAME))

  { cat(i, "of", length(SCOPUS_vector), "scopus=", SCOPUS_vector[i], "\n")
  if (!is.na(SCOPUS_vector[i]) & !SCOPUS_vector[i]=='' & !SCOPUS_vector[i]=="\"\"" )
  {
    print("Scopus i not NA, beginning scopus ID extraction")
    test <- author_data(au_id=SCOPUS_vector[i])
   # View(test$full_data$author)
    
    
    if (length(test$entries) > 1)
    {print(paste("NON-NA SCOPUS ID - Entered:length(test$entries > 1)", length(test$entries)))
      all.coauthors_first_order[i] <- list(get_papers(test))
      print("SCOPID Extraction was successful.")
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"SUCCESSFUL","NOT-ATTEMPTED","SUCCESSFUL")

      }
    else if (length(test$entries) == 1)
    {print(paste("NON-NA SCOPUS ID - Entered:length(test$entries == 1)", length(test$entries)))
      print(paste("SCOPID Extraction was NOT successful, attempting ORCID ID input into SCOPUS API as alternative, using", ORCID_vector[i]))
      test <- author_data(au_id=ORCID_vector[i], searcher='ORCID')
      
      if (length(test$entries) > 1)
      {all.coauthors_first_order[i] <- list(get_papers(test))
      print("Successfully extracted using ORCID ID")
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"UNSUCCESSFUL","SUCCESSFUL","SUCCESSFUL")

      }
      else if (length(test$entries)==1) 
      {print(paste("ORCID extraction unsuccessful making", i, "NA dataframe"))
        all.coauthors_first_order[i] <- list(data.frame(doi=NA, title=NA,abstract =NA,Venue=NA,scopus=NA, firstname=NA,surname=NA ,initials=NA, pubmedid = NA,affil=NA, country = NA,year=NA))
        Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"UNSUCCESSFUL","UNSUCCESSFUL","UNSUCCESSFUL")
}
        
      }}
  
  else if (is.na(SCOPUS_vector[i]) |SCOPUS_vector[i]=='')
  {print(paste(i, "SCOPUS", SCOPUS_vector[i], "is NA will attempt using ORCID ID in SCOPUS API instead:", ORCID_vector[i]))
    if (!is.na(ORCID_vector[i]) & nchar(ORCID_vector[i])==19)
      
    {
      test <- author_data(au_id=ORCID_vector[i], searcher='ORCID')
      if (length(test$entries) > 1) {all.coauthors_first_order[i] <- list(get_papers(test))
      print("Successfully extracted using ORCID ID in SCOPUS")
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"NOT-PROVIDED","SUCCESSFUL","SUCCESSFUL")}
      else if (length(test$entries)==1) 
      { #print(paste("ORCID extraction unsuccessful making attempting using ORCID ID in Web-Of-Science API"))
        #ID <- ORCID_vector[i]
        #Preparing W-O-S specific ResearcherIDs - AI= Author Identifiers
        #query1 <- paste0('AI=(\"',ID,'\")')
        # Download data for Researcher ID query for get papers function
        #test <- pull_wos(query1, sid = sid)
        #if (nrow(test$publication) > 0)
        #{
        #print("Web-of-Science extraction successful")
        #all.coauthors_first_order[i] <- list(get_papers_WOS(test))}
        #else if (nrow(test$publication) == 0)
        #{
        
        
        # print("WOS ORCID ID UNSUCCESSFUL, attempting to use PUBMED WITH ORCID ID as substitute")
        #  myQuery <- str_c(unlist(str_split(ORCID_vector[i], '-')), collapse='')
        #  myIdList <- get_pubmed_ids(myQuery)
        #  if (myIdList$Count > 0)
        # {
        #    t <- fetch_pubmed_data(pubmed_id_list = myIdList, retmax =myIdList$RetMax, retstart = myIdList$RetStart)
        #    t2 <- table_articles_byAuth(t, included_authors = "all", getKeywords = TRUE)  
        #    all.coauthors_first_order[i] <- list(get_papers_pubmed(t2))
        print(paste("ORCID extraction unsuccessful making", i, "NA dataframe"))
        all.coauthors_first_order[i] <- list(data.frame(doi=NA, title=NA,abstract =NA,Venue=NA,scopus=NA, firstname=NA,surname=NA ,initials=NA, pubmedid = NA,affil=NA, country = NA,year=NA))
        Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","UNSUCCESSFUL","UNSUCCESSFUL")
      } 
    }
    
    else {print(paste("WARNING: NONE CAPTURED BY SCOPUS EXTRACT OR SCOPUS USING ORCID ID OR WOS/PUBMED EXTRACTS DEFAULTING TO NA DATAFRAME"))
      all.coauthors_first_order[i] <- list(data.frame(doi=NA, title=NA,abstract =NA,Venue=NA,scopus=NA, firstname=NA,surname=NA ,initials=NA, pubmedid = NA,affil=NA, country = NA,year=NA))
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","NOT-PROVIDED","UNSUCCESSFUL")}
  }
}
#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data"
setwd(dir)
getwd()
dir()

Extraction_summary_df_SCOPUS <- Extraction_summary_df
save(Extraction_summary_df_SCOPUS, file = "Extraction_summary_df_SCOPUS_v1.Rdata")


all.coauthors_first_order_SCOPUS_EVALv1 <- all.coauthors_first_order 
save(all.coauthors_first_order_SCOPUS_EVALv1, file = "all.coauthors_first_order_SCOPUS_EVALv1.Rdata")
View(all.coauthors_first_order_SCOPUS_EVALv1)

#all.df <- do.call(rbind.data.frame,all.coauthors_first_order_SCOPUS_EVALv1)
#View(all.df)

