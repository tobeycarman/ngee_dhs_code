#!/usr/bin/env python


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import datetime as dt
import cfunits

# define date range of interest (1970 - 2029)
start = dt.datetime.strptime('1970-01-01', '%Y-%m-%d')
end = dt.datetime.strptime('2029-12-1', '%Y-%m-%d')


# Open the historic netcdf file
hds = nc.Dataset("../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/historic-climate.nc")
pds = nc.Dataset("../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/projected-climate.nc")
sidx = nc.date2index(start, hds.variables['time'], hds.variables['time'].calendar)
eidx = nc.date2index(end, pds.variables['time'], pds.variables['time'].calendar)

if (hds.variables['X'].size > 1) or (hds.variables['Y'].size > 1):
  print "WARNING!"
if (pds.variables['X'].size > 1) or (pds.variables['Y'].size > 1):
  print "WARNING!"

d = {}
dp = {}

for var in ['tair', 'precip','nirr','vapor_press']:
  # Extract the data from 1970 to the end of the file
  d[var] = hds.variables[var][sidx:,0,0]

  # extract data from start of file
  dp[var] = pds.variables[var][:eidx+1,0,0]


# Turn into dataframes
hdf = pd.DataFrame(d)
pdf = pd.DataFrame(dp)

# build nice index
hdates = nc.num2date(hds.variables['time'][sidx:], hds.variables['time'].units, hds.variables['time'].calendar)
hdates = [i.strftime() for i in hdates]
hdates = pd.DatetimeIndex(hdates)

pdates = nc.num2date(pds.variables['time'][:eidx+1], pds.variables['time'].units, pds.variables['time'].calendar)
pdates = [i.strftime() for i in pdates]
pdates = pd.DatetimeIndex(pdates)

hdf.index = hdates
pdf.index = pdates

# Get rid of overlapping data, prefering historic
fdf = pd.concat([hdf,pdf])
fdf[~fdf.index.duplicated(keep='first')]
# This is dumb - may not be a problem, as it appears that the files were 
# prepared correctly such that there is no overlap.


# heath, shrub, tussock
#tab20c.colors[0], tab20c.colors[4], tab20c.colors[8]

# Make an individual file for each output variable
for output_var in ['NPP', 'SoilOrgC', 'LAI', 'HeteroResp']:

  dt_idx = pd.DatetimeIndex(start='1970-01-01', freq='MS', periods=12*60)

  if output_var == 'NPP':
    shrub04 = pd.read_csv("PEcAn_2000001137/ensemble.ts.2000001184.NPP.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001154/ensemble.ts.2000001204.NPP.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001131/ensemble.ts.2000001180.NPP.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.DataFrame(cfunits.Units.conform(tussk05.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    shrub04 = pd.DataFrame(cfunits.Units.conform(shrub04.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    heath07 = pd.DataFrame(cfunits.Units.conform(heath07.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    output_var_units = "g C m-2 month-1"
  elif output_var == 'SoilOrgC':
    tussk05 = pd.read_csv("PEcAn_2000001169/ensemble.ts.2000001231.SoilOrgC.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001157/ensemble.ts.2000001208.SoilOrgC.1970.2029.Rdata.csv").transpose()
    shrub04 = pd.read_csv("PEcAn_2000001166/ensemble.ts.2000001226.SoilOrgC.1970.2029.Rdata.csv").transpose()
    output_var_units = 'kg C m-2'
  elif output_var == 'LAI':
    shrub04 = pd.read_csv("PEcAn_2000001165/ensemble.ts.2000001223.LAI.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001168/ensemble.ts.2000001229.LAI.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001164/ensemble.ts.2000001222.LAI.1970.2029.Rdata.csv").transpose()
    output_var_units = "m-2/m-2"
  elif output_var == 'HeteroResp':
    shrub04 = pd.read_csv("PEcAn_2000001138/ensemble.ts.2000001186.HeteroResp.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.read_csv("PEcAn_2000001132/ensemble.ts.2000001182.HeteroResp.1970.2029.Rdata.csv").transpose()
    heath07 = pd.read_csv("PEcAn_2000001129/ensemble.ts.2000001177.HeteroResp.1970.2029.Rdata.csv").transpose()
    tussk05 = pd.DataFrame(cfunits.Units.conform(tussk05.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    shrub04 = pd.DataFrame(cfunits.Units.conform(shrub04.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    heath07 = pd.DataFrame(cfunits.Units.conform(heath07.values, cfunits.Units("kg C m-2 s-1"), cfunits.Units("g C m-2 month-1")), index=dt_idx)
    output_var_units = "g C m-2 month-1"
  else:
    pass # should never get here...

  #units_list = ("g C m-2 month-1","g C m-2 month-1","g C m-2 month-1")
  tab20c = plt.cm.get_cmap('tab20c')

  fig = plt.figure(figsize=(15,7))

  # One axes for each input driver
  ax0 = plt.subplot2grid((2,2), (0, 0))
  ax1 = plt.subplot2grid((2,2), (1, 0))
  ax2 = plt.subplot2grid((2,2), (0, 1))
  ax3 = plt.subplot2grid((2,2), (1, 1))

  for driving_var, ax_inst in zip(fdf.columns, [ax0,ax1,ax2,ax3]):

    # Plot a different series (color) for each site/community
    for cmt, cmtlabel, color in zip([heath07, shrub04, tussk05], ("Koug. CMT07 (Heath)","Koug. CMT04 (Shrub)","Koug. CMT05 (Tussock)"), [tab20c.colors[0], tab20c.colors[4], tab20c.colors[8]]):
      ax_inst.scatter(fdf[driving_var], cmt.mean(axis=1), alpha=.55, color=color, label=cmtlabel)
      ax_inst.set_xlabel("{} {}".format(driving_var, hds.variables[driving_var].units))
      ax_inst.set_ylabel("{} {}".format(output_var, output_var_units))
      legnd = ax_inst.legend()
      #ax_inst.x

  plt.suptitle("{} vs driving variables".format(output_var))

  #plt.show(block=True)
  plt.savefig("frs_{}_vs_driver_vars.pdf".format(output_var))


# Read the ensemble output, assign datetime index

# make dataframe with index of nice datetime indicies and then a column for each output variable
# and a column for each input driver

# mkae plots

#################

# idx   NPP HR SoilC LAI tair precip vapo nirr


# ds = pd.read_hdf("../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/historic-climate.nc")
# hds = nc.Dataset("../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/historic-climate.nc")
# pds = nc.Dataset("../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/projected-climate.nc")
# hds.variables
# hds.dimensions
# hds.dimensions['time']
# hds.dimensions['time'].units
# hds.variables['tair']
# !ncdump -h ../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_Kougarok_1x1/historic-climate.nc
# hds.variables['time']
# hds.variables['time'].units
# nc.date2index?
# nc.date2num?
# hds.time
# hds.variables['time'].units
# hds.variables['time'].units.split()
# pd.DatetimeIndex(start='1901-1-1', freq='MS', periods=1308)
# hds.variables['time']
# nc.date2index?
# dt.datetime.date('1970-1-1')
# dt.datetime.strptime('1970-1-1', '%Y-%m-%d')
# nc.date2num?
# nc.date2index
# nc.date2index?
# nc.date2index(dt.datetime.strptime('1970-1-1', '%Y-%m-%d'), hds.variables['time'])
# pd.DatetimeIndex(start='1901-1-1', freq='MS', periods=hds.variables['time'].size)
# hds.variables['time'].units
# hds.variables['time'].units.strip()
# hds.variables['time'].units.strip().split(' ')
# hds.variables['time'].units.strip().split(' ')[2]
# historic_file_dates = pd.DatetimeIndex(start=hds.variables['time'].units.strip().split(' ')[2], freq='MS', periods=hds.variables['time'].size)
# historic_file_dates
# nc.date2index(historic_file_dates, hds.variables['time'])
# nc.datetime?
# nc.date2num?
# historic_file_dates[0]
# pd.to_datetime(historic_file_dates)
# nc.date2index(pd.to_datetime(historic_file_dates), hds.variables['time'])
# pd.to_datetime(historic_file_dates[0])
# historic_file_dates[0].date()
# historic_file_dates.apply(lambda x: x.date())
# pd.to_datetime(historic_file_dates[0]).date
# pd.to_datetime(historic_file_dates[0]).date()
# pd.to_datetime(historic_file_dates).date()
# pd.to_datetime(historic_file_dates[:]).date()
# nc.date2index([x.date() for x in historic_file_dates], hds.variables['time'])
# historic_file_dates[0]
# a = historic_file_dates[0]
# a
# a.date()
# a.datetime()
# pd.to_datetime(historic_file_dates)
# pd.__version__
# a.to_datetime()
# nc.date2index([x.to_datetime() for x in historic_file_dates], hds.variables['time'])
# history