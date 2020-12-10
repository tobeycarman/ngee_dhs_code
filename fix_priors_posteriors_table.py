#!/usr/bin/env python

# T. Carman 2020

import sys
if 'post' in sys.argv[1]:
    outfile = "tbc-scratch/posteriors_table.csv"
elif 'prior' in sys.argv[1]:
    outfile ="tbc-scratch/priors_table.csv"


# This changes the names of the traits/parameters for easier reading...
# matching the parameter names that Eugenie used in her priors spreadsheet
swaps = [
  ["µmol m-2 s-1", "cuticular_cond", "Cuticular conductance"],
  ["unitless", "extinction_coefficient_diffuse","Extinction coefficient"],
  ["percent", "frprod_perc_10","Fine root productivity allocationn at 10 cm depth"],
  ["percent", "frprod_perc_20","Fine root productivity allocationn at 20 cm depth"],
  ["percent", "frprod_perc_30","Fine root productivity allocationn at 30 cm depth"],
  ["percent", "frprod_perc_40","Fine root productivity allocationn at 40 cm depth"],
  ["percent", "frprod_perc_50","Fine root productivity allocationn at 50 cm depth"],
  ["m s-1", "gcmax","gcmax; Maximum canopy conductance"],
  ["m2 m-2", "ilai","ilai; Starting value for leaf area index"],
  ["unitless", "klai","klai; Extinction coefficient for converting between LAI and foliar percent cover"],
  ["g N m-2", "labncon","labncon; Labile N concentration"],
  ["µmol m-2 s-1", "ppfd50","ppfd50; Amount of photosynthetically active radiation at which stomates partially (half) close"],
  ["degree_C", "pstemp_high","pstemp_high; The range of maximum temperatures for photosynthesis"],
  ["degree_C", "pstemp_low","pstemp_low; The range of minimal temperatures for photosynthesis"],
  ["degree_C", "pstemp_max","pstemp_max; Maximum temperature for photosynthesis"],
  ["degree_C", "pstemp_min","pstemp_min; Minimum temperature for photosynthesis"],
  ["m2 kg leaf-1", "SLA","SLA; specific leaf area"],
  ["W m-2", "SW_albedo","SW_albedo; Shortwave albedo"],
  ["Pa", "vpd_close","vpd_close; Vapor pressure deficit for leaf stomata fully closed"],
  ["Pa", "vpd_open","vpd_open; Vapor pressure deficit for leaf stomata fully opened"],
]

# add the units column...
with open(outfile) as f:
  data = f.readlines()
for i, line in enumerate(data):
  for units, origdesc, _ in swaps:
      if origdesc in line:
        line = line.strip().split(',')
        line.insert(2,'"{}"'.format(units))
        line = ','.join(line)
        line += '\n'
        data[i] = line
with open(outfile, 'w') as f:
  f.writelines(data)


# Swap out the strings.
with open(outfile) as f:
  data = f.read()
for i in swaps:
  data = data.replace(i[1], i[2])
with open(outfile, 'w') as f:
  f.write(data)

# Strip out the extraneous header lines 
# (leftover from lazily merging all the files)
with open(outfile) as f:
  data = f.readlines()
with open(outfile, 'w') as f:
  for line in data:
    if not all([i in line for i in ['parama', 'paramb','distn','n']]):
      f.write(line)

# Add a single header line at the top
with open(outfile) as f:
  data = f.readlines()
with open(outfile, 'w') as f:
  f.writelines(["pft,vname,units,distname,parama,paramb,n"])
  f.writelines(data)


