#!/usr/bin/env python

# ppp.py
# pecan postprocessing and plot

import os
import glob
import itertools
import errno
import datetime
import socket           # for getting hostname
import argparse
import textwrap
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
  },
  'VegC': {
    'from_units': 'kg C m-2',
    'to_units': 'g C m-2',
  },
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


def provenance_annotate(axes_instance):
  '''Works from figure coords, so you can pass any axes that might be on a figure.'''

  # ADD GIT INFO TO BOTTOM LEFT CORNER
  #import subprocess
  #subprocess.call(['git describe --all --long'.split(' ')])
  # OR
  #export GIT_DESCRIBE_TAG=$(git describe --all --long); ./ppp.py ...
  annotation = axes_instance.annotate(
      'date: {} rev: {}'.format(datetime.datetime.now(), os.environ['GIT_DESCRIBE_TAG']),
      xy=(0.5, 0), 
      #xytext=(0, 10),
      xycoords='figure points', #('axes fraction', 'figure fraction'),
      #textcoords='offset points',
      color='gray',
      size=8, ha='left', va='bottom'
  )

  return annotation

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

  custom_order=['NPP','LAI','VegC','HeteroResp','SoilOrgC']

  var_list = sorted(var_list, key=lambda x: custom_order.index(x))
  return var_list, syr, eyr


def load_all_sensan(run_suite_directory): 
  '''
  Examples
  --------

  tt.loc[(slice('dhs_1','dhs_3'),slice(None),slice('HeteroResp','NPP'), 'Salix', 'ilai'), :]


  '''

  def get_site(fp):
    '''
    Pulls the site out as the second to last element in an underscore 
    separated directory name, e.g.:
        /Users/tobeycarman/Documents/SEL/NGEE_Dec_2018_followup/ngee_dhs_runs/kougorak_cmt04
    '''
    return '_'.join(os.path.basename(fp).split('_')[0:-1])

  def get_cmt(fp):
    '''
    Pulls the cmt out as the last element in an underscore separated directory
    name, e.g.:
        /Users/tobeycarman/Documents/SEL/NGEE_Dec_2018_followup/ngee_dhs_runs/kougorak_cmt04
    '''
    return os.path.basename(fp).split('_')[-1]

  #DF = pd.DataFrame({})
  DFS = []
  runs = run_suite_directory
  for run in runs:
    dfs = []
    available_variables, sy, ey = find_available_vars_years(run)
    for var in available_variables:
      df = load_sensitivity_analysis(run, var, sy, ey, multi_index=True)
      dfs.append(df)
    dfB = pd.concat(dfs, keys=available_variables, names=['output_variable'])
    DFS.append(dfB)

  print zip([os.path.basename(i) for i in runs],[get_site(i) for i in runs],[get_cmt(i) for i in runs])

  DF = pd.concat(DFS, keys=zip([os.path.basename(i) for i in runs],[get_site(i) for i in runs],[get_cmt(i) for i in runs]), names=['key', 'site', 'cmt'])
  print DF[0:2]
  new_index = pd.MultiIndex.droplevel(DF.index, level=0)
  print new_index.levels
  print new_index.names
  print ''

  DF.index = new_index
  print DF[0:2]
  print ''

  DF_S = DF.sort_index(sort_remaining=True)

  return DF_S




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

  if multi_index:
    return pd.concat(data_frames, keys=[p.split('-')[-1] for p in pfts], names=['pft','param'])

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

    _ = provenance_annotate(ax0)

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

    _ = provenance_annotate(ax0)

    #plt.show(block=True)
    wrtite_file(run_output_dir, "frs_{}_vs_{}.png".format(yax_var, xax_var))

def string_from_slicetuple(st):
  level_order = ('site,cmt,outvar,pft,param'.split(','))
  s = ''
  for i, lo in zip(st, level_order):
    print i, lo
    print ''
    if type(i) == slice:
      def f(x):
        if x is not None:
          return x
        else:
          return ''
      s += '{}({}-{})_'.format(lo, f(i.start), f(i.stop))
    elif type(i) == str:
      s += '{}({})_'.format(lo,i)
    else:
      raise RuntimeError("Invalid type in string_from_slicetuple")
  return s


def make_heatmap_variance_decomposition(run_suite_directory, slice_tuple, exclude=[]):
  '''
  Parameters
  ----------
  run_suite_directory: path to a directory with a collection (suite) of
      PEcAn:dvmdostem runs. 
  '''

  # pean runs, so each run is collection of dvmdostem runs (ensemble, SA, etc)

  print "Looking here for a set of pecan:dvmdostem runs: {}".format(run_suite_directory)
  print "Will exclude these directories if they exist: {}".format(exclude)
  print os.listdir(run_suite_directory)
  print ''


  run_directories = filter(lambda x: os.path.isdir(os.path.join(os.path.abspath(run_suite_directory), x)), os.listdir(run_suite_directory))
  print run_directories
  print ''

  run_directories = filter(lambda y: y not in exclude, run_directories)
  print run_directories
  print ''

  runs = map(lambda x: os.path.join(os.path.abspath(run_suite_directory), x), run_directories)
  print runs
  print''

  df = load_all_sensan(runs)
  # This gets us a multiindexed dataframe. The last level of the index is
  # the parameters (SLA, ilai, etc).
  #    In [698]: df.index.levels[0:-1]
  #    Out[698]: FrozenList([
  #        [u'dhs_1', u'dhs_2', u'dhs_3', u'dhs_4', u'dhs_5', u'kougorak', u'southbarrow'],
  #        [u'cmt04', u'cmt05', u'cmt06', u'cmt07'],
  #        [u'HeteroResp', u'LAI', u'NPP', u'SoilOrgC'],
  #        [u'Betula', u'Decid', u'EGreen', u'Feather', u'Grasses', u'Lichens', u'Moss', u'Salix', u'Sedges', u'Sphag']
  #     ])
  #    In [699]: tt.index.names
  #    Out[699]: FrozenList([u'site', u'cmt', u'output_variable', u'pft', u'param'])

  #
  #slice_tuple = (slice(None), slice(None), 'NPP', slice(None), slice(None))
  #slice_tuple = (slice(None), slice(None), 'NPP', 'Betula', slice(None))


  #slice_tuple = (slice('dhs_1'), slice(None), slice(None), slice(None), slice(None))
  print slice_tuple
  print "==================="

  # Unstacking the index basically puts the index on the columns instead of the
  # rows. Makes it easy to pass to imshow. We unstack all but the last level, 
  # which leaves the parameters on the Y axis (rows)
  cv = df.loc[slice_tuple, 'coef.vars'].sort_index(level='pft')
  cv_ = cv.unstack(level=(0,1,2,3))

  el = df.loc[slice_tuple, 'elasticities'].sort_index(level='pft')
  el_ = el.unstack(level=(0,1,2,3))

  pv = df.loc[slice_tuple, 'partial.variances'].sort_index(level='pft')
  pv_ = pv.unstack(level=(0,1,2,3))

  reduced_param_slice_list = ['SLA','SW_albedo','extinction_coefficient_diffuse','gcmax','klai','labncon']
  short_name_list = ['sla','sw_albedo','ex_coef_diff','gcmax','klai','labcon']
  short_name_dict = {}
  for ln, sn in zip(reduced_param_slice_list, short_name_list):
    short_name_dict[ln] = sn

  short_name_list = 'sla,sw_alb,cut_cond,ex_coef_dif,fprod10,fprod20,fprod30,fprod40,fprod50,gcmax,ilai,klai,labncon,ppfd50,ptmp_h,ptmp_l,ptmp_mx,ptmp_mn,vpd_close,vpd_open'.split(',')
  short_name_dict = {}
  for ln, sn in zip(el_.index, short_name_list):
    short_name_dict[ln] = sn

  #from IPython import embed; embed()

  # if len(reduced_param_slice_list) != len(short_name_list):
  #   rasie RuntimeError("Something is wrong with the reduced name and parameter list!")

  def colorbar(mappable):
    '''Makes the colorbar the same size as the axes.
    Poached from: https://joseph-long.com/writing/colorbars/ '''
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax)

  W = 10
  H = 10

  # Dynamic aspect ratio seems to help keep pixels kinda square
  if len(cv_.columns) <= len(cv_.index):
    W = H * len(cv_.columns) / len(cv_.index)

  # Problem with tight_layout w/o this bit
  if W < H/2:
    W = H/2

  plt.rcParams['font.family'] = 'sans-serif'

  fig = plt.figure(figsize=(W,H))

  ax0 = plt.subplot2grid((3,1), (0,0))
  ax1 = plt.subplot2grid((3,1), (1,0))
  ax2 = plt.subplot2grid((3,1), (2,0))

  ax0.set_title("Parameter Uncertainty (coef.variances)", fontsize=9) # Coef. Variance (%)
  ax1.set_title("Sensitivity (elasticities)", fontsize=9) # Elasticity
  ax2.set_title("Output Uncertainty (partial.variances)", fontsize=9) # Partial Variance (%)

  img0 = ax0.imshow(cv_, aspect='auto', interpolation='nearest', cmap='viridis_r')
  img1 = ax1.imshow(el_.loc[reduced_param_slice_list], aspect='auto', interpolation='nearest', cmap='seismic', norm=MidpointNormalize(midpoint=0, vmin=el_.min().min(), vmax=el_.max().max())) # diverging cmap
  img2 = ax2.imshow(pv_.loc[reduced_param_slice_list], aspect='auto', interpolation='nearest', cmap='plasma_r')

  # for ax, img in zip((ax0,ax1,ax2), (img0, img1,img2)):
  #   ax.vlines([4.5, 9.5, 14.5], -0.5, img.get_array().shape[0]-0.5, colors='black', linestyle='-', linewidth=.5)

  #diverging maps: Spectral, coolwarm, PiYG, RdYlGn seismic

  # Tick strategy:
  # - use major ticks for center of pixel (centering label text on pixels)
  # - use minor ticks for pixel edges, and grid lines

  # y axis, major ticks
  for ax in [ax0]:
    ax.set_yticks(np.arange(0, len(cv_.index)))
    ax.set_yticklabels([short_name_dict[i] for i in cv_.index], fontsize=8)
  
  for ax in (ax1,ax2):
    ax.set_yticks(np.arange(0, len(reduced_param_slice_list)))
    #ax.set_yticklabels(el_.loc[reduced_param_slice_list].index, fontsize=8)
    ax.set_yticklabels([short_name_dict[i] for i in el_.loc[reduced_param_slice_list].index], fontsize=8)

  # # x axis, major ticks
  # for ax in (ax0,ax1):
  #   ax.set_xticks(np.arange(0, len(cv_.columns)),[])
  #   ax.set_xticklabels([])

  for ax in [ax0, ax1, ax2]:
    ax.set_xticks(np.arange(0, len(cv_.columns)))
    lbls = ["-".join(x) for x in cv_.columns]
    lbls = [i.replace('Decid', '').replace('Betula', '').replace('dhs_', 'site').replace('-cmt04-',' ').replace('NPP-','').replace('HeteroResp','').replace('SoilOrgC','') for i in lbls]
    ax.set_xticklabels(lbls, rotation=90, fontsize=8)

  # x and y axis, minor ticks
  for ax, img in zip([ax0,ax1,ax2],[img0,img1,img2]):
    nrows, ncols = img.get_array().shape
    ax.set_xticks(np.arange(-.5, ncols, 1), minor=True);
    ax.set_yticks(np.arange(-.5, nrows, 1), minor=True);

  # grid
  for ax in (ax0, ax1, ax2):
    ax.grid(which='major', axis='both', color='gray', linewidth=0.15, visible=False)
    ax.grid(which='minor', color='w', linestyle='-', linewidth=3.0)

  # Turn off spines
  for ax in (ax0,ax1,ax2):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

  # Try getting rid of extra antialiasing border issue
  # for ax in (ax0,ax1,ax2):
  #   ax.autoscale(enable=True, axis='both',tight=False)

  _ = provenance_annotate(ax1)

  # Turn on the colorbars...
  colorbar(img0)
  colorbar(img1)
  colorbar(img2)

  # Needed to keep labels from overflowing figure bounds...
  plt.tight_layout()

  fname_addition = string_from_slicetuple(slice_tuple)
  wrtite_file(run_suite_directory, "vd_heatmap_{}.pdf".format(fname_addition))
  

def make_vardecomp_figure(run_output_dir):
  vl, sy, ey = find_available_vars_years(run_output_dir)
  
  for v in vl:
    # Need to put this in a loop over vl
    pfts, data_frames = load_sensitivity_analysis(run_output_dir, v, sy, ey)

    fig = plt.figure(figsize=(8.5,11))
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

    # (left, bottom, right, top) in the normalized figure coordinate that the
    # whole subplots area (including labels) will fit into.
    # Default is (0, 0, 1, 1).
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.suptitle("Variance Decomposition for {}\n{}".format(v, run_output_dir))

    # Shrink current axis's height by 10% on the bottom
    for ax in [ax0, ax1, ax2]:
      box = ax.get_position()
      ax.set_position([box.x0, box.y0 + box.height * 0.1,
                       box.width, box.height * 0.9])

    # Put a legend below current axis
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
              #fancybox=True, shadow=True, 
              ncol=1)

    _ = provenance_annotate(ax1)

    #plt.show(block=True)
    wrtite_file(run_output_dir, "variance_decomposition_{}.pdf".format(v))


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

  _ = provenance_annotate(axes[0])

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

  #from IPython import embed; embed()
  _ = provenance_annotate(axes[0])

  #plt.show(block=True)
  wrtite_file(run_output_dir, "timeseries.pdf")



def modex_smart_find_drivers(run_output_dir):
  from lxml import etree
  tree = etree.parse( os.path.join(run_output_dir, 'pecan.METProcess.xml') ) 
  p = os.path.dirname( tree.findall('run/inputs/met/path/path1')[0].text )
  return p


def do_it_all(directory):

  make_timeseries_figure(directory)
  make_box_plot_figure(directory)
  make_vardecomp_figure(directory)

  hostname = socket.gethostname()
  if 'modex' in hostname:
    driving_path = modex_smart_find_drivers(directory)
  else:
    print "You might be shit out of luck!"
    driving_path = "../dvmdostem-input-catalog/cru-ts40_ar5_rcp85_mri-cgcm3_dh_site_1_1x1/"

  make_frs_figure(directory, 'LAI', 'drivers', driving_data_path=driving_path)
  make_frs_figure(directory, 'HeteroResp', 'drivers', driving_data_path=driving_path)
  make_frs_figure(directory, 'NPP', 'drivers', driving_data_path=driving_path)
  make_frs_figure(directory, 'SoilOrgC', 'drivers', driving_data_path=driving_path)
  make_frs_figure(directory, 'VegC', 'drivers', driving_data_path=driving_path)

  make_frs_figure(directory, 'LAI', 'HeteroResp')
  make_frs_figure(directory, 'LAI', 'SoilOrgC')
  make_frs_figure(directory, 'LAI', 'NPP')
  make_frs_figure(directory, 'LAI', 'VegC')
  #make_frs_figure(directory, 'LAI', 'LAI')

  make_frs_figure(directory, 'HeteroResp', 'SoilOrgC')
  make_frs_figure(directory, 'HeteroResp', 'NPP')
  make_frs_figure(directory, 'HeteroResp', 'VegC')
  #make_frs_figure(directory, 'HeteroResp', 'LAI')
  #make_frs_figure(directory, 'HeteroResp', 'HeteroResp')

  make_frs_figure(directory, 'NPP', 'SoilOrgC')
  make_frs_figure(directory, 'NPP', 'VegC')
  #make_frs_figure(directory, 'NPP', 'HeteroResp')
  #make_frs_figure(directory, 'NPP', 'LAI')
  #make_frs_figure(directory, 'NPP', 'NPP')

  make_frs_figure(directory, 'SoilOrgC', 'VegC')
  #make_frs_figure(directory, 'SoilOrgC', 'NPP')
  #make_frs_figure(directory, 'SoilOrgC', 'LAI')
  #make_frs_figure(directory, 'SoilOrgC', 'HeteroResp')
  #make_frs_figure(directory, 'SoilOrgC', 'SoilOrgC')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
      Post processing and plotting for pecan runs.
    ''')
  )
  parser.add_argument('--run-directory', nargs=1,
      #type=argparse.FileType('r'),
      metavar=('DIRECTORY'), 
      help=textwrap.dedent('''Path to directory with PEcAn run in it.'''))

  parser.add_argument('--run-suite-directory', nargs=1,
      #type=argparse.FileType('r'),
      metavar=('DIRECTORY'), 
      help=textwrap.dedent('''Path to directory with a bunch of PEcAn runs in it.'''))

  args = parser.parse_args()

  #do_it_all(args.run_directory)

  # slice tuple in this order: 
  # [u'site', u'cmt', u'output_variable', u'pft', u'param'])
  #slice_tuple = (slice(None), slice(None), 'NPP', slice(None), slice(None))
  #slice_tuple = (slice(None), slice(None), 'NPP', 'Betula', slice(None))

  #slice_tuple = (slice('dhs_1', 'dhs_3'),slice(None),slice('LAI','VegC'),'Betula',slice(None))
  #make_heatmap_variance_decomposition(directory, slice_tuple, exclude=['yearly_runs', 'plots'])


  #for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  for outvar in 'VegC,LAI,SoilOrgC,HeteroResp,NPP'.split(','):
    for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
      slice_tuple = (site,slice(None),outvar,slice(None),slice(None))
      make_heatmap_variance_decomposition(directory, slice_tuple, exclude=['yearly_runs', 'plots'])

  # Each site (all cmts, all pfts) and all variables
  # for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  #   slice_tuple = (site, slice(None), slice(None), slice(None), slice(None))
  #   make_heatmap_variance_decomposition(directory, slice_tuple, exclude=['yearly_runs', 'plots'])

  # # Look at each community type next to all sites
  # for cmt in 'cmt04,cmt05,cmt06,cmt07'.split(','):
  #   slice_tuple = (slice(None), cmt, slice(None), slice(None), slice(None))
  #   make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # slice_tuple = (slice(None), 'cmt06', slice(None), slice(None), slice(None))
  # make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # betula decid feather salix
  # betual egreen sedges sphag
  # decid egreen lichen Moss
  # feather grass sedges spahg

  # # Look at each PFT
  # for pft in 'Betula Decid Feather Salix EGreen Sedges Sphag Moss Lichen Grasses'.split(' '):
  #   for v in 'NPP,LAI,SoilOrgC,HeteroResp'.split(','):
  #     slice_tuple = (slice(None), slice(None), v, pft, slice(None))
  #     make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  #   for v in 'NPP,LAI,SoilOrgC,HeteroResp'.split(','):
  #     slice_tuple = (site, slice(None), v, slice(None), slice(None))
  #     make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # [u'site', u'cmt', u'output_variable', u'pft', u'param'])
  # NOTE: to get only Betula and Decid, use slice(Betula, EGreen), - EGreen does not
  # exist in cmt04, so it works. Changed file names manually. 
  # Not sure why I can't get just a tuple to work for the slice??
  # for var in 'NPP,SoilOrgC,HeteroResp'.split(','):
  #   slice_tuple = ( slice('dhs_1', 'dhs_5'), 'cmt04', var, slice('Betula','EGreen'), slice(None))
  #   make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # # Each site (all cmts, all pfts) and NPP
  # for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  #   slice_tuple = (site, slice(None), 'NPP', slice(None), slice(None))
  #   make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # Each site (all cmts, all pfts) and SoilOrgC
  # for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  #   slice_tuple = (site, slice(None), 'SoilOrgC', slice(None), slice(None))
  #   make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])

  # # Each site (all cmts, all pfts) and HeteroResp
  # for site in 'dhs_1,dhs_2,dhs_3,dhs_4,dhs_5,kougorak,southbarrow'.split(','):
  #   slice_tuple = (site, slice(None), 'HeteroResp', slice(None), slice(None))
  #   make_heatmap_variance_decomposition(args.run_suite_directory[0], slice_tuple, exclude=['yearly_runs', 'plots'])




  print "****** DONE ******"

