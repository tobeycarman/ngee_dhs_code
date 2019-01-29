#!/usr/bin/env python

# Tobey Carman, November 2018

# TIMESERIES PLOTS

# Scripts for creating plots for NGEE meeting in early December.
# To be presented by E.Euskirchen and S.Serbin.

# See code from AGU meeting 2017. This is basically the same thing, but extended
# to include more PFTs.

# Use the ngee_2018_data_prep.sh script to setup for this script.

import pandas as pd
import numpy as np
import cfunits
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, MaxNLocator

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


def make_timeseries_plot(dataset_list, label_list, yax_label, suptitle, savename):

  # MAKE THE TIMESERIES FIGURE(S)
  fig2 = plt.figure(figsize=(15,7))

  ax0 = plt.subplot2grid((3, 1), (0, 0))
  ax1 = plt.subplot2grid((3, 1), (1, 0))
  ax2 = plt.subplot2grid((3, 1), (2, 0))
  ax_ds = zip(
      (ax0, ax1, ax2),
      dataset_list,
      label_list,
      (tab20c.colors[0], tab20c.colors[4], tab20c.colors[8])
    )

  START=240 #1990
  END=540   #2015

  for ax, ds, txt, custcol in ax_ds:
    ax.plot(dt_idx[START:END], ds[START:END].quantile(.025, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
    ax.plot(dt_idx[START:END], ds[START:END].quantile(.975, 1), linewidth=0, color="black", alpha=0.5, linestyle=':')
    ax.plot(dt_idx[START:END], ds[START:END].median(1), linewidth=1.0, color=custcol, label="median", alpha=0.5)
    ax.fill_between(dt_idx[START:END].to_pydatetime(), ds[START:END].quantile(.025, 1), ds[START:END].quantile(.975, 1), color='gray', alpha=0.35)

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