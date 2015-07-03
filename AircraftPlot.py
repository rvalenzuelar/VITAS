# Module for dual-Doppler plotting of NOAA P-3 tail radar.
#
#
# Raul Valenzuela
# June, 2015
#

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import ImageGrid
from os.path import expanduser,isfile
from Terrain import make_terrain_array
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import scipy.ndimage as scipy
import itertools as it
import gdal

class SynthPlot(object):

	def __init__(self):
		self.var=None
		self.windb=None
		self.panel=None
		self.slicen=None
		self.sliceo=None
		self.zoomOpt=None	
		self.figure_size=(None,None)
		self.rows_cols=(None,None)
		self.windb_size=None
		self.windb_jump=None
		self.zlevel_textsize=None
		self.geo_textsize=None
		self.windv_scale=None
		self.windv_width=None
		self.cmap_value=None
		self.cmap_name=None
		self.lats=None 
		self.lons=None
		self.extent={'lx':' ','rx':' ','by':' ','ty':' '}
		self.extentv={'lx':' ','rx':' ','by':' ','ty':' '}
		self.coast={'lon':' ', 'lat': ' '}
		self.flight_lat=None
		self.flight_lon=None
		self.maskLat=None
		self.maskLon=None
		self.minz=None
		self.maxz=None
		self.scale=None
		self.axesval={'x':' ','y':' ','z':' '}
		self.zlevels=[]
		self.slice_type=None
		self.u_array=[]
		self.v_array=[]
		self.w_array=[]
		self.terrain=None

	def set_geographic(self,synth):

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
	
	def set_flight_level(self,stdtape):

		jmp=5
		fp = zip(*stdtape[::jmp])
		self.flight_lat=fp[0]
		self.flight_lon=fp[1]

	def set_panel(self,option):

		# set some plotting values and stores
		# vertical level in a list of arrays
		if option == 'single':
			self.figure_size=(8,8)
			self.rows_cols=(1,1)
			self.windb_size=6.5
			self.windb_jump=2
			self.zlevel_textsize=12
			self.windv_scale=0.5
			self.windv_width=2

		elif option == 'multi':
			self.figure_size=(8,12)
			self.rows_cols=(3,2)
			self.windb_size=5
			self.windb_jump=5
			self.zlevel_textsize=10
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
			self.figure_size=(12,10)
			self.rows_cols=(rows,cols)
			self.windb_size=5
			self.windb_jump=5
			self.geo_textsize=12
			self.windv_scale=0.5
			self.windv_width=2

	def set_colormap(self,field):

		# define colormap range
		if field == 'DBZ':
			self.cmap_value=[-15,45]
			self.cmap_name='nipy_spectral'
		elif field == 'U':
			self.cmap_value=[-20,20]
			self.cmap_name='Accent'
		elif field == 'V':
			self.cmap_value=[-10,30]
			self.cmap_name='Accent'			
		elif field in ['WVA','WUP']:
			self.cmap_value=[-2,2]
			self.cmap_name='PRGn'			
		elif field in ['SPH','SPD']:
			if self.slice_type == 'horizontal':
				self.cmap_value=[5,20]
				self.cmap_name='Accent'
			else:
				self.cmap_value=[0,35]
				self.cmap_name='Accent'			
		elif field == 'CON':
			self.cmap_value=[-1,1]
			self.cmap_name='RdBu_r'
		elif field == 'VOR':
			self.cmap_value=[-1,1]
			self.cmap_name='PuOr'

	def get_slices(self,array):

		if self.slice_type == 'horizontal':
			slice_group  = self.chop_horizontal(array)
			return slice_group

		elif self.slice_type == 'vertical':
			slice_group = self.chop_vertical(array)
			return slice_group

	def get_extent(self):

		''' return a list with extent '''
		extent=[	self.extent['lx'],
					self.extent['rx'],
					self.extent['by'],
					self.extent['ty']]		

		return extent

	def chop_horizontal(self, array):

		zvalues=self.axesval['z']

		# set  vertical level in a list of arrays
		if self.panel:
			choped_array = [array[:,:,self.panel[0]] for i in range(6)]
			self.zlevels = [zvalues[self.panel[0]] for i in range(6)]	
		else:
			choped_array = [array[:,:,i+1] for i in range(6)]
			self.zlevels = [zvalues[i+1] for i in range(6)]
			
		return choped_array

	def chop_vertical(self,array):

		array=np.squeeze(array)
		lats=self.shrink(self.lats,mask=self.maskLat)
		lons=self.shrink(self.lons,mask=self.maskLon)

		slices=[]
		if self.sliceo=='zonal':		
			for coord in self.slicez:
				idx=self.find_nearest(lats,coord)
				slices.append(array[:,idx,:])
		elif self.sliceo=='meridional':
			for coord in self.slicem:
				idx=self.find_nearest(lons,-coord)
				slices.append(array[idx,:,:])
		# elif self.sliceo=='cross':
		# elif self.sliceo=='along:

		return slices

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

	def add_slice_line(self,axis):

		if self.slice_type =='horizontal':
			x0 = y0 = None
			if self.slicem:
				y0=min(self.shrink(self.lats,mask=self.maskLat))
				y1=max(self.shrink(self.lats,mask=self.maskLat))
				for value in self.slicem:
					x0 = x1 = -value
					axis.plot([x0,x1],[y0,y1],'ro-')

			if self.slicez:
				x0=min(self.shrink(self.lons,mask=self.maskLon))
				x1=max(self.shrink(self.lons,mask=self.maskLon))
				for value in self.slicez:
					y0 = y1 = value
					axis.plot([x0,x1],[y0,y1],'ro-')				

		elif self.slice_type =='vertical':
			x0=x1=y0=y1=None			
			if self.sliceo=='meridional':
				x0=min(self.shrink(self.lats,mask=self.maskLat))
				x1=max(self.shrink(self.lats,mask=self.maskLat))
			if self.sliceo=='zonal':
				x0=min(self.shrink(self.lons,mask=self.maskLon))
				x1=max(self.shrink(self.lons,mask=self.maskLon))
			
			x0=x0*self.scale
			x1=x1*self.scale
			if self.all_same(self.zlevels):
				y0 = y1 = self.zlevels[0]
				axis.plot([x0,x1],[y0,y1],'ro-')
			else:
				for value in self.zlevels:
					y0 = y1 = value


					axis.plot([x0,x1],[y0,y1],'ro-')

	def add_windvector(self,grid_ax,comp1,comp2):

		if self.slice_type == 'horizontal':
			xjump=self.windb_jump
			yjump=self.windb_jump

			lons=self.shrink(self.lons,mask=self.maskLon)
			x=self.resample(lons,res=xjump)

			lats=self.shrink(self.lats,mask=self.maskLat)
			y=self.resample(lats,res=yjump)

			uu=self.resample(comp1,xres=xjump,yres=yjump)
			vv=self.resample(comp2,xres=xjump,yres=yjump)

			Q=grid_ax.quiver(x,y,uu,vv, 
								units='dots', 
								scale=self.windv_scale, 
								scale_units='dots',
								width=self.windv_width)
			qk=grid_ax.quiverkey(Q,0.8,0.08,10,r'$10 \frac{m}{s}$')
			grid_ax.set_xlim(self.extent['lx'],self.extent['rx'])
			grid_ax.set_ylim(self.extent['by'], self.extent['ty'])			

		elif self.slice_type == 'vertical':

			xjump=2
			if self.sliceo=='meridional':
				lats=self.shrink(self.lats,mask=self.maskLat)
				x=self.resample(lats,res=xjump)
			elif self.sliceo=='zonal':		
				lons=self.shrink(self.lons,mask=self.maskLon)
				x=self.resample(lons,res=xjump)

			zvalues=self.shrink(self.axesval['z'],mask=self.zmask)
			zjump=1
			y=self.resample(zvalues,res=zjump)

			hor= self.resample(comp1,xres=xjump,yres=zjump)
			ver= self.resample(comp2,xres=xjump,yres=zjump)

			Q=grid_ax.quiver(x*self.scale,y, hor, ver,
								units='dots', 
								scale=0.5, 
								scale_units='dots',
								width=1.5)
			qk=grid_ax.quiverkey(Q,0.95,0.8,10,r'$10 \frac{m}{s}$')
	
	def zoom_in(self,zoom_type):

		if zoom_type == 'offshore':
			self.extent['by']=38.1
			self.extent['ty']=39.1
			self.extent['lx']=-124.1
			self.extent['rx']=-122.9
		elif zoom_type == 'onshore':
			self.extent['by']=38.3
			self.extent['ty']=39.4
			self.extent['lx']=-123.9
			self.extent['rx']=-122.6	
		self.maskLat= np.logical_and(self.lats >= self.extent['by'], 
										self.lats <= self.extent['ty'])
		self.maskLon= np.logical_and(self.lons >= self.extent['lx'], 
										self.lons <= self.extent['rx'])

	def shrink(self,array, **kwargs):

		if len(kwargs)==1:
			array=array[kwargs['mask']]

		elif len(kwargs)==2:
			MaskDimX=kwargs['xmask']
			MaskDimY=kwargs['ymask']
			array=array[MaskDimX][:,MaskDimY]

		if len(array)==1:
			return array[0]
		else:
			return array

	def resample(self,array,**kwargs):



		if len(kwargs)==1:
			array=array[::kwargs['res']]

		elif len(kwargs)==2:
			yjump=kwargs['yres']
			xjump=kwargs['xres']
			array= array[::yjump,::xjump]

		return array

	def find_nearest(self,array,value):

		idx = (np.abs(array-value)).argmin()
		return idx

	def adjust_ticklabels(self,g):
		
		g.set_xlim(self.extent_vertical[0], self.extent_vertical[1])
		g.set_ylim(0,self.maxz)
		
		new_xticklabel = [str(np.around(val/self.scale,1)) for val in g.get_xticks()]
		g.set_xticklabels(new_xticklabel)

		new_yticklabel = [str(val) for val in g.get_yticks()]
		new_yticklabel[0]=' '
		new_yticklabel[-1]=' '
		g.set_yticklabels(new_yticklabel)		

	def all_same(self,array):
		b= all(x == array[0] for x in array)
		return b

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
		else:
			self.set_panel('multi')

		self.slice_type='horizontal'
		self.set_colormap(self.var)

		fig = plt.figure(figsize=(self.figure_size))

		plot_grids=ImageGrid( fig,111,
								nrows_ncols = self.rows_cols,
								axes_pad = 0.0,
								add_all = True,
								share_all=False,
								label_mode = "L",
								cbar_location = "top",
								cbar_mode="single")
	

		extent1=self.get_extent()
		if self.zoomOpt:
			self.zoom_in(self.zoomOpt[0])

		extent2=self.get_extent()

		print_terrain=False
		if self.terrain.file:
			dtm=make_terrain_array()
			dtm_data=dtm['data'] # 2D
			print_terrain=True
			# dtm_array=dtm['mask'] # 3D

		field_group = self.get_slices(field_array)
		ucomp = self.get_slices(u_array)
		vcomp = self.get_slices(v_array)		

		# creates iterator group
		group=zip(plot_grids,self.zlevels,field_group,ucomp,vcomp)

		if print_terrain:
			plt.figure()
			plt.plot(self.coast['lon'], self.coast['lat'], color='r')
			plt.plot(self.flight_lon, self.flight_lat,color='r')		
			plt.imshow(dtm_data,interpolation='none',cmap='terrain_r',vmin=500,vmax=501,extent=dtm['extent'])
			plt.colorbar()
			plt.xlim(extent2[0], extent2[1])
			plt.ylim(extent2[2], extent2[3])				
			plt.draw()

		# make gridded plot
		for g,k,field,u,v in group:

			g.plot(self.coast['lon'], self.coast['lat'], color='b')
			g.plot(self.flight_lon, self.flight_lat)		

			im = g.imshow(field.T,
							interpolation='none',
							origin='lower',
							extent=extent1,
							vmin=self.cmap_value[0],
							vmax=self.cmap_value[1],
							cmap=self.cmap_name)

			if print_terrain:
				dtm_smooth=scipy.zoom(dtm_data,3)
				print dtm_data.shape
				print dtm_smooth.shape
				sys.exit()
				cont=g.contour(dtm['xg'],dtm['yg'],dtm_smooth,colors='k')
				g.clabel(cont,fontsize=9)


			if self.windb:
				self.add_windvector(g,u.T,v.T)

			# if self.slicem or self.slicez:
			self.add_slice_line(g)

			g.set_xlim(extent2[0], extent2[1])
			g.set_ylim(extent2[2], extent2[3])				

			g.grid(True, which = 'major',linewidth=1)
			g.grid(True, which = 'minor',alpha=0.5)
			g.minorticks_on()

			ztext='MSL='+str(k)+'km'
			g.text(	0.1, 0.08,
					ztext,
					fontsize=self.zlevel_textsize,
					horizontalalignment='left',
					verticalalignment='center',
					transform=g.transAxes)

		 # add color bar
		plot_grids.cbar_axes[0].colorbar(im)
		fig.suptitle(' Dual-Doppler Synthesis: '+ self.get_var_title(self.var) )

		# show figure
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

		field_array=self.shrink(field_array,xmask=self.maskLon,ymask=self.maskLat)
		u_array=self.shrink(u_array,xmask=self.maskLon,ymask=self.maskLat)
		v_array=self.shrink(v_array,xmask=self.maskLon,ymask=self.maskLat)
		w_array=self.shrink(w_array,xmask=self.maskLon,ymask=self.maskLat)

		""" get list with slices """
		field_group = self.get_slices(field_array)
		uComp  = self.get_slices(u_array)
		vComp  = self.get_slices(v_array)
		wComp  = self.get_slices(w_array)

		self.minz=0.25
		self.maxz=5.0
		zvalues=self.axesval['z']
		self.zmask= np.logical_and(zvalues >= self.minz, zvalues <= self.maxz)

		self.scale=20
		if self.sliceo=='meridional':
			# self.extent_vertical=[self.lat_bot*self.scale,
			# 						self.lat_top*self.scale,
			# 						self.minz,
			# 						self.maxz ]
			self.extentv['lx']=self.extent['by']*self.scale
			self.extentv['rx']=self.extent['ty']*self.scale
			self.extentv['ty']=self.maxz
			self.extentv['by']=self.minz
			horizontalComp=vComp
			geo_axis='Lon: '
		elif self.sliceo=='zonal':
			# self.extent_vertical=[self.lon_left*self.scale,
			# 						self.lon_right*self.scale,
			# 						self.minz,
			# 						self.maxz ]
			self.extentv['lx']=self.extent['lx']*self.scale
			self.extentv['rx']=self.extent['rx']*self.scale
			self.extentv['ty']=self.maxz
			self.extentv['by']=self.minz									
			horizontalComp=uComp
			geo_axis='Lat: '
			
		"""creates iterator group """
		group=zip(plot_grids,
					field_group,
					horizontalComp,
					wComp)

		"""make gridded plot """
		p=0
		for g,field,h_comp,w_comp in group:

			field=field[: ,self.zmask]
			h_comp=h_comp[: ,self.zmask]
			w_comp=w_comp[: ,self.zmask]

			im = g.imshow(field.T,
							interpolation='none',
							origin='lower',
							extent=self.extent_vertical,
							vmin=self.cmap_value[0],
							vmax=self.cmap_value[1],
							cmap=self.cmap_name)
			
			if self.windb:
				self.add_windvector(g,h_comp.T,w_comp.T)

			self.add_slice_line(g)

			g.grid(True, which = 'major',linewidth=1)
			g.grid(True, which = 'minor',alpha=0.5)
			g.minorticks_on()

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
							vmin=self.cmap_value[0],
							vmax=self.cmap_value[1],
							cmap=self.cmap_name)

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

