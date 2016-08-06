# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 16:47:17 2016

@author: raul
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 17:25:58 2016

@author: raul
"""

import vitas
import matplotlib.pyplot as plt
import seaborn as sns
import Meteoframes as mf
import sounding as so
import numpy as np
from rv_utilities import linear_reg
from matplotlib import rcParams

rcParams['xtick.labelsize'] = 15
rcParams['ytick.labelsize'] = 15
rcParams['legend.fontsize'] = 15
rcParams['axes.labelsize'] = 15
rcParams['legend.handletextpad'] = 0.2
rcParams['mathtext.default'] = 'sf'

sns.set_style("whitegrid")

sound_dates={3:['2001-01-23 16:19',
                '2001-01-23 18:05',
                '2001-01-23 19:57',
                '2001-01-23 22:00',
                '2001-01-24 00:01',
                '2001-01-24 01:45',
                '2001-01-24 04:00'],
             7:['2001-02-17 12:34',
                '2001-02-17 13:52',
                '2001-02-17 14:50',
                '2001-02-17 15:47',
                '2001-02-17 16:59',
                '2001-02-17 18:06',
                '2001-02-17 18:58',
                '2001-02-17 19:43',
                '2001-02-17 20:50',
                '2001-02-17 21:51',
                '2001-02-17 22:58',]
                }

#par = ['-c c03/leg05.cdf -s 010123I.nc --prof (38.4,-123.3) --no_plot','3',3]
#par = ['-c c03/leg13.cdf -s 010123I.nc --prof (38.31,-123.04) --no_plot','3',4]
#par = ['-c c03/leg14.cdf -s 010123I.nc --prof (38.4,-123.1) --no_plot','3',4]
#par = ['-c c07/leg04.cdf -s 010217I.nc --prof (38.35,-123.08) --no_plot','7',5]
#par = ['-c c07/leg06.cdf -s 010217I.nc --prof (38.62,-123.4) --no_plot','7',6]


ncdf = ['-c c03/leg02.cdf',
        '-c c03/leg12.cdf',
        '-c c03/leg20.cdf',
        '-c c07/leg05.cdf']
        
flev = [' -s 010123I.nc',' -s 010217I.nc']

prof = [' --prof (38.32,-123.07)',
        ' --prof (38.32,-123.07)',
        ' --prof (38.23,-123.20)',
        ' --prof (38.32,-123.07)']

near = ' --nearest (4.5,12)'
#near = ''

' suitable comparisons '
params=list()
params.append([ncdf[0]+flev[0]+prof[0]+near+' --no_plot','3',3])
params.append([ncdf[1]+flev[0]+prof[1]+near+' --no_plot','3',4])
params.append([ncdf[2]+flev[0]+prof[2]+near+' --no_plot','3',5])
params.append([ncdf[3]+flev[1]+prof[3]+near+' --no_plot','7',5])

synth_time=list()
synth_time.append('2133-2137 UTC\n23Jan01')
synth_time.append('2354-2357 UTC\n23Jan01')
synth_time.append('0127-0136 UTC\n24Jan01')
synth_time.append('1756-1759 UTC\n17Feb01')                 

wprof_time=list()
wprof_time.append('2200 UTC\n23Jan01')
wprof_time.append('0001 UTC\n24Jan01')
wprof_time.append('0145 UTC\n24Jan01')
wprof_time.append('1806 UTC\n17Feb01')


p3ulist = list()
p3vlist = list()

bSulist = list()
bSvlist = list()

for n,par in enumerate(params):
    
    " synth data "
    out = vitas.main(par[0])
    p3u = out[0]
    p3v = out[1]
    p3wU = out[2] # from 230deg
    p3z = out[3]
    p3ulist.extend(p3u[:16])    
    p3vlist.extend(p3v[:16])    
    
    
    " balloon data " 
    infiles3,_ = so.get_sounding_files(par[1], homedir='/localdata')
    infiles3.sort()
    df = mf.parse_sounding2(infiles3[par[2]])
    bSu = df.u.values
    bSv = df.v.values
    bSz = df.index.values

    """ reduce resolution of bS by averaging 100-m layer
        centered at p3 altitude """
    bot = 25    
    top = 26
    for z in p3z[:16]:    
        center_idx = np.where(bSz==z*1000.)[0]
        if not center_idx:
            bSulist.append(np.nan)
            bSvlist.append(np.nan)
        else:
            c = center_idx[0]
            bSulist.append(bSu[c-bot:c+top].mean())    
            bSvlist.append(bSv[c-bot:c+top].mean())    

const = True
res_u = linear_reg(bSulist, p3ulist, const=const)
res_v = linear_reg(bSvlist, p3vlist, const=const)

out_u = res_u.params[0],res_u.params[1], res_u.rsquared, res_u.nobs
out_v = res_v.params[0],res_v.params[1], res_v.rsquared, res_v.nobs
inter_u, slope_u, rsquared_u, nobs_u = out_u
inter_v, slope_v, rsquared_v, nobs_v = out_v

stat = 'Slope:{:2.2f}\nIntercep:{:2.2f}\nR-sqr:{:2.2f}\nN:{:2.0f}'
stat_u = stat.format(slope_u, inter_u, rsquared_u, nobs_u)
stat_v = stat.format(slope_v, inter_v, rsquared_v, nobs_v)

x0u,y0u = np.arange(-15,16), np.arange(-15,16)
x0v,y0v = np.arange(0,41), np.arange(0,41)


fig,ax = plt.subplots(1,2,figsize=(12,5))


ax[0].scatter(bSulist,p3ulist,s=80,alpha=0.8)
ax[0].plot(x0u,y0u,color='k')
if const is True:
    ax[0].plot(x0u,inter_u+x0u*slope_u,'r--')
else:
    ax[0].plot(x0u,x0u*slope_u,'r--')
ax[0].set_xlabel(r'u-comp sounding $[ms^{-1}]$')
ax[0].set_ylabel(r'u-comp p3-synth $[ms^{-1}]$')
ax[0].set_xlim([-15,15])
ax[0].set_ylim([-15,15])
ax[0].text(0.05,0.95,stat_u,transform=ax[0].transAxes,
           va='top',size=15)

ax[1].scatter(bSvlist,p3vlist,s=80,alpha=0.8)
ax[1].plot(x0v, y0v,color='k')
if const is True:
    ax[1].plot(x0v,inter_v+x0v*slope_v,'r--')
else:
    ax[1].plot(x0v,x0v*slope_v,'r--')
ax[1].set_xlabel(r'v-comp sounding $[ms^{-1}]$')
ax[1].set_ylabel(r'v-comp p3-synth $[ms^{-1}]$')
ax[1].set_xlim([0,40])
ax[1].set_ylim([0,40])
ax[1].text(0.05,0.95,stat_v,transform=ax[1].transAxes,
           va='top',size=15)

plt.subplots_adjust(wspace=0.25)

#plt.show()
fname='/home/raul/Desktop/synth-wprof-scatter.png'
plt.savefig(fname, dpi=150, format='png',papertype='letter',
            bbox_inches='tight')


