import vitas
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import Polygon

sns.reset_orig()

def main(plot=True):

	if plot:
		field='DBZ'
		origin='(38.1,-123.9)'
		az='50'
		dist='160'

		synthinfo, legcomp = get_composite(field,origin,az,dist)

		stats = get_stats(legcomp)

		# map_section(synthinfo)
		# plot_using(stats,'dbz', synthinfo)
		# plot_using(stats,'along', synthinfo)
		plot_using(stats,'orthog', synthinfo)


		return stats,synthinfo

def map_section(synth):

		import basemap_shaded as bmap
		from custom_cmap import make_cmap
	
		warm = make_cmap(colors='warm_humid')	
		loc2={'BBY':(38.32,-123.07), 'CZD':(38.61,-123.22), 'FRS':(38.51,-123.25)}
		linesec=synth.slice
		fmt='({:1.2f},{:1.2f})'
		origin=fmt.format(linesec[0][0],linesec[0][1])
		end=fmt.format(linesec[1][0],linesec[1][1])
		az=str(synth.azimuth)
		dist=str(synth.distance)

		fig,ax=plt.subplots(figsize=(9,8))
		bmap.plot_geomap(ax=ax,shaded=False,domain=0,cmap=warm, locations=loc2,
								colorbar=True,linesec=linesec)
		plt.suptitle('Origin:'+origin+' End: '+end+ ' Az:'+az+'deg Dist:'+dist+'km')
		plt.tight_layout()
		plt.subplots_adjust(left=0.06)
		plt.show(block=False)

def plot_using(stats, field, synthinfo):

	data=stats[field]
	tcolor=['r', 'r','r', 'r','r','r']
	if field == 'dbz':
		vmin=[15, 10,50, 5,25, 0]
		vmax=[30, 90,500, 9,45, 19]
	elif field == 'along':
		vmin=[5, 40, 0, 5, 15, 0]
		vmax=[25, 120,10, 10, 30, 19]
	elif field == 'orthog':
		# vmin=[-18,10, -120,     2, -10, 0]
		# vmax=[0,   80,       0,  16,  10, 19]
		vmin=[5,	10, 0,     2,  15, 0]
		vmax=[10,   80, 10,  16,  25, 19]

	c1=plt.cm.BuPu(0)
	c2=plt.cm.BuPu(128)
	c3=plt.cm.BuPu(255)
	custom_cmap=custom_div_cmap(ncolors=11,mincol=c1,midcol=c2,maxcol=c3)
	
	cmaps={ 'dbz':['viridis','jet','viridis','jet','viridis',custom_cmap],
			   'along':['viridis','jet','viridis','jet','viridis',custom_cmap], 
			   # 'orthog':['viridis_r','jet','viridis_r','jet','viridis',custom_cmap]
			   'orthog':['viridis','jet','viridis','jet','viridis',custom_cmap]
			   }
	zaxis=synthinfo.axesval['z']
	origin=str(synthinfo.slice[0])
	az=str(synthinfo.azimuth)
	dist=str(synthinfo.distance)

	fig,ax=plt.subplots(3,2,figsize=(14,8))
	ax=np.reshape(ax, (6,1))
	for n in range(6):
		axis=ax[n][0]
		im=axis.imshow(data['value'][n],interpolation='none',origin='lower',
							extent=[0, float(dist), zaxis.min(), zaxis.max()],
							aspect='auto',cmap=cmaps[field][n],vmin=vmin[n],vmax=vmax[n])
		
		
		div=make_axes_locatable(axis)
		cax=div.append_axes('right',size='5%',pad=0.05)
		plt.colorbar(im,cax=cax)
		add_terrain_profile(ax=axis, synth=synthinfo)
		axis.text(0.01,0.9,data['name'][n],color=tcolor[n],transform=axis.transAxes)
		plt.suptitle('Field:'+field.upper()+' Origin:'+origin+ ' Az:'+az+'deg Dist:'+dist+'km')
		axis.set_ylim([0,7.5])
	plt.tight_layout()
	plt.subplots_adjust(top=0.92)
	plt.show(block=False)	

def add_terrain_profile(ax=None, synth=None):

	elevprof=synth.terrain.array['profile']

	''' to kilometers '''
	elevprof=elevprof/1000.0
	
	dist = np.linspace(0,synth.distance, len(elevprof))
	verts=zip(dist,elevprof)+[(synth.distance,0.)]

	fc=synth.terrainProfileFacecolor
	ec=synth.terrainProfileEdgecolor
	''' large zorder so keep terrain polygon on top '''
	poly=Polygon(verts,facecolor=fc,edgecolor=ec, zorder= 10000000)
	ax.add_patch(poly)

def get_stats(legcomp):

	' compute 2D statistics over time axis '

	dbz=legcomp[0]
	along=legcomp[1]
	orthog=legcomp[2]

	data={'dbz':dbz, 'along':along, 'orthog':orthog}
	stats={}
	stats['dbz']={}
	stats['along']={}
	stats['orthog']={}
	for key,value in data.iteritems():
		vmean=np.nanmean(value,axis=2)
		vmax=np.nanmax(value,axis=2)
		vmin=np.nanmin(value,axis=2)
		vvar=np.nanvar(value,axis=2)
		vstd=np.nanstd(value,axis=2)
		vbool=value.copy()
		vbool[~np.isnan(vbool)]=1
		vcount=np.nansum(vbool,axis=2)	
		vsum=np.nansum(value,axis=2)
		vsum[vcount==0.]=np.nan
		if key in ['along','orthog']:
			stats[key]['value']= [ vmean, vvar, vmin, vstd, vmax, vcount]
			stats[key]['name']=[ 'mean', 'variance','min', 'stddev','max','count']
		else:
			stats[key]['value']= [ vmean, vvar, vsum, vstd, vmax, vcount]
			stats[key]['name']=[ 'mean', 'variance','sum', 'stddev','max','count']
	return stats

def get_composite(field,origin,az,dist):

	runs=[]
	runs.append(['', '-c', 'c03/leg01.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg02.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg03.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg05.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg08.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg09.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg12.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg13.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg14.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg16.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c03/leg20.cdf', '-s', '010123I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])

	runs.append(['', '-c', 'c04/leg10.cdf', '-s', '010125I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c04/leg11.cdf', '-s', '010125I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])

	runs.append(['', '-c', 'c05/leg23.cdf', '-s', '010209I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c05/leg32.cdf', '-s', '010209I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])

	runs.append(['', '-c', 'c07/leg03.cdf', '-s', '010217I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c07/leg04.cdf', '-s', '010217I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c07/leg05.cdf', '-s', '010217I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])
	runs.append(['', '-c', 'c07/leg06.cdf', '-s', '010217I.nc', '-f', field, '-sl', origin, '-az', az, '-di',dist,'--multi'])

	for n,r in enumerate(runs):
		sys.argv = r
		if n == 0:	
			synthinfo,sec =vitas.main()
			dbz=sec[0].data
			along=sec[1][0].data
			orthog=sec[1][1].data
		else:
			_,sec=vitas.main()
			dbz=np.dstack((dbz,sec[0].data))
			along=np.dstack((along,sec[1][0].data))
			orthog=np.dstack((orthog,sec[1][1].data))
		
	return synthinfo, [dbz,along,orthog]

def custom_div_cmap(ncolors=11, name='custom_div_cmap',
                    mincol='blue', midcol='white', maxcol='red'):
    
    """ 
    Create a custom diverging colormap with three colors
    
    Default is blue to white to red with 11 colors.  Colors can be specified
    in any way understandable by matplotlib.colors.ColorConverter.to_rgb()
    source: http://pyhogs.github.io/colormap-examples.html
    """

    from matplotlib.colors import LinearSegmentedColormap 
    
    cmap = LinearSegmentedColormap.from_list(name=name, 
                                             colors =[mincol, midcol, maxcol],
                                             N=ncolors)
    return cmap

stats,synthinfo=main()