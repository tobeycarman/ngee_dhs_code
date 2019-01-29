# Tobey Carman November 2018

# THIS SCRIPT IS FOR GETTING AND PREPPING THE DATA

# Scripts for creating plots for NGEE meeting in early December.
# To be presented by E.Euskirchen and S.Serbin.

# See code from AGU meeting 2017. This is basically the same thing, but extended
# to include more PFTs.

# 1) Do runs (on modex presumably)
# 2) Get data from modex to computer with pyhton libs for analysis. Only need to
#    copy the .Rdata files, not the actual simulation outputs.
# 3) Convert .Rdata to .csv
#
# Then use the other 2 scripts to:
#
# 4) Read csv into pandas
# 5) reanalyse and plot

################################################################################
#
# NOTE: Not intended to run as a script - simply copy/paste snippets as needed!
#
################################################################################


declare -a SIMARR=( "2000001129" "2000001131" "2000001132" "2000001137" "2000001138" "2000001139" "2000001141" )
declare -a SIMARR=( "2000001129" "2000001131" "2000001132" "2000001137")
declare -a SIMARR=( "2000001138" "2000001139" "2000001141" )
declare -a SIMARR=( "2000001146" "2000001149" )
declare -a SIMARR=( "2000001154" )

# SoilOrgC and LAI runs
declare -a SIMARR=( "2000001157" "2000001164" "2000001165" "2000001166" "2000001168" "2000001169"  )

# 1/18/2019, trial run
declare -a SIMARR=("2000001190")

# On modex, bundle up the data
# There is not need for *all* of the simulation results, just the stuff that
# is summarized in the .Rdata files
for SIM in "${SIMARR[@]}"
do
  cd /data/Model_Output/pecan.output/PEcAn_$SIM
  find . -name "*.Rdata" -exec tar -rvf ~/PEcAn_$SIM.tar {} \;
  cd ~
done

# Now, on OSX host (or VM), get the data from Modex
cd ~/Documents/SEL/NGEE_Dec_2018_followup
for SIM in "${SIMARR[@]}"
do
  if [ ! -e PEcAn_$SIM.tar ]
  then
    echo "Get it: PEcAn_$SIM.tar"
    scp modex.bnl.gov:PEcAn_$SIM.tar .
    mkdir PEcAn_$SIM
    cd PEcAn_$SIM
    tar -xvf ../PEcAn_$SIM.tar
    cd ..
  else
    echo "Already seem to have PEcAn_$SIM.tar"
  fi
done

# And finally, convert from .Rdata to csv so we can easily read with pandas.
# This works, but leaves .Rdata in the csv filename
for F in $(find . -name "ensemble.ts.[0-9]*.Rdata")
do
cat <<EOF > oneoffR.R
setwd("$(dirname $F)")
load("$(basename $F)")
write.table(ensemble.ts, "$(basename $F).csv", sep=",")
EOF
Rscript --vanilla oneoffR.R
done

for F in $(find . -name "sensitivity.results*.Rdata")
do
cat <<EOF > oneoffR.R
setwd("$(dirname $F)")
load("$(basename $F)")
for (PFTNAME in names(sensitivity.results)) {
  new_file_name <- paste0("$(basename $F)", ".", PFTNAME, ".csv")
  print(new_file_name)
  write.table(sensitivity.results[[PFTNAME]][["variance.decomposition.output"]], new_file_name, sep=",")
}
EOF
Rscript --vanilla oneoffR.R
done
