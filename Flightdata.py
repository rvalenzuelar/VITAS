
'''
***************************************
	Class for plotting flight level
	data

	Raul Valenzuela
	August, 2015
*************************************** 
'''


import matplotlib.colors as colors
import matplotlib.cm as cmx
import Terrain

from Common import *
from itertools import product
from scipy.spatial import cKDTree

class FlightPlot(object):

	def __init__(self,**kwargs):

		self.met=None
		self.flightPath=None
		self.name=None
		self.time=None

		for key,value in kwargs.iteritems():
			if key == 'meteo':
				self.met=value
			elif key == 'flightPath':
				self.flightPath=value
			elif key == 'name':
				self.name=value
			elif key == 'time':
				self.time=value

	def plot_meteo(self,xaxis,dots):

		topo=Terrain.get_topo(lats=self.met['lats'], lons=self.met['lons'])

		varname={	0:{'var':'atemp','name': 'air temperature',
							'loc':3,'ylim':None,'fmt':False},
					1:{'var':'dewp','name': 'dew point temp',
							'loc':3,'ylim':None,'fmt':False},
					2:{'var':'wdir','name':'wind direction',
							'loc':(0.05,0.9),'ylim':None,'fmt':True},							
					3:{'var':'apres','name': 'air pressure',
							'loc':(0.05,0.9),'ylim':None,'fmt':False},						
					4:{'var':'relh','name':'relative humidity',
							'loc':(0.05,0.05),'ylim':[80,101],'fmt':True},							
					5:{'var':'wspd','name': 'wind speed',
							'loc':(0.05,0.9),'ylim':None,'fmt':True},
					6:{'var':'galt','name': 'geopotential alt',
							'loc':(0.05,0.9),'ylim':None,'fmt':True},
					7:{'var':'jwlwc','name':'liquid water content',
							'loc':(0.05,0.9),'ylim':None,'fmt':False},
					8:{'var':'wvert','name':'vertical velocity',
							'loc':(0.05,0.9),'ylim':[-2,4],'fmt':True},
					9:{'var':'palt','name': 'pressure alt',
							'loc':(0.05,0.9),'ylim':None,'fmt':True}}


		fig, ax = plt.subplots(3,3, sharex=True,figsize=(15,10))
		axs=ax.ravel()
		for i in varname.items():
			item	=	i[0]			
			var		=	i[1]['var']
			name	=	i[1]['name']
			loc		=	i[1]['loc']
			ylim	=	i[1]['ylim']
			ax		=	axs[item-1]
			if item < 2: # air temp and dew point in the same plot
				axs[0].plot(xaxis,self.met[var],label=name)
				if ylim: axs[0].set_ylim(ylim)
				if item == 1:
					axs[0].grid(True)
					axs[0].legend(loc=loc,frameon=False)
			else:
				ax.plot(xaxis,self.met[var],label=name)
				if item == 6: 
					ax2 = ax.twinx()
					ax2.plot(xaxis,topo,'r')
					ax2.set_ylabel('topography [m]', color='r')
					for tl in ax2.get_yticklabels():
						tl.set_color('r')
				if ylim: ax.set_ylim(ylim)
				ax.grid(True)
				ax.annotate(name, fontsize=16,
									xy=loc, 
									xycoords='axes fraction')
				if item == 8:
					ax.set_xlabel('Distance from beginning of flight [km]')

		new_xticks=[xaxis[i] for i in dots]
		adjust_xaxis(axs,new_xticks)
		adjust_yaxis(axs) # --> it's affecting formatter
		l1='Flight level meteorology for '+self.name
		l2='\nStart time: '+self.time[0].strftime('%Y-%m-%d %H:%M')+' UTC'
		l3='\nEnd time: '+self.time[1].strftime('%Y-%m-%d %H:%M')+' UTC'
		fig.suptitle(l1+l2+l3,y=0.98)
		fig.subplots_adjust(bottom=0.08,top=0.9,
							hspace=0,wspace=0.2)
		plt.draw


	def compare_with_synth(self,**kwargs):

		""" Method description
			----------------------------
			Comparison between the synthesis field and flight level
			data is achieved by:

			1) Find all the indexes of the synth grid where the flight trajectory intersects
			2) Filter out repeated indexes of the trajectory (LINE)
			3) Save geographic coordinates of the LINE
			4) In the synth grid, search the 9 nearest neighbors along each point of LINE
			5) Fill missing synth values by averaging the neighbors
			6) In the flight data, search 15 values nearest to each point of LINE 
			7) Average each set of 15 values of the flight array
		"""

		synth=kwargs['array']
		synth_lons=kwargs['x']
		synth_lats=kwargs['y']
		synth_z=kwargs['z']
		zlevel=kwargs['level']
		zoom=kwargs['zoom']

		idx = np.where(synth_z==zlevel)
		data = np.squeeze(synth[:,:,idx])

		flgt_lats,flgt_lons=zip(*self.flightPath)
		flight_wspd=self.met['wspd']
		flight_altitude=self.met['palt']

		flgt_lats = np.asarray(around(flgt_lats,4))
		flgt_lons = np.asarray(around(flgt_lons,4))
		synth_lats = np.asarray(around(synth_lats,4))
		synth_lons = np.asarray(around(synth_lons,4))

		idx_lat=[]
		idx_lon=[]
		for lat,lon in zip(flgt_lats,flgt_lons):
			idx_lat.append(find_index_recursively(array=synth_lats,value=lat,decimals=4))
			idx_lon.append(find_index_recursively(array=synth_lons,value=lon,decimals=4))

		""" filter out repeated indexes """
		indexes_filtered=[]
		first=True
		for val in zip(idx_lon,idx_lat):
			if first:
				val_foo=val
				indexes_filtered.append(val)
				first=False
			elif val!=val_foo:
				indexes_filtered.append(val)
				val_foo=val

		""" save geographic coordinates of the line """
		line_lat=[]
		line_lon=[]		
		for lon,lat in indexes_filtered:
			line_lon.append(synth_lons[lon])
			line_lat.append(synth_lats[lat])			
		linesynth=zip(line_lon,line_lat)

		""" search nearest neighbors """
		synth_coord=list(product(synth_lons,synth_lats))
		tree = cKDTree(synth_coord)
		neigh = 9
		dist, idx = tree.query(linesynth, k=neigh, eps=0, p=2, distance_upper_bound=0.1)

		""" convert to one-column array """
		grid_shape=data.shape
		data = data.reshape(grid_shape[0]*grid_shape[1],1)

		""" gets the center point """
		idx_split=zip(*idx)
		idx0 = list(idx_split[0])

		""" extract center point value """
		data_extract=data[idx0]

		""" average neighbors """
		data_extract2=[]
		for i in idx:
			data_extract2.append(np.nanmean(data[i]))

		""" save center points of line """
		line_center=[]
		line_neighbors=[]
		for i in idx:
			value=np.unravel_index(i[0], grid_shape)
			line_center.append(value)
			for j in i[1:]:
				value=np.unravel_index(j, grid_shape)
				line_neighbors.append(value)

		""" convert back to 2D array """
		data=data.reshape(121,131)
	

		""" swap coordinates to (lon,lat)"""
		flight_coord = [(t[1], t[0]) for t in self.flightPath]
		tree = cKDTree(flight_coord)
		neigh = 15
		dist, idx = tree.query(linesynth, k=neigh, eps=0, p=2, distance_upper_bound=0.1)

		""" average flight data """
		flgt_mean=[]
		flgt_altitude=[]
		for i in idx:
			flgt_mean.append(np.nanmean(flight_wspd[i]))
			flgt_altitude.append(np.nanmean(flight_altitude[i]))


		""" make plots """

		jet = plt.get_cmap('jet')
		cNorm = colors.Normalize(vmin=np.amin(data), vmax=np.amax(data))
		scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
		synth_alt=str(int(zlevel[0]*1000))
		flgt_alt=str(int(np.average(flgt_altitude)))
		antext1='Synthesis alt: '+synth_alt+' m MSL'
		antext2='Flight level alt: '+flgt_alt+' m MSL'
		title1='Horizontal wind speed\n'+self.name
		title2='Flight level and P3 synthesis comparison\n'+self.name


		''' grid '''
		plt.figure()
		im=plt.imshow(data.T,	interpolation='none',origin='lower')
		for p,val in zip(line_center,data_extract2):
			colorVal=scalarMap.to_rgba(val)
			plt.plot(p[0],p[1],color=colorVal,marker='s',markersize=6,linestyle='none')
		if zoom=='onshore':
			plt.xlim([30,100]), plt.ylim([30,110])
		elif zoom=='offshore':
			plt.xlim([20,90]), plt.ylim([10,90])
		plt.xlabel('X')
		plt.ylabel('Y')
		plt.colorbar(im)
		plt.annotate(antext1, xy=(0.1, 0.95), xycoords="axes fraction",fontsize=14)
		plt.suptitle(title1)
		plt.grid(which='major')
		plt.draw()

		''' timeseries '''
		fig, ax1 = plt.subplots()
		ln1=ax1.plot(data_extract,'bo',label='raw synthesis wind')
		ln2=ax1.plot(data_extract2,'rs',label='synthesis wind interpolated')
		ln3=ax1.plot(flgt_mean,'g',label='flight wind')
		ax1.set_ylabel('wind speed [m/s]')
		ax1.set_xlabel('Points along line')
		ax2=ax1.twinx()
		vmin=min(flgt_altitude)-50
		vmax=max(flgt_altitude)+50
		ln4=ax2.plot(flgt_altitude,'black',label='flight altitude')
		ax2.set_ylim([vmin,vmax])
		ax2.set_ylabel('Meters MSL')
		lns=ln1+ln2+ln3+ln4
		labs=[l.get_label() for l in lns]
		ax2.legend(lns,labs,numpoints=1,loc=4,prop={'size':10})
		ax2.annotate(antext1, xy=(0.5, 0.9), xycoords="axes fraction",fontsize=14)
		plt.grid(which='major')
		plt.suptitle(title2)
		plt.draw()


		''' scatter '''
		x_range=[0, 40]
		y_range=[0, 40]
		plt.figure()
		ax=plt.subplot(111)
		ax.scatter(data_extract2,flgt_mean)
		ax.plot(x_range, y_range, color='k', linestyle='-', linewidth=2)
		ax.annotate(antext2, xy=(0.08, 0.9), xycoords="axes fraction",fontsize=14)
		ax.annotate(antext1, xy=(0.08, 0.85), xycoords="axes fraction",fontsize=14)
		ax.set_aspect(1)
		ax.grid(which='major')
		ax.set_xlim(x_range)
		ax.set_ylim(y_range)
		plt.suptitle(title2)
		plt.xlabel('synthesis WSPD')
		plt.ylabel('flight WSPD')

		plt.draw()

def adjust_yaxis(axes):

	for i in range(9):
		newlabels=[]
		yticks=axes[i].get_yticks()

		""" make list of new ticklabels """
		for y in yticks:
			if i in [2,6]:
				newlabels.append(str(y))
			else:
				newlabels.append("{:.0f}".format(y))

		""" delete overlapping ticklabels """
		if i in [0,1,2]:
			newlabels[0]=''
			axes[i].set_yticklabels(newlabels)
		elif i in [3,4,5]:
			newlabels[0]=''
			newlabels[-1]=''
			axes[i].set_yticklabels(newlabels)
		elif i == 6:
			newlabels[-2]=''
			axes[i].set_yticklabels(newlabels)
		elif i in [7,8]:
			newlabels[-1]=''
			axes[i].set_yticklabels(newlabels)

def adjust_xaxis(axes,new_xticks):

	for i in [6,7,8]:
		xticks=axes[i].get_xticks()
		new_xticks = round_to_closest_int(new_xticks,10)
		axes[i].set_xticks(new_xticks)
