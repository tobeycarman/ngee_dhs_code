#!/bin/bash

# T. Carman, 2019

# A script for submitting pecan runs over the command line
# (instead of the web interface). 
#
# Assumes that you have a pecan.xml file in a directory
# that will be used for the pecan run(s). A log file will
# be saved there as well. **NOTE** this script will clean
# the directory of everything but the pecan.xml file 
# before it starts.
# 
# Assumes that you have a workflow.R script next to this script.
#
# **NOTE** killing the process won't work correctly after the
# model jobs have launched, so you only have a few minutes at
# the beginning to stop things. Once we start using the 
# modellauncher part of PEcAn, this should be less of a problem.
#

PECANFILE=$1

WORK_DIR=$(dirname $PECANFILE)

LOGFILE="$WORK_DIR/workflow.log"


echo "Starting with pecan file: $PECANFILE"

echo "Cleaning up directory: $WORK_DIR"
echo "Found $(ls $WORK_DIR | grep -v pecan.xml | wc -l) files..."
for F in $(ls $WORK_DIR | grep -v pecan.xml)
do
  echo "Removing $WORK_DIR/$F"
  rm -r $WORK_DIR/$F
done

echo "Writing to log file: $LOGFILE"


nohup Rscript workflow.R $PECANFILE > $LOGFILE 2>&1 &
echo $! > save_pid.txt

# Spit out process number...
echo "PID of started nohup process is: $(cat save_pid.txt)"


