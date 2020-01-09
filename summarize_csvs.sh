#!/bin/bash

# T. Carman Dec 2019

# Snippets of code to summarize csv files...

# With sensitivity.results files, there is one file per each
# output variable, per PFT, per site, so about 600 small csv
# csv files. Also due to the way R exports tables to csv
# there columns are not labled correctly (missing first column
# label and it shifts everything to the left).

# This adds a column name to each csv file and dumps them
# all to a single file.
for f in $(find . -name "sensitivity.results*.csv"); do 
  echo $f;
  sed '1s/^/"Parameter",/g' $f; # Look at first line, anchor to start and replace 
  echo "";
done > /tmp/sens_res.csv
