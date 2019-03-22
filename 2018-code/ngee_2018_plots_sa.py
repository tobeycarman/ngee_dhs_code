#!/usr/bin/env python

# Tobey Carman, November 2018

# SENSITIVITY ANALYSIS PLOTS

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

##################################

# Read in data
heath07_NPP_sa_Decid   = pd.read_csv("PEcAn_2000001131/sensitivity.results.2000001179.NPP.1970.2029.Rdata.CMT07-Decid.csv")
heath07_NPP_sa_EGreen  = pd.read_csv("PEcAn_2000001131/sensitivity.results.2000001179.NPP.1970.2029.Rdata.CMT07-EGreen.csv")
heath07_NPP_sa_Moss    = pd.read_csv("PEcAn_2000001131/sensitivity.results.2000001179.NPP.1970.2029.Rdata.CMT07-Moss.csv")
heath07_NPP_sa_Lichens = pd.read_csv("PEcAn_2000001131/sensitivity.results.2000001179.NPP.1970.2029.Rdata.CMT07-Lichens.csv")

heath07_HeteroResp_sa_Decid   = pd.read_csv("PEcAn_2000001129/sensitivity.results.2000001176.HeteroResp.1970.2029.Rdata.CMT07-Decid.csv")
heath07_HeteroResp_sa_EGreen  = pd.read_csv("PEcAn_2000001129/sensitivity.results.2000001176.HeteroResp.1970.2029.Rdata.CMT07-EGreen.csv")
heath07_HeteroResp_sa_Moss    = pd.read_csv("PEcAn_2000001129/sensitivity.results.2000001176.HeteroResp.1970.2029.Rdata.CMT07-Moss.csv")
heath07_HeteroResp_sa_Lichens = pd.read_csv("PEcAn_2000001129/sensitivity.results.2000001176.HeteroResp.1970.2029.Rdata.CMT07-Lichens.csv")

heath07_LAI_sa_Decid    = pd.read_csv("PEcAn_2000001164/sensitivity.results.2000001220.LAI.1970.2029.Rdata.CMT07-Decid.csv")
heath07_LAI_sa_EGreen   = pd.read_csv("PEcAn_2000001164/sensitivity.results.2000001220.LAI.1970.2029.Rdata.CMT07-EGreen.csv")
heath07_LAI_sa_Moss     = pd.read_csv("PEcAn_2000001164/sensitivity.results.2000001220.LAI.1970.2029.Rdata.CMT07-Moss.csv")
heath07_LAI_sa_Lichens  = pd.read_csv("PEcAn_2000001164/sensitivity.results.2000001220.LAI.1970.2029.Rdata.CMT07-Lichens.csv")

heath07_SoilC_sa_Decid   = pd.read_csv("PEcAn_2000001157/sensitivity.results.2000001207.SoilOrgC.1970.2029.Rdata.CMT07-Decid.csv")
heath07_SoilC_sa_EGreen  = pd.read_csv("PEcAn_2000001157/sensitivity.results.2000001207.SoilOrgC.1970.2029.Rdata.CMT07-EGreen.csv")
heath07_SoilC_sa_Moss    = pd.read_csv("PEcAn_2000001157/sensitivity.results.2000001207.SoilOrgC.1970.2029.Rdata.CMT07-Moss.csv")
heath07_SoilC_sa_Lichens = pd.read_csv("PEcAn_2000001157/sensitivity.results.2000001207.SoilOrgC.1970.2029.Rdata.CMT07-Lichens.csv")

# Re-index off of a PFT that has all params/priors defined
# (mosses and lichens didn't have priors for fine root production)
heath07_NPP_sa_Moss = heath07_NPP_sa_Moss.reindex(heath07_NPP_sa_Decid.index)
heath07_NPP_sa_Lichens = heath07_NPP_sa_Lichens.reindex(heath07_NPP_sa_Decid.index)

heath07_HeteroResp_sa_Moss = heath07_HeteroResp_sa_Moss.reindex(heath07_HeteroResp_sa_Decid.index)
heath07_HeteroResp_sa_Lichens = heath07_HeteroResp_sa_Lichens.reindex(heath07_HeteroResp_sa_Decid.index)

heath07_LAI_sa_Moss = heath07_LAI_sa_Moss.reindex(heath07_LAI_sa_Decid.index)
heath07_LAI_sa_Lichens = heath07_LAI_sa_Lichens.reindex(heath07_LAI_sa_Decid.index)

heath07_SoilC_sa_Moss = heath07_SoilC_sa_Moss.reindex(heath07_SoilC_sa_Decid.index)
heath07_SoilC_sa_Lichens = heath07_SoilC_sa_Lichens.reindex(heath07_SoilC_sa_Decid.index)

# Now sort on the index so that all the fr_prods come out together
for df in (heath07_NPP_sa_EGreen, heath07_NPP_sa_Decid, heath07_NPP_sa_Lichens, heath07_NPP_sa_Moss):
  df.sort_index(inplace=True, ascending=False)

for df in (heath07_HeteroResp_sa_EGreen, heath07_HeteroResp_sa_Decid, heath07_HeteroResp_sa_Lichens, heath07_HeteroResp_sa_Moss):
  df.sort_index(inplace=True, ascending=False)

for df in (heath07_LAI_sa_Decid, heath07_LAI_sa_EGreen, heath07_LAI_sa_Moss, heath07_LAI_sa_Lichens):
  df.sort_index(inplace=True, ascending=False)

for df in (heath07_SoilC_sa_Decid, heath07_SoilC_sa_EGreen, heath07_SoilC_sa_Moss, heath07_SoilC_sa_Lichens):
  df.sort_index(inplace=True, ascending=False)

# ####################################

shrub04_NPP_sa_Decid   = pd.read_csv("PEcAn_2000001137/sensitivity.results.2000001183.NPP.1970.2029.Rdata.CMT04-Decid.csv")
shrub04_NPP_sa_Salix   = pd.read_csv("PEcAn_2000001137/sensitivity.results.2000001183.NPP.1970.2029.Rdata.CMT04-Salix.csv")
shrub04_NPP_sa_Betula  = pd.read_csv("PEcAn_2000001137/sensitivity.results.2000001183.NPP.1970.2029.Rdata.CMT04-Betula.csv")
shrub04_NPP_sa_Feather = pd.read_csv("PEcAn_2000001137/sensitivity.results.2000001183.NPP.1970.2029.Rdata.CMT04-Feather.csv")

shrub04_HeteroResp_sa_Decid   = pd.read_csv("PEcAn_2000001138/sensitivity.results.2000001185.HeteroResp.1970.2029.Rdata.CMT04-Decid.csv")
shrub04_HeteroResp_sa_Salix   = pd.read_csv("PEcAn_2000001138/sensitivity.results.2000001185.HeteroResp.1970.2029.Rdata.CMT04-Salix.csv")
shrub04_HeteroResp_sa_Betula  = pd.read_csv("PEcAn_2000001138/sensitivity.results.2000001185.HeteroResp.1970.2029.Rdata.CMT04-Betula.csv")
shrub04_HeteroResp_sa_Feather = pd.read_csv("PEcAn_2000001138/sensitivity.results.2000001185.HeteroResp.1970.2029.Rdata.CMT04-Feather.csv")

shrub04_SoilC_sa_Decid   = pd.read_csv("PEcAn_2000001166/sensitivity.results.2000001224.SoilOrgC.1970.2029.Rdata.CMT04-Decid.csv")
shrub04_SoilC_sa_Salix   = pd.read_csv("PEcAn_2000001166/sensitivity.results.2000001224.SoilOrgC.1970.2029.Rdata.CMT04-Salix.csv")
shrub04_SoilC_sa_Betula  = pd.read_csv("PEcAn_2000001166/sensitivity.results.2000001224.SoilOrgC.1970.2029.Rdata.CMT04-Betula.csv")
shrub04_SoilC_sa_Feather = pd.read_csv("PEcAn_2000001166/sensitivity.results.2000001224.SoilOrgC.1970.2029.Rdata.CMT04-Feather.csv")

shrub04_LAI_sa_Decid   = pd.read_csv("PEcAn_2000001165/sensitivity.results.2000001221.LAI.1970.2029.Rdata.CMT04-Decid.csv")
shrub04_LAI_sa_Salix   = pd.read_csv("PEcAn_2000001165/sensitivity.results.2000001221.LAI.1970.2029.Rdata.CMT04-Salix.csv")
shrub04_LAI_sa_Betula  = pd.read_csv("PEcAn_2000001165/sensitivity.results.2000001221.LAI.1970.2029.Rdata.CMT04-Betula.csv")
shrub04_LAI_sa_Feather = pd.read_csv("PEcAn_2000001165/sensitivity.results.2000001221.LAI.1970.2029.Rdata.CMT04-Feather.csv")

# Re-index off of a PFT that has all params/priors defined
# (feather didn't have priors for fine root production)
shrub04_NPP_sa_Feather = shrub04_NPP_sa_Feather.reindex(shrub04_NPP_sa_Betula.index)
shrub04_HeteroResp_sa_Feather = shrub04_HeteroResp_sa_Feather.reindex(shrub04_HeteroResp_sa_Betula.index)
shrub04_SoilC_sa_Feather = shrub04_SoilC_sa_Feather.reindex(shrub04_SoilC_sa_Betula.index)
shrub04_LAI_sa_Feather = shrub04_LAI_sa_Feather.reindex(shrub04_LAI_sa_Betula.index)

# Now sort on the index so that all the fr_prods come out together
for df in (shrub04_NPP_sa_Feather, shrub04_NPP_sa_Betula, shrub04_NPP_sa_Salix, shrub04_NPP_sa_Decid):
  df.sort_index(inplace=True, ascending=False)

for df in (shrub04_HeteroResp_sa_Feather, shrub04_HeteroResp_sa_Betula, shrub04_HeteroResp_sa_Salix, shrub04_HeteroResp_sa_Decid):
  df.sort_index(inplace=True, ascending=False)

for df in (shrub04_LAI_sa_Decid, shrub04_LAI_sa_Salix, shrub04_LAI_sa_Betula, shrub04_LAI_sa_Feather):
  df.sort_index(inplace=True, ascending=False)

for df in (shrub04_SoilC_sa_Decid, shrub04_SoilC_sa_Salix, shrub04_SoilC_sa_Betula, shrub04_SoilC_sa_Feather):
  df.sort_index(inplace=True, ascending=False)

# #####################################

tussk05_NPP_sa_Sphag   = pd.read_csv("PEcAn_2000001154/sensitivity.results.2000001203.NPP.1970.2029.Rdata.CMT05-Sphag.1.csv")
tussk05_NPP_sa_EGreen  = pd.read_csv("PEcAn_2000001154/sensitivity.results.2000001203.NPP.1970.2029.Rdata.CMT05-EGreen.1.csv")
tussk05_NPP_sa_Betula  = pd.read_csv("PEcAn_2000001154/sensitivity.results.2000001203.NPP.1970.2029.Rdata.CMT05-Betula.csv")
tussk05_NPP_sa_Sedges  = pd.read_csv("PEcAn_2000001154/sensitivity.results.2000001203.NPP.1970.2029.Rdata.CMT05-Sedges.csv")

tussk05_HeteroResp_sa_Sphag   = pd.read_csv("PEcAn_2000001132/sensitivity.results.2000001181.HeteroResp.1970.2029.Rdata.CMT05-Sphag.csv")
tussk05_HeteroResp_sa_EGreen  = pd.read_csv("PEcAn_2000001132/sensitivity.results.2000001181.HeteroResp.1970.2029.Rdata.CMT05-EGreen.csv")
tussk05_HeteroResp_sa_Betula  = pd.read_csv("PEcAn_2000001132/sensitivity.results.2000001181.HeteroResp.1970.2029.Rdata.CMT05-Betula.csv")
tussk05_HeteroResp_sa_Sedges  = pd.read_csv("PEcAn_2000001132/sensitivity.results.2000001181.HeteroResp.1970.2029.Rdata.CMT05-Sedges.csv")

tussk05_LAI_sa_Spahg = pd.read_csv("PEcAn_2000001168/sensitivity.results.2000001228.LAI.1970.2029.Rdata.CMT05-Sphag.1.csv")
tussk05_LAI_sa_EGreen = pd.read_csv("PEcAn_2000001168/sensitivity.results.2000001228.LAI.1970.2029.Rdata.CMT05-EGreen.1.csv")
tussk05_LAI_sa_Betula = pd.read_csv("PEcAn_2000001168/sensitivity.results.2000001228.LAI.1970.2029.Rdata.CMT05-Betula.csv")
tussk05_LAI_sa_Sedges = pd.read_csv("PEcAn_2000001168/sensitivity.results.2000001228.LAI.1970.2029.Rdata.CMT05-Sedges.csv")

tussk05_SoilC_sa_Sphag = pd.read_csv("PEcAn_2000001169/sensitivity.results.2000001230.SoilOrgC.1970.2029.Rdata.CMT05-Sphag.1.csv")
tussk05_SoilC_sa_EGreen = pd.read_csv("PEcAn_2000001169/sensitivity.results.2000001230.SoilOrgC.1970.2029.Rdata.CMT05-EGreen.1.csv")
tussk05_SoilC_sa_Betula = pd.read_csv("PEcAn_2000001169/sensitivity.results.2000001230.SoilOrgC.1970.2029.Rdata.CMT05-Betula.csv")
tussk05_SoilC_sa_Sedges = pd.read_csv("PEcAn_2000001169/sensitivity.results.2000001230.SoilOrgC.1970.2029.Rdata.CMT05-Sedges.csv")

# Re-index off of a PFT that has all params/priors defined
# (feather didn't have priors for fine root production)
tussk05_LAI_sa_Sphag = tussk05_LAI_sa_Spahg.reindex(tussk05_LAI_sa_Betula.index)
tussk05_SoilC_sa_Sphag = tussk05_SoilC_sa_Sphag.reindex(tussk05_SoilC_sa_Betula.index)

# Somehow on the first runs, one of the PFTs was missing a few 
# priors (labcon and fr_prod_perc_50?), so here we reindex them all
#tussk05_NPP_sa_Sphag = tussk05_NPP_sa_Sphag.reindex(tussk05_NPP_sa_Betula.index)
#tussk05_HeteroResp_sa_Sphag = tussk05_HeteroResp_sa_Sphag.reindex(tussk05_HeteroResp_sa_Betula.index)
tussk05_NPP_sa_Sphag  = tussk05_NPP_sa_Sphag.reindex(shrub04_NPP_sa_Betula.index)
tussk05_NPP_sa_EGreen = tussk05_NPP_sa_EGreen.reindex(shrub04_NPP_sa_Betula.index)
tussk05_NPP_sa_Betula = tussk05_NPP_sa_Betula.reindex(shrub04_NPP_sa_Betula.index)
tussk05_NPP_sa_Sedges = tussk05_NPP_sa_Sedges.reindex(shrub04_NPP_sa_Betula.index)

tussk05_HeteroResp_sa_Sphag  = tussk05_HeteroResp_sa_Sphag.reindex(shrub04_HeteroResp_sa_Betula.index)
tussk05_HeteroResp_sa_EGreen = tussk05_HeteroResp_sa_EGreen.reindex(shrub04_HeteroResp_sa_Betula.index)
tussk05_HeteroResp_sa_Betula = tussk05_HeteroResp_sa_Betula.reindex(shrub04_HeteroResp_sa_Betula.index)
tussk05_HeteroResp_sa_Sedges = tussk05_HeteroResp_sa_Sedges.reindex(shrub04_HeteroResp_sa_Betula.index)

# Now sort on the index so that all the fr_prods come out together
for df in (tussk05_NPP_sa_Sedges, tussk05_NPP_sa_Betula, tussk05_NPP_sa_EGreen, tussk05_NPP_sa_Sphag):
  df.sort_index(inplace=True, ascending=False)

for df in (tussk05_HeteroResp_sa_Sedges, tussk05_HeteroResp_sa_Betula, tussk05_HeteroResp_sa_EGreen, tussk05_HeteroResp_sa_Sphag):
  df.sort_index(inplace=True, ascending=False)

for df in (tussk05_LAI_sa_Spahg, tussk05_LAI_sa_EGreen, tussk05_LAI_sa_Betula, tussk05_LAI_sa_Sedges):
  df.sort_index(inplace=True, ascending=False)

for df in (tussk05_SoilC_sa_Sphag, tussk05_SoilC_sa_EGreen, tussk05_SoilC_sa_Betula, tussk05_SoilC_sa_Sedges):
  df.sort_index(inplace=True, ascending=False)


def make_fig(datadict={}):

  fig = plt.figure(figsize=(11,10))

  ax0 = plt.subplot2grid((1, 3), (0, 0))
  ax1 = plt.subplot2grid((1, 3), (0, 1))
  ax2 = plt.subplot2grid((1, 3), (0, 2))

  ax0.set_title("Parameter Uncertainty") # Coef. Variance (%)
  #   barh(y, width, height, left)
  ax0.barh(np.arange(.7,20,1), datadict['data'][0]['coef.vars'], align='edge', height=.2, color=datadict['color'], alpha=1.00, linewidth=0.5, hatch="", edgecolor=(1,1,1,1), label=datadict['labels'][0])
  ax0.barh(np.arange(.5,20,1), datadict['data'][1]['coef.vars'], align='edge', height=.2, color=datadict['color'], alpha=0.75, linewidth=0.5, hatch="", edgecolor=(1,1,1,1), label=datadict['labels'][1])
  ax0.barh(np.arange(.3,20,1), datadict['data'][2]['coef.vars'], align='edge', height=.2, color=datadict['color'], alpha=0.50, linewidth=0.5, hatch="", edgecolor=(1,1,1,1), label=datadict['labels'][2])
  ax0.barh(np.arange(.1,20,1), datadict['data'][3]['coef.vars'], align='edge', height=.2, color=datadict['color'], alpha=0.25, linewidth=0.5, hatch="", edgecolor=(1,1,1,1), label=datadict['labels'][3])

  ax1.set_title("Sensitivity") # Elasticity
  ax1.barh(np.arange(.7,20,1), datadict['data'][0].elasticities, align='edge', height=.2, color=datadict['color'], alpha=1.00, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][0])
  ax1.barh(np.arange(.5,20,1), datadict['data'][1].elasticities, align='edge', height=.2, color=datadict['color'], alpha=0.75, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][1])
  ax1.barh(np.arange(.3,20,1), datadict['data'][2].elasticities, align='edge', height=.2, color=datadict['color'], alpha=0.50, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][2])
  ax1.barh(np.arange(.1,20,1), datadict['data'][3].elasticities, align='edge', height=.2, color=datadict['color'], alpha=0.25, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][3])

  ax2.set_title("Output Uncertainty") # Partial Variance (%)
  ax2.barh(np.arange(.7,20,1), datadict['data'][0]['partial.variances'],  align='edge', height=.2, color=datadict['color'], alpha=1.00, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][0])
  ax2.barh(np.arange(.5,20,1), datadict['data'][1]['partial.variances'],  align='edge', height=.2, color=datadict['color'], alpha=0.75, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][1])
  ax2.barh(np.arange(.3,20,1), datadict['data'][2]['partial.variances'],  align='edge', height=.2, color=datadict['color'], alpha=0.50, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][2])
  ax2.barh(np.arange(.1,20,1), datadict['data'][3]['partial.variances'],  align='edge', height=.2, color=datadict['color'], alpha=0.25, linewidth=0.5, edgecolor=(1,1,1,1), label=datadict['labels'][3])

  # major y ticks - no labels, use grid for dividing params
  ax0.set_yticklabels([], minor=False)

  # minor y ticks - use for labeling parameters
  ax0.set_yticks(np.arange(.5, 20, 1), minor=True)
  ax0.set_yticklabels(datadict['data'][0].index, minor=True)

  for a in [ax0, ax1, ax2]:
    # handle major ticks
    a.set_yticklabels([])
    a.set_yticks(np.arange(1, 20, 1), minor=False)
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
  plt.suptitle("Variance Decomp. {}".format(datadict['savename']))

  # Shrink current axis's height by 10% on the bottom
  for ax in [ax0, ax1, ax2]:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

  # Put a legend below current axis
  ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            #fancybox=True, shadow=True, 
            ncol=1)

  plt.savefig("var_decom_{}.pdf".format(datadict['savename']), facecolor="white", transparent=True)
  #plt.show(block=True)
 
#tab10 = plt.cm.get_cmap('tab10')
tab20c = plt.cm.get_cmap('tab20c')

heath_labels = (
    "CMT07 (Heath): 51.46% total veg C Lichens",
    "CMT07 (Heath): 24.27% total veg C EGreen ",
    "CMT07 (Heath): 20.24% total veg C Decid ",
    "CMT07 (Heath):  2.08% total veg C Moss ",
)
heath07_NPP = {
  'data': (
     heath07_NPP_sa_Lichens,
     heath07_NPP_sa_EGreen, 
     heath07_NPP_sa_Decid, 
     heath07_NPP_sa_Moss, 
  ),
  'labels': heath_labels,
  'color': tab20c.colors[0],
  'savename': 'heath07_NPP',
}
heath07_HR = {
  'data': (
     heath07_HeteroResp_sa_Lichens,
     heath07_HeteroResp_sa_EGreen, 
     heath07_HeteroResp_sa_Decid, 
     heath07_HeteroResp_sa_Moss, 
  ),
  'labels':heath_labels,
  'color': tab20c.colors[0],
  'savename': 'heath07_HeteroResp',
}
heath07_LAI = {
  'data': (
     heath07_LAI_sa_Lichens,
     heath07_LAI_sa_EGreen, 
     heath07_LAI_sa_Decid, 
     heath07_LAI_sa_Moss, 
  ),
  'labels':heath_labels,
  'color': tab20c.colors[0],
  'savename': 'heath07_LAI',
}
heath07_SoilC = {
  'data': (
     heath07_SoilC_sa_Lichens,
     heath07_SoilC_sa_EGreen, 
     heath07_SoilC_sa_Decid, 
     heath07_SoilC_sa_Moss, 
  ),
  'labels':heath_labels,
  'color': tab20c.colors[0],
  'savename': 'heath07_SoilOrgC',
}
make_fig(heath07_NPP)
make_fig(heath07_HR)
make_fig(heath07_LAI)
make_fig(heath07_SoilC)

shrub_labels = (
    "CMT04 (Shrub): 57.91% total veg C Betula",
    "CMT04 (Shrub): 22.42% total veg C Salix",
    "CMT04 (Shrub):  8.91% total veg C Feather",
    "CMT04 (Shrub):  4.78% total veg C Decid ",
)
shrub04_NPP = {
  'data': (
     shrub04_NPP_sa_Betula, 
     shrub04_NPP_sa_Salix, 
     shrub04_NPP_sa_Feather,
     shrub04_NPP_sa_Decid, 
  ),
  'labels': shrub_labels,
  'color': tab20c.colors[4],
  'savename': 'shrub04_NPP',
}
shrub04_HR = {
  'data': (
     shrub04_HeteroResp_sa_Betula, 
     shrub04_HeteroResp_sa_Salix, 
     shrub04_HeteroResp_sa_Feather,
     shrub04_HeteroResp_sa_Decid, 
  ),
  'labels': shrub_labels,
  'color': tab20c.colors[4],
  'savename': 'shrub04_HeteroResp',
}
shrub04_LAI = {
  'data': (
     shrub04_LAI_sa_Betula, 
     shrub04_LAI_sa_Salix, 
     shrub04_LAI_sa_Feather,
     shrub04_LAI_sa_Decid, 
  ),
  'labels': shrub_labels,
  'color': tab20c.colors[4],
  'savename': 'shrub04_LAI',
}
shrub04_SoilC = {
  'data': (
     shrub04_SoilC_sa_Betula, 
     shrub04_SoilC_sa_Salix, 
     shrub04_SoilC_sa_Feather,
     shrub04_SoilC_sa_Decid, 
  ),
  'labels': shrub_labels,
  'color': tab20c.colors[4],
  'savename': 'shrub04_SoilOrgC',
}
make_fig(shrub04_NPP)
make_fig(shrub04_HR)
make_fig(shrub04_LAI)
make_fig(shrub04_SoilC)

tussk_labels = (
    "CMT05 (Tussock): 34.20% total veg C Sedges",
    "CMT05 (Tussock): 26.96% total veg C EGreen",
    "CMT05 (Tussock): 10.93% total veg C Spahg",
    "CMT05 (Tussock):  9.87% total veg C Betula",
)
tussk05_NPP = {
  'data': (
     tussk05_NPP_sa_Sedges,
     tussk05_NPP_sa_EGreen, 
     tussk05_NPP_sa_Sphag, 
     tussk05_NPP_sa_Betula, 
  ),
  'labels': tussk_labels,
  'color': tab20c.colors[8],
  'savename': 'tussk05_NPP',
}
tussk05_HR = {
  'data': (
     tussk05_HeteroResp_sa_Sedges,
     tussk05_HeteroResp_sa_EGreen, 
     tussk05_HeteroResp_sa_Sphag, 
     tussk05_HeteroResp_sa_Betula, 
  ),
  'labels': tussk_labels,
  'color': tab20c.colors[8],
  'savename': 'tussk05_HeteroResp',
}
tussk05_LAI = {
  'data': (
     tussk05_LAI_sa_Sedges,
     tussk05_LAI_sa_EGreen, 
     tussk05_LAI_sa_Sphag, 
     tussk05_LAI_sa_Betula, 
  ),
  'labels': tussk_labels,
  'color': tab20c.colors[8],
  'savename': 'tussk05_LAI',
}
tussk05_SoilC = {
  'data': (
     tussk05_SoilC_sa_Sedges,
     tussk05_SoilC_sa_EGreen, 
     tussk05_SoilC_sa_Sphag, 
     tussk05_SoilC_sa_Betula, 
  ),
  'labels': tussk_labels,
  'color': tab20c.colors[8],
  'savename': 'tussk05_SoilOrgC',
}
make_fig(tussk05_NPP)
make_fig(tussk05_HR)
make_fig(tussk05_LAI)
make_fig(tussk05_SoilC)
