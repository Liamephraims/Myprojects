#Copyright © 2020 Liamephraims

#Primary authors:
library(XML)
library(xml2)
library(stringr)
library(rscopus)
library(rorcid)

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

#Loading in Validation Dataset:
UTS_PUBLICATIONS <- read.csv("TEST_10_SAMPLE_data_PUBS_MASTER.csv", 
                             header = TRUE, 
                             quote="\"", 
                             stringsAsFactors= TRUE, 
                             strip.white = TRUE)
#Removing duplicate researcher records (do to more than 1 row for researchers with > 1 IDs) as this creates bug in extraction.

UTS_researchers <- UTS_researchers[UTS_researchers$ORCID.ID != "",]
#View(UTS_PUBLICATIONS)
#cleaning for publications valdiation:
for (row in 1:nrow(UTS_PUBLICATIONS))
#  row <- 1
{
  if (UTS_PUBLICATIONS$RE_flag[row] != "no"){
    re_key = UTS_PUBLICATIONS$RE_flag[row]
    print(re_key)
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
  
  within_AUTH_key = as.character(UTS_PUBLICATIONS$within_AUTH_key[row])
  print(within_AUTH_key)
  if (within_AUTH_key == "" | within_AUTH_key == "\"\"" ){
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
   #i <- 1
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
  print(cleaned_author_list)
  print("HEREEE")
  cleaned_author_list <- paste(unlist(cleaned_author_list), collapse="; ")
  print(cleaned_author_list)
  UTS_PUBLICATIONS$cleaned_author_list[row] <- cleaned_author_list
}


#cleaning for publications valdiation:
x <- str_split(UTS_PUBLICATIONS$cleaned_author_list, ";")

UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED <- sapply(1:length(x), function(i) {
  #i <- 579
  #j <- 1
  name_cleaned <- sapply(1:length(x[[i]]), function(j){
    name <- str_split(str_trim(x[[i]][j])," |-|'|,")
    if (length(name[[1]]) <= 2){
      lname <- name[[1]][1]
      if (str_trim(lname) == ",") {
        lname <- "NA"
      }
      fname <- str_sub(name[[1]][2],1,1)
      if (str_trim(fname) == ",") {
        fname <- "NA"
      }
      
      }
    if (length(name[[1]]) > 2){
      lname <- paste(name[[1]][1:length(name[[1]])-1],sep="",collapse="")
      if (str_trim(lname) == ",") {
        lname <- "NA"
      }
      fname <- str_sub(name[[1]][length(name[[1]])],1,1)
      if (str_trim(fname) == ",") {
        fname <- "NA"
      }
    }
    cleaned <-   str_to_upper(paste(lname,fname,sep=","))
    return(cleaned)})
  
  return(unlist(name_cleaned))})
UTS_PUBLICATIONS <- UTS_PUBLICATIONS[,c("ALL_AUTHORS_CLEANED", "ARTICLE_CHAPTER_PAPER_TITLE", "JOURNAL_TITLE","YEAR")]
#"VITTORIO,O" %in% unique(unlist(UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED))
#View(UTS_PUBLICATIONS)

#Getting paper abstracts from scopus using DOIs & SCOPUS IDs


#Potentially do not need this - as title_abstract_dict contains all abstracts for all titles extracted,
#therefore can be used for primary and secondary author - same as scopus extraction.

#getabstract <- function(y){
 # abstract = abstract_retrieval(UTS_PUBLICATIONS$DOI[y], identifier = "doi")
  #if (length(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts) != 0)
#  {return(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)}
 # else {abstract2 <- abstract_retrieval(UTS_PUBLICATIONS$SCOPUS.ID[y], identifier = "scopus_id") 
  #if (length(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)!= 0)
  #  return(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)
  
  #else if ((length(abstract2$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)== 0))
  #{return(NA)}}}
#UTS_PUBLICATIONS$abstract_scopus <- 
#!!!!!!!!!!!!BUG IN SCOPUS ABSTRACT EXTRACTION - constant instead of indexer!!!!!!!1! 05/06/2020


#!!!!!!!Function for ORCID profile merging with reference networks for all or some of authors (all for study)?!!!!!!!!!!!
getabstract <- function(x){
  print("GETTING ABSTRACT...")
  abstract = abstract_retrieval(papers[x,2], identifier = "doi")
  if (length(abstract$content) != 0){
    if (length(abstract$content$`abstracts-retrieval-response`) != 0){
  if (length(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts) != 0)
  {return(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts)}}}
  else {return(NA)}}

get_doi <- function(x){
  #  This pulls the DOIs out of the ORCiD record:
  list.x <- x$`external-ids.external-id`
  
  #  We have to catch a few objects with NULL DOI information:
  do.call(rbind.data.frame,lapply(list.x, function(x){
    
    if(length(x)==0){data.frame(value=NA)}
    else
    {
      if(((!'doi' %in% x[,1]) & (!'DOI' %in% x[,1]) )){
        data.frame(value=NA)
      } else{
        data.frame(value = x[which(x[,1] %in% 'doi'|x[,1] %in% 'DOI'),2])
      }}
  }))
}
#test <- get_papers(x)
#View(test)
#length(unique(test$title))
#x <- orcid_works(UTS_researchers$ORCID.ID[2])
get_papers <- function(x){
#View(x)
#all.coauthors_first_order <- test
#orcid_df <- do.call(rbind.data.frame,list(all.coauthors_first_order))
#View(orcid_df)  
#length(unique(orcid_df$doi))
  
  
  all.papers <- x[[1]][[1]] # this is where the papers are.
  org_temp <- NA
  try( org_temp <- orcid_employments(UTS_researchers$ORCID.ID[j])[[1]]$`affiliation-group`$summaries[[1]][23])
  if (is.null(org_temp)) {org_temp <- NA}
  print(paste('Org temp (organisation) is', org_temp))
  jconf <- as.character(all.papers$`journal-title.value`)
  if (is.null(jconf)) {jconf <- NA}
  
  papers <- data.frame(title = all.papers$'title.title.value',
                       doi   = get_doi(all.papers),
                       org = org_temp,
                       jconf = jconf,
                       date = all.papers$`publication-date.year.value`
                       
  )
  
  
  paper.doi <- lapply(1:nrow(papers), function(h){
    if(length(papers!=0)){
      if(!is.na(papers[h,2])) 
      {return(orcid_doi(dois = check_dois(papers[h,2])$good, fuzzy = FALSE))}
      else
      {return(NA)}}})
  

  your.papers <- lapply(1:length(paper.doi), function(x){
    print("ENTERED")
    if(length(paper.doi[[x]]) == 0 || is.na(paper.doi[[x]])){
     #data.frame(doi=NA, orcid=NA, name_clean=NA, organisation=NA,jconf=NA,date=NA,abstract=NA, title = NA)
      data.frame(doi=NA, orcid=NA, name_clean=NA, organisation=NA,jconf=NA,date=NA, title = NA)
      
    } else {
      name_vec <- c()
      print("HERE1")
      name_space <- orcid_person(paper.doi[[x]][[1]]$'orcid-identifier.path')
      if (length(name_space)>0){
        for (j in 1:length(name_space))
        {
          if (length(name_space[[j]]$name$`given-names`$value)==0 & length(name_space[[j]]$name$`family-name`$value==0)){
            name_vec <- NA}
          else if(length(name_space[[j]]$name$`given-names`$value)>0 & length(name_space[[j]]$name$`family-name`$value>0))
          {
            name_vec[j] <- paste(name_space[[j]]$name$`given-names`$value, name_space[[j]]$name$`family-name`$value, sep=' ')
          }
          
          else if ((is.null(name_space[[j]]$name$`given-names`$value) & is.null(name_space[[j]]$name$`family-name`$value)))
          {#print("NAME SPACE IS NULL!!!!!!!!!!!!!!!!!!!!!!!!!!")
            name_vec <- NA}
          else {print("ELSE EXCEPTION - CONDITION NOT CAUGHT FOR NAME_SPACE")
            print(paste("VALUE IS:",name_space[[j]]$name$`given-names`$value, ":name_space[[j]]$name$`given-names`$value - FINAL"))
            print(paste("VALUE IS:",name_space[[j]]$name$`family-name`$value, "name_space[[j]]$name$`family-names`$value - FINAL"))}
          
        }}
      print("HERE2")
      data.frame(doi = papers[x,2],
                 orcid = paper.doi[[x]][[1]]$'orcid-identifier.path',
                 name_clean = name_vec,
                 organisation = papers[x,3],
                 jconf = papers[x,4],
                 date = papers[x,5],
                 title = papers[x,1],
                 #abstract = getabstract(x),
                 stringsAsFactors = FALSE)
    }})
  do.call(rbind.data.frame, your.papers)
}



#for (i in 1:nrow(UTS_PUBLICATIONS)){
#  UTS_PUBLICATIONS$abstract[i] <- getabstract(i)
#}
# Creating abstract XML file for primary reference network.

#Moving to correct directory:
dir <- "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison"
setwd(dir)
getwd()
dir()

UTS_researchers$name_clean <- sapply(1:nrow(UTS_researchers),function(y){
  
  lname <- str_to_upper(str_trim(UTS_researchers$SURNAME[y]))
  lname_clean <- str_split(lname, " |-|'")
  lname_clean <- paste(lname_clean[[1]], sep="",collapse="")
  print(lname_clean)
  fname <-str_sub(str_to_upper(str_trim(UTS_researchers$FIRST_NAME[y])),1,1)
  print(fname)
  return(paste(lname_clean,fname,sep=",",collapse=","))
})
#REMOVE: JACOBS,C + VITTORIO,O also throws an error.
#unique(UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED)
#sample_authors <- list("VITTORIO,O", "AGAR,M","ANAZODO,A", "BARTON,M","GREBELY,J","BUTLER,T","DELANEY,G", "JAFFE,A","ROBERTS,T",
#                       "BAJOREK,B",
#                       "BEBAWY,M",
#                       "BERLE,D",
#                       "BRYANT,L",
##                       "DUA,K",
#                       "FREEMANSANDERSON,A",
#                       "GOLZAN,M", "JACOBS,C", "GROVE,R", "HEMSLEY,B", "KENNEDY,D") 
#FOR DISSERTATION AS ONLY USING 10 SAMPLE AUTHORS TO EVALUATE TOOL WILL ONLY EXTRACT FOR THESE 10:
#unique_authors <- unique(UTS_researchers[!UTS_researchers$name_clean %in% sample_authors, ]$name_clean) #look at this.
unique_authors <- unique(UTS_researchers$name_clean)
#FOR DISSERTATION AS ONLY USING 10 SAMPLE AUTHORS TO EVALUATE TOOL WILL ONLY EXTRACT FOR THESE 10:
#unique_authors <- list("VITTORIO,O", "AGAR,M","ANAZODO,A", "BARTON,M","GREBELY,J","BUTLER,T","DELANEY,G",
#                       "JAFFE,A" ,"ROBERTS,T") #look at this.
#TIM CHURCHES

#Extracting authors papers for each university author:
for (i in 1:length(unique_authors)){
  pub_title_list <- list()
  pub_count <- 1
  ego <- unique_authors[i]
  print(paste(ego, "ego"))
  for (j in 1:nrow(UTS_PUBLICATIONS))
  {
    pub_author_list <- UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED[[j]]
    #print(pub_author_list)
    if (ego %in% pub_author_list & !(as.character(UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE[j]) %in% pub_title_list)) {
      pub_title_list[pub_count] <- as.character(UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE[j])
      print(pub_count)
      pub_count <- pub_count + 1
      UTS_PUBLICATIONS$ALL_AUTHORS_CLEANED[j]
    }}
  if (length(pub_title_list)>0){
    
    UTS_researchers$AUTHOR_PUBS[i] <- paste(unlist(pub_title_list),sep="<>", collapse="<>")
    UTS_researchers$pub_count[i] <- pub_count-1
  }
  else {print(paste(pub_title_list, "not accepted possibly empty (no pubs for author, trying ORCID extraction for author", ego))
    UTS_researchers$AUTHOR_PUBS[i] <- NA
    UTS_researchers$pub_count[i] <- pub_count-1}
  print("AUTHOR HAS NO PAPERS!!!!!!!!!!!!!!!!!!!")
}

#NOTE: IF NOT CONFERENCES ALREADY MERGED INTO JOURNAL THEN NEEDS TO BE UPDATED FOR THIS:

#iew(UTS_researchers[is.na(UTS_researchers$AUTHOR_PUBS),])
UTS_PUBLICATIONS$Venue <- as.character(UTS_PUBLICATIONS$JOURNAL_TITLE)

#ADD ORCIDS PAPERS TO PRIMARY AUTHOR PIPELINE?

#<!!!!!!!!!!!!!!!!!ADDING ORCIDS EXTRACTION HERE FOR PRIMARY AUTHORS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!>

#Creating total publication count dictionary for main and refs for primary authors:
total_cnt_df_ref <- data.frame("author" <- NA,"ref_total_count"<- NA)
colnames(total_cnt_df_ref)[1] <- "author"
colnames(total_cnt_df_ref)[2] <- "ref_total_count"
rownames(total_cnt_df_ref) <- c()


#!!!!!!!!!!!!!!!!!!BEGINNING OF PRIMARY_REF XML FILE PREP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Creating the abstract_title.txt for author disambiguation algorithm for primary.
#Get primary ref network XML files ready.
#Check to see that ref network pipeline is the same for main pipeline.
#if ORCID ID then attempt ORCID extraction for supplement to reference network:
  #name matching between UNI database and ORCID DBS.
#i <- 1
#for (j in 2:2){  #note: 1 is bajorek
#j <- 2
#q <- 2
#TESTING:
Extraction_summary_df <- data.frame(Name=NA, ORCID_REF_Total=NA, OVERALL_ORCID_STATUS=NA)

#UTS_researchers <- UTS_researchers[UTS_researchers$name_clean == "MEHTA,P",]
for (j in 1:nrow(UTS_researchers)){
  ego <- UTS_researchers$name_clean[j]
  title_doi_list <- list()
  doi_count <- 1
  pub_cnt <- 0
  duplicate_count <- 0
  ego_pub_list <- unique(str_split(UTS_researchers$AUTHOR_PUBS[j],"<>")[[1]])

  #Creating the XML raw file Tree format root for author 
  prefix.xml <- "
  <author_set>
</author_set>
  "
  doc = xmlTreeParse(prefix.xml, useInternalNodes = T,addFinalizer = TRUE) 
  root = xmlRoot(doc)  #FIND ROOT 
  #firstname tag# 
  FnameNode = newXMLNode("FullName",ego, parent=root)
  print("Beginning XML extraction for university dbs extraction datasets for researcher reference network")
 
  
  for (i in 1:length(ego_pub_list)){
    dup <- FALSE
   # doi <- str_to_lower(str_trim(as.character(unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$DOI)[[1]])))
    title <- str_to_lower(str_trim(as.character(unique(ego_pub_list[i]))))
    #Cleaning author title:
    if (!is.na(title)){
      if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
        print(paste("Cleaning  title:",substr(title, nchar(title), nchar(title)),"from title end:",title))
        title <- substr(title,1,nchar(title)-1)
      }
      if (str_detect(substr(title, 1, 1), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
        print(paste("Cleaning  title:",substr(title, 1, 1),"from title beginning:",title))
        title <- substr(title,2,nchar(title))
      }}
    
   # if (!doi %in% title_doi_list & !title %in% title_doi_list & !is.na(title)){
    if (!title %in% title_doi_list & !is.na(title)){
      
  #    print(paste("doi", doi, "and title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
      print(paste("title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
     # if (!is.na(doi) & !doi == " ")   
     #   { #title_doi_list[doi_count] <- doi
      #   doi_count <- doi_count + 1}
      title_doi_list[doi_count] <- title
      doi_count <- doi_count + 1
    } 
    #else if (doi %in% title_doi_list | title %in% title_doi_list & !is.na(title))
    else if (title %in% title_doi_list & !is.na(title))
      
    {dup <- TRUE
    print(paste("title", title, "in title doi duplicate list: will ignore publication"))
    #print(paste("title", title,"or doi", doi, "in title doi duplicate list: will ignore publication"))
     duplicate_count <- duplicate_count + 1
     pub_cnt <- pub_cnt +1
     }
    if (dup == FALSE & !is.na(title) & !title == "NA") {
    print(paste("dup indicator is false - ", dup," - beginning XML extraction"))
    #increment pub count
    pub_cnt <- pub_cnt +1
    
    all.coauthors <- str_trim(paste(as.character(unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$ALL_AUTHORS_CLEANED)[[1]]),sep=" ",collapse=" "))
    venue <- str_to_lower(str_trim(as.character(unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$Venue)[[1]])))
    #abstract <- unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$abstract)[[1]])
    year <- str_to_lower(str_trim(as.character(unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$YEAR)[[1]])))
    if (length(str_split(year,"-")[[1]]) > 1){
      print(paste(year, "YEAR NEEDS FORMATTING!"))
      year <- str_split(year,"-")[[1]][1]
      print(paste("formatted year is",year))
    }
    #organisation <- str_to_lower(str_trim(as.character(unique(UTS_PUBLICATIONS[UTS_PUBLICATIONS$ARTICLE_CHAPTER_PAPER_TITLE==ego_pub_list[i], ]$ORGANISATION)[[1]])))
    #!!!!!!!!!! NO RELIABLE ORG DATA FOR REF NETWORKS WILL NO LONGER INCLUDE - USE YEAR INSTEAD !!!!!!!!
    
    
    
    #Then this is one of the authors publications - add to authors XML file:
    #count node
    cnt_name_var <- paste("cntNode", pub_cnt, sep = "")
    assign(cnt_name_var, newXMLNode("pub_count",pub_cnt,  parent=root))
    #Note: pub_count can be removed for faster effi
    #publication node
    pub_name_var1 <- paste("pubNode", pub_cnt, sep = "")
    temp <- assign(pub_name_var1, newXMLNode("publication", parent=root))
    #title tag
    titl_name_var <- paste("titleNode", pub_cnt, sep = "")
    assign(titl_name_var, newXMLNode("title",title,  parent=temp))
    #jconf tag
    jconf_name_var <- paste("jconfNode", pub_cnt, sep = "")
    assign(jconf_name_var, newXMLNode("jconf",venue,  parent=temp))
    #organization tag
    #jconf tag
    year_name_var <- paste("yearNode", pub_cnt, sep = "")
    assign(year_name_var, newXMLNode("year",year,  parent=temp))
    #affil_name_var <- paste("affilNode", pub_cnt, sep = "")
    #assign(affil_name_var, newXMLNode("organization",organisation,  parent=temp))
    #abstract tag
    #abstract_name_var <- paste("abstract", pub_cnt, sep = "")
    #assign(abstract_name_var, newXMLNode("abstract",abstract,  parent=temp))
    #doi tag
    #DOI_name_var <- paste("DOI", pub_cnt, sep = "")
    #assign(DOI_name_var, newXMLNode("DOI",doi,  parent=temp))
    #authors tag
    authors_name_var <- paste("authors", pub_cnt, sep = "")
    assign(authors_name_var, newXMLNode("authors",all.coauthors,  parent=temp))
    }}
  #Beginning ORCID phase for adding to XML file for author if author has ORCID ID:
  
  if (!UTS_researchers$ORCID.ID[j] == "\"\"" & !UTS_researchers$ORCID.ID[j] == '' & !is.na(UTS_researchers$ORCID.ID[j])) {
  
 # if (!UTS_researchers$ORCID.ID[j] == '' & !is.na(UTS_researchers$ORCID.ID[j])) {
    print("Author has ORCID XML extraction for researcher reference network")
    print("Checking if author surname, first inital is the same as author ego")
    orcid_name <- as.orcid(as.character(UTS_researchers$ORCID.ID[j]))
    if (!is.na(orcid_name) & !is.null(orcid_name)) {
    orcid_sname <- str_to_upper(str_trim(orcid_name[[1]]$name$`family-name`))
    if (length(orcid_sname)!=0){
    orcid_sname <- paste(str_split(orcid_sname, " |-|'")[[1]], sep="",collapse="")}
    else {orcid_sname <- NA}
    
    orcid_fname <-str_sub(str_trim(str_to_upper(orcid_name[[1]]$name$`given-names`)),1,1)
    if (length(orcid_fname)!=0){
      
    full_orcid_name <- paste(orcid_sname,orcid_fname,sep=",",collapse=",")
    }
    else {orcid_fname <- NA}
    
    print(paste("!!!!!!!!!!ORCID PROFILE NAME IS",full_orcid_name, "EGO (UNIVERSITY CLEANED NAME) IS",ego,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" ))
    if (full_orcid_name == ego)
    {
      print("Names are the same beginning ORCID extraction for author as supplement to University reference network for disambiguation.")
      
      
      #SUBSET HERE FOR UNIQUE UNSW RESEARCHERS ORCIDs for data extraction of papers and coauthors.
      x <- orcid_works(UTS_researchers$ORCID.ID[j])
     
      
      if (!nrow(x[[1]][[1]]) == 0) 
      {all.coauthors_first_order <- get_papers(x)
       orcid_df <- do.call(rbind.data.frame,list(all.coauthors_first_order))
      orcid_papers_count <- length(unique(orcid_df$doi))
      Extraction_summary_df[j, ] <- c(ego,orcid_papers_count,"SUCCESSFUL")

      
      #Now cleaning the name_clean from extracted ORCID profile in orcid_df:
      for (y in 1:nrow(orcid_df)){
        if (!is.na(orcid_df$name_clean[y]) & !is.null(orcid_df$name_clean[y])) {
          name <- str_split(str_to_upper(str_trim(orcid_df[y,'name_clean']))," ")
          orcid_fname <-str_sub(str_trim(str_to_upper(name[[1]][1])),1,1)
          sname <- name[[1]][2:length(name[[1]])]
          orcid_sname <- paste(str_split(sname, " |-|'")[[1]], sep="",collapse="")
          full_orcid_name <- paste(orcid_sname,orcid_fname,sep=",",collapse=",")
          orcid_df$name_clean[y] <- full_orcid_name
        }}
      print(paste("!!!!!!!!!!ORCID PROFILE NAME IS",full_orcid_name, "EGO (UNIVERSITY CLEANED NAME) IS",ego,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" ))
      
      
      
      if (!is.null(orcid_df))
      {
        pub_df <- data.frame("title" <- NA, "author_list" <- NA)
        colnames(pub_df)[1] <- "title"
        colnames(pub_df)[2] <- "author_list"
        ##View(pub_df)
        dataset_unique <- unique(orcid_df$title)
        #print(dataset_unique)
        #Creating unique pub dataframe with associated author_lists for each pub:
        for (z in 1:nrow(orcid_df))
        {
          #The publication to build author list for:
        #if (!is.na(dataset_unique[j])){
         # print(z)
          pub <- dataset_unique[z]
          print(paste("pub is ",pub))
          if (!is.na(pub)){
          if (!pub %in% pub_df$title){
            author_list <- list("NULL")
            print(paste("Author_list is", author_list))
            cnt <- 0
            print(paste("Beginning count is:", cnt))
            for (i in 1:nrow(orcid_df)){
              
            if (!is.na(orcid_df[i,"title"]) & !is.na(orcid_df[i,"name_clean"])){
              if (orcid_df[i,"title"] == pub & !(orcid_df[i,"name_clean"] %in% author_list)){
                author_list[cnt + 1] <- orcid_df[i,"name_clean"]
                print(paste("Author",orcid_df[i,"name_clean"], "not in author_list so adding", unlist(orcid_df[i,"name_clean"]), "to", "author_list at index", cnt + 1 ))
                cnt <- cnt + 1
              }
            
            } 
            pub_df[z,"title"] <- as.character(dataset_unique[z])
            pub_df[z,"author_list"] <- paste(author_list, collapse = " ")
            print(pub_df[z,])}
          
          #}
        }}}
      #View(orcid_df)
       # View(pub_df)
        #Now applying author_lists to each pubication of each author record
        for (y in 1:nrow(orcid_df))
        {# print(y)
     #y <- 24
          #Error was occuring here. Fixed.
          #print(pub_df[pub_df$title == dataset[y, "title"],c("author_list")])
          #print(dataset[y,])
         if (!is.na(orcid_df[y, "title"])){
           test <- pub_df[pub_df$title == orcid_df[y, "title"],c("author_list")]
           for (k in 1:length(test)){
             if (length(test) > 0){
               if (!is.na(test[[k]]))  {orcid_df[y, "author_list"] <- test[[k]]}
             
            }
             }
             #added first index look-up as second index returning NA
         
        # View(orcid_df)
          
         }}
       

      #XML extraction:
        
        for (y in 1:nrow(orcid_df)){
         # print(y)
          #print(paste(orcid_df[y,"name_clean"], ego))
          
        if (!is.na(orcid_df[y,"name_clean"]) & !is.na(orcid_df[y,"title"])){
          
          if (orcid_df[y,"name_clean"] == ego){
            #Checking paper is not a duplicate:
            dup <- FALSE
            doi <- str_to_lower(str_trim(as.character(unique(orcid_df[y,"doi"]))))
            title <- str_to_lower(str_trim(as.character(unique(orcid_df[y,"title"]))))
            year <- str_trim(as.character(unique(orcid_df[y,"date"])))
            if (length(str_split(year,"-")[[1]]) > 1){
              print(paste(year, "YEAR NEEDS FORMATTING!"))
              year <- str_split(year,"-")[[1]][1]
              print(paste("formatted year is",year))
            }
            #Cleaning author title:
            if (!is.na(title)){
              if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
                print(paste("Cleaning orcid title:",substr(title, nchar(title), nchar(title)),"from title end:",title))
                title <- substr(title,1,nchar(title)-1)
              }
              if (str_detect(substr(title, 1, 1), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
                print(paste("Cleaning orcid title:",substr(title, 1, 1),"from title beginning:",title))
                title <- substr(title,2,nchar(title))
              }}
            if (!doi %in% title_doi_list & !title %in% title_doi_list & !is.na(title)){
              print(paste("doi", doi, "and title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
              if (!is.na(doi) & !doi == " ")
              {title_doi_list[doi_count] <- doi
              doi_count <- doi_count + 1}
              title_doi_list[doi_count] <- title
              doi_count <- doi_count + 1
            } 
            else if (doi %in% title_doi_list | title %in% title_doi_list & !is.na(title))
            {dup <- TRUE
            print(paste("title", title,"or doi", doi, "in title doi duplicate list: will ignore publication - ORCID EXTRACTION"))
            duplicate_count <- duplicate_count + 1
            pub_cnt <- pub_cnt +1}
            if (dup == FALSE & !is.na(title) & !title == "NA") {
              print(paste("dup indicator is false - ", dup," - beginning XML ORCID extraction"))
            
            
            #increment pub count
            pub_cnt <- pub_cnt +1
            #Then this is one of the authors publications - add to authors XML file:
            #count node
            cnt_name_var <- paste("cntNode", pub_cnt, sep = "")
            assign(cnt_name_var, newXMLNode("pub_count",pub_cnt,  parent=root))
            #Note: pub_count can be removed for faster effi
            #publication node
            pub_name_var1 <- paste("pubNode", pub_cnt, sep = "")
            temp <- assign(pub_name_var1, newXMLNode("publication", parent=root))
            #title tag
            #cleaning orcid extracted title:
            title <- str_trim(str_to_lower(title))
            if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
              print(paste("CLEANED:",substr(title, nchar(title), nchar(title))))
              title <- substr(title,1,nchar(title)-1)
            }
            titl_name_var <- paste("titleNode", pub_cnt, sep = "")
            assign(titl_name_var, newXMLNode("title",title,  parent=temp))
            #jconf tag
            jconf <- str_to_lower(str_trim(orcid_df[y,"jconf"]))
            jconf_name_var <- paste("jconfNode", pub_cnt, sep = "")
            assign(jconf_name_var, newXMLNode("jconf",jconf,  parent=temp))
            #organization tag
            organisation <- str_to_lower(str_trim(orcid_df[y,"organisation"]))
            affil_name_var <- paste("affilNode", pub_cnt, sep = "")
            assign(affil_name_var, newXMLNode("organization",organisation,  parent=temp))
            
            #year tag
            year_name_var <- paste("yearNode", pub_cnt, sep = "")
            assign(year_name_var, newXMLNode("year",year,  parent=temp))
            #abstract tag
            #abstract_name_var <- paste("abstract", pub_cnt, sep = "")
           # assign(abstract_name_var, newXMLNode("abstract",orcid_df[y,"abstract"],  parent=temp))
            #doi tag
            DOI_name_var <- paste("DOI", doi, sep = "")
            assign(DOI_name_var, newXMLNode("DOI",doi,  parent=temp))
            #authors tag
            author_list <- str_trim(orcid_df[y,"author_list"])
            authors_name_var <- paste("authors", pub_cnt, sep = "")
            assign(authors_name_var, newXMLNode("authors",author_list,  parent=temp))
            
            
          }}}}}
        #Name the XML Doc:
        print(paste("!Scraped", pub_cnt, "ORCID profile publications for author!", ego))}
      
      else if (nrow(x[[1]][[1]]) == 0) {
        orcid_papers_count <- 0
        Extraction_summary_df[j, ] <- c(ego,orcid_papers_count,"UNSUCCESSFUL")
      }
        
        print(paste("THERE WAS", duplicate_count, "duplicate publications blocked between ORCID and University database XML extraction"))
      }
      
      
      
      }}
        
#load(file="C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\ORCID_UTSSPHERE_test\\all.coauthors_first_order_ORCID.Rdata")
  

#Name the XML Doc:
print(paste("Scraped", pub_cnt, "total publications for author", ego))
#docName(doc) = ego
#print the created pub XML doc for author
#adding total count node:
total_cnt_name_var <- paste("total_cnt", pub_cnt-duplicate_count, sep = "")
assign(total_cnt_name_var, newXMLNode("total_cnt",pub_cnt-duplicate_count,  parent=root))
#Saving to total_cnt_df for disambig filtering/checks:
print(paste("HERE", total_cnt_df_ref$author[j], ego))
print(paste(total_cnt_df_ref$ref_total_count[j],(pub_cnt-duplicate_count)))
print(paste("EGO", ego, length(ego), class(ego)))

total_cnt_df_ref[j,]$author <- ego
total_cnt_df_ref[j,]$ref_total_count <- (pub_cnt-duplicate_count)


#cat(saveXML(doc))
text<-read_xml(saveXML(doc))

#Save XML file for author:
if ((pub_cnt-duplicate_count) >0){
#if (!is.na(UTS_researchers$AUTHOR_PUBS[j])){
#saveXML(doc, file= saveXML(doc, file=paste(paste(unlist(str_split(ego,",")), collapse="."), ".xml",collapse="",sep=""))) - not correctly fornatted (does not return spacing between tags)
write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML\\REF\\"
                             ,paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_REF.xml",collapse="",sep=""),sep=""), option = "as_xml")

print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_REF.xml",collapse="",sep=""), "XML file saved"))}
}
#!!!!!!!!!!!!!!!!!!END OF PRIMARY_REF XML FILE PREP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#Preparing text file for author:total count ref dict.
setwd("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML")
author_total <- total_cnt_df_ref
author_total <- unique(author_total)
#View(title_abstract)
formatted_text <- ""
for (i in 1:nrow(author_total))
{
  formatted_text <- paste(formatted_text,paste(paste(author_total[i,"author"],author_total[i,"ref_total_count"], sep="<>"), collapse="\n"), "\n")
  print(length(formatted_text))
}
formatted_text <- paste("\n",formatted_text, sep="\n",collapse="\n")
write.table(formatted_text, file = "author_total_ref.txt", sep = "\t",
            row.names = FALSE, col.names = FALSE)

#Adding in ORCID count of publications extracted to extraction summary doc:
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\Extraction_summary_df_FINAL.Rdata")
#!!!!!!!!Adding an extra row to make same size (need to clean this up/remve for future use)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Extraction_summary_df[11,] <- c(NA,NA,NA)
final_extraction_summary <- cbind(final_extraction_summary, Extraction_summary_df)
write.xlsx(final_extraction_summary, "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\Extraction_Summary.xlsx")


#Creating reference networks for secondary authors using extracted authors indivudal  GED over average of scopus/wos/PUBMED individually)
    
#LOADING IN SECONDARY extracted author datasets for scopus, WOS and pubmed individually:
#load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\SCOPUS_UTSSPHERE_test\\all.coauthors_first_order_SCOPUS_DIAMB_df.Rdata")
#load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\PUBMED_UTSSPHERE_test\\all.coauthors_first_order_PUBMED_DIAMB_df.Rdata")
#load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\WEB_OF_SCIENCE_UTSSPHERE_test\\all.coauthors_first_order_WOS_DIAMB_df.Rdata")

#PUBMED_df <- all.coauthors_first_order_PUBMED_DIAMB_df[, c("surname", "firstname", "venue", "affil", "title", "abstract")]
#View(PUBMED_df)
#sum(is.na(PUBMED_df$surname))
#WOS_df <- all.coauthors_first_order_WOS_DIAMB_df[, c("surname", "firstname", "venue", "affil", "title", "abstract")]
#View(WOS_df)
#sum(is.na(WOS_df$surname))
#all.coauthors_first_order_SCOPUS_DIAMB_df$venue <- all.coauthors_first_order_SCOPUS_DIAMB_df$Venue
#SCOPUS_df <- all.coauthors_first_order_SCOPUS_DIAMB_df[, c("surname", "firstname", "venue", "affil", "title", "abstract")]
#View(SCOPUS_df)
#sum(is.na(SCOPUS_df$surname))

#cleaning names

name_clean <- function(i, dataset)
{
  surname_comps <- strsplit(toupper(str_trim(dataset$surname[i])), " |-|'")
  
  #print(final_df$surname[i])
  surname <- paste(unlist(surname_comps), collapse="")
  #print(paste(unlist(surname_comps), collapse=""))
  
  first <- substr(toupper(str_trim(dataset$firstname[i])), 1, 1)
  #print(first)
  final <- paste(surname, first,sep=",")
  print(final)
  return(final)
  
}
#cleaning names for PUBMED
#for (i in 1:nrow(PUBMED_df))
#{
#  PUBMED_df$name_clean[i] <- name_clean(i,PUBMED_df)
  
#}
#for (i in 1:nrow(WOS_df))
#{
#  WOS_df$name_clean[i] <- name_clean(i,WOS_df)
  
#}
#for (i in 1:nrow(SCOPUS_df))
#{
#  SCOPUS_df$name_clean[i] <- name_clean(i,SCOPUS_df)
  
#}
#View(WOS_df)
#View(SCOPUS_df)
#View(PUBMED_df)

#Creating 'Secondary author Reference Network XML file for SCOPUS:
#SCOPUS_df <- unique(SCOPUS_df)
#WOS_df <- unique(WOS_df)
#PUBMED_df <- unique(PUBMED_df)
#WOS_df <-  WOS_df[!is.na(WOS_df),]
##WOS_df <- WOS_df[!is.na(WOS_df$surname),]
#SCOPUS_df <- SCOPUS_df[!is.na(SCOPUS_df$surname),]
#PUBMED_df <- PUBMED_df[!is.na(PUBMED_df$surname),]



#Creating function for turning a given primary/secondary author main to XML & secondary author ref network to XML:
#author_extracted_dataset_to_XML <- function(dataset, network_type, secondary_ref_type, total_cnt_dataframe){

author_extracted_dataset_to_XML <- function(dataset, network_type, secondary_ref_type){
  primary_auth_count <- 0
  #Creating total publication count dictionary for main and refs for primary authors:
  total_cnt_df_main <- data.frame("author" <- NA,"main_total_count"<- NA)
  colnames(total_cnt_df_main)[1] <- "author"
  colnames(total_cnt_df_main)[2] <- "main_total_count"
  rownames(total_cnt_df_main) <- c()
# Processing final dataset for format of author disambiguation and XML processing.
pub_df <- data.frame("title" <- NA, "author_list" <- NA)
colnames(pub_df)[1] <- "title"
colnames(pub_df)[2] <- "author_list"
##View(pub_df)
dataset_unique <- unique(dataset$title)
#Creating unique pub dataframe with associated author_lists for each pub:
for (j in 1:length(dataset_unique))
{
  #The publication to build author list for:
 # if (!is.na(dataset_unique[j])){
  pub <- dataset_unique[j]
  print(paste("pub is ",pub))
  if (!pub %in% pub_df$title){
    author_list <- list("NULL")
    print(paste("Author_list is", author_list))
    cnt <- 0
    print(paste("Beginning count is:", cnt))
    for (i in 1:nrow(dataset)){
      
      #if (!is.na(dataset[i,"title"]) & !is.na(dataset[i,"surname"])){
        if (dataset[i,"title"] == pub & !(dataset[i,"name_clean"] %in% author_list)){
          author_list[cnt + 1] <- dataset[i,"name_clean"]
          print(paste("Author",dataset[i,"name_clean"], "not in author_list so adding", unlist(dataset[i,"name_clean"]), "to", "author_list at index", cnt + 1 ))
          cnt <- cnt + 1
        }}
      
     # } 
    
    pub_df[j,"title"] <- dataset_unique[j]
    pub_df[j,"author_list"] <- paste(author_list, collapse = " ")
    print(pub_df[j,])}
  
  #}
  }

#Now applying author_lists to each pubication of each author record
for (y in 1:nrow(dataset))
{
  #Error was occuring here. Fixed.
  #print(pub_df[pub_df$title == dataset[y, "title"],c("author_list")])
  #print(dataset[y,])
  #dataset[y, "author_list"] <- pub_df[pub_df$title == dataset[y, "title"] & !is.na(pub_df$title),c("author_list")]
  dataset[y, "author_list"] <- pub_df[pub_df$title == dataset[y, "title"],c("author_list")]
  
}
#Setting Directory for XML files to be saved to:
if (network_type == "primary"){
  setwd("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML")}
else if (network_type == "secondary_ref"|network_type == "secondary_main"){
  setwd("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\SECONDARY_AUTHORS_XML")}


#Check correct dir:
print(paste("Working directory for saving XML files is:",getwd()))
#Now creating  dataframe for each author consisting of XML tags for each of authosr publications
name_cleans_unique <- unique(dataset$name_clean)

#for (x in 1:1){
#for (x in 1:length(name_cleans_unique)){
  
for (x in 1:length(name_cleans_unique)){
  print(paste("Beginning author", x, "out of", length(name_cleans_unique), "authors"))
  ego <- name_cleans_unique[x]
  title_doi_list <- list()
  doi_count <- 1
  pub_cnt <- 0
  duplicate_count <- 0
  pub_cnt <- 0
  print(paste("Ambiguous Author is", ego))
  print(paste("There are",nrow(dataset[dataset$name_clean == ego,]), "publications co-authored by author", ego))
  #Creating the XML raw file Tree format root for author 
  prefix.xml <- "
  <author_set>
</author_set>
  "
  doc = xmlTreeParse(prefix.xml, useInternalNodes = T,addFinalizer = TRUE) 
  help(xmlTreeParse)
  root = xmlRoot(doc)  #FIND ROOT 
  #firstname tag# 
  FnameNode = newXMLNode("FullName",ego, parent=root)
  if (ego %in% unique_authors & network_type=="primary"){
    for (y in 1:nrow(dataset)){
      
      
      if (dataset[y,"name_clean"] == ego){
        
        dup <- FALSE
        doi <- str_to_lower(str_trim(as.character(unique(dataset[y,"doi"]))))
        title <- str_to_lower(str_trim(as.character(unique(dataset[y,"title"]))))
        if (!is.na(title)){
          if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
            print(paste("Cleaning  title:",substr(title, nchar(title), nchar(title)),"from title end:",title))
            title <- substr(title,1,nchar(title)-1)
          }
          if (str_detect(substr(title, 1, 1), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
            print(paste("Cleaning  title:",substr(title, 1, 1),"from title beginning:",title))
            title <- substr(title,2,nchar(title))
          }}        
        
        if (!doi %in% title_doi_list & !title %in% title_doi_list & !is.na(title)){
          print(paste("doi", doi, "and title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
          if (!is.na(doi) & !doi == " ")
          {title_doi_list[doi_count] <- doi
          doi_count <- doi_count + 1}
          title_doi_list[doi_count] <- title
          doi_count <- doi_count + 1
        } 
        else if (doi %in% title_doi_list | title %in% title_doi_list & !is.na(title))
        {dup <- TRUE
        print(paste("title", title,"or doi", doi, "in title doi duplicate list: will ignore publication"))
        duplicate_count <- duplicate_count + 1
        pub_cnt <- pub_cnt +1
        }
        if (dup == FALSE & !is.na(title) & !title == "NA") {
          print(paste("dup indicator is false - ", dup," - beginning XML extraction for primary main"))
        #increment pub count
        pub_cnt <- pub_cnt +1
        #Then this is one of the authors publications - add to authors XML file:
        #count node
        cnt_name_var <- paste("cntNode", pub_cnt, sep = "")
        assign(cnt_name_var, newXMLNode("pub_count",pub_cnt,  parent=root))
        #Note: pub_count can be removed for faster effi
        #publication node
        pub_name_var1 <- paste("pubNode", pub_cnt, sep = "")
        temp <- assign(pub_name_var1, newXMLNode("publication", parent=root))
        #title tag
        titl_name_var <- paste("titleNode", pub_cnt, sep = "")
        assign(titl_name_var, newXMLNode("title",dataset[y,"title"],  parent=temp))
        #jconf tag
        jconf <- str_to_lower(str_trim(dataset[y,"venue"]))
        jconf_name_var <- paste("jconfNode", pub_cnt, sep = "")
        assign(jconf_name_var, newXMLNode("jconf",jconf,  parent=temp))
        #organization tag
        affil <- str_to_lower(str_trim(dataset[y,"affil"]))
        affil_name_var <- paste("affilNode", pub_cnt, sep = "")
        assign(affil_name_var, newXMLNode("organization",affil,  parent=temp))
        #abstract tag
        abstract <- str_to_lower(str_trim(dataset[y,"abstract"]))
        abstract_name_var <- paste("abstract", pub_cnt, sep = "")
        assign(abstract_name_var, newXMLNode("abstract",abstract,  parent=temp))
        #doi tag
        DOI_name_var <- paste("DOI", pub_cnt, sep = "")
        assign(DOI_name_var, newXMLNode("DOI",doi,  parent=temp))
        #year tag
        year <- str_to_lower(str_trim(dataset[y,"year"]))
        if (length(str_split(year,"-")[[1]]) > 1){
          print(paste(year, "YEAR NEEDS FORMATTING!"))
          year <- str_split(year,"-")[[1]][1]
          print(paste("formatted year is",year))
        }
        year_name_var <- paste("year", pub_cnt, sep = "")
        assign(year_name_var, newXMLNode("year",year,  parent=temp))
        #authors tag
        authors_name_var <- paste("authors", pub_cnt, sep = "")
        assign(authors_name_var, newXMLNode("authors",dataset[y,"author_list"],  parent=temp))
      }}}
    #Name the XML Doc:
    #adding total count node:
    total_cnt_name_var <- paste("total_cnt", pub_cnt-duplicate_count, sep = "")
    assign(total_cnt_name_var, newXMLNode("total_cnt",pub_cnt-duplicate_count,  parent=root))
    #Saving to total_cnt_df for disambig filtering/checks:
    print(paste("HERE", total_cnt_df_main$author[j], ego))
    print(paste(total_cnt_df_main$main_total_count[j],(pub_cnt-duplicate_count)))
    print(paste("EGO", ego, length(ego), class(ego)))
    primary_auth_count <- primary_auth_count + 1
    total_cnt_df_main[primary_auth_count,]$author <- ego
    total_cnt_df_main[primary_auth_count,]$main_total_count <- (pub_cnt-duplicate_count)

    }
  
  else if (startsWith(network_type, 'secondary') & !(ego %in% unique_authors)){
    for (y in 1:nrow(dataset)){
      
      
      if (dataset[y,"name_clean"] == ego){
        
        dup <- FALSE
        doi <- str_to_lower(str_trim(as.character(unique(dataset[y,"doi"]))))
        title <- str_to_lower(str_trim(as.character(unique(dataset[y,"title"]))))
        if (!doi %in% title_doi_list & !title %in% title_doi_list & !is.na(title)){
          print(paste("doi", doi, "and title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
          if (!is.na(doi) & !doi == " ")
          {title_doi_list[doi_count] <- doi
          doi_count <- doi_count + 1}
          title_doi_list[doi_count] <- title
          doi_count <- doi_count + 1
        } 
        else if (doi %in% title_doi_list | title %in% title_doi_list)
        {dup <- TRUE
        print(paste("title", title,"or doi", doi, "in title doi duplicate list: will ignore publication"))
        duplicate_count <- duplicate_count + 1
        pub_cnt <- pub_cnt +1
        }
        if (dup == FALSE & !is.na(title) & !title == "NA") {
          print(paste("dup indicator is false - ", dup," - beginning XML extraction for secondary main"))
          #increment pub count
          pub_cnt <- pub_cnt +1
          #Then this is one of the authors publications - add to authors XML file:
          #count node
          cnt_name_var <- paste("cntNode", pub_cnt, sep = "")
          assign(cnt_name_var, newXMLNode("pub_count",pub_cnt,  parent=root))
          #Note: pub_count can be removed for faster effi
          #publication node
          pub_name_var1 <- paste("pubNode", pub_cnt, sep = "")
          temp <- assign(pub_name_var1, newXMLNode("publication", parent=root))
          #title tag
          titl_name_var <- paste("titleNode", pub_cnt, sep = "")
          assign(titl_name_var, newXMLNode("title",title,  parent=temp))
          #jconf tag
          jconf <- str_to_lower(str_trim(dataset[y,"venue"]))
          jconf_name_var <- paste("jconfNode", pub_cnt, sep = "")
          assign(jconf_name_var, newXMLNode("jconf",jconf,  parent=temp))
          #organization tag
          affil <- str_to_lower(str_trim(dataset[y,"affil"]))
          affil_name_var <- paste("affilNode", pub_cnt, sep = "")
          assign(affil_name_var, newXMLNode("organization",affil,  parent=temp))
          #abstract tag
          abstract <- str_to_lower(str_trim(dataset[y,"abstract"]))
          abstract_name_var <- paste("abstract", pub_cnt, sep = "")
          assign(abstract_name_var, newXMLNode("abstract",abstract,  parent=temp))
          #year tag
          year <- str_to_lower(str_trim(dataset[y,"year"]))
          if (length(str_split(year,"-")[[1]]) > 1){
            print(paste(year, "YEAR NEEDS FORMATTING!"))
            year <- str_split(year,"-")[[1]][1]
            print(paste("formatted year is",year))
          }
          year_name_var <- paste("year", pub_cnt, sep = "")
          assign(year_name_var, newXMLNode("year",year,  parent=temp))
          
          #authors tag
          authors_name_var <- paste("authors", pub_cnt, sep = "")
         assign(authors_name_var, newXMLNode("authors",dataset[y,"author_list"],  parent=temp))
         #doi tag
         DOI_name_var <- paste("DOI", pub_cnt, sep = "")
         assign(DOI_name_var, newXMLNode("DOI",doi,  parent=temp))
      }}}
    #Name the XML Doc:
    #adding total count node:
    total_cnt_name_var <- paste("total_cnt", pub_cnt-duplicate_count, sep = "")
    assign(total_cnt_name_var, newXMLNode("total_cnt",pub_cnt-duplicate_count,  parent=root))
    #Saving to total_cnt_df for disambig filtering/checks:
    print(paste("HERE", total_cnt_df_main$author[j], ego))
    print(paste(total_cnt_df_main$main_total_count[j],(pub_cnt-duplicate_count)))
    print(paste("EGO", ego, length(ego), class(ego)))
    primary_auth_count <- primary_auth_count + 1
    total_cnt_df_main[primary_auth_count,]$author <- ego
    total_cnt_df_main[primary_auth_count,]$main_total_count <- (pub_cnt-duplicate_count)
    }
  
  #docName(doc) = ego
  #print the created pub XML doc for author
  #cat(saveXML(doc))
  text<-read_xml(saveXML(doc))
  
  #Save XML file for author and check if primary or secondary author:
  if (ego %in% unique_authors & network_type == "primary" & (pub_cnt-duplicate_count)>0) #unique_authors is primary UNI DBS extracted authors.
  {  #saveXML(doc, file= saveXML(doc, file=paste(paste(unlist(str_split(ego,",")), collapse="."), ".xml",collapse="",sep=""))) - not correctly fornatted (does not return spacing between tags)
    write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML\\MAIN\\"
                                 ,paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_MAIN.xml",collapse="",sep=""),sep=""), option = "as_xml")

    print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_MAIN.xml",collapse="",sep=""), "XML file saved"))}
  
  else if (network_type == "secondary_main" & !(ego %in% unique_authors) & (pub_cnt-duplicate_count)>0) { 
    write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\SECONDARY_AUTHORS_XML\\MAIN\\"
                                 ,paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_MAIN.xml",collapse="",sep=""),sep=""), option = "as_xml")
      print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_MAIN.xml",collapse="",sep=""), "XML file saved"))}
  
  else if (network_type == "secondary_ref" & !(ego %in% unique_authors)){
  
    if (secondary_ref_type == "scopus"){
      write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\DISAMBIGUATION\\Authors_XML\\secondary_authors\\scopus_ref\\",paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_SCOPUS.xml",collapse="",sep=""),sep=""), option = "as_xml")
      print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_SCOPUS.xml",collapse="",sep=""), "XML file saved"))
    }
    else if (secondary_ref_type == "wos"){
      write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\DISAMBIGUATION\\Authors_XML\\secondary_authors\\wos_ref\\",paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_WOS.xml",collapse="",sep=""),sep=""), option = "as_xml")
      print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_WOS.xml",collapse="",sep=""), "XML file saved"))
    }
    else if (secondary_ref_type == "pubmed"){
      write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\DISAMBIGUATION\\Authors_XML\\secondary_authors\\pubmed_ref\\",paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_PUBMED.xml",collapse="",sep=""),sep=""), option = "as_xml")
      print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_SECONDARY_REF_PUBMED.xml",collapse="",sep=""), "XML file saved"))
    }
    else {print("NO secondary ref type defined")}
    
    
   
  }} 
return(total_cnt_df_main)}

#Creating Secondary Network Refs for WOS:
#author_extracted_dataset_to_XML(dataset = WOS_df,network_type = "secondary_ref",secondary_ref_type="wos")
#Creating Secondary Network Refs for SCOPUS:
#author_extracted_dataset_to_XML(dataset = SCOPUS_df,network_type = "secondary_ref",secondary_ref_type="scopus")
#Creating Secondary Network Refs for PUBMED:
#author_extracted_dataset_to_XML(dataset = PUBMED_df,network_type = "secondary_ref",secondary_ref_type="pubmed")



#FINAL MERGED AUTHOR DATASETS:


load(file="C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\all.coauthors_final_df.Rdata")
final_df <- unique(final_df)
#Cleaning titles for de-duplication by removing trailing full stops and non-alphabetical characters:
for (i in 1:length(final_df$title)){
  final_df$title[i] <- str_trim(str_to_lower(final_df$title[i]))
  if (str_detect(substr(final_df$title[i], nchar(final_df$title[i]), nchar(final_df$title[i])), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
    print(paste("CLEANED:",substr(final_df$title[i], nchar(final_df$title[i]), nchar(final_df$title[i]))))
    final_df$title[i] <- substr(final_df$title[i],1,nchar(final_df$title[i])-1)
  }}
#View(final_df)
#Preparing secondary main XML files:
author_extracted_dataset_to_XML(dataset=final_df,network_type = "secondary_main",secondary_ref_type="none")
#Preparing primary main XML files:
#TEST - final_df <- final_df[final_df$name_clean == "MEHTA,P",]
total_cnt_df_main = author_extracted_dataset_to_XML(dataset=final_df,network_type = "primary",secondary_ref_type="none")

#Should now have primary main and reference and secondary mains and references for each author of final dataset.

#Creating the author_totalcnt.txt for author disambiguation algorithm for primary authors total counts
#setwd("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\UTS_COHORT_VALIDATION SET\\DISAMBIGUATION")

#Preparing text file for author:total count main dict.
author_total <- total_cnt_df_main
author_total <- unique(author_total)
#View(title_abstract)
formatted_text <- ""
for (i in 1:nrow(author_total))
{
  formatted_text <- paste(formatted_text,paste(paste(author_total[i,"author"],author_total[i,"main_total_count"], sep="<>"), collapse="\n"), "\n")
  print(length(formatted_text))
}
formatted_text <- paste("\n",formatted_text, sep="\n",collapse="\n")
write.table(formatted_text, file = "author_total_main.txt", sep = "\t",
            row.names = FALSE, col.names = FALSE)



#Creating extracted primary author main ORCID profiles to add to disambiguated researcher profiles after disambiguation:

#Creating the abstract_title.txt for author disambiguation algorithm for primary.
setwd("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML")

title_abstract <- final_df[, c("title", "abstract")]
title_abstract <- unique(title_abstract)
#View(title_abstract)
formatted_text <- ""
for (i in 1:nrow(title_abstract))
{
  formatted_text <- paste(formatted_text,paste(paste(title_abstract[i,"title"], title_abstract[i,"abstract"], sep="<>"), collapse="\n"), "\n")
  print(length(formatted_text))
}
#10 Sample authors for extraction/disambiguation evaluation:
#Churches T
#Agar	M
#Anazodo	A
#Barton	M 
#Grebely	J
#Butler	T 
#Delaney	G
#Jaffe	A
#Roberts	T
#Vittorio	O
#"BAJOREK,B"
#"BEBAWY,M"
#"BERLE,D"
#"BRYANT,L"
#"DUA,K"
#"FREEMANSANDERSON,A"
#"GOLZAN,M"

##########################ORCID EXTRACTION for PRIMARY AUTHOR ORCID PROFILE PAPER SETS#########################
#FOR DISSERTATION AS ONLY USING 10 SAMPLE AUTHORS TO EVALUATE TOOL WILL ONLY EXTRACT FOR THESE 10:
#unique_authors <- list("VITTORIO,O")  #, "AGAR,M","ANAZODO,A", "BARTON,M","GREBELY,J","BUTLER,T","DELANEY,G",
#                       "JAFFE,A","ROBERTS,T") #look at this.
                        #TIM CHURCHES

for (j in 1:length(unique_authors)){
  pub_cnt <- 0
  ego <- unique_authors[j]
  print(paste("Ambiguous Author is", ego))
  #Creating the XML raw file Tree format root for author 
  prefix.xml <- "
  <author_set>
</author_set>
  "
  doc = xmlTreeParse(prefix.xml, useInternalNodes = T,addFinalizer = TRUE) 
  help(xmlTreeParse)
  root = xmlRoot(doc)  #FIND ROOT 
  #firstname tag# 
  FnameNode = newXMLNode("FullName",ego, parent=root)
  #Adding in Authors ORCID papers if primary author:
  print("!Entering ORCIDID for MAIN!")
  orcid_id <- UTS_researchers[UTS_researchers$name_clean == ego & !is.na(UTS_researchers$ORCID.ID)
                            & !UTS_researchers$ORCID.ID == "" & !UTS_researchers$ORCID.ID == "\"\"" ,c("ORCID.ID")]


  print("ORCID ID IS:")
  print(orcid_id)
  
if (!length(orcid_id) == 0){
  if (!orcid_id == '' & !is.na(orcid_id) & !orcid_id == "\"\"") {
  
  # if (!UTS_researchers$ORCID.ID[j] == '' & !is.na(UTS_researchers$ORCID.ID[j])) {
  print("Author has ORCID XML extraction for researcher main network")
  print("Checking if author surname, first inital is the same as author ego")
  print("HERE1")
  orcid_name <- as.orcid(as.character(orcid_id))
  print(("HERE2"))
  if (!is.na(orcid_name) & !is.null(orcid_name)) {
    orcid_sname <- str_to_upper(str_trim(orcid_name[[1]]$name$`family-name`))
    if (length(orcid_sname)!=0){
      orcid_sname <- paste(str_split(orcid_sname, " |-|'")[[1]], sep="",collapse="")}
    else {orcid_sname <- NA}
    
    orcid_fname <-str_sub(str_trim(str_to_upper(orcid_name[[1]]$name$`given-names`)),1,1)
    if (length(orcid_fname)!=0){
      
      full_orcid_name <- paste(orcid_sname,orcid_fname,sep=",",collapse=",")
    }
    else {orcid_fname <- NA}
    
    print(paste("!!!!!!!!!!ORCID PROFILE NAME IS",full_orcid_name, "EGO (UNIVERSITY CLEANED NAME) IS",ego,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" ))
    if (full_orcid_name == ego)
    {
      print("Names are the same beginning ORCID extraction for author as supplement to University reference network for disambiguation.")
      
      
      #SUBSET HERE FOR UNIQUE UNSW RESEARCHERS ORCIDs for data extraction of papers and coauthors.
      x <- orcid_works(orcid_id)
      print(x[[1]][[1]])
      
      if (!nrow(x[[1]][[1]]) == 0) 
      {all.coauthors_first_order <- get_papers(x)
      orcid_df <- do.call(rbind.data.frame,list(all.coauthors_first_order))
      
      #Now cleaning the name_clean from extracted ORCID profile in orcid_df:
      for (y in 1:nrow(orcid_df)){
        if (!is.na(orcid_df$name_clean[y]) & !is.null(orcid_df$name_clean[y])) {
          name <- str_split(str_to_upper(str_trim(orcid_df[y,'name_clean']))," ")
          orcid_fname <-str_sub(str_trim(str_to_upper(name[[1]][1])),1,1)
          sname <- name[[1]][2:length(name[[1]])]
          orcid_sname <- paste(str_split(sname, " |-|'")[[1]], sep="",collapse="")
          full_orcid_name <- paste(orcid_sname,orcid_fname,sep=",",collapse=",")
          orcid_df$name_clean[y] <- full_orcid_name
        }}
      print(paste("!!!!!!!!!!ORCID PROFILE NAME IS",full_orcid_name, "EGO (UNIVERSITY CLEANED NAME) IS",ego,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" ))
      
      
      
      if (!is.null(orcid_df))
      {
        pub_df <- data.frame("title" <- NA, "author_list" <- NA)
        colnames(pub_df)[1] <- "title"
        colnames(pub_df)[2] <- "author_list"
        ##View(pub_df)
        dataset_unique <- unique(orcid_df$title)
        #print(dataset_unique)
        #Creating unique pub dataframe with associated author_lists for each pub:
        for (z in 1:nrow(orcid_df))
        {
          #The publication to build author list for:
          #if (!is.na(dataset_unique[j])){
          # print(z)
          pub <- dataset_unique[z]
          print(paste("pub is ",pub))
          if (!is.na(pub)){
            if (!pub %in% pub_df$title){
              author_list <- list("NULL")
              print(paste("Author_list is", author_list))
              cnt <- 0
              print(paste("Beginning count is:", cnt))
              for (i in 1:nrow(orcid_df)){
                
                if (!is.na(orcid_df[i,"title"]) & !is.na(orcid_df[i,"name_clean"])){
                  if (orcid_df[i,"title"] == pub & !(orcid_df[i,"name_clean"] %in% author_list)){
                    author_list[cnt + 1] <- orcid_df[i,"name_clean"]
                    print(paste("Author",orcid_df[i,"name_clean"], "not in author_list so adding", unlist(orcid_df[i,"name_clean"]), "to", "author_list at index", cnt + 1 ))
                    cnt <- cnt + 1
                  }
                  
                } 
                pub_df[z,"title"] <- as.character(dataset_unique[z])
                pub_df[z,"author_list"] <- paste(author_list, collapse = " ")
                print(pub_df[z,])}
              
              #}
            }}}
        #View(orcid_df)
        # View(pub_df)
        #Now applying author_lists to each pubication of each author record
        for (y in 1:nrow(orcid_df))
        {# print(y)
          #y <- 24
          #Error was occuring here. Fixed.
          #print(pub_df[pub_df$title == dataset[y, "title"],c("author_list")])
          #print(dataset[y,])
          if (!is.na(orcid_df[y, "title"])){
            test <- pub_df[pub_df$title == orcid_df[y, "title"],c("author_list")]
            for (k in 1:length(test)){
              if (length(test) > 0){
                if (!is.na(test[[k]]))  {orcid_df[y, "author_list"] <- test[[k]]}
                
              }
            }
            #added first index look-up as second index returning NA
            
            # View(orcid_df)
            
          }}
        
        
        #XML extraction:
        
        for (y in 1:nrow(orcid_df)){
          # print(y)
          #print(paste(orcid_df[y,"name_clean"], ego))
          
          if (!is.na(orcid_df[y,"name_clean"]) & !is.na(orcid_df[y,"title"])){
            
            if (orcid_df[y,"name_clean"] == ego){
              #Checking paper is not a duplicate:
              dup <- FALSE
              doi <- str_to_lower(str_trim(as.character(unique(orcid_df[y,"doi"]))))
              title <- str_to_lower(str_trim(as.character(unique(orcid_df[y,"title"]))))
            
              year <- str_trim(as.character(unique(orcid_df[y,"date"])))
              if (length(str_split(year,"-")[[1]]) > 1){
                print(paste(year, "YEAR NEEDS FORMATTING!"))
                year <- str_split(year,"-")[[1]][1]
                print(paste("formatted year is",year))
              }
              #Cleaning author title:
              if (!is.na(title)){
                if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
                  print(paste("Cleaning orcid title:",substr(title, nchar(title), nchar(title)),"from title end:",title))
                  title <- substr(title,1,nchar(title)-1)
                }
                if (str_detect(substr(title, 1, 1), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
                  print(paste("Cleaning orcid title:",substr(title, 1, 1),"from title beginning:",title))
                  title <- substr(title,2,nchar(title))
                }}
              
              #CHecking if ORCID title is in the title-abstract dictionary if not then attempting to add
              #the abstract through SCOPUS:
              if (!title %in% title_abstract[,"title"]){
                abstract = abstract_retrieval(doi, identifier = "doi")
                if (length(abstract$content) != 0){
                if (length(abstract$content$`abstracts-retrieval-response`) != 0){
                if (length(abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts) != 0)
                { abstract = abstract$content$`abstracts-retrieval-response`$item$bibrecord$head$abstracts}}}
                else { abstract = NA}
                if (!is.na(abstract)){
                  rows <- length(title_abstract$title)
                  title_abstract[rows + 1, "title"] <- title
                  title_abstract[rows+ 1, "abstract"] <- abstract
                  formatted_text <- paste(formatted_text,paste(paste(title_abstract[rows+1,"title"], title_abstract[rows+1,"abstract"], sep="<>"), collapse="\n"), "\n")
                  print(length(formatted_text))
                  print(paste("!ORCID TITLE AND ABSTRACT ADDED TO TITLE-ABSTRACT DICTIONARY!"))
                }

              
              
              }
            #Removing checks for duplicates from previous extraction of main xmls as no longer requiried:  
             # if (!doi %in% title_doi_list & !title %in% title_doi_list & !is.na(title)){
            #    print(paste("doi", doi, "and title", title, "not in title doi duplicate list - adding to list and commencing extraction:"))
            #    if (!is.na(doi) & !doi == " ")
            #    {title_doi_list[doi_count] <- doi
            #    doi_count <- doi_count + 1}
            #    title_doi_list[doi_count] <- title
            #    doi_count <- doi_count + 1
            #  } 
              #else if (doi %in% title_doi_list | title %in% title_doi_list & !is.na(title))
              #{dup <- TRUE
              #print(paste("title", title,"or doi", doi, "in title doi duplicate list: will ignore publication - ORCID EXTRACTION"))
              #duplicate_count <- duplicate_count + 1
              #pub_cnt <- pub_cnt +1}
              if (dup == FALSE & !is.na(title) & !title == "NA") {
                print(paste("dup indicator is false - ", dup," - beginning XML ORCID extraction"))
                
                
                #increment pub count
                pub_cnt <- pub_cnt +1
                #Then this is one of the authors publications - add to authors XML file:
                #count node
                cnt_name_var <- paste("cntNode", pub_cnt, sep = "")
                assign(cnt_name_var, newXMLNode("pub_count",pub_cnt,  parent=root))
                #Note: pub_count can be removed for faster effi
                #publication node
                pub_name_var1 <- paste("pubNode", pub_cnt, sep = "")
                temp <- assign(pub_name_var1, newXMLNode("publication", parent=root))
                #title tag
                #cleaning orcid extracted title:
                title <- str_trim(str_to_lower(title))
                if (str_detect(substr(title, nchar(title), nchar(title)), "^[^\\p{L}\\p{Nd}]+$") == TRUE){
                  print(paste("CLEANED:",substr(title, nchar(title), nchar(title))))
                  title <- substr(title,1,nchar(title)-1)
                }
                
                titl_name_var <- paste("titleNode", pub_cnt, sep = "")
                assign(titl_name_var, newXMLNode("title",title,  parent=temp))
                #jconf tag
                jconf <- str_to_lower(str_trim(orcid_df[y,"jconf"]))
                jconf_name_var <- paste("jconfNode", pub_cnt, sep = "")
                assign(jconf_name_var, newXMLNode("jconf",jconf,  parent=temp))
                #organization tag
                organisation <- str_to_lower(str_trim(orcid_df[y,"organisation"]))
                affil_name_var <- paste("affilNode", pub_cnt, sep = "")
                assign(affil_name_var, newXMLNode("organization",organisation,  parent=temp))
                
                #year tag
                year_name_var <- paste("yearNode", pub_cnt, sep = "")
                assign(year_name_var, newXMLNode("year",year,  parent=temp))
                #abstract tag
                #abstract_name_var <- paste("abstract", pub_cnt, sep = "")
                # assign(abstract_name_var, newXMLNode("abstract",orcid_df[y,"abstract"],  parent=temp))
                #doi tag
                DOI_name_var <- paste("DOI", doi, sep = "")
                assign(DOI_name_var, newXMLNode("DOI",doi,  parent=temp))
                #authors tag
                author_list <- str_trim(orcid_df[y,"author_list"])
                authors_name_var <- paste("authors", pub_cnt, sep = "")
                assign(authors_name_var, newXMLNode("authors",author_list,  parent=temp))
                
                
              }}}}} 
      #Name the XML Doc:
      print(paste("!Scraped", pub_cnt, "ORCID profile publications for author!", ego))}
      
      #print(paste("THERE WAS", duplicate_count, "duplicate publications blocked between ORCID and University database XML extraction"))
   
      text<-read_xml(saveXML(doc))
      
      #Save XML file for author and check if primary or secondary author:
      if (ego %in% unique_authors & (pub_cnt)>0) #unique_authors is primary UNI DBS extracted authors.
      {  #saveXML(doc, file= saveXML(doc, file=paste(paste(unlist(str_split(ego,",")), collapse="."), ".xml",collapse="",sep=""))) - not correctly fornatted (does not return spacing between tags)
        write_xml(text, file = paste("C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\2-3 - Disambiguation and Network Comparison (IGM)\\2-Running Disambiugation and Cluster Comparison\\PRIMARY_AUTHORS_XML\\ORCID\\"
                                     ,paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_ORCID.xml",collapse="",sep=""),sep=""), option = "as_xml")
        
        print(paste(paste(paste(unlist(str_split(ego,",")), collapse="."), "_PRIMARY_ORCID.xml",collapse="",sep=""), "XML file saved"))}
      
      
       }
    
    
    
  }}}
  
  }
#Creating final verison of title-abstract dict including latest ORCID titles.
formatted_text <- paste("\n",formatted_text, sep="\n",collapse="\n")
write.table(formatted_text, file = "title_abstract_disseration_test.txt", sep = "\t",
            row.names = FALSE, col.names = FALSE)
##########################ORCID EXTRACTION END#########################
#SAVING AS ORCID PAPER PROFILE FOR PRIMARY AUTHOR TO BE ADDED TO DISAMBIGUATED AUTHOR SETS POST DISAMBIGUATION:
    
  
  
  
  