# Module for dual-Doppler plotting of NOAA P-3 tail radar.
#
#
# Raul Valenzuela
# June, 2015
#

import Terrain 
import sys

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.patches import Polygon
from Common import *



class SynthPlot(object):

	def __init__(self):

		self.axesval={'x':None,'y':None,'z':None}
		self.cmapName=None
		self.cmapRange=None
		self.coast={'lon':None, 'lat':None}
		self.coastColor=None
		self.coastWidth=None
		self.coastStyle=None
		self.extent={'lx':None,'rx':None,'by':None,'ty':None}
		self.figure_size=None
		self.file=None
		self.flight={'lon':None, 'lat':None}
		self.flightColor=None
		self.flightWidth=None
		self.flightStyle=None
		self.flightDotOn=False
		self.flightDotColor=None
		self.flightDotSize=None
		self.flight_track_distance=None
		self.flight_dot_index=None
		self.geo_textsize=None
		self.horizontalGridMajorOn=False
		self.horizontalGridMinorOn=False
		self.verticalGridMajorOn=False
		self.verticalGridMinorOn=False		
		self.horizontal={'xminor':None,'xmajor':None,'yminor':None,'ymajor':None}
		self.lats=None 
		self.lons=None
		self.panel=None
		self.rows_cols=(None,None)
		self.scale=None
		self.slice_type=None
		self.slicen=None
		self.sliceo=None
		self.sliceLineColor=None
		self.sliceLineWidth=None
		self.sliceLineStyle=None
		self.synth_start=None
		self.synth_end=None
		self.terrain=None
		self.terrainContours=None
		self.terrainContourColors=None
		self.u_array=[]
		self.v_array=[]
		self.var=None
		self.w_array=[]
		self.wind=None
		self.windv_jump=None
		self.windv_color=None
		self.windv_scale=None
		self.windv_width=None
		self.windv_edgecolor=None
		self.windv_linewidth=None
		self.windv_magnitude=None
		self.zlevel_textsize=None
		self.zlevels=[]
		self.zoomCenter=None
		self.zoomDelta=None
		self.zoomOpt=None

	def config(self,config):
		try:
			self.cmapName=config['synthesis_field_cmap_name']
			self.cmapRange=config['synthesis_field_cmap_range']
			self.coastColor=config['coast_line_color']
			self.coastStyle=config['coast_line_style']
			self.coastWidth=config['coast_line_width']
			self.figure_size=config['figure_size']
			self.flightColor=config['flight_line_color']
			self.flightDotColor=config['flight_dot_color']
			self.flightDotOn=config['flight_dot_on']				
			self.flightDotSize=config['flight_dot_size']
			self.flightStyle=config['flight_line_style']				
			self.flightWidth=config['flight_line_width']
			self.horizontalGridMajorOn=config['synthesis_horizontal_gridmajor_on']
			self.horizontalGridMinorOn=config['synthesis_horizontal_gridminor_on']
			self.sliceLineColor=config['section_slice_line_color']
			self.sliceLineStyle=config['section_slice_line_style']
			self.sliceLineWidth=config['section_slice_line_width']
			self.terrainContourColors=config['terrain_contours_color']
			self.terrainContours=config['terrain_contours']
			self.terrainProfileEdgecolor=config['terrain_profile_edgecolor']
			self.terrainProfileFacecolor=config['terrain_profile_facecolor']
			self.verticalGridMajorOn=config['synthesis_vertical_gridmajor_on']
			self.verticalGridMinorOn=config['synthesis_vertical_gridminor_on']
			self.windv_verticalComp=config['wind_vector_vertical_component']
			self.windv_color=config['wind_vector_color']
			self.windv_edgecolor=config['wind_vector_edgecolor']
			self.windv_jump=config['wind_vector_jump']
			self.windv_linewidth=config['wind_vector_linewidth']
			self.windv_magnitude=config['wind_vector_magnitude']
			self.windv_scale=config['wind_vector_scale']
			self.zoomCenter=config['zoom_center']
			self.zoomDelta=config['zoom_del']
		except KeyError as e:
			print "Please add the "+e.args[0]+" key to vitas.config\n"
			sys.exit()

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

	def set_panel(self,**kwargs):

		isWind=False
		for key,value in kwargs.iteritems():
			if key == 'option':
				option=value
			elif key == 'wind':
				isWind=value

		"""
		set some plotting values and stores
		vertical level in a list of arrays
		"""
		if option == 'single':			
			self.rows_cols=(1,1)
			self.zlevel_textsize=16
			self.windv_width=2

		elif option == 'multi':
			self.rows_cols=(3,2)
			self.windv_jump['x']=self.windv_jump['x']+3
			self.windv_jump['y']=self.windv_jump['y']+3
			self.zlevel_textsize=12
			self.windv_width=2

		elif option == 'vertical':
			if self.var == 'SPD' and not isWind:
				cols=2 #(U,V)
			else:
				cols=1
			if self.sliceo=='meridional':
				rows=len(self.slicem)
			elif self.sliceo=='zonal':
				rows=len(self.slicez)
			self.rows_cols=(rows,cols)
			self.geo_textsize=12
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
					'SPD': 'Horizontal wind speed [m/s]',
					'U': 'wind u-component [m/s]',
					'V': 'wind v-component[m/s]',
					'VOR': 'Vorticity [1/s]',
					'CON': 'Convergence [1/s]',
					'WVA': 'wind w-component (variational) [m/s]',
					'WUP': 'wind w-component (vertical integration) [m/s]'}
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

		if self.slice_type =='horizontal':
			x0 = y0 = None
			if self.slicem:
				y0=min(self.lats)
				y1=max(self.lats)
				for value in self.slicem:
					x0 = x1 = -value
					line=axis.plot([x0,x1],[y0,y1])
					self.sliceLine_setup(line)

			if self.slicez:
				x0=min(self.lons)
				x1=max(self.lons)
				for value in self.slicez:
					y0 = y1 = value
					line=axis.plot([x0,x1],[y0,y1])
					self.sliceLine_setup(line)

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
				line=axis.plot([x0,x1],[y0,y1])
				self.sliceLine_setup(line)
			else:
				for value in self.zlevels:
					y0 = y1 = value
					line=axis.plot([x0,x1],[y0,y1])
					self.sliceLine_setup(line)

	def sliceLine_setup(self,line):

		plt.setp(line,	color=self.sliceLineColor,
						linewidth=self.sliceLineWidth,
						linestyle=self.sliceLineStyle)

	def add_windvector(self,grid_ax,comp1,comp2):

		if self.slice_type == 'horizontal':

			xjump=self.windv_jump['x']
			yjump=self.windv_jump['y']

			x=resample(self.lons,res=xjump)
			y=resample(self.lats,res=yjump)

			uu=resample(comp1,xres=xjump,yres=yjump)
			vv=resample(comp2,xres=xjump,yres=yjump)

			Q=grid_ax.quiver(x,y,uu,vv, 
								units='dots', 
								scale=self.windv_scale, 
								scale_units='dots',
								width=self.windv_width,
								color=self.windv_color,
								linewidth=self.windv_linewidth,
								edgecolor=self.windv_edgecolor)
			symbol = '$'+str(self.windv_magnitude)+r'\frac{m}{s}$'
			qk=grid_ax.quiverkey(Q, 0.15, 0.1, self.windv_magnitude, symbol, labelpos='W',
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
			zjump=self.windv_jump['z']
			y=resample(zvalues,res=zjump)

			hor= resample(comp1,xres=xjump,yres=zjump)
			ver= resample(comp2,xres=xjump,yres=zjump)

			Q=grid_ax.quiver(x*self.scale,y, hor, ver,
								units='dots', 
								scale=0.5, 
								scale_units='dots',
								width=self.windv_width,
								color=self.windv_color,
								linewidth=self.windv_linewidth,
								edgecolor=self.windv_edgecolor)
			qk=grid_ax.quiverkey(Q, 0.95, 0.8, 10, r'$10 \frac{m}{s}$')

	def add_flight_path(self,axis):

		""" plot line """
		x=self.flight['lon']
		y= self.flight['lat']
		axis.plot(x,y,	color=self.flightColor,
						linewidth=self.flightWidth,
						linestyle=self.flightStyle)

		if self.flightDotOn:		
			""" add dots and text """
			frequency=10 # [km]
			[dist_from_p0,idxs] = get_distance_along_flight_track(lon=x, lat=y, 
																ticks_every=frequency)
			
			for i in idxs:
				value=round_to_closest_int(dist_from_p0[i],frequency)
				self.add_flight_dot(axis,y[i],x[i],value)

			self.flight_track_distance=dist_from_p0
			self.flight_dot_index=idxs

	def add_flight_dot(self,axis,lat,lon,position):

		if not self.panel:
			self.flightDotSize=8

		fontsize=int(self.flightDotSize*0.8)
		prop={'fontsize':fontsize,'color':(1,1,1),
				'horizontalalignment':'center',
				'verticalalignment':'center'}			
		axis.text(lon,lat,str(position),prop)
		axis.plot(lon,lat,	marker='o',
							color=self.flightDotColor,
							markersize=self.flightDotSize)				

	def add_coastline(self,axis):
		x=self.coast['lon']
		y=self.coast['lat']
		axis.plot(x, y,
					color=self.coastColor,
					linewidth=self.coastWidth,
					linestyle=self.coastStyle)

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
		fc=self.terrainProfileFacecolor
		ec=self.terrainProfileEdgecolor
		poly=Polygon(verts,facecolor=fc,edgecolor=ec)
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

	def horizontal_plane(self , **kwargs):

		field_array=kwargs['field']
		u_array=self.u_array
		v_array=self.v_array
		w_array=self.w_array

		if self.mask:
			field_array.mask=w_array.mask
			u_array.mask=w_array.mask
			v_array.mask=w_array.mask

		if self.panel:
			self.set_panel(option='single')
			figsize=self.figure_size['single']
		else:
			self.set_panel(option='multi')
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
			opt=self.zoomOpt[0]
			extent2=zoom_in(self,extent1,self.zoomCenter[opt])
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

			if self.horizontalGridMajorOn:
				g.grid(True, which = 'major',linewidth=1)

			if self.horizontalGridMinorOn:
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

			# g.subplots_adjust(bottom=0.04,top=0.95)

		''' add color bar '''
		plot_grids.cbar_axes[0].colorbar(im)
		titext='Dual-Doppler Synthesis: '+ self.get_var_title(self.var)+'\n'
		line_start='\nStart time: '+self.synth_start.strftime('%Y-%m-%d %H:%M')+' UTC'
		line_end='\nEnd time: '+self.synth_end.strftime('%Y-%m-%d %H:%M')+' UTC'
		fig.suptitle(titext+self.file+line_start+line_end)

		# plt.tight_layout()
		plt.draw()

	def vertical_plane(self,**kwargs):

		field_array=None
		for key,value in kwargs.iteritems():
			if key == 'field':
				isWind=False			
				field_array=value
			if key == 'spd':
				isWind=True
				windname=value
			elif key == 'sliceo':
				self.sliceo=value

		u_array=self.u_array
		v_array=self.v_array
		w_array=self.w_array

		self.slice_type='vertical'
		self.set_panel(option=self.slice_type,wind=isWind)		

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
		uComp  = self.get_slices(u_array)
		vComp  = self.get_slices(v_array)
		wComp  = self.get_slices(w_array)
		profiles = Terrain.get_altitude_profile(self)

		if isWind:
			if windname == 'u':
				field_group = uComp
				colorName='U'
				varName=colorName
			elif windname == 'v':
				field_group = vComp
				colorName='V'
				varName=colorName
			elif windname == 'w':
				field_group = wComp
				colorName=self.var
				varName=self.var
		else:
			field_group = self.get_slices(field_array)
			varName=self.var

		''' field extent '''
		extent1=self.get_extent()

		''' if zoomOpt is false then extent1=extent2 '''			
		if self.zoomOpt:
			opt=self.zoomOpt[0]
			extent2=zoom_in(self,extent1,self.zoomCenter[opt])
		else:
			extent2=extent1

		''' scale for horizontal axis'''
		self.scale=20

		''' adjust vertical extent '''
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

			if isWind:
				im=self.add_field(g,array=field.T,name=colorName,ext=extent3)
			else:
				im=self.add_field(g,array=field.T,name=self.var,ext=extent3)

			self.add_terrain_profile(g,prof,profax)

			if self.wind and not isWind:
				self.add_windvector(g,h_comp.T,w_comp.T)

			self.add_slice_line(g)

			g.set_xlim(extent4[0], extent4[1])
			g.set_ylim(extent4[2], extent4[3])	

			if p == 0:
				self.match_horizontal_grid(g)

			self.adjust_ticklabels(g)

			if self.verticalGridMajorOn:
				g.grid(True, which = 'major',linewidth=1)

			if self.verticalGridMinorOn:
				g.grid(True, which = 'minor',alpha=0.5)
				g.minorticks_on()

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
		# fig.suptitle(' Dual-Doppler Synthesis: '+self.get_var_title(self.var) )

		titext='Dual-Doppler Synthesis: '+ self.get_var_title(varName)+'\n'
		line_start='\nStart time: '+self.synth_start.strftime('%Y-%m-%d %H:%M')+' UTC'
		line_end='\nEnd time: '+self.synth_end.strftime('%Y-%m-%d %H:%M')+' UTC'		
		fig.suptitle(titext+self.file+line_start+line_end)

		# show figure
		plt.draw()
	





