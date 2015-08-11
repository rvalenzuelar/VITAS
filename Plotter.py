#
# Function plotter
#
# Raul Valenzuela
# July 2015

from os import getcwd
import sys
import AircraftPlot as AP
import Terrain
import numpy as np

def plot_terrain(SynthPlot,**kwargs):

	terrain=kwargs['terrain']
	slope=kwargs['slope']

	if terrain:
	 	Terrain.plot_altitude_map(SynthPlot)

	if slope:
	 	Terrain.plot_slope_map(SynthPlot)

def plot_flight_meteo(SynthPlot,Synth,StdTape, **kwargs):

	meteo=kwargs['meteo']

	if meteo:
		met=StdTape.get_meteo(Synth.start, Synth.end)	
		flight_name = Synth.file[-13:]
		flight=AP.FlightPlot(meteo=met, name=flight_name)
		flight_xaxis=SynthPlot.flight_track_distance
		flight_dots=SynthPlot.flight_dot_index
		flight.plot_meteo(flight_xaxis,flight_dots)
		

def compare_synth_flight(Synth,StdTape,**kwargs):

	level = kwargs['level']
	zoomOpt = kwargs['zoomin']
	

	met=StdTape.get_meteo(Synth.start, Synth.end)	
	flight_path=StdTape.get_path(Synth.start, Synth.end)	
	flight_name = Synth.file[-13:]
	flight=AP.FlightPlot(meteo=met,name=flight_name,flightPath=flight_path)

	lat=Synth.LAT
	lon=Synth.LON
	z=Synth.Z

	""" synthesis horizontal velocity"""
	array=get_HorizontalWindSpeed(Synth.U,Synth.V)

	flight.compare_with_synth(array=array,x=lon,y=lat,z=z,level=z[level],zoom=zoomOpt[0])
	

def plot_synth(SYNTH , FLIGHT, DTM,**kwargs):

	"""creates synthesis plot instance """
	P=AP.SynthPlot()

	"""set variables """
	P.var = kwargs['var']
	P.wind = kwargs['wind']
	P.panel = kwargs['panel']
	P.zoomOpt = kwargs['zoomIn']
	P.mask = kwargs['mask']

	""" configure plot using vitas.config file '"""
	P.config(kwargs['config'])

	""" terrain array """
	P.terrain = DTM

	try:
		P.slicem=sorted(kwargs['slicem'],reverse=True)
	except TypeError:
		P.slicem=None
	try:
		P.slicez=sorted(kwargs['slicez'],reverse=True)
	except TypeError:
		P.slicez=None

	""" synthesis time """
	P.synth_start=SYNTH.start
	P.synth_end=SYNTH.end

	""" set common variables """
	P.axesval['x']=SYNTH.X
	P.axesval['y']=SYNTH.Y
	P.axesval['z']=SYNTH.Z
	P.u_array=SYNTH.U
	P.v_array=SYNTH.V
	if P.windv_verticalComp=='WVA':
		P.w_array=SYNTH.WVA
	elif P.windv_verticalComp=='WUP':
		P.w_array=SYNTH.WUP
	P.file=SYNTH.file

	""" general  geographic domain boundaries """
	P.set_geographic_extent(SYNTH)

	""" flight path from standard tape """
	fpath=FLIGHT.get_path(SYNTH.start, SYNTH.end)
	P.set_flight_path(fpath)

	""" coast line """
	P.set_coastline()

	""" get array """
	if P.var == 'SPD':
		array=get_HorizontalWindSpeed(P.u_array,P.v_array)
	else:
		array=getattr(SYNTH , P.var)		


	""" make horizontal plane plot """
	P.horizontal_plane(field=array)
	
	""" make vertical plane plots """
	velocity_fields=['SPD','WVA','WUP']
	if P.slicem:
		if P.var not in velocity_fields:
			P.vertical_plane(field=array,sliceo='meridional')	
		else:
			P.vertical_plane(spd='u',sliceo='meridional')
			P.vertical_plane(spd='v',sliceo='meridional')
			P.vertical_plane(spd='w',sliceo='meridional')

	if P.slicez:
		if P.var not in velocity_fields:
			P.vertical_plane(field=array,sliceo='zonal')	
		else:
			P.vertical_plane(spd='u',sliceo='zonal')
			P.vertical_plane(spd='v',sliceo='zonal')
			P.vertical_plane(spd='w',sliceo='zonal')

	return P

def get_TotalWindSpeed(U,V,W):

	return np.sqrt(U**2 + V**2 + W**2)
		
def get_HorizontalWindSpeed(U,V):

	return np.sqrt(U**2 + V**2)

def get_MeridionalWindSpeed(V,W):

	return np.sqrt(V**2 + W**2)

def get_ZonalWindSpeed(U,W):

	return np.sqrt(U**2 + W**2)