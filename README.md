README.md 
=========

Parts of the code are setup to run on T.Carman's local workstation, and
parts are to be run on tcarman@modex.bnl.gov.

Overall workflow is like so:

0. Update and compile desired versions of PEcAn and dvmdostem.
1. Update dvmdostem-input-catalog (use dvmdostem update-mirror.sh script). 
2. Run model (via pecan) over the various experiment cases.
 - Adjust pecan xml file(s) for run(s)
 - submit with nohup_wrapper.sh
 - preprocessing (pecan meta analysis) happens on head node
 - model runs are submitted by qsub and happen on other nodes
 - model2netcdf I think runs on head node
3. run posthoc_easa.R
 - use the ph_nohup_wrapper.sh
 - this does not use qsub - all work is done on head!!
4. Convert Rdata to csv files using rdata2csv.sh
5. rsync to local
 - change into ~/Documents/SEL/NGEE_Dec_2018_followup
 - rename (move) the ngee_dhs_runs directory to archive
 - then get the new stuff
    `$ rsync -avz --exclude "*/out/*" --exclude "*/run/*" --exclude="*/yearly_runs/*" modex.bnl.gov:/data/tcarman/ngee_dhs_runs .`
6. run plotting with ppp.py


