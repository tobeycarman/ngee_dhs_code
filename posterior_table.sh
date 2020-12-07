#!/bin/bash

# T. Carman
# create posteriors table
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




# Some R, not particularly useful...
# for(trait in seq(1,ncol(prior.distns))){
#     for(prop in seq(1,nrow(prior.distns))) {
#         #print(c(rownames(prior.distns)[prop],"--->", prop, prior.distns[]))
#         if (is.numeric(prior.distns[[prop,trait]]) && is.numeric(post.distns[[prop,trait]])) {
#             delta = prior.distns[[prop,trait]] - post.distns[[prop,trait]]
#         } else {
#             delta = "-"
#         }
#         print(c(delta, rownames(prior.distns)[prop], prior.distns[[prop,trait]], post.distns[[prop,trait]]), right = true)
#     }
# }
