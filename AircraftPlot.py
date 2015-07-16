# Module for dual-Doppler plotting of NOAA P-3 tail radar.
#
#
# Raul Valenzuela
# June, 2015
#

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.patches import Polygon
from itertools import product
from scipy.spatial import cKDTree

import Terrain 
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np
import sys


class SynthPlot(object):

	def __init__(self):

		self.axesval={'x':None,'y':None,'z':None}
		self.cmapName=None
		self.cmapRange=None
		self.coast={'lon':None, 'lat':None}
		self.coastColor=None
		self.coastWidth=None
		self.extent={'lx':None,'rx':None,'by':None,'ty':None}
		self.figure_size=None
		self.flight={'lon':None, 'lat':None}
		self.flightColor=None
		self.flightWidth=None
		self.flightStyle=None
		self.flightPointColor=None
		self.flightPointSize=None
		self.geo_textsize=None
		self.gridmajorOn=False
		self.gridminorOn=False
		self.horizontal={'xminor':None,'xmajor':None,'yminor':None,'ymajor':None}
		self.lats=None 
		self.lons=None
		self.panel=None
		self.rows_cols=(None,None)
		self.scale=None
		self.slice_type=None
		self.slicen=None
		self.sliceo=None
		self.terrain=None
		self.terrainContours=None
		self.terrainContourColors=None
		self.u_array=[]
		self.v_array=[]
		self.var=None
		self.w_array=[]
		self.wind=None
		self.wind_jump=None
		self.windb_size=None
		self.windv_scale=None
		self.windv_width=None
		self.zlevel_textsize=None
		self.zlevels=[]
		self.zoomCenter=None
		self.zoomDelta=None
		self.zoomOpt=None

	def config(self,config):

		self.zoomCenter=config['zoom_center']
		self.zoomDelta=config['zoom_del']
		self.coastColor=config['coast_line_color']
		self.coastWidth=config['coast_line_width']
		self.flightColor=config['flight_line_color']
		self.flightWidth=config['flight_line_width']
		self.flightStyle=config['flight_line_style']				
		self.flightPointColor=config['flight_point_color']
		self.flightPointSize=config['flight_point_size']
		self.terrainContours=config['terrain_contours']
		self.terrainContourColors=config['terrain_contours_color']
		self.cmapName=config['synthesis_field_cmap_name']
		self.cmapRange=config['synthesis_field_cmap_range']
		self.wind_jump=config['wind_vector_jump']
		self.figure_size=config['figure_size']
		self.gridmajorOn=config['synthesis_gridsmajor_on']
		self.gridminorOn=config['synthesis_gridsminor_on']		

	def set_geographic_extent(self,synth):

		self.lats=synth.LAT
		self.extent['by']=min(synth.LAT)
		self.extent['ty']=max(synth.LAT)

		self.lons=synth.LON 
		self.extent['lx']=min(synth.LON)
		self.extent['rx']=max(synth.LON)

	def set_coastline(self):

		M = Basemap(		projection='cyl',
							llcrnrlat=self.extent['by'],
							urcrnrlat=self.extent['ty'],
							llcrnrlon=self.extent['lx'],
							urcrnrlon=self.extent['rx'],
							resolution='i')
		coastline = M.coastpolygons

		self.coast['lon']= coastline[1][0][13:-1]
		self.coast['lat']= coastline[1][1][13:-1]
	
	def set_flight_path(self,stdtape):

		fp = zip(*stdtape)
		self.flight['lat']=fp[0]
		self.flight['lon']=fp[1]

	def set_panel(self,option):

		"""
		set some plotting values and stores
		vertical level in a list of arrays
		"""
		if option == 'single':			
			self.rows_cols=(1,1)
			self.windb_size=6.5
			self.zlevel_textsize=16
			self.windv_scale=0.5
			self.windv_width=2

		elif option == 'multi':
			self.rows_cols=(3,2)
			self.windb_size=5
			self.wind_jump['x']=self.wind_jump['x']+3
			self.wind_jump['y']=self.wind_jump['y']+3
			self.zlevel_textsize=12
			self.windv_scale=0.5
			self.windv_width=2

		elif option == 'vertical':
			if self.var == 'SPH':
				cols=2
			else:
				cols=1
			if self.sliceo=='meridional':
				rows=len(self.slicem)
			elif self.sliceo=='zonal':
				rows=len(self.slicez)
			self.rows_cols=(rows,cols)
			self.windb_size=5
			self.geo_textsize=12
			self.windv_scale=0.5
			self.windv_width=2

	def get_slices(self,array):

		if self.slice_type == 'horizontal':
			slice_group  = chop_horizontal(self,array)
			return slice_group

		elif self.slice_type == 'vertical':
			slice_group = chop_vertical(self,array)
			return slice_group

	def get_extent(self):

		''' return a list with extent '''
		extent=[	self.extent['lx'],
					self.extent['rx'],
					self.extent['by'],
					self.extent['ty']]		

		return extent

	def get_var_title(self,var):
		var_title={	'DBZ': 'Reflectivity factor [dBZ]',
					'SPD': 'Total wind speed [m/s]',
					'SPH': 'Horizontal wind speed [m/s]',
					'VOR': 'Vorticity',
					'CON': 'Convergence',
					'U': 'wind u-component [m/s]',
					'V': 'wind v-component [m/s]',
					'WVA': 'wind w-component [m/s] (variational)',
					'WUP': 'wind w-component [m/s] (integration)'}
		title=var_title[var]
		
		if self.slice_type == 'vertical' and self.sliceo == 'zonal':
			title = title.replace("Horizontal ","Zonal ")
		elif self.slice_type == 'vertical' and self.sliceo  == 'meridional':
			title = title.replace('Horizontal','Meridional')

		return title

	def adjust_ticklabels(self,g):
		
				
		# newval=[]
		# for val in list(self.horizontal['yticks']):
		# 	newval.append(val*self.scale)
		# g.set_xticks(newval)
		# new_xticklabel = [str(np.around(val/self.scale,1)) for val in newval]
		# g.set_xticklabels(new_xticklabel)

		new_xticklabel = [str(np.around(val/self.scale,1)) for val in g.get_xticks()]
		g.set_xticklabels(new_xticklabel)

		# g.set_xticks([38.2,38.3,38.4,38.5])
		# new_xticklabel = [str(np.around(val/self.scale,1)) for val in g.get_xticks()]
		# g.set_xticklabels(new_xticklabel)

		new_yticklabel = [str(val) for val in g.get_yticks()]
		new_yticklabel[0]=' '
		new_yticklabel[-1]=' '
		g.set_yticklabels(new_yticklabel)		

	def add_slice_line(self,axis):

		line_fmt='ro-'

		if self.slice_type =='horizontal':
			x0 = y0 = None
			if self.slicem:
				y0=min(self.lats)
				y1=max(self.lats)
				for value in self.slicem:
					x0 = x1 = -value
					axis.plot([x0,x1],[y0,y1],line_fmt)

			if self.slicez:
				x0=min(self.lons)
				x1=max(self.lons)
				for value in self.slicez:
					y0 = y1 = value
					axis.plot([x0,x1],[y0,y1],line_fmt)				

		elif self.slice_type =='vertical':
			x0=x1=y0=y1=None			
			if self.sliceo=='meridional':
				x0=min(self.lats)
				x1=max(self.lats)
			if self.sliceo=='zonal':
				x0=min(self.lons)
				x1=max(self.lons)
			
			x0=x0*self.scale
			x1=x1*self.scale
			if all_same(self.zlevels):
				y0 = y1 = self.zlevels[0]
				axis.plot([x0,x1],[y0,y1],line_fmt)
			else:
				for value in self.zlevels:
					y0 = y1 = value
					axis.plot([x0,x1],[y0,y1],line_fmt)

	def add_windvector(self,grid_ax,comp1,comp2):

		if self.slice_type == 'horizontal':

			xjump=self.wind_jump['x']
			yjump=self.wind_jump['y']

			x=resample(self.lons,res=xjump)
			y=resample(self.lats,res=yjump)

			uu=resample(comp1,xres=xjump,yres=yjump)
			vv=resample(comp2,xres=xjump,yres=yjump)

			Q=grid_ax.quiver(x,y,uu,vv, 
								units='dots', 
								scale=self.windv_scale, 
								scale_units='dots',
								width=self.windv_width)
			qk=grid_ax.quiverkey(Q, 0.15, 0.1, 10, r'$10 \frac{m}{s}$', labelpos='W',
				 					fontproperties={'weight': 'bold'})
			grid_ax.set_xlim(self.extent['lx'],self.extent['rx'])
			grid_ax.set_ylim(self.extent['by'], self.extent['ty'])			

		elif self.slice_type == 'vertical':

			# xfoo=range(131)
			# yfoo=range(44)
			# plt.figure()
			# plt.quiver(xfoo,yfoo,comp1,comp2,
			# 			units='dots',
			# 			scale=0.5,
			# 			scale_units='dots',
			# 			width=1.5)
			# plt.axis([40,100,0,15])
			# plt.draw()

			xjump=2
			if self.sliceo=='meridional':
				lats=self.lats
				x=resample(lats,res=xjump)
			elif self.sliceo=='zonal':		
				lons=self.lons
				x=resample(lons,res=xjump)

			zvalues=self.axesval['z']
			zjump=self.wind_jump['z']
			y=resample(zvalues,res=zjump)

			hor= resample(comp1,xres=xjump,yres=zjump)
			ver= resample(comp2,xres=xjump,yres=zjump)

			Q=grid_ax.quiver(x*self.scale,y, hor, ver,
								units='dots', 
								scale=0.5, 
								scale_units='dots')
			qk=grid_ax.quiverkey(Q, 0.95, 0.8, 10, r'$10 \frac{m}{s}$')

	def add_flight_path(self,axis):

		""" plot line """
		x=self.flight['lon']
		y= self.flight['lat']
		axis.plot(x,y,	color=self.flightColor,
						linewidth=self.flightWidth,
						linestyle=self.flightStyle)

		""" add dots and text """
		for i in range(len(x)):
			if i%100 == 0:
				prop={'fontsize':self.flightPointSize,'color':(1,1,1),
						'horizontalalignment':'center',
        					'verticalalignment':'center'}
				axis.text(x[i],y[i],str(i/100),prop)
				axis.plot(x[i],y[i],
					marker='o',color=self.flightPointColor,markersize=self.flightPointSize)				

	def add_coastline(self,axis):
		x=self.coast['lon']
		y=self.coast['lat']
		axis.plot(x, y,color=self.coastColor,linewidth=self.coastWidth)

	def add_field(self,axis,**kwargs):

		array=kwargs['array']
		name=kwargs['name']
		extent=kwargs['ext']

		im = axis.imshow(array,
						interpolation='none',
						origin='lower',
						extent=extent,
						vmin=self.cmapRange[name][0],
						vmax=self.cmapRange[name][1],
						cmap=self.cmapName[name])

		return im

	def add_terrain_profile(self,axis,profile,profaxis):

		''' to kilometers '''
		profile=profile/1000.0
		
		if self.sliceo=='zonal':
			lons=profaxis*self.scale
			verts=zip(lons,profile)+[(lons[-1],0)]
		elif self.sliceo=='meridional':
			lats=profaxis[::-1]*self.scale
			profile=profile[::-1]
			verts=zip(lats,profile)+[(lats[-1],0)]
		poly=Polygon(verts,fc='0.9',ec='0.5')
		# print verts
		axis.add_patch(poly)

	def match_horizontal_grid(self,axis):

		if self.sliceo=='meridional':
			major = self.horizontal['ymajor']
			minor = self.horizontal['yminor']
			
		elif self.sliceo=='zonal':
			major = self.horizontal['xmajor']
			minor = self.horizontal['xminor']

		major_ticks=major*self.scale
		minor_ticks=minor*self.scale

		axis.set_xticks(major_ticks)                                                       
		axis.set_xticks(minor_ticks, minor=True) 

	def horizontal_plane(self ,**kwargs):

		field_array=kwargs['field']
		u_array=self.u_array
		v_array=self.v_array
		w_array=self.w_array

		if self.mask:
			field_array.mask=w_array.mask
			u_array.mask=w_array.mask
			v_array.mask=w_array.mask

		if self.panel:
			self.set_panel('single')
			figsize=self.figure_size['single']
		else:
			self.set_panel('multi')
			figsize=self.figure_size['multi']

		self.slice_type='horizontal'

		fig = plt.figure(figsize=figsize)

		plot_grids=ImageGrid( fig,111,
								nrows_ncols = self.rows_cols,
								axes_pad = 0.0,
								add_all = True,
								share_all=False,
								label_mode = "L",
								cbar_location = "top",
								cbar_mode="single")
	
		''' field extent '''
		extent1=self.get_extent()

		''' if zoomOpt is false then extent1=extent2 '''			
		if self.zoomOpt:
			if self.zoomOpt[0] == 'offshore':
				center=(38.6,-123.5)
			elif self.zoomOpt[0] == 'onshore':
				center=(38.85,-123.25)
			extent2=zoom_in(extent1,center)
		else:
			extent2=extent1


		''' make slices '''
		field_group = self.get_slices(field_array)
		ucomp = self.get_slices(u_array)
		vcomp = self.get_slices(v_array)		

		''' creates iterator group '''
		group=zip(plot_grids,self.zlevels,field_group,ucomp,vcomp)

		# make gridded plot
		for g,k,field,u,v in group:


			self.add_coastline(g)
			self.add_flight_path(g)
			im=self.add_field(g,array=field.T,name=self.var,ext=extent1)

			if self.terrain.file:
				Terrain.add_contour(g,self)

			if self.wind:
				self.add_windvector(g,u.T,v.T)

			# if self.slicem or self.slicez:
			self.add_slice_line(g)

			g.set_xlim(extent2[0], extent2[1])
			g.set_ylim(extent2[2], extent2[3])				

			if self.gridmajorOn:
				g.grid(True, which = 'major',linewidth=1)

			if self.gridminorOn:
				g.grid(True, which = 'minor',alpha=0.5)
				g.minorticks_on()

			ztext=str(k)+'km MSL'
			g.text(	0.05, 0.03,
					ztext,
					fontsize=self.zlevel_textsize,
					horizontalalignment='left',
					verticalalignment='center',
					transform=g.transAxes)

			self.horizontal['ymajor'] = g.get_yticks(minor=False)
			self.horizontal['yminor'] = g.get_yticks(minor=True)
			self.horizontal['xmajor'] = g.get_xticks(minor=False)
			self.horizontal['xminor'] = g.get_xticks(minor=True)			


		''' add color bar '''
		plot_grids.cbar_axes[0].colorbar(im)
		fig.suptitle(' Dual-Doppler Synthesis: '+ self.get_var_title(self.var) )

		plt.tight_layout()
		plt.draw()

	def vertical_plane(self,**kwargs):

		field_array=kwargs['field']
		self.sliceo=kwargs['sliceo']
		u_array=self.u_array
		v_array=self.v_array
		w_array=self.w_array

		self.slice_type='vertical'
		self.set_panel(self.slice_type)		

		figsize=self.figure_size['vertical']
		fig = plt.figure(figsize=figsize)

		plot_grids=ImageGrid( fig,111,
								nrows_ncols = self.rows_cols,
								axes_pad = 0.0,
								add_all = True,
								share_all=False,
								label_mode = "L",
								cbar_location = "top",
								cbar_mode="single",
								aspect=True)

		""" get list with slices """
		field_group = self.get_slices(field_array)
		uComp  = self.get_slices(u_array)
		vComp  = self.get_slices(v_array)
		wComp  = self.get_slices(w_array)
		profiles = Terrain.get_altitude_profile(self)

		''' field extent '''
		extent1=self.get_extent()

		''' if zoomOpt is false then extent1=extent2 '''			
		if self.zoomOpt:
			if self.zoomOpt[0] == 'offshore':
				center=(38.6,-123.5)
			elif self.zoomOpt[0] == 'onshore':
				center=(38.85,-123.25)
			extent2=zoom_in(extent1,center)
		else:
			extent2=extent1

		self.scale=20
		if self.sliceo=='meridional':
			extent3=adjust_extent(self,extent1,'meridional','data')
			extent4=adjust_extent(self,extent2,'meridional','detail')
			horizontalComp=vComp
			geo_axis='Lon: '

		elif self.sliceo=='zonal':
			extent3=adjust_extent(self,extent1,'zonal','data')
			extent4=adjust_extent(self,extent2,'zonal','detail')			
			horizontalComp=uComp
			geo_axis='Lat: '


		"""creates iterator group """
		group=zip(plot_grids,
					field_group,
					horizontalComp,
					wComp,
					profiles['altitude'],profiles['axis'])

		"""make gridded plot """
		p=0

		for g,field,h_comp,w_comp,prof,profax in group:

			im=self.add_field(g,array=field.T,name=self.var,ext=extent3)

			self.add_terrain_profile(g,prof,profax)

			if self.wind:
				self.add_windvector(g,h_comp.T,w_comp.T)

			self.add_slice_line(g)

			g.set_xlim(extent4[0], extent4[1])
			g.set_ylim(extent4[2], extent4[3])	

			if p == 0:
				self.match_horizontal_grid(g)

			g.grid(True, which = 'major',linewidth=1)


			self.adjust_ticklabels(g)

			if self.sliceo=='meridional':
				geotext=geo_axis+str(self.slicem[p])
			elif self.sliceo=='zonal':
				geotext=geo_axis+str(self.slicez[p])

			g.text(	0.03, 0.9,
					geotext,
					fontsize=self.zlevel_textsize,
					horizontalalignment='left',
					verticalalignment='center',
					transform=g.transAxes)
			p+=1

		 # add color bar
		plot_grids.cbar_axes[0].colorbar(im)
		fig.suptitle(' Dual-Doppler Synthesis: '+self.get_var_title(self.var) )

		# show figure
		plt.draw()
	
	def vertical_plane_velocity(self,**kwargs):

		spm_array=kwargs['fieldM'] # V-W component
		spz_array=kwargs['fieldZ'] # U-W component
		self.sliceo=kwargs['sliceo']

		u_array=self.u_array
		v_array=self.v_array
		w_array=self.w_array

		self.slice_type='vertical'
		self.set_panel(self.slice_type)
		self.set_colormap(self.var)

		fig = plt.figure(figsize=(self.figure_size))

		plot_grids=ImageGrid( fig,111,
								nrows_ncols = self.rows_cols,
								axes_pad = 0.0,
								add_all = True,
								share_all=False,
								label_mode = "L",
								cbar_location = "top",
								cbar_mode="single",
								aspect=True)

		spm_array=self.shrink(spm_array,xmask=self.maskLon,ymask=self.maskLat)
		spz_array=self.shrink(spz_array,xmask=self.maskLon,ymask=self.maskLat)
		u_array=self.shrink(u_array,xmask=self.maskLon,ymask=self.maskLat)
		v_array=self.shrink(v_array,xmask=self.maskLon,ymask=self.maskLat)
		w_array=self.shrink(w_array,xmask=self.maskLon,ymask=self.maskLat)

		spm_group = self.get_slices(spm_array)
		spz_group = self.get_slices(spz_array)
		uComp  = self.get_slices(u_array)
		vComp  = self.get_slices(v_array)
		wComp  = self.get_slices(w_array)

		self.minz=0.25
		self.maxz=5.0
		zvalues=self.axesval['z']
		self.zmask= np.logical_and(zvalues >= self.minz, zvalues <= self.maxz)

		self.scale=10
		if  self.sliceo=='meridional':
			self.extentv['lx']=self.extent['by']*self.scale
			self.extentv['rx']=self.extent['ty']*self.scale
			self.extentv['ty']=self.maxz
			self.extentv['by']=self.minz
			hComp=vComp
			geo_axis='Lon: '
			n=len(self.slicem)
			sliceVal=[x for pair in zip(self.slicem,self.slicem) for x in pair]
		elif self.sliceo=='zonal':
			self.extentv['lx']=self.extent['lx']*self.scale
			self.extentv['rx']=self.extent['rx']*self.scale
			self.extentv['ty']=self.maxz
			self.extentv['by']=self.minz
			hComp=uComp
			geo_axis='Lat: '
			n=len(self.slicez)
			sliceVal=[x for pair in zip(self.slicez,self.slicez) for x in pair]
		sph_group=[]
		for s in range(n):
			sph_group.append(spm_group[s])
			sph_group.append(spz_group[s])
		
		group=zip(plot_grids,sph_group)

		# make gridded plot
		p=0
		for g,s in group:

			s=s[: ,self.zmask]
			# hcomp=hcomp[: ,self.zmask]
			# wcomp=wcomp[: ,self.zmask]

			im = g.imshow(s.T,
							interpolation='none',
							origin='lower',
							extent=self.extent_vertical,
							vmin=self.cmap['range'][0],
							vmax=self.cmap['range'][1],
							cmap=self.cmap['name'])

			# self.add_windvector(g,hcomp,wcomp)

			self.add_slice_line(g)

			g.grid(True, which = 'major',linewidth=1)
			g.grid(True, which = 'minor',alpha=0.5)
			# g.minorticks_on()

			self.adjust_ticklabels(g)

			if p%2 ==0:
				geotext=geo_axis+str(sliceVal[p])
				g.text(	0.03, 0.9,
						geotext,
						fontsize=self.zlevel_textsize,
						horizontalalignment='left',
						verticalalignment='center',
						transform=g.transAxes)
			if p==0:
				g.text(	0.95, 0.9,
						'V-W',
						fontsize=self.zlevel_textsize,
						horizontalalignment='right',
						verticalalignment='center',
						transform=g.transAxes)								
			if p==1:
				g.text(	0.95, 0.9,
						'U-W',
						fontsize=self.zlevel_textsize,
						horizontalalignment='right',
						verticalalignment='center',
						transform=g.transAxes)				
			p+=1

		 # add color bar
		plot_grids.cbar_axes[0].colorbar(im)
		fig.suptitle(' Dual-Doppler Synthesis: '+self.get_var_title(self.var) )

		# show figure
		plt.draw()	

class FlightPlot(object):

	def __init__(self,**kwargs):

		self.met=None
		self.flightPath=None
		self.name=None

		for key,value in kwargs.iteritems():
			if key == 'meteo':
				self.met=value
			elif key == 'flightPath':
				self.flightPath=value
			elif key == 'name':
				self.name=value

	def plot_meteo(self):

		varname={	0:{'var':'atemp','name': 'air temperature',
									'loc':3,'ylim':None},
							1:{'var':'dewp','name': 'dew point temp',
									'loc':3,'ylim':None},
							4:{'var':'relh','name':'relative humidity',
									'loc':(0.05,0.05),'ylim':[80,101]},							
							7:{'var':'jwlwc','name':'liquid water content',
									'loc':(0.05,0.9),'ylim':None},
							2:{'var':'wdir','name':'wind direction',
									'loc':(0.05,0.9),'ylim':None},
							5:{'var':'wspd','name': 'wind speed',
									'loc':(0.05,0.9),'ylim':None},
							8:{'var':'wvert','name':'vertical velocity',
									'loc':(0.05,0.9),'ylim':None},
							3:{'var':'apres','name': 'air pressure',
									'loc':(0.05,0.9),'ylim':None},
							6:{'var':'galt','name': 'geopotential alt',
									'loc':(0.05,0.9),'ylim':None},
							9:{'var':'palt','name': 'pressure alt',
									'loc':(0.05,0.9),'ylim':None}}

		fig, ax = plt.subplots(3,3, sharex=True,figsize=(15,10))
		axs=ax.ravel()
		for i in varname.items():			
			var=i[1]['var']
			name=i[1]['name']
			loc=i[1]['loc']
			ylim=i[1]['ylim']
			if i[0] < 2:
				axs[0].plot(self.met[var],label=name)
				if ylim: axs[0].set_ylim(ylim)
				if i[0]==1:
					axs[0].grid(True)
					axs[0].legend(loc=loc,frameon=False)
			else:
				axs[i[0]-1].plot(self.met[var],label=name)
				if ylim: axs[i[0]-1].set_ylim(ylim)
				axs[i[0]-1].grid(True)
				axs[i[0]-1].annotate(name, 
									fontsize=16,
									xy=loc, 
									xycoords='axes fraction')


		self.adjust_xaxis(axs)
		self.adjust_yaxis(axs)
		fig.suptitle('Flight level meteorology for '+self.name,y=0.95)
		fig.subplots_adjust(bottom=0.04,top=0.9,
											hspace=0,wspace=0.2)
		plt.draw

	def adjust_yaxis(self,axes):

		for i in range(9):

			newlabels=[]
			yticks=axes[i].get_yticks()
			for y in yticks:
				newlabels.append(str(y))

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

	def adjust_xaxis(self,axes):

		for i in [6,7,8]:
			xticks=axes[i].get_xticks()
			newlabels=[]
			for x in xticks:
				newlabels.append(str(int(x/100)))
			axes[i].set_xticklabels(newlabels)

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
		data = data.reshape(121*131,1)

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
		grid_shape=(121,131)
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
		plt.figure()
		ax=plt.subplot(111)
		ax.scatter(data_extract2,flgt_mean)
		ax.plot([8, 20], [8, 20], color='k', linestyle='-', linewidth=2)
		ax.annotate(antext2, xy=(0.08, 0.9), xycoords="axes fraction",fontsize=14)
		ax.annotate(antext1, xy=(0.08, 0.85), xycoords="axes fraction",fontsize=14)
		ax.set_aspect(1)
		ax.grid(which='major')
		ax.set_xlim([8,20])
		ax.set_ylim([8,20])
		plt.suptitle(title2)
		plt.xlabel('synthesis WSPD')
		plt.ylabel('flight WSPD')

		plt.draw()

		# sys.exit()


'''	**********************************		
			Module functions 
	********************************** '''

def find_index_recursively(**kwargs):

	''' array and value have to have
			the same number of decimals
			positions
	'''
	array=kwargs['array']
	value=kwargs['value']
	decimals=kwargs['decimals'] #decimals of each element

	idx= np.where(array == value)
	array_new=array
	value_new=value
	while len(idx[0])==0:

		decimals-=1
		if decimals <0:
			return None
		array_new = np.asarray(around(array_new,decimals))
		value_new = round(value_new,decimals)
		idx= np.where(array_new == value_new)
	
	if len(idx[0])>1:
		idxx=find_nearest(array[idx[0]],value)
		return idx[0][idxx]
	else:
		return idx[0][0]
							 						
def around(array,decimals):

	rounded=[]
	for val in array:
		rounded.append(round(val,decimals))
	return rounded

def find_nearest(array,value):

	idx = (np.abs(array-value)).argmin()
	return idx

def chop_horizontal(self, array):

	zvalues=self.axesval['z']

	''' set  vertical level in a list of arrays '''
	if self.panel:
		choped_array = [array[:,:,self.panel[0]] for i in range(6)]
		self.zlevels = [zvalues[self.panel[0]] for i in range(6)]	
	else:
		choped_array = [array[:,:,i+1] for i in range(6)]
		self.zlevels = [zvalues[i+1] for i in range(6)]
		
	return choped_array

def chop_vertical(self,array):

	array=np.squeeze(array)

	slices=[]
	if self.sliceo=='zonal':		
		for coord in self.slicez:
			idx=find_nearest(self.lats,coord)
			slices.append(array[:,idx,:])
	elif self.sliceo=='meridional':
		for coord in self.slicem:
			idx=find_nearest(self.lons,-coord)
			slices.append(array[idx,:,:])
	# elif self.sliceo=='cross':
	# elif self.sliceo=='along:

	return slices	

def resample(array,**kwargs):

	if len(kwargs)==1:
		array=array[::kwargs['res']]

	elif len(kwargs)==2:
		yjump=kwargs['yres']
		xjump=kwargs['xres']
		array= array[::yjump,::xjump]

	return array

def all_same(array):
	b= all(x == array[0] for x in array)

	return b

def zoom_in(in_extent,center_point):

	y,x=center_point
	inext=in_extent
	outext=[None,None,None,None]
	delx=1.2 #[deg]
	dely=1.1 #[deg]

	if x<inext[0] or x>inext[1] or y<inext[2] or y>inext[3]:
		print "Zoom center point out of geographic extention boundaries"
		sys.exit()

	outext[0]=x-delx/2
	outext[1]=x+delx/2
	outext[2]=y-dely/2
	outext[3]=y+dely/2

	if outext[0]<inext[0]:outext[0]=inext[0]
	if outext[1]>inext[1]:outext[1]=inext[1]
	if outext[2]<inext[2]:outext[2]=inext[2]
	if outext[3]>inext[3]:outext[3]=inext[3]
		
	return outext	


def adjust_extent(self,ori_extent,orient,type_extent):

	# print ori_extent

	out_extent=[None,None,None,None]

	if orient == 'meridional':
		out_extent[0]=ori_extent[2] *self.scale
		out_extent[1]=ori_extent[3] *self.scale
	elif orient == 'zonal':
		out_extent[0]=ori_extent[0] *self.scale
		out_extent[1]=ori_extent[1] *self.scale

	# print out_extent
		
	if type_extent=='data':
		zvalues=self.axesval['z']		
		out_extent[2]=min(zvalues)
		out_extent[3]=max(zvalues)
	elif type_extent=='detail':
		out_extent[2]=0.0
		out_extent[3]=5.0			

	# print out_extent
	
	return out_extent

