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


declare -a SIMARR=("dhs_1_cmt04" "dhs_1_cmt05"
"dhs_2_cmt04" "dhs_2_cmt05"
"dhs_3_cmt04" "dhs_3_cmt05"
"dhs_4_cmt04" "dhs_4_cmt05"
"dhs_5_cmt04" "dhs_5_cmt05"
"kougorak_cmt04" "kougorak_cmt05" "kougorak_cmt07"
"southbarrow_cmt06")

# On modex, bundle up the data
# There is not need for *all* of the simulation results, just the stuff that
# is summarized in the .Rdata files
for SIM in "${SIMARR[@]}"
do
  cd /data/tcarman/ngee_dhs_runs/$SIM
  find . -name "*.Rdata" -exec tar -rvf ~/$SIM.tar {} \;
  cd ~
done

# Now, on OSX host (or VM), get the data from Modex
cd ~/Documents/SEL/NGEE_Dec_2018_followup
for SIM in "${SIMARR[@]}"
do
  if [ ! -e PEcAn_$SIM.tar ]
  then
    echo "Get it: PEcAn_$SIM.tar"
    scp modex.bnl.gov:$SIM.tar .
    mkdir $SIM
    cd $SIM
    tar -xvf ../$SIM.tar
    cd ..
  else
    echo "Already seem to have $SIM.tar"
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
