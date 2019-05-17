#!/bin/bash

# T Carman Spring 2019

function usage() {
  echo "Usage:
    $ ./ph_nohup_wrapper.sh path/to/pecan/dir
  "
}

if [[ $# -ne 1 ]]; then
  echo "Invalid arguments! Must pass one path to a pecan run directory."
  usage
  exit
fi

WORKING_DIR=$1  # e.g.: ngee_dhs_runs/dhs_1_cmt04

nohup ./posthoc_easa.R "$WORKING_DIR" AvailN GPP LAI NPP NUptakeLab NUptakeSt OrgN HeteroResp AutoResp SoilOrgC VegC VegN > "$WORKING_DIR"/posthoc_easa.log 2>&1 &

echo $! > "$WORKING_DIR"/save_easa_pid.txt

echo "PID of started nohup process is: $(cat $WORKING_DIR/save_easa_pid.txt)"


