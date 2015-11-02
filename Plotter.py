#
# Function plotter
#
# Raul Valenzuela
# July 2015

from os import getcwd

import sys
import Radardata as rd
import Flightdata as fd
import Terrain
import numpy as np
import Common as cm
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime

from plotWindprof import get_filenames,make_arrays

import seaborn as sns
from geographiclib.geodesic import Geodesic


def plot_terrain(SynthPlot,**kwargs):

	terrain=kwargs['terrain']
	slope=kwargs['slope']
	terrain_file=kwargs['terrain_file']

	if terrain:
	 	Terrain.plot_altitude_map(SynthPlot,terrain_file)

	if slope:
	 	Terrain.plot_slope_map(SynthPlot)

def plot_flight_meteo(SYNTH,FLIGHT, **kwargs):

	flight_xaxis, flight_xticks =get_xaxis(SYNTH,FLIGHT)
	met = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)	
	flight_name = SYNTH.file[-13:]
	flight = fd.FlightPlot(meteo=met, name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.plot_meteo(flight_xaxis,flight_xticks)
		

def print_covariance(SYNTH,FLIGHT):

	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.print_covariance_matrix(data)

def print_correlation(SYNTH,FLIGHT):

	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.print_correlation_matrix(data)

def plot_wind_comp_var(SYNTH,FLIGHT):

	flight_xaxis, _ =get_xaxis(SYNTH,FLIGHT)
	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.plot_wind_comp_var(data, flight_xaxis)

def plot_tke(SYNTH,FLIGHT):

	flight_xaxis, _ =get_xaxis(SYNTH,FLIGHT)
	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.plot_tke(data,flight_xaxis)	

def plot_vertical_heat_flux(SYNTH,FLIGHT):

	flight_xaxis, _ =get_xaxis(SYNTH,FLIGHT)
	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.plot_vertical_heat_flux(data,flight_xaxis)	

def plot_vertical_momentum_flux(SYNTH,FLIGHT,terrain):

	flight_xaxis, _ =get_xaxis(SYNTH,FLIGHT)
	flight_name = SYNTH.file[-13:]
	data = FLIGHT.get_meteo(SYNTH.start, SYNTH.end)
	flight = fd.FlightPlot(name=flight_name, time=[SYNTH.start, SYNTH.end])
	flight.plot_vertical_momentum_flux(data,flight_xaxis,terrain)	

def get_xaxis(SYNTH,FLIGHT):
	""" flight path from standard tape """
	fpath=FLIGHT.get_path(SYNTH.start, SYNTH.end)
	fp=zip(*fpath)
	x = fp[1] # longitude
	y = fp[0] # latitude
	frequency=10 #[km]
	[flight_xaxis, flight_xticks] = cm.get_distance_along_flight_track(lon=x,lat=y,
															ticks_every=frequency)
	return flight_xaxis,flight_xticks

def compare_synth_flight(Synth,StdTape,**kwargs):

	level = kwargs['level']
	zoomOpt = kwargs['zoomin']
	
	met=StdTape.get_meteo(Synth.start, Synth.end)	
	flight_path=StdTape.get_path(Synth.start, Synth.end)	
	flight_name = Synth.file[-13:]
	flight=fd.FlightPlot(meteo=met,name=flight_name,flightPath=flight_path)

	lat=Synth.LAT
	lon=Synth.LON
	z=Synth.Z

	""" synthesis horizontal velocity"""
	array=get_HorizontalWindSpeed(Synth.U,Synth.V)

	flight.compare_with_synth(array=array,met='wspd',x=lon,y=lat,z=z,level=z[level])
	flight.compare_with_synth(array=Synth.WUP,met='wvert',x=lon,y=lat,z=z,level=z[level])


def compare_with_windprof(SYNTH,**kwargs):

	# field = kwargs['field']
	loc=kwargs['location']
	U = SYNTH.U
	V = SYNTH.V
	LAT=SYNTH.LAT
	LON=SYNTH.LON
	Z=SYNTH.Z
	st=SYNTH.start
	en=SYNTH.end

	''' synthesis '''
	lat_idx=cm.find_index_recursively(array=LAT,value=loc['lat'],decimals=2)
	lon_idx=cm.find_index_recursively(array=LON,value=loc['lon'],decimals=2)
	uprof = U[lon_idx,lat_idx,:]
	vprof = V[lon_idx,lat_idx,:]
	sprofspd=np.sqrt(uprof**2+vprof**2)
	sprofdir=270. - ( np.arctan2(vprof,uprof) * 180./np.pi )

	''' wind profiler '''
	case=loc['case']
	wpfiles = get_filenames(case)
	print case
	wspd,wdir,time,hgt = make_arrays(files= wpfiles, resolution='coarse',surface=False)
	print time
	idx = time.index(datetime.datetime(st.year, st.month, st.day, st.hour, 0))
	wprofspd = wspd[:,idx]
	wprofdir = wdir[:,idx]


	''' profile '''
	with sns.axes_style("darkgrid"):
		fig,ax=plt.subplots(1,2, figsize=(9,9), sharey=True)
		
		n=0
		hl1=ax[n].plot(sprofspd,Z,'-o',label='P3-SYNTH (250 m)')
		hl2=ax[n].plot(wprofspd,hgt,'-o',label='WPROF-COARSE (100 m)')
		ax[n].set_xlabel('wind speed [m s-1]')
		ax[n].set_ylabel('height AGL [km]')
		lns = hl1 + hl2
		labs = [l.get_label() for l in lns]
		ax[n].legend(lns, labs, loc=0)

		n=1
		ax[n].plot(sprofdir,Z,'-o',label='P3-SYNTH')
		ax[n].plot(wprofdir,hgt,'-o',label='WPROF')
		ax[n].set_xlabel('wind direction [deg]')
		ax[n].invert_xaxis()
		t1='Comparison between P3-synthesis and ' +loc['name']+' wind profiler'
		t2='\nDate: ' + st.strftime('%Y-%m-%d')
		t3='\nSynthesis time: ' + st.strftime('%H:%M') + ' to ' + en.strftime('%H:%M UTC') 
		t4='\nWind profiler time: ' + time[idx].strftime('%H:%M') + ' to ' + time[idx+1].strftime('%H:%M UTC') 
		fig.suptitle(t1+t2+t3+t4)
		plt.ylim([0,5])
		
		plt.draw()

def plot_synth(SYNTH , FLIGHT, DTM,**kwargs):

	"""creates synthesis plot instance """
	P=rd.SynthPlot()

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
	try:
		coord0 = kwargs['slice'][0]
		azim = kwargs['azimuth'][0] #[deg]
		dist = kwargs['distance'][0] * 1000. #[m]
		gd = Geodesic.WGS84.Direct(coord0[0], coord0[1], 
										azim, dist)
		coord1 = (gd['lat2'], gd['lon2'])
		P.slice=[coord0,coord1]
		P.azimuth=azim
		P.distance=dist /1000. #[km]
	except TypeError:
		P.slice=None

	""" synthesis time """
	P.synth_start=SYNTH.start
	P.synth_end=SYNTH.end

	""" set common variables """
	P.axesval['x']=SYNTH.Y
	P.axesval['y']=SYNTH.X
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

	if P.slice:
		# if P.var not in velocity_fields:
		# 	P.cross_section(field=array)
		# else:
		# 	P.cross_section(spd=array)
		P.cross_section(field=array)			

	return P

def get_TotalWindSpeed(U,V,W):

	return np.sqrt(U**2 + V**2 + W**2)
		
def get_HorizontalWindSpeed(U,V):

	return np.sqrt(U**2 + V**2)

def get_MeridionalWindSpeed(V,W):

	return np.sqrt(V**2 + W**2)

def get_ZonalWindSpeed(U,W):

	return np.sqrt(U**2 + W**2)