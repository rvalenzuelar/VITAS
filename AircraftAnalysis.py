#
# Module for dual-Doppler analisis of NOAA P-3 tail radar.
#
# Included classes:
#
# Stdtape:
#	Stdtape files contains flight level information, where
#	latitude and longitude coordinates are corrected
#	using GPS+INS
#
# Synthesis:
#	Reads a CEDRIC file with the dual-Doppler 
#	synthesis.
#
# Raul Valenzuela
# June, 2015
#

from netCDF4 import Dataset
from geographiclib.geodesic import Geodesic
import pandas as pd	
import datetime
import numpy as np
import subprocess


class Stdtape(object):
	def __init__(self, *args):

		self.file= args[0]
		self.LAT = self.read_stdtape('LAT')
		self.LON = self.read_stdtape('LON')
		self.GALT = self.read_stdtape('GEOPOT_ALT')
		self.PALT = self.read_stdtape('PRES_ALT')
		self.DATETIME = self.read_stdtape('DATETIME')

		'''creates dictionary '''
		dict_stdtape={}
		dict_stdtape['lats']=self.LAT
		dict_stdtape['lons']=self.LON
		dict_stdtape['galt']=self.GALT
		dict_stdtape['palt']=self.PALT

		''' pandas dataframe for standar tape '''
		self.df=pd.DataFrame(data=dict_stdtape,index=self.DATETIME)

	def read_stdtape(self,var):

		# open standard tape file for reading
		stdtape_file = Dataset(self.file,'r') 

		if var != 'DATETIME':		
			array = stdtape_file.variables[var][:]
		else:		
			base_time=stdtape_file.variables['base_time'][:]
			stdtape_secs=stdtape_file.variables['Time'][:]
			array=pd.to_datetime(stdtape_secs+base_time,unit='s')

		# close the file
		stdtape_file.close()

		return array

	def get_path(self,start_time, end_time):

		start = self.df.index.searchsorted(start_time)
		end = self.df.index.searchsorted(end_time)
		lat = self.df.ix[start:end]['lats'].values
		lon = self.df.ix[start:end]['lons'].values
		
		return zip(lat, lon)

class Synthesis(object):
	def __init__(self,*args):

		self.file= args[0]
		self.X = self.read_synth('x')
		self.Y = self.read_synth('y')
		self.Z = self.read_synth('z')
		self.U = self.read_synth('F2U')
		self.V = self.read_synth('F2V')
		self.WUP = self.read_synth('WUPF2')
		self.WVA = self.read_synth('WVARF2')
		self.VOR = self.read_synth('VORT2')
		self.CON = self.read_synth('CONM2')
		self.DBZ = self.read_synth('MAXDZ')
		self.SPD = self.get_TotalWindSpeed(self.WVA)
		self.SPH = self.get_HorizontalWindSpeed()
		self.SPM = self.get_MeridionalWindSpeed(self.WVA)
		self.SPZ = self.get_ZonalWindSpeed(self.WVA)
		self.LAT = self.set_geoGrid('latitude')
		self.LON = self.set_geoGrid('longitude')
		self.start = self.read_time('start')
		self.end = self.read_time('end')


	def read_synth(self, var):

		# open netCDF file for reading 
		synth = Dataset(self.file,'r') 

		# assing values from synthesis to instance attirbutes
		if var in ['x','y','z']:
			array = synth.variables[var][:]
		else:
			scale = getattr(synth.variables[var],'scale_factor')
			array = np.squeeze(synth.variables[var][:])/scale 
			array = self.adjust_dimensions(array)

		# close netCDF  file.
		synth.close()

		return array

	def read_time(self,thisTime):

		# open netCDF file for reading 
		synth = Dataset(self.file,'r') 

		# parse time				
		st = ''.join(synth.variables['start_time'][:])
		sd = ''.join(synth.variables['start_date'][:])
		et = ''.join(synth.variables['end_time'][:])
		ed = ''.join(synth.variables['end_date'][:])

		# close netCDF  file.
		synth.close()

		# parse start and end datetime
		if int(sd[0:2]) > 4:
			yy=int('19'+sd[0:2])
		else:
			yy=int('20'+sd[0:2])
		yr=[yy,yy]
		dy= [int(sd[3:5]),int(ed[3:5])]
		mo= [int(sd[6:8]),int(ed[6:8])]
		hr = [int(st[0:2]),int(et[0:2])]
		mn = [int(st[3:5]),int(et[3:5])]
		sc = [int(st[6:8]),int(et[6:8])]

		if thisTime =='start':
			return datetime.datetime(yr[0],mo[0],dy[0],hr[0],mn[0],sc[0])
		else:
			return datetime.datetime(yr[1],mo[1],dy[1],hr[1],mn[1],sc[1])

	def adjust_dimensions(self, array):
		# adjust axes to fit (X,Y,Z) dimensions
		# in 3D arrays
		return  np.swapaxes(array,0,2)
		
	def print_shapes(self):

		print "\nArray shapes:"
		print "--------------------"
		for attr, value in self.__dict__.iteritems():	
			if attr not in ['file', 'start','end'] and len(value)>0:
				try:
					print ( "%4s = %s" % (attr, value.shape) )
				except AttributeError:
					print ( "%4s = %s" % (attr, len(value) ) )
		print ""

	def print_axis(self,axis):

		# open netCDF file for reading 
		synth = Dataset(self.file,'r') 
		nc_vars = [var for var in synth.variables]  # list of nc variables

		print "\nAxis: "+axis.upper()
		print "-----------------------------"
		for var in nc_vars:
			if var == axis:
				print synth.variables[var][:]
				
		print ""

		# close netCDF  file.
		synth.close()		

	def print_global_atts(self):
		# open netCDF file for reading 
		synth = Dataset(self.file,'r') 
		nc_vars = [var for var in synth.variables]  # list of nc variables

		print "\nGlobal attributes:"
		print "-----------------------------"
		exclude=['x','y','z','grid_type','nyquist_velocities','el']
		for var in nc_vars:
			if var.islower() and var not in exclude:
				value=synth.variables[var][:]
				if value.ndim == 0:
					print ( "%22s = %s" % (var, value) )
				elif value.ndim == 1:
					if value.dtype.char =='S':
						print ( "%22s = %s" % (var, ''.join(value)) )
					else:
						if len(value)>1:
							print ( "%22s = %s" % (var, value[:]) )
						else:
							print ( "%22s = %s" % (var, value[0]) )
				else:
					continue
		print ""

		# close netCDF  file.
		synth.close()

	def set_geoGrid(self, geo_axis):

		ref_point = [38.3191, -123.0729] # Bodega Bay
		geo_grid = []
		if geo_axis == 'longitude':
			for x in self.X:
				if x <0:
					az=270
				else:
					az=90
				line = Geodesic.WGS84.Line(ref_point[0], ref_point[1], az)
				lp = line.Position(abs(x)*1000)
				geo_grid.append( lp['lon2'] )
			return np.asarray(geo_grid)
		elif geo_axis == 'latitude':
			for y in self.Y:
				if y <0:
					az=180
				else:
					az=0
				line = Geodesic.WGS84.Line(ref_point[0], ref_point[1], az)
				lp = line.Position(abs(y)*1000)
				geo_grid.append( lp['lat2'] )
			return np.asarray(geo_grid)
		else:
			print "Error in geo_axis name"
			exit()

	def get_TotalWindSpeed(self,W):

		return np.sqrt(self.U**2+self.V**2+W**2)
			
	def get_HorizontalWindSpeed(self):

		return np.sqrt(self.U**2+self.V**2)

	def get_MeridionalWindSpeed(self,W):

		return np.sqrt(self.V**2+W**2)

	def get_ZonalWindSpeed(self,W):

		return np.sqrt(self.U**2+W**2)

