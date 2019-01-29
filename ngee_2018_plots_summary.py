#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import datetime as dt
import cfunits

'''
# One file per community type, per variable
!find . -name "*ensemble.ts.[0-9]*" | grep Soil| grep csv
./PEcAn_2000001169/ensemble.ts.2000001231.SoilOrgC.1970.2029.Rdata.csv
./PEcAn_2000001157/ensemble.ts.2000001208.SoilOrgC.1970.2029.Rdata.csv
./PEcAn_2000001166/ensemble.ts.2000001226.SoilOrgC.1970.2029.Rdata.csv
'''
tab20c = plt.cm.get_cmap('tab20c')

def mname2idx(mname):
  return dt.datetime.strptime('{} 1 1970'.format(mname), '%B %d %Y')

def midx2mname(midx):
  return dt.date(year=1970, month=midx, day=1).strftime('%B')

def make_er_up(axes_inst, ds, label, color, ylabel):
  # For some reason, the Rdata file is organized with rows for the ensembles,
  # and columns for the timesteps. I find this confusing...
  #a = ds.transpose()

  # Make a nice datetime index to work with 
  dt_idx = pd.DatetimeIndex(start="1-1-1970", periods=60*12, freq="MS") # 60 years, start of month

  # And re-index our dataframe...
  ds.index = dt_idx

  d={i:np.array(ds[ds.index.month==i]).ravel() for i in range(1,13)}

  ddd = pd.DataFrame(d)
  ddd.columns = [midx2mname(i) for i in ddd.columns]

  # The docs are confusing, but this seems to work...
  axes_inst.boxplot(
      ddd.transpose(),
      labels=ddd.columns,
      sym='',             # don't show fliers (stuff beyond IQR)
      notch=False,        # no notches at confidence interval
      whis=[2.5,97.5],    # how far the whiskers should extend
      patch_artist=True,  # use a patch so that there is a facecolor
      boxprops=dict(linestyle='-', linewidth=1.0, color=color, facecolor=color, alpha=0.75),
      medianprops=dict(color='black')
  )
  axes_inst.set_title(label)
  axes_inst.set_ylabel(ylabel)

for k in ['NPP','SoilOrgC','HeteroResp','LAI']:
  # Make a nice datetime index to work with 
  dt_idx = pd.DatetimeIndex(start="1-1-1970", periods=60*12, freq="MS") # 60 years, start of month

  if k == 'NPP':
    shrub04 = pd.read_csv("PEcAn_2000001137/ensemble.ts.2000001184.NPP.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001154/ensemble.ts.2000001204.NPP.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001131/ensemble.ts.2000001180.NPP.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.DataFrame(cfunits.Units.conform(tussk05.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    shrub04 = pd.DataFrame(cfunits.Units.conform(shrub04.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    heath07 = pd.DataFrame(cfunits.Units.conform(heath07.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    units_list = ("g C m-2 month-1","g C m-2 month-1","g C m-2 month-1")
  elif k == 'SoilOrgC':
    tussk05 = pd.read_csv("PEcAn_2000001169/ensemble.ts.2000001231.SoilOrgC.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001157/ensemble.ts.2000001208.SoilOrgC.1970.2029.Rdata.csv").transpose()
    shrub04 = pd.read_csv("PEcAn_2000001166/ensemble.ts.2000001226.SoilOrgC.1970.2029.Rdata.csv").transpose()
    units_list = ("kg C m-2","kg C m-2","kg C m-2")
  elif k == 'HeteroResp':
    shrub04 = pd.read_csv("PEcAn_2000001138/ensemble.ts.2000001186.HeteroResp.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001132/ensemble.ts.2000001182.HeteroResp.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001129/ensemble.ts.2000001177.HeteroResp.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.DataFrame(cfunits.Units.conform(tussk05.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    shrub04 = pd.DataFrame(cfunits.Units.conform(shrub04.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    heath07 = pd.DataFrame(cfunits.Units.conform(heath07.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    units_list = ("g C m-2 month-1","g C m-2 month-1","g C m-2 month-1")
  elif k == 'LAI':
    shrub04 = pd.read_csv("PEcAn_2000001165/ensemble.ts.2000001223.LAI.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001168/ensemble.ts.2000001229.LAI.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001164/ensemble.ts.2000001222.LAI.1970.2029.Rdata.csv").transpose()
    units_list = ("m-2/m-2","m-2/m-2","m-2/m-2")
  else:
    pass # should never get here...

  # Make the figs
  fig = plt.figure(figsize=(15,7))

  ax0 = plt.subplot2grid((3, 1), (0, 0))
  ax1 = plt.subplot2grid((3, 1), (1, 0))
  ax2 = plt.subplot2grid((3, 1), (2, 0))
  ax_ds = zip(
      (ax0, ax1, ax2),
      (heath07, shrub04, tussk05), 
      ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
      (tab20c.colors[0], tab20c.colors[4], tab20c.colors[8]),
      units_list,
    )

  for ax, ds, label, color, ylabel in ax_ds:
    make_er_up(ax, ds, label, color, ylabel)

  plt.suptitle("{} with median line and whiskers at 2.5% and 97.5%".format(k))
  plt.savefig("boxplot_{}_monthly.pdf".format(k))

# Could use this to put the box plot of *all* the data on the right.
# fig = plt.figure(figsize=(15,7))
# shape=(3,8)
# ax0m = plt.subplot2grid(shape, (0,0), rowspan=1, colspan=7)
# ax0t = plt.subplot2grid(shape, (0,7), rowspan=1, colspan=1)

# ax1m = plt.subplot2grid(shape, (1,0), rowspan=1, colspan=7)
# ax1t = plt.subplot2grid(shape, (1,7), rowspan=1, colspan=1)

# ax2m = plt.subplot2grid(shape, (2,0), rowspan=1, colspan=7)
# ax2t = plt.subplot2grid(shape, (2,7), rowspan=1, colspan=1)






