#!/usr/bin/env python

# Tobey Carman, November 2018

# TIMESERIES PLOTS

# Scripts for creating plots for NGEE meeting in early December.
# To be presented by E.Euskirchen and S.Serbin.

# See code from AGU meeting 2017. This is basically the same thing, but extended
# to include more PFTs.

# Use the ngee_2018_data_prep.sh script to setup for this script.

import os
import glob
import pandas as pd
import numpy as np
import cfunits
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, MaxNLocator

# Build up a configuration dict with info about our runs.
config = dict(
  runs=[
    dict( site="dhs_1", cmt="cmt04", ),
    dict( site="dhs_2", cmt="cmt04", ),
    dict( site="dhs_3", cmt="cmt04", ),
    dict( site="dhs_4", cmt="cmt04", ),
    dict( site="dhs_5", cmt="cmt04", ),
    dict( site="dhs_1", cmt="cmt05", ),
    dict( site="dhs_2", cmt="cmt05", ),
    dict( site="dhs_3", cmt="cmt05", ),
    dict( site="dhs_4", cmt="cmt05", ),
    dict( site="dhs_5", cmt="cmt05", ),
    dict( site="kougorak", cmt="cmt04", ),
    dict( site="kougorak", cmt="cmt05", ),
    dict( site="kougorak", cmt="cmt07", ),
    dict( site="southbarrow", cmt="cmt06", ),
  ]
)

# Fill out some more info that I am too lazy to type by hand
for r in config['runs']:
    r['vars'] = 'NPP,LAI,HeteroResp,SoilOrgC'.split(',')
    r['years'] = (1990,2015)


#
def load_ensemble_ts(path, var, year_start, year_end):
  # Something like: dhs_1_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv
  g = os.path.join(path, "ensemble.ts.*.{}.{}.{}.Rdata.csv".format(var, year_start, year_end))
  fl = glob.glob(g) 
  print g
  print "trying to open:", fl

  if len(fl) > 1:
    print fl
    raise RuntimeError("Too many files found!")
  elif len(fl) < 1:
    print fl
    raise RuntimeError("Not enough files found!")
  return pd.read_csv(fl[0]).transpose()

# Load all the data into the config object. 
for run in config['runs']:
  for var in run['vars']:
    # Load the data into memory...
    startyr, endyr = run['years']

    df = load_ensemble_ts("../NGEE_Dec_2018_followup/yearly_runs/{}_{}".format(run['site'], run['cmt']), var, startyr, endyr )

    #dt_dix = pd.DatetimeIndex(start="1-1-{}".format(startyr), periods=(endyr-startyr)+1, freq='MS')

    run['ens_ts_{}'.format(var)] = df


def df_convert_index(dataFrame, start="1-1-1990"):

  if any([x in dataFrame.index[0] for x in "NPP HR".split(" ")]):
    from_units = cfunits.Units("kg C m-2 s-1")
    to_units = cfunits.Units("g C m-2 month-1")

  if any([x in dataFrame.index[0] for x in "".split(" ")]):
    pass

  months, ens_members = dataFrame.shape
  #print months, ens_members

  dt_idx = pd.DatetimeIndex(start=start, periods=months, freq="MS")
  #print dt_idx.shape
  #print dataFrame.shape
  #dataFrame = dataFrame.transpose()
  #print dataFrame.shape

  dataFrame = pd.DataFrame(cfunits.Units.conform(dataFrame.values, from_units, to_units), index=dt_idx)

  return dataFrame


dhs1_shrub04_ts_NPP = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv").transpose()
dhs2_shrub04_ts_NPP = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_2_cmt04/ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv").transpose()
dhs3_shrub04_ts_NPP = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_3_cmt04/ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv").transpose()
dhs4_shrub04_ts_NPP = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_4_cmt04/ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv").transpose()
dhs5_shrub04_ts_NPP = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_5_cmt04/ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv").transpose()

dhs1_shrub04_ts_HeteroResp = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv").transpose()
dhs2_shrub04_ts_HeteroResp = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_2_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv").transpose()
dhs3_shrub04_ts_HeteroResp = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_3_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv").transpose()
dhs4_shrub04_ts_HeteroResp = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_4_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv").transpose()
dhs5_shrub04_ts_HeteroResp = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_5_cmt04/ensemble.ts.2000001299.HeteroResp.1990.2015.Rdata.csv").transpose()

dhs1_shrub04_ts_SOC = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/ensemble.ts.2000001299.SOC.1990.2015.Rdata.csv").transpose()
dhs2_shrub04_ts_SOC = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_2_cmt04/ensemble.ts.2000001299.SOC.1990.2015.Rdata.csv").transpose()
dhs3_shrub04_ts_SOC = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_3_cmt04/ensemble.ts.2000001299.SOC.1990.2015.Rdata.csv").transpose()
dhs4_shrub04_ts_SOC = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_4_cmt04/ensemble.ts.2000001299.SOC.1990.2015.Rdata.csv").transpose()
dhs5_shrub04_ts_SOC = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_5_cmt04/ensemble.ts.2000001299.SOC.1990.2015.Rdata.csv").transpose()

dhs1_shrub04_ts_LAI = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/ensemble.ts.2000001299.LAI.1990.2015.Rdata.csv").transpose()
dhs2_shrub04_ts_LAI = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_2_cmt04/ensemble.ts.2000001299.LAI.1990.2015.Rdata.csv").transpose()
dhs3_shrub04_ts_LAI = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_3_cmt04/ensemble.ts.2000001299.LAI.1990.2015.Rdata.csv").transpose()
dhs4_shrub04_ts_LAI = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_4_cmt04/ensemble.ts.2000001299.LAI.1990.2015.Rdata.csv").transpose()
dhs5_shrub04_ts_LAI = pd.read_csv("../NGEE_Dec_2018_followup/yearly_runs/dhs_5_cmt04/ensemble.ts.2000001299.LAI.1990.2015.Rdata.csv").transpose()


make_timeseries_plot(
    (dhs1_shrub04_ts_HeteroResp, dhs2_shrub04_ts_HeteroResp, ....), 
    ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
    "m-2/m-2",
    "LAI",
    "timeseries_LAI.pdf"
)





# Read in data
heath07_ts_HR  =   pd.read_csv("PEcAn_2000001129/ensemble.ts.2000001177.HeteroResp.1970.2029.Rdata.csv").transpose()
heath07_ts_NPP =   pd.read_csv("PEcAn_2000001131/ensemble.ts.2000001180.NPP.1970.2029.Rdata.csv").transpose()
heath07_ts_LAI =   pd.read_csv("PEcAn_2000001164/ensemble.ts.2000001222.LAI.1970.2029.Rdata.csv").transpose()
heath07_ts_SoilC = pd.read_csv("PEcAn_2000001157/ensemble.ts.2000001208.SoilOrgC.1970.2029.Rdata.csv").transpose()

shrub04_ts_HR  =   pd.read_csv("PEcAn_2000001138/ensemble.ts.2000001186.HeteroResp.1970.2029.Rdata.csv").transpose()
shrub04_ts_NPP =   pd.read_csv("PEcAn_2000001137/ensemble.ts.2000001184.NPP.1970.2029.Rdata.csv").transpose()
shrub04_ts_LAI =   pd.read_csv("PEcAn_2000001165/ensemble.ts.2000001223.LAI.1970.2029.Rdata.csv").transpose()
shrub04_ts_SoilC = pd.read_csv("PEcAn_2000001166/ensemble.ts.2000001226.SoilOrgC.1970.2029.Rdata.csv").transpose()

tussk05_ts_HR  =   pd.read_csv("PEcAn_2000001132/ensemble.ts.2000001182.HeteroResp.1970.2029.Rdata.csv").transpose()
tussk05_ts_NPP =   pd.read_csv("PEcAn_2000001154/ensemble.ts.2000001204.NPP.1970.2029.Rdata.csv").transpose()
tussk05_ts_LAI =   pd.read_csv("PEcAn_2000001168/ensemble.ts.2000001229.LAI.1970.2029.Rdata.csv").transpose()
tussk05_ts_SoilC = pd.read_csv("PEcAn_2000001169/ensemble.ts.2000001231.SoilOrgC.1970.2029.Rdata.csv").transpose()




# Build nice date time index
dt_idx = pd.DatetimeIndex(start="1-1-1970", periods=60*12, freq="MS") # 60 years, start of month

# Convert to more manageable units
heath07_ts_HR_tu     = pd.DataFrame(cfunits.Units.conform(heath07_ts_HR.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
heath07_ts_NPP_tu    = pd.DataFrame(cfunits.Units.conform(heath07_ts_NPP.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
shrub04_ts_HR_tu     = pd.DataFrame(cfunits.Units.conform(shrub04_ts_HR.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
shrub04_ts_NPP_tu    = pd.DataFrame(cfunits.Units.conform(shrub04_ts_NPP.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
tussk05_ts_HR_tu     = pd.DataFrame(cfunits.Units.conform(tussk05_ts_HR.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
tussk05_ts_NPP_tu    = pd.DataFrame(cfunits.Units.conform(tussk05_ts_NPP.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)

# No need to convert units on LAI and SoilOrgC


tab20c = plt.cm.get_cmap('tab20c')


# # MAKE THE TIMESERIES FIGURE(S)
# fig = plt.figure(figsize=(15,7))

# ax0 = plt.subplot2grid((3, 1), (0, 0))
# ax1 = plt.subplot2grid((3, 1), (1, 0))
# ax2 = plt.subplot2grid((3, 1), (2, 0))
# ax_ds = zip(
#     (ax0, ax1, ax2),
#     (heath07_ts_HR_tu, shrub04_ts_HR_tu, tussk05_ts_HR_tu), 
#     ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
#     (tab20c.colors[0], tab20c.colors[4], tab20c.colors[8])
#   )

# START=240 #1990
# END=540   #2015

# for ax, ds, txt, custcol in ax_ds:
#   ax.plot(dt_idx[START:END], ds[START:END].quantile(.025, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
#   ax.plot(dt_idx[START:END], ds[START:END].quantile(.975, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
#   ax.plot(dt_idx[START:END], ds[START:END].median(1), linewidth=1.0, color=custcol, label="median", alpha=0.5)
#   ax.fill_between(dt_idx[START:END].to_pydatetime(), ds[START:END].quantile(.025, 1), ds[START:END].quantile(.975, 1), color='gray', alpha=0.35)

#   # Proxy artist for the legend
#   pa = ax.fill(np.nan, np.nan, color='gray', linewidth=.5, alpha=0.35, label="95% CI")
#   ax.legend(loc='best')

#   # box = ax.get_position()
#   # ax.set_position([box.x0, box.y0 + box.height * 0.1,
#   #                  box.width, box.height * 0.9])

#   # # Put a legend below current axis
#   # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

#   ax.set_ylabel("g C m-2 month-1")

#   ax.set_title(txt)

# plt.suptitle("HeteroResp")
# plt.savefig("timeseries_HeteroResp.pdf")
# #plt.show(block=True)


# # MAKE THE TIMESERIES FIGURE(S)
# fig2 = plt.figure(figsize=(15,7))

# ax0 = plt.subplot2grid((3, 1), (0, 0))
# ax1 = plt.subplot2grid((3, 1), (1, 0))
# ax2 = plt.subplot2grid((3, 1), (2, 0))
# ax_ds = zip(
#     (ax0, ax1, ax2),
#     (heath07_ts_NPP_tu, shrub04_ts_NPP_tu, tussk05_ts_NPP_tu), 
#     ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
#     (tab20c.colors[0], tab20c.colors[4], tab20c.colors[8])
#   )

# START=240 #1990
# END=540   #2015

# for ax, ds, txt, custcol in ax_ds:
#   ax.plot(dt_idx[START:END], ds[START:END].quantile(.025, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
#   ax.plot(dt_idx[START:END], ds[START:END].quantile(.975, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
#   ax.plot(dt_idx[START:END], ds[START:END].median(1), linewidth=1.0, color=custcol, label="median", alpha=0.5)
#   ax.fill_between(dt_idx[START:END].to_pydatetime(), ds[START:END].quantile(.025, 1), ds[START:END].quantile(.975, 1), color='gray', alpha=0.35)

#   # Proxy artist for the legend
#   pa = ax.fill(np.nan, np.nan, color='gray', linewidth=.5, alpha=0.35, label="95% CI")
#   ax.legend(loc='best')

#   # box = ax.get_position()
#   # ax.set_position([box.x0, box.y0 + box.height * 0.1,
#   #                  box.width, box.height * 0.9])

#   # # Put a legend below current axis
#   # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

#   ax.set_ylabel("g C m-2 month-1")

#   ax.set_title(txt)

# plt.suptitle("NPP")
# plt.savefig("timeseries_NPP.pdf")
# #plt.show(block=True)


def make_timeseries_plot(dataset_list, label_list, color_list, yax_label, suptitle, savename):

  # MAKE THE TIMESERIES FIGURE(S)
  fig2 = plt.figure(figsize=(15,7))

  axes = [plt.subplot2grid((len(dataset_list),1),(i, 0)) for i, x in enumerate(dataset_list)]

  

  # ax0 = plt.subplot2grid((3, 1), (0, 0))
  # ax1 = plt.subplot2grid((3, 1), (1, 0))
  # ax2 = plt.subplot2grid((3, 1), (2, 0))
  ax_ds = zip(
      axes,
      dataset_list,
      label_list,
      color_list
    )

  #START=240 #1990
  #END=540   #2015

  for ax, ds, txt, custcol in ax_ds:
    print type(ds)
    ax.plot(ds.index[0:], ds[0:].quantile(.025, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
    ax.plot(ds.index[0:], ds[0:].quantile(.975, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
    ax.plot(ds.index[0:], ds[0:].median(1), linewidth=1.0, color=custcol, label="median", alpha=0.5)
    ax.fill_between(ds.index[0:].to_pydatetime(), ds[0:].quantile(.025, 1), ds[0:].quantile(.975, 1), color='gray', alpha=0.35)

    # Proxy artist for the legend
    pa = ax.fill(np.nan, np.nan, color='gray', linewidth=.5, alpha=0.35, label="95% CI")
    ax.legend(loc='best')

    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.1,
    #                  box.width, box.height * 0.9])

    # # Put a legend below current axis
    # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

    ax.set_ylabel(yax_label)

    ax.set_title(txt)

  plt.suptitle(suptitle)
  plt.savefig(savename)
  #plt.show(block=True)

make_timeseries_plot(
  (df_convert_index(filter(lambda x: x['site']=='dhs_1' and x['cmt']=='cmt04', config['runs'])[0]['ens_ts_NPP']),
   df_convert_index(filter(lambda x: x['site']=='dhs_2' and x['cmt']=='cmt04', config['runs'])[0]['ens_ts_NPP']),
   df_convert_index(filter(lambda x: x['site']=='dhs_3' and x['cmt']=='cmt04', config['runs'])[0]['ens_ts_NPP']),
   df_convert_index(filter(lambda x: x['site']=='dhs_4' and x['cmt']=='cmt04', config['runs'])[0]['ens_ts_NPP']),
   df_convert_index(filter(lambda x: x['site']=='dhs_5' and x['cmt']=='cmt04', config['runs'])[0]['ens_ts_NPP'])),
  ('dhs1_cmt04,dhs2_cmt04,dhs3_cmt04,dhs4_cmt04,dhs5_cmt04'.split(',')),
  ("red","green","blue","orange","yellow"),
  "???",
  "timseries",
  "test.pdf"  
)

make_timeseries_plot(
    (heath07_ts_LAI, shrub04_ts_LAI, tussk05_ts_LAI), 
    ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
    "m-2/m-2",
    "LAI",
    "timeseries_LAI.pdf"
)

make_timeseries_plot(
    (heath07_ts_SoilC, shrub04_ts_SoilC, tussk05_ts_SoilC), 
    ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)",),
    "kg C m-2",
    "SoilOrgC",
    "timeseries_SoilOrgC.pdf"
)


''' JUNK BELOW '''