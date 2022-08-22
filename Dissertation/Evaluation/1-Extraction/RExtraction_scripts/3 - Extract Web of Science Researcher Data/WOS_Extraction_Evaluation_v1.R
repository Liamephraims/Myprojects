#Copyright © 2020 Liamephraims

library(dplyr)
library(ggplot2)
library(skimr)
library(wosr)
library(dplyr)
library(igraph)
library(visNetwork)
library(stringr)
library(easyPubMed)
library(rorcid)
library(rscopus)


#Using this SPHERE UTS-UNSW Based Dataset from the Department of Medicine UNSW, we will apply our recommendation collaboration methdology
#focused on this cohort of researchers and with this dataset and additionally associated papers and grants datasets for these researchers
#allowing for valdiation - thus this dataset will be named 'Valdiation dataset' and UTS_researchers interchangeably.

#install.packages("wosr")
library(wosr)
# Get session ID using IP-Address (Note: Wifi-IP needs to be at any institution who has access to Web of Science account- university)
sid <- auth(NULL, NULL)


#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\University_Input_datasets"
setwd(dir)
getwd()
dir()

Extraction_summary_df <- data.frame(Name=NA, WOS_Total=NA,WOS_ID_Successful=NA,WOS_ORCID_Successful=NA, OVERALL_WOS_STATUS=NA)


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


###First test for extracting Web of Science authors and papers from Web of science API using SPHERE Dataset of Cohort UTS Researchers in Validation Dataset
#Based on the 'Gathering Bibliometric Information from the Scopus API using wosr' from the Johns Hopkins Bloomberg School of Public Health authored by John Muschelli, 2018.
#<Covers both rscopus and bibliometrix packages>

#Subsetting for Researchers at UTS Cohort who have a WOS ID (inclusive of duplicates):
UNSW_WOS_SUBSET <- UTS_researchers[((UTS_researchers$RESEARCHER.ID != '')&(!is.na(UTS_researchers$RESEARCHER.ID)))|
                                        ((UTS_researchers$ORCID.ID != '')&(!is.na(UTS_researchers$ORCID.ID))),]
UNSW_WOS_SUBSET$RESEARCHER.ID <- as.character(UNSW_WOS_SUBSET$RESEARCHER.ID)
print(paste("Initial amount of UTS researchers in validation dataset is",length(UTS_researchers$RESEARCHER.ID), 
            "With only", length(UNSW_WOS_SUBSET$RESEARCHER.ID), "of these researchers with Researcher IDs OR ORCID IDS"))
#10 WOS researcher IDS or ORCiD IDs in total.




#This will be our vector of WOS ID researchers for data extraction and vizualisation:
WOS_vector <- as.character(UTS_researchers$RESEARCHER.ID)
NAME_vector <- UTS_researchers$SURNAME
ORCID_vector <- as.character(UTS_researchers$ORCID.ID)





#############GET_PAPERS FOR WOS API##############################################################################
#Get an author's papers and all co-authors names and papers:
#ID <- WOS_vector[8]
#Preparing W-O-S specific ResearcherIDs - AI= Author Identifiers
##query1 <- paste0('AI=(\"',ID,'\")')
#test <- pull_wos(query1, sid = sid)
#x <- test


#Pull affiliation data for each author within get_papers function.
getaffil <- function(y, x, papers){
  print("Beginning")   
  ADDRESS_COL <- 4
  if (!is.null(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3]))
  {print('null')
    Addy_nums <- as.array(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3])
    print("initial addy numbers are:")
    print(Addy_nums)
    
    #Taking first affiliation if more than 1 affiliation for author (first by default) to avoid error 
    if (length(x$author[x$author$ut==papers[y,2],3]) != length(Addy_nums) & length(Addy_nums)!=0 )
      #create a new list for addy_nums array:
      
    {#find each author
      print("entered addy num 2")
      addy_nums2 <- list()
      for (i in 1:nrow(x$author[x$author$ut==papers[y,2],])) {
        row <- i #researcher
        
        author_no <-x$author[x$author$ut==papers[y,2],][row, 2]
        print("author_no is:")
        print(author_no)
        #Does each author have 1 or more addresses?
        if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) > 1)
          #than researcher has more then 1 address - so we will take the first as default
          #If so, take the first addresses only for this author
        { 
          test <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]
          print(paste("test is:", test))
          
          test2 <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]
          print(paste("test2 is:", test2))
          if (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test, ADDRESS_COL] != 0)) 
          {
            print(paste("trying to make addy_nums2[i]: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]}
          else if  (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test2, ADDRESS_COL] != 0)) 
          { print(paste("test1 failed - trying to make addy_nums2[i] 4 test2: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]}
          else
          { 
            print("failed test 2 - making NA for researcher with > 1 addresses")
            addy_nums2[i] <- NA}
        }
        #Otherwise, add in researchs only address to new address array:
        else if(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 1) {
          print("Using resarchers only address, as nrows for author == 1")
          
          addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][,2]}
        else if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 0 |
                 is.null(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),])))
        {print("Making resarchers only address NA, as nrows for author not == 0 | is.null(researchers address no.)")
          addy_nums2[i] <- NA }
      }
      #Replace address numbers array with updated address number array only taking first address for each 
      #author as default to correct unequal rows in get papers when extracting address data.
      Addy_nums <- as.array(unlist(addy_nums2))
      print("New addy numbers are")
      print(Addy_nums)
    }
    print('MID')
    for (i in 1:length(Addy_nums))
    {
      print(Addy_nums[i])  
      if (length(Addy_nums) == 0 )
      {Addy_nums[i] <- NA}
      
      else {Addy <- x$address[x$address$ut == papers[y,2] & x$address$addr_no == Addy_nums[i], ADDRESS_COL] 
      print(paste("here",Addy))
      if (length(Addy) == 0)
      {Addy_nums[i] = NA}
      else 
      {Addy_nums[i] = Addy}}
      
    }
    return(Addy_nums)}
  
  else {print("end")
    return(NA)}}


#Pull city data for each author within get_papers function.
getcity <- function(y, x, papers){
  print("Beginning")   
  ADDRESS_COL <- 5
  if (!is.null(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3]))
  {print('null')
    Addy_nums <- as.array(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3])
    print("initial addy numbers are:")
    print(Addy_nums)
    
    #Taking first affiliation if more than 1 affiliation for author (first by default) to avoid error 
    if (length(x$author[x$author$ut==papers[y,2],3]) != length(Addy_nums) & length(Addy_nums)!=0 )
      #create a new list for addy_nums array:
      
    {#find each author
      print("entered addy num 2")
      addy_nums2 <- list()
      for (i in 1:nrow(x$author[x$author$ut==papers[y,2],])) {
        row <- i #researcher
        
        author_no <-x$author[x$author$ut==papers[y,2],][row, 2]
        print("author_no is:")
        print(author_no)
        #Does each author have 1 or more addresses?
        if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) > 1)
          #than researcher has more then 1 address - so we will take the first as default
          #If so, take the first addresses only for this author
        { 
          test <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]
          print(paste("test is:", test))
          
          test2 <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]
          print(paste("test2 is:", test2))
          if (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test, ADDRESS_COL] != 0)) 
          {
            print(paste("trying to make addy_nums2[i]: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]}
          else if  (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test2, ADDRESS_COL] != 0)) 
          { print(paste("test1 failed - trying to make addy_nums2[i] 4 test2: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]}
          else
          { 
            print("failed test 2 - making NA for researcher with > 1 addresses")
            addy_nums2[i] <- NA}
        }
        #Otherwise, add in researchs only address to new address array:
        else if(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 1) {
          print("Using resarchers only address, as nrows for author == 1")
          
          addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][,2]}
        else if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 0 |
                 is.null(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),])))
        {print("Making resarchers only address NA, as nrows for author not == 0 | is.null(researchers address no.)")
          addy_nums2[i] <- NA }
      }
      #Replace address numbers array with updated address number array only taking first address for each 
      #author as default to correct unequal rows in get papers when extracting address data.
      Addy_nums <- as.array(unlist(addy_nums2))
      print("New addy numbers are")
      print(Addy_nums)
    }
    print('MID')
    for (i in 1:length(Addy_nums))
    {
      print(Addy_nums[i])  
      if (length(Addy_nums) == 0 )
      {Addy_nums[i] <- NA}
      
      else {Addy <- x$address[x$address$ut == papers[y,2] & x$address$addr_no == Addy_nums[i], ADDRESS_COL] 
      print(paste("here",Addy))
      if (length(Addy) == 0)
      {Addy_nums[i] = NA}
      else 
      {Addy_nums[i] = Addy}}
      
    }
    return(Addy_nums)}
  
  else {print("end")
    return(NA)}}

#Pull country data for each author within get_papers function.
getcountry <- function(y, x, papers){
  print("Beginning")   
  ADDRESS_COL <- 7
  if (!is.null(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3]))
  {print('null')
    Addy_nums <- as.array(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3])
    print("initial addy numbers are:")
    print(Addy_nums)
    
    #Taking first affiliation if more than 1 affiliation for author (first by default) to avoid error 
    if (length(x$author[x$author$ut==papers[y,2],3]) != length(Addy_nums) & length(Addy_nums)!=0 )
      #create a new list for addy_nums array:
      
    {#find each author
      print("entered addy num 2")
      addy_nums2 <- list()
      for (i in 1:nrow(x$author[x$author$ut==papers[y,2],])) {
        row <- i #researcher
        
        author_no <-x$author[x$author$ut==papers[y,2],][row, 2]
        print("author_no is:")
        print(author_no)
        #Does each author have 1 or more addresses?
        if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) > 1)
          #than researcher has more then 1 address - so we will take the first as default
          #If so, take the first addresses only for this author
        { 
          test <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]
          print(paste("test is:", test))
          
          test2 <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]
          print(paste("test2 is:", test2))
          if (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test, ADDRESS_COL] != 0)) 
          {
            print(paste("trying to make addy_nums2[i]: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]}
          else if  (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test2, ADDRESS_COL] != 0)) 
          { print(paste("test1 failed - trying to make addy_nums2[i] 4 test2: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]))
            addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]}
          else
          { 
            print("failed test 2 - making NA for researcher with > 1 addresses")
            addy_nums2[i] <- NA}
        }
        #Otherwise, add in researchs only address to new address array:
        else if(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 1) {
          print("Using resarchers only address, as nrows for author == 1")
          
          addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][,2]}
        else if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 0 |
                 is.null(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),])))
        {print("Making resarchers only address NA, as nrows for author not == 0 | is.null(researchers address no.)")
          addy_nums2[i] <- NA }
      }
      #Replace address numbers array with updated address number array only taking first address for each 
      #author as default to correct unequal rows in get papers when extracting address data.
      Addy_nums <- as.array(unlist(addy_nums2))
      print("New addy numbers are")
      print(Addy_nums)
    }
    print('MID')
    for (i in 1:length(Addy_nums))
    {
      print(Addy_nums[i])  
      if (length(Addy_nums) == 0 )
      {Addy_nums[i] <- NA}
      
      else {Addy <- x$address[x$address$ut == papers[y,2] & x$address$addr_no == Addy_nums[i], ADDRESS_COL] 
      print(paste("here",Addy))
      if (length(Addy) == 0)
      {Addy_nums[i] = NA}
      else 
      {Addy_nums[i] = Addy}}
      
    }
    return(Addy_nums)}
  
  else {print("end")
    return(NA)}}

#Pull state data for each author within get_papers function.
getstate <- function(y, x, papers){
  print("Beginning")   
  ADDRESS_COL <- 6
  if (!is.null(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3]))
  {print('null')
    Addy_nums <- as.array(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no %in% x$author[x$author$ut == papers[y,2],2]),3])
  print("initial addy numbers are:")
  print(Addy_nums)
  
  #Taking first affiliation if more than 1 affiliation for author (first by default) to avoid error 
  if (length(x$author[x$author$ut==papers[y,2],3]) != length(Addy_nums) & length(Addy_nums)!=0 )
    #create a new list for addy_nums array:
    
  {#find each author
    print("entered addy num 2")
    addy_nums2 <- list()
    for (i in 1:nrow(x$author[x$author$ut==papers[y,2],])) {
      row <- i #researcher
      
      author_no <-x$author[x$author$ut==papers[y,2],][row, 2]
      print("author_no is:")
      print(author_no)
      #Does each author have 1 or more addresses?
      if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) > 1)
        #than researcher has more then 1 address - so we will take the first as default
        #If so, take the first addresses only for this author
      { 
        test <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]
        print(paste("test is:", test))
        
        test2 <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]
        print(paste("test2 is:", test2))
        if (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test, ADDRESS_COL] != 0)) 
        {
          print(paste("trying to make addy_nums2[i]: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]))
          addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][1,2]}
        else if  (length(x$address[x$address$ut == papers[y,2] & x$address$addr_no == test2, ADDRESS_COL] != 0)) 
        { print(paste("test1 failed - trying to make addy_nums2[i] 4 test2: ",x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]))
          addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][2,2]}
        else
        { 
          print("failed test 2 - making NA for researcher with > 1 addresses")
          addy_nums2[i] <- NA}
      }
      #Otherwise, add in researchs only address to new address array:
      else if(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 1) {
        print("Using resarchers only address, as nrows for author == 1")
        
        addy_nums2[i] <- x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),][,2]}
      else if (nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),]) == 0 |
               is.null(nrow(x$author_address[(x$author_address$ut == papers[y,2]) & (x$author_address$author_no == author_no),])))
      {print("Making resarchers only address NA, as nrows for author not == 0 | is.null(researchers address no.)")
        addy_nums2[i] <- NA }
    }
    #Replace address numbers array with updated address number array only taking first address for each 
    #author as default to correct unequal rows in get papers when extracting address data.
    Addy_nums <- as.array(unlist(addy_nums2))
    print("New addy numbers are")
    print(Addy_nums)
  }
  print('MID')
  for (i in 1:length(Addy_nums))
  {
    print(Addy_nums[i])  
    if (length(Addy_nums) == 0 )
    {Addy_nums[i] <- NA}
    
    else {Addy <- x$address[x$address$ut == papers[y,2] & x$address$addr_no == Addy_nums[i], ADDRESS_COL] 
    print(paste("here",Addy))
    if (length(Addy) == 0)
    {Addy_nums[i] = NA}
    else 
    {Addy_nums[i] = Addy}}
    
  }
  return(Addy_nums)}
  
  else {print("end")
    return(NA)}}



get_papers <- function(x){
  #Extracting all authors papers with DOI, ut (WOS -specific paper idenitifer) & titles
  
  papers <- data.frame(title = x$publication$title,
                       ut = x$publication$ut,
                       doi   = x$publication$doi)
  #View(papers)
  if (!nrow(papers)==0){
    paper.doi <- lapply(1:nrow(papers), function(y){
      if(length(papers!=0)){
        if(!is.na(papers[y,3]) & !(papers[y,3] == '')) 
        {return(list(as.character(x$publication$doi[y])))}
        else if ((is.na(papers[y,3])|(papers[y,3] == '')) & (!is.na(papers[y,2]) & !(papers[y,2] == '') ))
        {return(list(as.character(papers[y,2])))}
        
        else
        {return(NA)}}})
    #View(paper.doi)
    #y <- 1
    
    
      your.papers <- lapply(1:nrow(papers), function(y){
    
        if(nrow(papers[y,]) == 0 | is.na(papers[y,])){
          data.frame(doi=NA,daisng_id=NA, firstname=NA,surname=NA ,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA)
        } else {
          #print(getaffil(y, x))
          #print(getstate(y, x))
          #print(getcountry(y, x))
          #print(x$publication[x$publication$ut == papers[y,2],2])
          #print(x$publication[x$publication$ut == papers[y,2],7])
          #print(x$author[x$author$ut==papers[y,2],3])
          #print(length(x$author[x$author$ut==papers[y,2],3]))
          #View(x$publication[x$publication$ut == "WOS:000443552200002",])
          #x$author[x$author$ut== "WOS:000443552200002",]
          #x$address[x$author_address$addr_no ==1 & x$author_address$ut== "WOS:000443552200002",]
         # View(papers)
        
          data.frame(doi = paper.doi[[y]][[1]]
                     ,daisng_id = x$author[x$author$ut==papers[y,2],7],
                     firstname = x$author[x$author$ut==papers[y,2],"first_name"],
                     surname = x$author[x$author$ut==papers[y,2],"last_name"],
                     ut = as.character(papers[y,2]),
                     abstract = x$publication[x$publication$ut == papers[y,2],7],
                     title = x$publication[x$publication$ut == papers[y,2],2],
                     venue = x$publication[x$publication$ut == papers[y,2],3],
                     date = str_split(as.character(x$publication[x$publication$ut == papers[y,2],4]), "-")[[1]][1],
                     affil = getaffil(y, x, papers),
                     city = getcity(y, x, papers),
                     state = getstate(y, x, papers),
                     country = getcountry(y, x, papers),
                     stringsAsFactors = FALSE)
        }})
      #View(your.papers)
      }  
     else {your.papers <- data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA) }
      do.call(rbind.data.frame, your.papers)
}

#TESTING/DEBUGGING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#test_index 
#ID <- ifelse(WOS_vector[i] != "", WOS_vector[i], ORCID_vector[i])
#Preparing W-O-S specific ResearcherIDs - AI= Author Identifiers
##query1 <- paste0('AI=(\"',ID,'\")')
#x <- pull_wos(query1, sid = sid)

#x$publication$date
#test <-  get_papers(pull_wos(query1, sid = sid))


#Firstly, we will get the papers (get_papers) for all researchers that have UNIQUE researcher/ORCID IDs from our WOS validation dataset vector.
print(paste("There are", length(WOS_vector), " researchers with scopus IDs - commencing data extraction - possibly including duplicates"))

#Extracting co-authors of each researcher and concatenating into a list of coauthors for each primary author+DOI+scopus_id - this will thereby get all first-order networks of each researcher.
all.coauthors_first_order <- list()
#for (i in 1:length(WOS_vector))
  for (i in 1:length(WOS_vector))
    
{ cat(i, "of", length(WOS_vector), "WOS=", WOS_vector[i], "\n")
  if ((WOS_vector[i] != '') & (!is.na(WOS_vector[i])) & !WOS_vector[i] == "\"\"")
    { ID <- WOS_vector[i]
    #Preparing W-O-S specific ResearcherIDs - AI= Author Identifiers
      query1 <- paste0('AI=(\"',ID,'\")')
      test <- pull_wos(query1, sid = sid)
      if (nrow(test$publication) > 0)
      # Download data for Researcher ID query for get papers function
      {all.coauthors_first_order[i] <- list(get_papers(pull_wos(query1, sid = sid)))
      print("WOS Extraction Successful")
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"SUCCESSFUL","NOT-REQUIRED","SUCCESSFUL")}
      else if (nrow(test$publication) == 0)
      {
        print("WOS Researcher ID Extraction was unsuccessful - defaulting to ORCID Extraction")
        ID <- ORCID_vector[i]
        if ((ID != '') & (!is.na(ID)))
        {
                if (nchar(ID) == 19)
                  
                    {
                  query1 <- paste0('AI=(\"',ID,'\")')
                  test <- pull_wos(query1, sid = sid)
                  if (nrow(test$publication) > 0)
                    # Download data for Researcher ID query for get papers function
                      {all.coauthors_first_order[i] <- list(get_papers(pull_wos(query1, sid = sid)))
                      print("ORCID Extraction Successful")
                      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"UNSUCCESSFUL","SUCCESSFUL","SUCCESSFUL")}
                  else if (nrow(test$publication) == 0)
                  {print(paste("ORCID ID extraction unsuccessful making", i, "NA dataframe"))
                   all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA))}
                  Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"UNSUCCESSFUL","UNSUCCESSFUL","UNSUCCESSFUL")
                   #   all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA, name=NA, ut=NA))
                    #print(paste(i, "is ORCID ID with length", length(ID), "allowing for PUBMED ORCID ID extraction to be attempted"))
                    #myQuery <- str_c(unlist(str_split(ID, '-')), collapse='')
                    #myIdList <- get_pubmed_ids(myQuery)
                    #if (myIdList$Count > 0)
                    #{
                    #  t <- fetch_pubmed_data(pubmed_id_list = myIdList, retmax =myIdList$RetMax, retstart = myIdList$RetStart)
                    #  t2 <- table_articles_byAuth(t, included_authors = "all", getKeywords = TRUE)  
                    #  all.coauthors_first_order[i] <- list(get_papers_pubmed(t2))
                    #  print("PUBMED ORCID ID extraction was successful")
                  #    
                   # }
                  #  else if (myIdList$Count == 0)
                   # { "PUBMED ORCID ID UNSUCCESSFUL, attempting to use SCOPUS WITH ORCID ID as substitute"
                    #   test <- author_data(au_id=WOS_vector[i], searcher='ORCID')
                     #  if (length(test$entries) > 1)
                    #        {all.coauthors_first_order[i] <- list(get_papers_SCOPUS(test))
                    #         print("Successfully extracted using SCOPUS WITH ORCID ID")}
                    ##       {print(paste("ORCID ID SCOPUS extraction unsuccessful making", i, "NA dataframe"))
                      #   all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA, name=NA, ut=NA))
                }
          else if (nchar(ID) != 19)
          {print(paste(ID, "is not a ORCID identifer with length of", length(ID), "thus ORCID extraction unsuccessful - defaulting to NULL"))
            all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA))
            Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"UNSUCCESSFUL","NOT-PROVIDED","UNSUCCESSFUL")}}
        }
        
  
  }
    
    
  else if  ((ORCID_vector[i] != '') & (!is.na(ORCID_vector[i])) & (ORCID_vector[i] !="\"\"") )
    {
       print(paste(WOS_vector[i], "is either NA or '', defaulting to ORCID identifer:, ", ORCID_vector[i]))
       ID <- ORCID_vector[i]
       if (nchar(ID) == 19)
        
      {
        query1 <- paste0('AI=(\"',ID,'\")')
        test <- pull_wos(query1, sid = sid)
        if (nrow(test$publication) > 0)
          # Download data for Researcher ID query for get papers function
        {all.coauthors_first_order[i] <- list(get_papers(test))
        print("ORCID Extraction Successful")
        Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],length(unique(all.coauthors_first_order[i][[1]]$doi)),"NOT-PROVIDED","SUCCESSFUL","SUCCESSFUL")}
        else if (nrow(test$publication) == 0)
        {print(paste("ORCID ID extraction unsuccessful making", i, "NA dataframe"))
         all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA))
         Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","UNSUCCESSFUL","UNSUCCESSFUL")}
        #   all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA, name=NA, ut=NA))
        #print(paste(i, "is ORCID ID with length", length(ID), "allowing for PUBMED ORCID ID extraction to be attempted"))
        #myQuery <- str_c(unlist(str_split(ID, '-')), collapse='')
        #myIdList <- get_pubmed_ids(myQuery)
        #if (myIdList$Count > 0)
        #{
        #  t <- fetch_pubmed_data(pubmed_id_list = myIdList, retmax =myIdList$RetMax, retstart = myIdList$RetStart)
        #  t2 <- table_articles_byAuth(t, included_authors = "all", getKeywords = TRUE)  
        #  all.coauthors_first_order[i] <- list(get_papers_pubmed(t2))
        #  print("PUBMED ORCID ID extraction was successful")
        #    
        # }warnings()
        #  else if (myIdList$Count == 0)
        # { "PUBMED ORCID ID UNSUCCESSFUL, attempting to use SCOPUS WITH ORCID ID as substitute"
        #   test <- author_data(au_id=WOS_vector[i], searcher='ORCID')
        #  if (length(test$entries) > 1)
        #        {all.coauthors_first_order[i] <- list(get_papers_SCOPUS(test))
        #         print("Successfully extracted using SCOPUS WITH ORCID ID")}
        ##       {print(paste("ORCID ID SCOPUS extraction unsuccessful making", i, "NA dataframe"))
        #   all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA, name=NA, ut=NA))
      }
      else if (nchar(ID) != 19)
      {print(paste(ID, "is not a ORCID identifer with length of", length(ID), "thus ORCID extraction unsuccessful - defaulting to NULL"))
        all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA))
        Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","NOT-PROVIDED","UNSUCCESSFUL")}}
    else if  ( ((WOS_vector[i] == '') | (is.na(WOS_vector[i]))) & ((ORCID_vector[i] == '') | (ORCID_vector[i] == "\"\"") | (is.na(ORCID_vector[i]))) )
    {
      print(paste(WOS_vector[i], " WOS ID is NA or '' - defaulting to NA and", ORCID_vector[i], "ORCID ID is also NA or ''- making NA dataframe"))
      all.coauthors_first_order[i] <- list(data.frame(doi=NA,daisng_id=NA,firstname=NA,surname=NA,ut=NA,abstract=NA,title=NA,venue=NA,date=NA,affil=NA,city=NA,state=NA,country=NA))
      Extraction_summary_df[i, ] <- c(UTS_researchers$name_clean[i],0,"NOT-PROVIDED","NOT-PROVIDED","UNSUCCESSFUL")
    }

  }
View(all.coauthors_first_order)

#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data"
setwd(dir)
getwd()
dir()

Extraction_summary_df_WOS <- Extraction_summary_df
save(Extraction_summary_df_WOS, file = "Extraction_summary_df_WOS_v1.Rdata")

all.coauthors_first_order_WOS_EVAL_v1 <- all.coauthors_first_order
save(all.coauthors_first_order_WOS_EVAL_v1, file = "all.coauthors_first_order_WOS_EVAL_v1.Rdata")
View(all.coauthors_first_order_WOS_EVAL_v1)





       