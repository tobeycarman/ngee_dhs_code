#!/bin/bash

function usage() {
  echo "Usage:
    $ ./rdata2csv.sh path/to/pecan/dir
  "
}

if [[ $# -ne 1 ]]; then
  echo "Invalid arguments! Must pass one path to a pecan run directory."
  usage
  exit
fi


WORKING_DIR=$1
echo Looking for files in "$WORKING_DIR"

# And finally, convert from .Rdata to csv so we can easily read with pandas.
# This works, but leaves .Rdata in the csv filename
for F in $(find $WORKING_DIR -name "ensemble.ts.[0-9]*.Rdata")
do
cat <<EOF > oneoffR.R
setwd("$(dirname $F)")
load("$(basename $F)")
write.table(ensemble.ts, "$(basename $F).csv", sep=",")
EOF
Rscript --vanilla oneoffR.R
done

for F in $(find $WORKING_DIR -name "sensitivity.results*.Rdata")
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

