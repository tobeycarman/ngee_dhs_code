#!/bin/bash

# T. Carman, Dec 2020

# NOTE: Not designed to be run as a script! Use by copying relevant 
# bits of code to the appropriate interperter...

# Collate a posteriors table or priors table.
# This code works the same for priors if you substitute 
# "prior.distns.Rdata" for "post.disnts.MA.Rdata"
#
# The posterior distribution data exists in .Rdata files in 
# the run folders like this:
#     $ ngee_dhs_runs/dhs_1_cmt04/pft/CMT04-Betula/post.distns.MA.Rdata

# goal here is to pull all the data out and into a single table
# with a column for the PFT name (pft + cmt)

# Copy all the data into the pecan directory which is mounted
# in the pecan docker stack, so that I can use Rstudio 
# to muck around with it.
# had to install gnu coreutils (port install coreutils) to get
# gcp command and use explicit path because gcp is aliased to
# "git cherry pick"...
for f in $(find ngee_dhs_runs -name "post.distns.MA.Rdata"); 
do 
   # --parents flag not provided with macOS cp, but maintains
   # directory structure...
  /opt/local/bin/gcp --parents $f ~/Documents/SEL/PEcAn/PECAN/tbc-scratch;
done
# Turns out the above was not necessary as I have R installed
# on my host. So the following script will run, but I guess
# I used Rstudio to view the .Rdata files and poke around
# to see how everything is laid out...


# Convert .Rdata to csv so I can work with it in python
for F in $(find tbc-scratch -name post.distns.MA.Rdata);
do
# write the R script to convert to csv
cat <<EOF > oneoffR.R
setwd("$(dirname $F)")
load("$(basename $F)")
write.table(post.distns, "$(basename $F.csv)", sep=",")
EOF
# Call the script
Rscript --vanilla oneoffR.R
done

# Pull the CMT/PFT name out of the file path and 
# prepend it to every line in the file
echo "" > posteriors_table.csv
for f in $(find tbc-scratch/ -name "post.distns.MA.Rdata.csv"); do
  # f name looks something like this:
  # kougorak_cmt04/pft/CMT04-Salix/post.distns.MA.Rdata
  CMT=$(python -c "import sys; print(sys.argv[1].split('/')[-2])" $f);
  sed s/^/\"$CMT\"\,/g $f >> posteriors_table.csv
done


## ---------------------------------------------------------------------------
# The following code is python
# This changes the names of the traits/parameters for easier reading...
# matching the parameter names that Eugenie used in her priors spreadsheet
swaps = [
  ["cuticular_cond", "Cuticular conductance"],
  ["extinction_coefficient_diffuse","Extinction coefficient"],
  ["frprod_perc_10","Fine root productivity allocationn at 10 cm depth"],
  ["frprod_perc_20","Fine root productivity allocationn at 20 cm depth"],
  ["frprod_perc_30","Fine root productivity allocationn at 30 cm depth"],
  ["frprod_perc_40","Fine root productivity allocationn at 40 cm depth"],
  ["frprod_perc_50","Fine root productivity allocationn at 50 cm depth"],
  ["gcmax","gcmax; Maximum canopy conductance"],
  ["ilai","ilai; Starting value for leaf area index"],
  ["klai","klai; Extinction coefficient for converting between LAI and foliar percent cover"],
  ["labncon","labncon; Labile N concentration"],
  ["ppfd50","ppfd50; Amount of photosynthetically active radiation at which stomates partially (half) close"],
  ["pstemp_high","pstemp_high; The range of maximum temperatures for photosynthesis"],
  ["pstemp_low","pstemp_low; The range of minimal temperatures for photosynthesis"],
  ["pstemp_max","pstemp_max; Maximum temperature for photosynthesis"],
  ["pstemp_min","pstemp_min; Minimum temperature for photosynthesis"],
  ["SLA","SLA; specific leaf area"],
  ["SW_albedo","SW_albedo; Shortwave albedo"],
  ["vpd_close","vpd_close; Vapor pressure deficit for leaf stomata fully closed"],
  ["vpd_open","vpd_open; Vapor pressure deficit for leaf stomata fully opened"],
]

# Swap out the strings.
with open("posteriors_table.csv") as f:
  data = f.read()
for i in swaps:
  data = data.replace(i[0], i[1])
with open("posteriors_table.csv", 'w') as f:
  f.write(data)

# Strip out the extraneous header lines 
# (leftover from lazily mergeing all the files)
with open("posteriors_table.csv") as f:
  data = f.readlines()
with open("posteriors_table.csv", 'w') as f:
  for line in data:
    if not all([i in line for i in ['parama', 'paramb','distn','n']]):
      f.write(line)

# Add a single header line at the top
with open("posteriors_table.csv") as f:
  data = f.readlines()
with open("posteriors_table.csv", 'w') as f:
  f.writelines(["pft,vname,distname,parama,paramb,n"])
  f.writelines(data)


##------------------------------------------------------------------------------
# Now finally, some R code that will add in the columns for 
# confidence interval bounds

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
  return(list(cimin, cimax))
}

# Read in our existing table that we created above - works the same for the 
# priors table
df <- read.csv("tbc-scratch/posteriors_table.csv")

# make some empty lists
cimin <- c()
cimax <- c()
# Fill the lists using functions defined above
for(i in 1:nrow(df)){
  a <- get.ci(df$distname[i], df$parama[i], df$paramb[i])
  cimin <- append(cimin, a[1])
  cimax <- append(cimax, a[2])
}

# Add new columns to the dataframe
df$cimin <- cimin
df$cimax <- cimax

df$cimin <- as.numeric(cimin)
df$cimax <- as.numeric(cimax)

# Write back to csv
write.csv(df, file="tbc-scratch/posteriors_table.csv", dec=".", row.names=FALSE)

