import vitas
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


sns.reset_orig()

field='DBZ'
point='(38.1,-122.95)'
az='338'
dist='160'

runs=[]
runs.append(['', '-c', 'c03/leg01.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg02.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg03.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg05.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg08.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg09.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg12.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg13.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg14.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg16.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c03/leg20.cdf', '-s', '010123I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])

runs.append(['', '-c', 'c04/leg10.cdf', '-s', '010125I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c04/leg11.cdf', '-s', '010125I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])

runs.append(['', '-c', 'c05/leg23.cdf', '-s', '010209I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c05/leg32.cdf', '-s', '010209I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])

runs.append(['', '-c', 'c07/leg03.cdf', '-s', '010217I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c07/leg04.cdf', '-s', '010217I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c07/leg05.cdf', '-s', '010217I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])
runs.append(['', '-c', 'c07/leg06.cdf', '-s', '010217I.nc', '-f', field, '-sl', point, '-az', az, '-di',dist,'--multi'])

for n,r in enumerate(runs):
	sys.argv = r
	if n == 0:	
		a=vitas.main().data
	else:
		b=vitas.main().data
		a=np.dstack((a,b))
	print a.shape


amean=np.nanmean(a,axis=2)
asum=np.nansum(a,axis=2)
amax=np.nanmax(a,axis=2)

avar=np.nanvar(a,axis=2)
astd=np.nanstd(a,axis=2)
abool=a.copy()
abool[~np.isnan(abool)]=1
acount=np.nansum(abool,axis=2)

data=[	amean, avar, 
		asum, astd, 
		amax, acount]
dname=[ 	'mean', 'variance',
			'sum', 'stddev',
			'max','count']
dnaco=[ 	'k', 'k',
			'w', 'k',
			'k','w']

fig,ax=plt.subplots(3,2)
ax=np.reshape(ax, (6,1))
for n in range(6):
	axis=ax[n][0]
	im=axis.imshow(data[n],interpolation='none',origin='lower')
	div=make_axes_locatable(axis)
	cax=div.append_axes('right',size='5%',pad=0.05)
	plt.colorbar(im,cax=cax)
	axis.text(0.05,0.9,dname[n],color=dnaco[n],transform=axis.transAxes)
plt.show(block=False)

