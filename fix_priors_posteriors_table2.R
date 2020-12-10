#!/usr/bin/env Rscript

# T. Carman, Dec 2020

##------------------------------------------------------------------------------
# Now finally, some R code that will add in the columns for 
# confidence interval bounds
args <- commandArgs(TRUE)
#print(args)
if ("post" %in% args[1]) {
  outfile <- "tbc-scratch/posteriors_table.csv"
}
if ("prior" %in% args[1]) {
  outfile <- "tbc-scratch/priors_table.csv"
}

# This function was copied from the prior_stats_image.R script
# (in this repo) which was copied from the PEcAn codebase
pr.dens <- function(distn, parama, paramb, n = 1000, alpha = 0.001) {
  alpha <- ifelse(alpha < 0.5, alpha, 1-alpha)
  n <- ifelse(alpha == 0.5, 1, n)
  range.x <- do.call(paste('q', distn, sep = ""), list(c(alpha, 1-alpha), parama, paramb))
  seq.x   <- seq(from = range.x[1], to = range.x[2], length.out = n)
  dens.df <- data.frame(x = seq.x,
                        y = do.call(paste('d', distn, sep=""),
                                    list(seq.x, parama, paramb)))
  return(dens.df)
}

# A function to get the confidence interval bounds, given the 
# distribution name and parameters
get.ci <- function(distn, parama, paramb, n = 1000, alpha = .001) {
  pd = pr.dens(distn, parama, paramb)
  cdf <- data.frame(x=pd$x, y=do.call(paste("p",sep="",distn), list(pd$x,parama,paramb)))
  cimin <- cdf$x[cdf$y<=0.025][1]
  cimax <- cdf$x[cdf$y>=0.975][1]
  med <- cdf$x[cdf$y>=0.5][1]
  return(list(cimin, cimax, med))
}

# Read in our existing table that we created above - works the same for the 
# priors table
df <- read.csv(outfile)

# make some empty lists
cimin <- c()
cimax <- c()
med <- c()
# Fill the lists using functions defined above
for(i in 1:nrow(df)){
  a <- get.ci(df$distname[i], df$parama[i], df$paramb[i])
  cimin <- append(cimin, a[1])
  cimax <- append(cimax, a[2])
  med <- append(med, a[3])
}

# Add new columns to the dataframe
df$cimin <- cimin
df$cimax <- cimax
df$median <- med

df$cimin <- as.numeric(cimin)
df$cimax <- as.numeric(cimax)
df$median <- as.numeric(med)

# Write back to csv
write.csv(df, file=outfile, dec=".", row.names=FALSE)