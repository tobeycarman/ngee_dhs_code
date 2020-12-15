# README for prior and posterior summary tables

PEcAn's method for keeping the prior and posteriors for the runs is that
each run has a small `.Rdata` file for priors and posteriors used for that run. 
We assembled some scripts that can merge all these disparate files into
one larger csv file so that we could browse the data in one place without needing
 to use `R`.

The scripts are as follows:
1. `collate_priors_posteriors.sh` - collects all the .Rdata files converst so csv, and merges to single file
2. `fix_priors_posteriors_table.py` - prettify parameter names, add units column
3. `fix_priors_posteriors_table2.R` - adds median and confidence interval columns

## Column Descriptions

* pftname = name of the community type and PFT (4 = shrub tundra, 5 = tussock tundra, 6 = wet sedge tundra , 7 = heath tundra)
* vname = variable (parameter) name
* units = the units of measurement
* distname = statistical distribution assigend to the parameter range of values, using R distributions
* parama = first parameter of the distribution
* paramb = second parameter of the distribution
* n = the number of samples in the Bety DB for the parameter/variable 
* cimin = lower confidence interval
* cimax = upper confidence interval
* median = median value of the parameter