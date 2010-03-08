#!Rscript

N <- 100
## set.seed(8675309)
## set.seed(314159)
## set.seed(1234567)
## set.seed(7654321)

## Used for mturk expers
set.seed(05241981)

userid <- runif(N, 0, 100000)
key <- runif(N, 0, 100000)

userid <- trunc(userid)
key <- trunc(key)

write.table(data.frame(userid = userid, key = key),
            "userid_key_header.csv",
            row.names = FALSE,
            col.names = TRUE, sep=",")

write.table(data.frame(userid = userid, key = key),
            "userid_key.csv",
            row.names = FALSE,
            col.names = FALSE, sep=",")
