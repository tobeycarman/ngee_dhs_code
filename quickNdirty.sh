#!/bin/bash

# T. Carman, March 2019
# 
# 'cust_model2netcdf.R' is a copy of:
#      modex.bnl.gov:/data/software/pecan_dev/models/dvmdostem/R/model2netcdf.dvmdostem.R
# with VegC added to the outputs to translate.
# 

OKF="oklist.txt"
MF="missinglist.txt"

###### FIRST, UNCOMMENT THIS AND MAKE FILE LISTS
# echo -n "" > $OKF
# echo -n "" > $MF
# for END_PATH in $(find . -type d -name "yearly_runs" -prune -o -path "*/out/*" -type d -print)
# do 
#   FULL_PATH="/data/tcarman/ngee_dhs_runs/$END_PATH"
#   if [[ $(ncdump -h $FULL_PATH/2015.nc | grep "double VegC" | wc -l) -lt 1 ]]
#   then
#     echo "$FULL_PATH" >> $MF
#   else
#     echo "$FULL_PATH" >> $OKF
#   fi
# done

###### THEN RE-COMMENT ABOVE AND USE THIS PART
# This is a qsub array job. First, count the lines in the 
# missing list so we know how many tasks we'll need. Then 
# submit this script like this:
#     $ qsub -t 1-$(wc -l missinglist.txt)%100
# The %100 tells qsub not to have more than 100 concurrent tasks.
cd /data/tcarman/ngee_dhs_runs
echo "PBS_ARRAYID is: $PBS_ARRAYID"
FFP=$(tail -n+"$PBS_ARRAYID" $MF | head -n 1)
echo "Will call qd with $FFP"

./qd.sh "$FFP"

