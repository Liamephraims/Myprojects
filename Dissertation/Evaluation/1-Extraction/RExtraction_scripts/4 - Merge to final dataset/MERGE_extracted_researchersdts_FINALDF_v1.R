#Copyright © 2020 Liamephraims

library(stringr)
library(xlsx)

#Creating final Extraction Summary document and saving output as excel:
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\Extraction_summary_df_SCOPUS_v1.Rdata")
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\Extraction_summary_df_PUBMED_v1.Rdata")
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\Extraction_summary_df_WOS_v1.Rdata")

final_extraction_summary <- cbind(Extraction_summary_df_WOS, Extraction_summary_df_PUBMED[,2:length(Extraction_summary_df_PUBMED)])
Extraction_summary_df_SCOPUS[11,] <- NA
final_extraction_summary <- cbind(final_extraction_summary,Extraction_summary_df_SCOPUS[,2:length(Extraction_summary_df_SCOPUS)])

save(final_extraction_summary, file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\Extraction_summary_df_FINAL.Rdata")

write.xlsx(final_extraction_summary, "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\Extraction_Summary.xlsx")

#Merging three networks together for stage two - diambiguation.
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\all.coauthors_first_order_PUBMED_EVAL_v1.Rdata")
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\all.coauthors_first_order_SCOPUS_EVALv1.Rdata")
load(file = "C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\all.coauthors_first_order_WOS_EVAL_v1.Rdata")
all.coauthors_first_order_PUBMED_EVAL_v1 <- all.coauthors_first_order_EVAL_v1
#Converting these from list to dataframes:
all.coauthors_first_order_PUBMED_EVAL_v1 <- do.call(rbind.data.frame,all.coauthors_first_order_PUBMED_EVAL_v1)
all.coauthors_first_order_SCOPUS_EVALv1 <- do.call(rbind.data.frame,all.coauthors_first_order_SCOPUS_EVALv1)
all.coauthors_first_order_WOS_EVAL_v1 <- do.call(rbind.data.frame,all.coauthors_first_order_WOS_EVAL_v1)
#taking variables used from disambig paper for merging together in stage two.
PUBMED_df <- all.coauthors_first_order_PUBMED_EVAL_v1[, c("surname", "firstname", "venue", "affil", "title", "abstract", "doi","year")]
View(PUBMED_df)
sum(is.na(PUBMED_df$surname))





#all.coauthors_first_order_WOS_EVAL_v1$year <- all.coauthors_first_order_WOS_EVAL_v1$date
#Cleaning date to year-only for WOS:
for (i in 1:nrow(all.coauthors_first_order_WOS_EVAL_v1)){
  print(str_split(as.character(all.coauthors_first_order_WOS_EVAL_v1$date[i]),"-")[[1]][1])
  print(all.coauthors_first_order_WOS_EVAL_v1$date[i])
  all.coauthors_first_order_WOS_EVAL_v1$date_clean[i] <- str_split(as.character(all.coauthors_first_order_WOS_EVAL_v1$date[i]),"-")[[1]][1]
}
all.coauthors_first_order_WOS_EVAL_v1$year <- all.coauthors_first_order_WOS_EVAL_v1$date_clean

WOS_df <- all.coauthors_first_order_WOS_EVAL_v1[, c("surname", "firstname", "venue", "affil", "title", "abstract", "doi","year")]

View(WOS_df)
sum(is.na(WOS_df$surname))



all.coauthors_first_order_SCOPUS_EVALv1$venue <- all.coauthors_first_order_SCOPUS_EVALv1$Venue
SCOPUS_df <- all.coauthors_first_order_SCOPUS_EVALv1[, c("surname", "firstname", "venue", "affil", "title", "abstract", "doi","year")]
View(SCOPUS_df)
sum(is.na(SCOPUS_df$surname))

final_df <- rbind(WOS_df, SCOPUS_df)
final_df <- rbind(final_df,PUBMED_df)
final_df <- unique(final_df)
nrow(final_df)
nrow(unique(final_df))

final_df <- final_df[!is.na(final_df$surname),]
nrow(final_df)
nrow(unique(final_df))
#cleaning names

name_clean <- function(i)
{
  surname_comps <- strsplit(toupper(str_trim(final_df$surname[i])), " |-|'|,")
  
  #print(final_df$surname[i])
  surname <- paste(unlist(surname_comps), collapse="")
  #print(paste(unlist(surname_comps), collapse=""))
  
  first <- substr(toupper(str_trim(final_df$firstname[i])), 1, 1)
  #print(first)
  final <- paste(surname, first,sep=",")
  print(final)
  return(final)
 
}

for (i in 1:nrow(final_df))
{
  final_df$name_clean[i] <- name_clean(i)
  
}

#length(unique(final_df$name_clean))
#length(unique(final_df$surname))
table(final_df$name_clean)
#View(table(final_df$affil))

#View(final_df)

save(final_df,file="C:\\Users\\Liam Ephraims\\Desktop\\LiamDissertation\\Evaluation\\1-Extraction\\RExtracted_Researcher_data\\all.coauthors_final_df.Rdata")
View(final_df)




