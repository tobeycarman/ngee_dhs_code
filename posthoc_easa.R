#!/usr/bin/env Rscript

# T. Carman Jan 2019

# Written as a helper/crutch for performing Ensemble Analysis (EA) 
# and Sensitivity Analysis (SA). Basically the PEcAn run can't be 
# for more than one variable at a time, so this script runs the 
# EA and SA for another variable after a PEcAn is done with all
# the model runs. 

# Loading the pecan libraries is slow, so first process the command
# line arguments.

args = commandArgs(trailingOnly=TRUE) 

# test if there is at least one argument: if not, return an error
if (length(args) < 2) {
  stop("At least two arguments must be supplied:\n",
       " - a path to a working directory containing a pecan.xml file\n", 
       " - one or more variable names to be processed.\n", 
       "The pecan.xml file must in turn have an outdir path set that\n",
       "points toward a directory with all the PEcAn outputs.", call.=FALSE)
} else {
  working_dir = args[1]
  var_list = args[-1]    # All but the first argument
} 

# for (new_variable in var_list){
#   print(new_variable)
# }
# q()

# Load all the pecan libs
library(PEcAn.all)
library(PEcAn.utils)
library(RCurl)

# Load the settings object. Start by loading the base pecan.xml file that
# is found in the "working_dir". Then adjust the settings$outdir to be the 
# "working dir" passed on the command line. Note that this is not always 
# necessary, but if the directories have been moved after they were initially
# run and the pecan.xml files have the original paths, then it is necessary to
# make sure the path is correct so that all the outputs can be found and 
# processed. Then load the *last* pecan file, which is the pecan.CONFIGS.xml.
# And finally, make sure that the settings$outdir is again correctly set to the
# working_dir passed on the command line
settings <- PEcAn.settings::read.settings(inputfile=file.path(working_dir, "pecan.xml"))
settings$outdir <- working_dir
settings <- PEcAn.settings::read.settings(inputfile=file.path(settings$outdir, "pecan.CONFIGS.xml"))
settings$outdir <- working_dir

#print(settings$outdir)

for (new_variable in var_list) {

  settings$ensemble$variable <- new_variable
  settings$sensitivity.analysis$variable <- new_variable
  
  # Process the model results
  runModule.get.results(settings)
  
  # Run the EA
  runModule.run.ensemble.analysis(settings, TRUE)
  
  # Run the SA
  runModule.run.sensitivity.analysis(settings, plot=FALSE)

}
