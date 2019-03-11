# Tobey Carman, Spring 2019

# Snippets for post processing plotting and retrieving data from 
# NGEE PEcAn runs, for work with E.Euskirchen and S.Serbin.

# Runs are generally done on modex, sometimes post processing and plotting on 
# modex, sometimes locally, and then generally you want to retrieve data
# from modex, either final plots, or .Rdata and .csv files that can be used to 
# plot locally.

# General functionality is:
#  - finding appropriate files and converting from .Rdata to .csv for easy
#    import into python/pandas
#  - running plotting scripts over different combinations of run directories
#  - copying data (with rsync) from the remote to a local machine

################################################################################
#
# NOTE: Not intended to run as a script - simply copy/paste snippets as needed!
#
################################################################################

declare -a RUNLIST=(
"dhs_1_cmt04" "dhs_1_cmt05"
"dhs_2_cmt04" "dhs_2_cmt05"
"dhs_3_cmt04" "dhs_3_cmt05"
"dhs_4_cmt04" "dhs_4_cmt05"
"dhs_5_cmt04" "dhs_5_cmt05"
"kougorak_cmt04" "kougorak_cmt05" "kougorak_cmt07" "southbarrow_cmt06")

for RUN in ${RUNLIST[@]}:
do

# #./posthoc_easa.R ngee_dhs_runs/"$RUN" LAI HeteroResp SoilOrgC
# cd ngee_dhs_runs/$RUN
# ##################
# # And finally, convert from .Rdata to csv so we can easily read with pandas.
# # This works, but leaves .Rdata in the csv filename
# for F in $(find . -name "ensemble.ts.[0-9]*.Rdata")
# do
# cat <<EOF > oneoffR.R
# setwd("$(dirname $F)")
# load("$(basename $F)")
# write.table(ensemble.ts, "$(basename $F).csv", sep=",")
# EOF
# Rscript --vanilla oneoffR.R
# done

# for F in $(find . -name "sensitivity.results*.Rdata")
# do
# cat <<EOF > oneoffR.R
# setwd("$(dirname $F)")
# load("$(basename $F)")
# for (PFTNAME in names(sensitivity.results)) {
#   new_file_name <- paste0("$(basename $F)", ".", PFTNAME, ".csv")
#   print(new_file_name)
#   write.table(sensitivity.results[[PFTNAME]][["variance.decomposition.output"]], new_file_name, sep=",")
# }
# EOF
# Rscript --vanilla oneoffR.R
# done
# #################
./ppp.py ngee_dhs_runs/"$RUN"
#cd /data/tcarman/

done

#rsync -avz --exclude "*/out/*" --exclude "*/run/*" modex.bnl.gov:/data/tcarman/ngee_dhs_runs/dhs_1_cmt04 ngee_dhs_runs/

# Copy to local
cd /Users/tobeycarman/Documents/SEL/NGEE_Dec_2018_followup
rsync -avz --delte --exclude "*/out/*" --exclude "*/run/*" --exclude="*/yearly_runs/*" modex.bnl.gov:/data/tcarman/ngee_dhs_runs .


# Clean up some old cruft
find ngee_dhs_runs/kougorak_cmt04/plots/ -name "frs_*.pdf" | grep -v driver | xargs rm
find ngee_dhs_runs/kougorak_cmt04/plots/ -name variance_decomposition.pdf | xargs rm

find ngee_dhs_runs/kougorak_cmt05/plots/ -name "frs_*.pdf" | grep -v driver | xargs rm
find ngee_dhs_runs/kougorak_cmt05/plots/ -name variance_decomposition.pdf | xargs rm

find ngee_dhs_runs/kougorak_cmt07/plots/ -name "frs_*.pdf" | grep -v driver | xargs rm
find ngee_dhs_runs/kougorak_cmt07/plots/ -name variance_decomposition.pdf | xargs rm

find ngee_dhs_runs/southbarrow_cmt06/plots/ -name "frs_*.pdf" | grep -v driver | xargs rm
find ngee_dhs_runs/southbarrow_cmt06/plots/ -name variance_decomposition.pdf | xargs rm

for s in $(seq 1 5)
do
  for c in $(seq 4 5)
  do
    find ngee_dhs_runs/dhs_"$s"_cmt0"$c"/plots/ -name "frs_*.pdf" | grep -v driver | xargs rm
    find ngee_dhs_runs/dhs_"$s"_cmt0"$c"/plots/ -name variance_decomposition.pdf | xargs rm
  done
done




# Submitting the plotting script
nohup ./ppp.py ngee_dhs_runs/kougorak_cmt04/ > ngee_dhs_runs/kougorak_cmt04/plot.log 2>&1 &
nohup ./ppp.py ngee_dhs_runs/kougorak_cmt05/ > ngee_dhs_runs/kougorak_cmt05/plot.log 2>&1 &
nohup ./ppp.py ngee_dhs_runs/kougorak_cmt07/ > ngee_dhs_runs/kougorak_cmt07/plot.log 2>&1 &

nohup ./ppp.py ngee_dhs_runs/southbarrow_cmt06/ > ngee_dhs_runs/southbarrow_cmt06/plot.log 2>&1 &

for i in $(seq 1 5);
do
  nohup ./ppp.py ngee_dhs_runs/dhs_"$i"_cmt04/ > ngee_dhs_runs/dhs_"$i"_cmt04/plot.log 2>&1 &
  nohup ./ppp.py ngee_dhs_runs/dhs_"$i"_cmt05/ > ngee_dhs_runs/dhs_"$i"_cmt05/plot.log 2>&1 &
done


# For renaming files into flat directory with site and CMT in filename.
cd "/Users/tobeycarman/Documents/SEL/NGEE_Dec_2018_followup/ngee_dhs_runs"
mkdir ~/Downloads/testbed
for f in $(find . -wholename "*/plots/*");
do
  cp $f ~/Downloads/testbed/$(echo $f | python -c "import sys; s = sys.stdin.read(); s2 = s.strip().strip('.').strip('/').split('/')[0]; sys.stdout.write(s2)")_$(basename "$f")
done











