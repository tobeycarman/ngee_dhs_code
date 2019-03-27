#!/bin/bash

# T. Carman, March 2019
# Used to translate more output variables from PEcAn format to
# dvmdostem format.

FULL_PATH=$1

cd /data/tcarman/ngee_dhs_runs
source /home/tcarman/env_setup_pecan_cmdline.sh 
 
if [[ $(ncdump -h $FULL_PATH/2015.nc | grep "double VegC" | wc -l) -lt 1 ]]
then

  echo "Missing VegC! $FULL_PATH"
 
  echo ".libPaths(); source('cust_model2netcdf.R'); model2netcdf.dvmdostem('$FULL_PATH', '1990/01/01', '2015/12/31')" | R --vanilla

else
  echo "Must have completed in the interim...: $FULL_PATH"

fi


