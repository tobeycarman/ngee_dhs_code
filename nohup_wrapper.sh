#!/bin/bash


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


