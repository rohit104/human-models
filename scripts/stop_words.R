#!Rscript

data <- read.csv("clean_body.csv", as.is = TRUE, header=FALSE)
data$V3 <- gsub("\\\\n", "\n", data$V3)
split <- strsplit(tolower(data$V3), "\\W+")
doc.counts <- table(unlist(lapply(split, unique)))
stopwords <- readLines("stopwords.txt")
sorted <- sort(doc.counts, decreasing=TRUE)
sorted <- sorted[!(names(sorted) %in% stopwords)]
sorted <- sorted[nchar(names(sorted)) > 2]

cat(names(sorted[sorted >= 8]), file = "../vocabulary", sep = "\n")
