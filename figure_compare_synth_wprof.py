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

' suitable comparisons '
params=list()
params.append(['-c c03/leg02.cdf -s 010123I.nc --prof (38.31,-123.06) --no_plot','3',3])
params.append(['-c c03/leg12.cdf -s 010123I.nc --prof (38.32,-123.07) --no_plot','3',4])
params.append(['-c c03/leg20.cdf -s 010123I.nc --prof (38.23,-123.20) --no_plot','3',5])
params.append(['-c c07/leg05.cdf -s 010217I.nc --prof (38.35,-123.10) --no_plot','7',5])

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


fig,ax = plt.subplots(4,2,figsize=(7,11))

for n,par in enumerate(params):
    out = vitas.main(par[0])
    p3wspd = out[0][0]
    p3wdir = out[1][0]
    p3wU = out[2][0] # 50deg
    p3z = out[3]
    p3u = -p3wspd*np.sin(p3wdir*np.pi/180)
    p3v = -p3wspd*np.cos(p3wdir*np.pi/180)
    
    infiles3,_ = so.get_sounding_files(par[1], homedir='/localdata')
    infiles3.sort()
    df = mf.parse_sounding2(infiles3[par[2]])
    bSu = df.u.values
    bSv = df.v.values
    bSz = df.index.values
        
    l1 = ax[n,0].plot(p3u,p3z*1000,'.-')
    l2 = ax[n,0].plot(bSu,bSz,'--')
    ax[n,1].plot(p3v,p3z*1000,'.-')
    ax[n,1].plot(bSv,bSz,'--')
    
    ax[n,0].set_ylim([0,4000])
    ax[n,1].set_ylim([0,4000])
    ax[n,0].set_xlim([-20,20])
    ax[n,1].set_xlim([0,40])
    
    txt = 'P3-synth\n'+synth_time[n]+'\n\nWprof\n'+wprof_time[n]
    ax[n,1].text(40,1000,
                 txt,
                 ha='right')

    if n>0:
        ax[n,0].set_yticklabels([])
        ax[n,1].set_yticklabels([])
    else:
        ax[n,1].set_yticklabels([])
        ax[n,0].set_ylabel('Altitude MSL [m]')        
        
    if n<3:
        ax[n,0].set_xticklabels([])
        ax[n,1].set_xticklabels([])
    else:
        ax[n,0].set_xlabel('u-comp [ms-1]')
        ax[n,1].set_xlabel('v-comp [ms-1]')

    if n == 0:
        ax[n,0].legend(l1+l2,['P3-synth','Wprof'],
                        bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)


plt.subplots_adjust(hspace=0.05,wspace=0.05)
#plt.show()
fname='/home/raul/Desktop/p3-wprof-comparison.png'
plt.savefig(fname, dpi=150, format='png',papertype='letter',
            bbox_inches='tight')


