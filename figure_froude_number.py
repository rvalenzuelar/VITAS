# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 11:08:28 2016

@author: raul


Froude number analysis

"""


import vitas
#import matplotlib.pyplot as plt
import seaborn as sns
#import Meteoframes as mf
#import sounding as so
#import numpy as np
from matplotlib import rcParams
rcParams['xtick.labelsize'] = 15
rcParams['ytick.labelsize'] = 15
rcParams['legend.fontsize'] = 15
rcParams['axes.labelsize'] = 15
rcParams['legend.handletextpad'] = 0.2
rcParams['mathtext.default'] = 'sf'

sns.set_style("whitegrid")

params=list()
ncdf = '-c c07/leg04.cdf'
flev = ' -s 010217I.nc'
prof = ' --prof (38.6,-123.6)'
near = ' --nearest (4.5,12)'
#near = ' '
params.append([ncdf+flev+prof+near+' --no_plot','3',3])

out = vitas.main(params[0][0])

print out[1]




