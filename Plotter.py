#
# Function plotter
#
# Raul Valenzuela
# July 2015

from os import getcwd
import sys
import AircraftPlot as AP
import Terrain

def plot_terrain(SynthPlot,**kwargs):

	terrain=kwargs['terrain']
	slope=kwargs['slope']

	if terrain:
	 	Terrain.plot_altitude_map(SynthPlot)

	if slope:
	 	Terrain.plot_slope_map(SynthPlot)

def plot_flight_meteo(Synth,StdTape, **kwargs):

	meteo=kwargs['meteo']

	if meteo:
		met=StdTape.get_meteo(Synth.start, Synth.end)	
		flight=AP.FlightPlot(meteo=met)
		flight.timeseries()
		

def compare_synth_flight(Synth,StdTape,**kwargs):

	met=StdTape.get_meteo(Synth.start, Synth.end)	
	path=StdTape.get_path(Synth.start, Synth.end)	
	
	flight=AP.FlightPlot(meteo=met,path=path)

	lat=Synth.LAT
	lon=Synth.LON
	z=Synth.Z

	panel = kwargs['panel']

	print z[panel]

	array=Synth.SPH
	flight.compare_with_synth(array=array,x=lon,y=lat,z=z,level=z[panel])
	

def plot_synth(SYNTH , FLIGHT, DTM,**kwargs):

	"""creates synthesis plot instance """
	P=AP.SynthPlot()

	"""set variables """
	P.var = kwargs['var']
	P.wind = kwargs['wind']
	P.panel = kwargs['panel']
	P.zoomOpt = kwargs['zoomIn']
	P.mask = kwargs['mask']
	P.terrain = DTM

	try:
		P.slicem=sorted(kwargs['slicem'],reverse=True)
	except TypeError:
		P.slicem=None
	try:
		P.slicez=sorted(kwargs['slicez'],reverse=True)
	except TypeError:
		P.slicez=None

	""" get array """
	if P.var == 'SPD':
		P.var = 'SPH' # horizontal proyection
	array=getattr(SYNTH , P.var)		

	""" set common variables """
	P.axesval['x']=SYNTH.X
	P.axesval['y']=SYNTH.Y
	P.axesval['z']=SYNTH.Z
	P.u_array=SYNTH.U
	P.v_array=SYNTH.V
	P.w_array=SYNTH.WVA
	# P.w_array=SYNTH.WUP

	""" general  geographic domain boundaries """
	P.set_geographic_extent(SYNTH)

	""" flight path from standard tape """
	fpath=FLIGHT.get_path(SYNTH.start, SYNTH.end)
	P.set_flight_path(fpath)

	""" coast line """
	P.set_coastline()

	""" make horizontal plane plot """
	P.horizontal_plane(field=array)
	
	""" make vertical plane plots """		
	if P.slicem:
		if P.var == 'SPH' :
			P.vertical_plane_velocity(	fieldM=SYNTH.SPM, # meridional component
										fieldZ=SYNTH.SPZ,
										sliceo='meridional') # zonal component)
		else:
			P.vertical_plane(field=array,sliceo='meridional')	

	if P.slicez:
		if P.var == 'SPH' :
			P.vertical_plane_velocity(	fieldM=SYNTH.SPM, # meridional component
										fieldZ=SYNTH.SPZ,
										sliceo='zonal') # zonal component)
		else:
			P.vertical_plane(field=array,sliceo='zonal')	

	return P