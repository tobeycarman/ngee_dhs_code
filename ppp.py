#!/usr/bin/env python

# ppp.py
# pecan postprocessing and plot

import os
import glob
import errno
import datetime
import socket           # for getting hostname
import pandas as pd
import numpy as np
import cfunits
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable


config_dict = {
  'NPP': {
    'from_units': 'kg C m-2 s-1',
    'to_units': 'g C m-2 month-1',
  },
  'HeteroResp': {
    'from_units': 'kg C m-2 s-1',
    'to_units': 'g C m-2 month-1',
  },
  'LAI': {
    'from_units': 'm2/m2',
    'to_units': 'm2/m2',
  },
  'SoilOrgC': {
    'from_units': 'kg C m-2',
    'to_units': 'g C m-2',
  }
}

# set the colormap and centre the colorbar
class MidpointNormalize(colors.Normalize):
  """
  Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

  e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
  Poached from here: https://stackoverflow.com/questions/20144529/shifted-colorbar-matplotlib
  """
  def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
    self.midpoint = midpoint
    colors.Normalize.__init__(self, vmin, vmax, clip)

  def __call__(self, value, clip=None):
    # I'm ignoring masked values and all kinds of edge cases to make a
    # simple example...
    x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
    return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

def mname2idx(mname):
  '''Convert a textual month name (i.e. January) to numeric value (i.e. 1)'''
  return datetime.datetime.strptime('{} 1 1970'.format(mname), '%B %d %Y').month


def midx2mname(midx):
  '''Convert a numeric month value (i.e. 1) to a text month name (i.e. January)'''
  return datetime.date(year=1970, month=midx, day=1).strftime('%B')


def wrtite_file(directory, name):

  try:
    os.mkdir(os.path.join(directory, "plots"))
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise

  of = os.path.join(directory, "plots", name)
  if os.path.exists(of):
    print "Overwriting {}".format(of)
  plt.savefig(of)


def df_convert_index(dataFrame, start="1-1-1990"):

  var, ens_member = dataFrame.index[0].split(".")
  from_units = cfunits.Units(config_dict[var]['from_units'])
  to_units = cfunits.Units(config_dict[var]['to_units'])

  months, ens_members = dataFrame.shape

  dt_idx = pd.DatetimeIndex(start=start, periods=months, freq="MS")

  dataFrame = pd.DataFrame(cfunits.Units.conform(dataFrame.values, from_units, to_units), index=dt_idx)

  return dataFrame


def find_available_vars_years(run_output_dir):
  # Look in the run output directory for everything with ts and csv in the name
  files = sorted(glob.glob(os.path.join(run_output_dir, "*.ts.*.csv")))

  var_list = []
  syrs = []
  eyrs = []
  for f in files:
    # each f is somethign like this:
    # ensemble.ts.2000001299.NPP.1990.2015.Rdata.csv
    _, _, runid, var, syr, eyr, _, _ = os.path.basename(f).split('.')
    #print runid, var, syr, eyr
    var_list.append(var)
    syrs.append(syr)
    eyrs.append(eyr)

  # Check that everything is alright with respect to the avaibale years.
  syrs = set(syrs)
  eyrs = set(eyrs)
  if len(syrs) != 1 or len(eyrs) != 1:
    raise RuntimeError("There is a problem with the files in {}".format(run_output_dir))

  syr = syrs.pop()
  eyr = eyrs.pop()

  return var_list, syr, eyr



def load_sensitivity_analysis(path, var, year_start, year_end, multi_index=False):
  '''
  Looking for files like this, one file per variable, per pft:
  sensitivity.results.2000001397.HeteroResp.1990.2015.Rdata.CMT04-Betula.csv
  sensitivity.results.2000001397.HeteroResp.1990.2015.Rdata.CMT04-Decid.csv
  
  Parameters
  ----------
  path : string, path to directory of pecan:dvmdostem runs files (output, etc)
  var : string, the variable to look for
  year_start : int, the starting year expected to be in the file path
  year_end : int, the ending year expected to be in the file path
  multi_index : bool, return list of pfts and list of DatataFrames (False) or a 
      single multi-index DataFrame (True)
 

  Returns
  -------
  Returns a dataframe for each PFT for each variable
  '''
  g = os.path.join(path, "sensitivity.results.*.{}.{}.{}.Rdata.*.csv".format(var, year_start, year_end))
  fl = glob.glob(g)

  # fl should have one file for each pft.
  # Split on dots and take the 2nd to last item (last is the extension)
  pfts = [f.split(".")[-2] for f in fl]

  data_frames = []
  for f, pft in zip(fl, pfts):
    df = pd.read_csv(f)
    data_frames.append(df)

  # Find the DataFrame with the longest index (some PFTs don't have priors
  # for every variable).
  def find_suitable_index(data_frames):
    max_priors = np.max([len(df.index) for df in data_frames])
    for i, df in enumerate(data_frames):
      if len(df.index) == max_priors:
        return i

  # Reindex the dataframes
  i = find_suitable_index(data_frames)
  data_frames = [df.reindex(data_frames[i].index) for df in data_frames]

  # Sort so that all fr_prods come out together
  for df in data_frames:
    df.sort_index(inplace=True, ascending=False)

  return (pfts, data_frames)


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

def load_driving_data(driving_data_path, start='1990-01-01', end='2015-12-1'):

  # Open the historic netcdf file
  hds = nc.Dataset(os.path.join(driving_data_path, "historic-climate.nc"))
  pds = nc.Dataset(os.path.join(driving_data_path, "projected-climate.nc"))

  if (hds.variables['X'].size > 1) or (hds.variables['Y'].size > 1):
    print "WARNING! - This is a multi-pixel file. Careful which pixel you are working with!"
  if (pds.variables['X'].size > 1) or (pds.variables['Y'].size > 1):
    print "WARNING! - This is a multi-pixel file. Careful which pixel you are working with!"

  d = {}
  dp = {}

  for var in ['tair', 'precip','nirr','vapor_press']:
    # Extract the data from start to the end of the file
    d[var] = hds.variables[var][:,0,0]

    # extract data from start of file
    dp[var] = pds.variables[var][:,0,0]

  # Turn into dataframes
  hdf = pd.DataFrame(d)
  pdf = pd.DataFrame(dp)

  # build nice index
  hdates = nc.num2date(hds.variables['time'][:], hds.variables['time'].units, hds.variables['time'].calendar)
  hdates = [i.strftime() for i in hdates]
  hdates = pd.DatetimeIndex(hdates)

  pdates = nc.num2date(pds.variables['time'][:], pds.variables['time'].units, pds.variables['time'].calendar)
  pdates = [i.strftime() for i in pdates]
  pdates = pd.DatetimeIndex(pdates)

  hdf.index = hdates
  pdf.index = pdates

  # Get rid of overlapping data, prefering historic
  full_df = pd.concat([hdf,pdf])
  full_df[~full_df.index.duplicated(keep='first')] # Only necessary if the files overlap

  # Convert from strings to datetime objects
  start = datetime.datetime.strptime(start, '%Y-%m-%d')
  end = datetime.datetime.strptime(end, '%Y-%m-%d')
 
  var_unit_dict = {v:hds.variables[v].units for v in full_df.columns}

  return full_df[start:end], var_unit_dict


def make_frs_figure(run_output_dir, yax_var, xax_var, driving_data_path=None):
  ''' ??? '''
  var_list, syr, eyr = find_available_vars_years(run_output_dir)

  if yax_var != 'drivers' and yax_var not in var_list:
    raise RuntimeError("Variable '{}' not available in run output directory {}".format(yax_var, run_output_dir))
  if xax_var != 'drivers' and xax_var not in var_list:
    raise RuntimeError("Variable '{}' not available in run output directory {}".format(xax_var, run_output_dir))

  if xax_var == 'drivers':

    xax_data, var_unit_dict = load_driving_data(driving_data_path)
    yax_data = load_ensemble_ts(run_output_dir, yax_var, syr, eyr)

    yax_data = df_convert_index(yax_data)

    fig = plt.figure(figsize=(8.5,11))

    # One axes for each input driver
    ax0 = plt.subplot2grid((2,2), (0, 0))
    ax1 = plt.subplot2grid((2,2), (1, 0))
    ax2 = plt.subplot2grid((2,2), (0, 1))
    ax3 = plt.subplot2grid((2,2), (1, 1))

    for driving_var, ax_inst in zip(xax_data.columns, [ax0,ax1,ax2,ax3]):
      print "Driving variable: {}  full shape: {}  limited shape: {}".format(driving_var, xax_data.shape, xax_data[driving_var].shape)
      print "Yax var:{}  full shape:{}  mean shape:{}".format(yax_var, yax_data.shape, yax_data.mean(axis=1).shape)
      # Supposedly plot will be faster than scatter?
      ax_inst.plot(xax_data[driving_var], yax_data.mean(axis=1), marker='o', linewidth=0.0, alpha=0.25)
      ax_inst.set_xlabel("{} {}".format(driving_var, var_unit_dict[driving_var]))
      ax_inst.set_ylabel("{} {}".format(yax_var, config_dict[yax_var]['to_units']))

    plt.suptitle("{} vs driving variables\n{}\n{}".format(yax_var, driving_data_path, run_output_dir))

    #from IPython import embed; embed()
    #plt.show(block=True)
    wrtite_file(run_output_dir, "frs_driver_vs_{}.pdf".format(yax_var))

  else:

    yax_data = load_ensemble_ts(run_output_dir, yax_var, syr, eyr)
    xax_data = load_ensemble_ts(run_output_dir, xax_var, syr, eyr)

    yax_data = df_convert_index(yax_data)
    xax_data = df_convert_index(xax_data)

    fig = plt.figure(figsize=(15,7))

    ax0 = plt.subplot2grid((1,2), (0, 0))
    ax1 = plt.subplot2grid((1,2), (0, 1))

    print "yax var {} has {} timseries points for {} ensemble members for a total of {} points".format(yax_var, yax_data.shape[0], yax_data.shape[1], yax_data.size)
    print "xax var {} has {} timseries points for {} ensemble members for a total of {} points".format(xax_var, xax_data.shape[0], xax_data.shape[1], xax_data.size)


    ax0.set_title("All Ensemble Members ({}x{}={}points)".format(yax_data.shape[0], yax_data.shape[1], yax_data.size))
    p0 = ax0.plot(xax_data, yax_data, alpha=0.005, marker='o', linewidth=0.0, color='red')
    ax0.set_xlabel("{} {}".format(xax_var, config_dict[xax_var]['to_units']))
    ax0.set_ylabel("{} {}".format(yax_var, config_dict[yax_var]['to_units']))

    ax1.set_title("Ensemble Mean ({}x{}={}points)".format(yax_data.mean(axis=1).shape[0], 1, yax_data.mean(axis=1).size))
    p1 = ax1.scatter(xax_data.mean(axis=1), yax_data.mean(axis=1), alpha=0.25, marker='o', linewidth=0.0, color='blue')
    ax1.set_xlabel("{} {}".format(xax_var, config_dict[xax_var]['to_units']))
    ax1.set_ylabel("{} {}".format(yax_var, config_dict[yax_var]['to_units']))

    plt.suptitle("{} vs {}\n{}".format(yax_var, xax_var, run_output_dir))

    #plt.show(block=True)
    wrtite_file(run_output_dir, "frs_{}_vs_{}.png".format(yax_var, xax_var))
















def make_vardecomp_figure(run_output_dir):
  vl, sy, ey = find_available_vars_years(run_output_dir)
  
  # Need to put this in a loop over vl
  pfts, data_frames = load_sensitivity_analysis(run_output_dir, vl[0], sy, ey)

  fig = plt.figure(figsize=(15,7))
  ax0 = plt.subplot2grid((1, 3), (0, 0))
  ax1 = plt.subplot2grid((1, 3), (0, 1))
  ax2 = plt.subplot2grid((1, 3), (0, 2))

  ax0.set_title("Parameter Uncertainty") # Coef. Variance (%)
  ax1.set_title("Sensitivity") # Elasticity
  ax2.set_title("Output Uncertainty") # Partial Variance (%)
  
  for i, (pft, df) in enumerate(zip(pfts, data_frames)):
    yoffset = 0.9 - 0.80/len(pfts) - (i * 0.80/len(pfts)) # add from top to bottom, helps to match ledgend order.
    y_values = np.arange(yoffset, len(df.index), 1)
    height_values = np.ones(len(df.index)) * 0.80/len(pfts)
  
    #   barh(y, width, height, left)
    ax0.barh(y_values, df['coef.vars'],         height_values, align='edge', alpha=0.75, label=pft)
    ax1.barh(y_values, df['elasticities'],      height_values, align='edge', alpha=0.75, label=pft)
    ax2.barh(y_values, df['partial.variances'], height_values, align='edge', alpha=0.75, label=pft)


  # major y ticks - no labels, use grid for dividing params
  ax0.set_yticklabels([], minor=False)

  # minor y ticks - use for labeling parameters
  ax0.set_yticks(np.arange(.5, len(data_frames[0].index), 1), minor=True)
  ax0.set_yticklabels(data_frames[0].index, minor=True)

  for a in [ax0, ax1, ax2]:
    # handle major ticks
    a.set_yticklabels([])
    a.set_yticks(np.arange(1, len(data_frames[0].index), 1), minor=False)
    a.grid(which='major', axis='y', visible=True)

    a.xaxis.set_major_locator(MaxNLocator(3))   
    a.ticklabel_format(style='plain', axis='x')

    for x in a.get_xticklabels():
      pass
      #x.set_rotation(75)

  for a in [ax0, ax1]:
    #a.set_axis_bgcolor((1,1,1,0))
    a.set_facecolor((1,1,1,0))
    a.spines['left'].set_visible(False)
    a.spines['top'].set_visible(False)
    a.spines['right'].set_visible(False)

  #plt.tight_layout()
  plt.suptitle("Variance Decomp. {}".format('???'))

  # Shrink current axis's height by 10% on the bottom
  for ax in [ax0, ax1, ax2]:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

  # Put a legend below current axis
  ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            #fancybox=True, shadow=True, 
            ncol=1)

  plt.show(block=True)


def make_box_plot_figure(run_output_dir):
  '''Make a box plot figure with a subplot for each available variable'''
  var_list, syr, eyr = find_available_vars_years(run_output_dir)

  data_frames = [load_ensemble_ts(run_output_dir, v, syr, eyr) for v in var_list]
  data_frames = [df_convert_index(df) for df in data_frames]

  if len(data_frames) != len(var_list):
    raise RuntimeError("Hmmm, variable list is not equal to the number of loaded pandas DataFrames!")

  fig = plt.figure(figsize=(8.5,11))
  axes = [plt.subplot2grid( (len(var_list), 1), (i,0) ) for i, x in enumerate(var_list)]

  for ax, var, df in zip(axes, var_list, data_frames):
    d = {i:np.array(df[df.index.month==i]).ravel() for i in range(1,13)}
    dd = pd.DataFrame(d)
    dd.columns = [midx2mname(i) for i in dd.columns]
    ax.boxplot(
      dd.transpose(),
      sym='',
      notch=False,
      whis=[2.5, 97.5],
      patch_artist=True,
      boxprops=dict(linestyle='-', linewidth=1.0, alpha=0.75),
      medianprops=dict(),
    )
    ax.set_title(var)
    ax.set_ylabel(config_dict[var]['to_units'])

  for i, ax in enumerate(axes):
    ax.set_xlabel('')
    ax.set_xticklabels([])
    if i == len(axes)-1:
      ax.set_xlabel("Month")
      ax.set_xticklabels(dd.columns)
      #ax.set_xticklabels("Jan,Feb,Mar,Apr,Mar,Jun,Jul,Aug,Sep,Oct,Nov,Dec".split(','))

  #plt.tight_layout()
  #plt.show(block=True)
  plt.suptitle("Boxplot for {}".format(run_output_dir))
  wrtite_file(run_output_dir, "boxplot.pdf")



def make_timeseries_figure(run_output_dir):
  '''Make timeseries figure with a subplot for each available variable.'''

  var_list, syr, eyr = find_available_vars_years(run_output_dir)

  data_frames = [load_ensemble_ts(run_output_dir, v, syr, eyr) for v in var_list]
  data_frames = [df_convert_index(df) for df in data_frames]

  if len(data_frames) != len(var_list):
    raise RuntimeError("Hmmm, variable list is not equal to the number of loaded pandas DataFrames!")

  fig = plt.figure(figsize=(8.5,11))
  axes = [plt.subplot2grid( (len(var_list), 1), (i,0) ) for i, x in enumerate(var_list)]

  for ax, var, df in zip(axes, var_list, data_frames):
    ax.plot(df.index, df.quantile(0.025, 1), linewidth=0, color='black', alpha=0.5, linestyle=":")
    ax.plot(df.index, df.quantile(0.975, 1), linewidth=0, color='black', alpha=0.5, linestyle=":")
    ax.plot(df.index, df.median(1), linewidth=1.0, label='median', alpha=1.0)
    ax.fill_between(df.index.to_pydatetime(), df.quantile(.025, 1), df[0:].quantile(.975, 1), color='gray', alpha=0.35)
    ax.set_title(var)
    ax.set_ylabel(config_dict[var]['to_units'])

  for i, ax in enumerate(axes):
    if i == len(axes)-1:
      ax.set_xlabel("Time")
    else:
      ax.set_xticklabels([])    

  plt.suptitle("Timeseries with shaded 95% CI\n{}".format(run_output_dir))

  #plt.show(block=True)
  wrtite_file(run_output_dir, "timeseries.pdf")



def modex_smart_find_drivers(run_output_dir):
  from lxml import etree
  tree = etree.parse( os.path.join(run_output_dir, 'pecan.METProcess.xml') ) 
  p = os.path.dirname( tree.findall('run/inputs/met/path/path1')[0].text )
  return p
  plt.show(block=True)




#make_timeseries_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/")
#make_box_plot_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/")
#make_vardecomp_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04/")
#make_frs_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04", 'LAI', 'HeteroResp')
#make_frs_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04", 'LAI', 'SoilOrgC',)
make_frs_figure("../NGEE_Dec_2018_followup/yearly_runs/dhs_1_cmt04", 'LAI', 'drivers', driving_data_path="../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_dh_site_1_1x1/")





