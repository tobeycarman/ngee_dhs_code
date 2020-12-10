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

WHICH=$1
case $WHICH in
  *post*) BASEFILEPATTERN="post.distns.MA.Rdata" ;;
  *prior*) BASEFILEPATTERN="prior.distns.Rdata" ;;
  *) echo "Hmmm - unrecognized ARG: $1"; exit -1; ;;
esac

for f in $(find /Users/tobeycarman/Documents/SEL/ngee_dhs_code/ngee_dhs_runs -name "$BASEFILEPATTERN"); 
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
for F in $(find tbc-scratch -name "$BASEFILEPATTERN");
do

  case $F in
  *post*) DATA="post.distns" ;;
  *prior*) DATA="prior.distns" ;;
  *) echo "Hmmmm"; exit -1 ;;
  esac

# write the R script to convert to csv
cat <<EOF > oneoffR.R
setwd("$(dirname $F)")
load("$(basename $F)")
write.table($DATA, "$(basename $F.csv)", sep=",")
EOF
# Call the script
Rscript --vanilla oneoffR.R
done

# Pull the CMT/PFT name out of the file path and 
# prepend it to every line in the file
#
# Figure out if we are working on priors or posteriors
case $BASEFILEPATTERN in
  *prior*) OUTFILE="tbc-scratch/priors_table.csv"; FINDPATTERN="prior.distns.Rdata.csv" ;;
  *post*) OUTFILE="tbc-scratch/posteriors_table.csv"; FINDPATTERN="post.distns.MA.Rdata.csv" ;;
  *) echo "Hmmm..."; exit -1 ;;
esac

echo "" > $OUTFILE
for f in $(find tbc-scratch/ -name $FINDPATTERN); do
  # f name looks something like this:
  # kougorak_cmt04/pft/CMT04-Salix/post.distns.MA.Rdata
  # or kougorak_cmt04/pft/CMT04-Salix/prior.distns.Rdata
  CMT=$(python -c "import sys; print(sys.argv[1].split('/')[-2])" $f);
  echo $CMT
  sed s/^/\"$CMT\"\,/g $f >> $OUTFILE
done