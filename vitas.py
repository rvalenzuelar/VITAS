#!/usr/bin/env python

# Initialize VITAS
#
# Raul Valenzuela
# July, 2015



import Plotter
import sys
import matplotlib.pyplot as plt
import Filehandler as fh 
import ArgParser as parser
import ConfigParser as config
import os
import glob

def main( config, args ):
	
	cedfile = args.ced
	stdfile = args.std
	plotFields = args.field 
	print_shapes = args.print_shapes
	print_global_atts = args.print_global_atts
	print_axis = args.print_axis
	print_list_synth = args.print_list_synth
	terrain=args.terrain
	slope=args.slope
	meteo=args.meteo
	valid=args.valid

	""" print synhesis availables """
	if print_list_synth:
		synth_folder=fh.set_working_files(config=config)
		out=os.listdir(synth_folder)
		print "Synthesis directories available:"
		for f in out:
			print f
		usr_input = raw_input('\nIndicate directory: ')
		out=os.listdir(synth_folder+'/'+usr_input)
		print "\nSyntheses available:"
		out.sort()
		for f in out:
			if f[-3:]=='cdf': print f
		print '\n'
		sys.exit()


	""" retrieves synthesis and flight instances
		from AircraftAnalysis
	"""
	SYNTH,FLIGHT,TERRAIN=fh.set_working_files(cedfile=cedfile,
											stdfile=stdfile,
											config=config)

	""" print shape of attribute arrays """
	if print_shapes:
		SYNTH.print_shapes()
		if not print_global_atts: 
			sys.exit()

	""" print global attirutes of cedric synthesis """
	if print_global_atts:
		SYNTH.print_global_atts()
		sys.exit()

	""" print axis values """
	if print_axis:
		for ax in print_axis:
			if ax.isupper():
				ax=ax.lower()
			SYNTH.print_axis(ax)
		sys.exit()

	""" print synthesis time """
	print "Synthesis start time :%s" % SYNTH.start
	print "Synthesis end time :%s\n" % SYNTH.end

	""" add some locations """
	bby=geolocation(lat=38.32,lon=-123.05,name='BBY')
	czd=geolocation(lat=38.53,lon=-123.08,name='CZD')

	""" make synthesis plots """
	if plotFields:
		for f in plotFields:
			P=Plotter.plot_synth(SYNTH,FLIGHT,TERRAIN,
								var=f,
								wind=args.wind,
								panel=args.panel,
								slicem = args.slicem,
								slicez = args.slicez,
								zoomIn=args.zoomin,
								mask = args.mask,
								config=config,
								locations=[bby,czd])

	""" make terrain plots """
	if terrain or slope:
		Plotter.plot_terrain(P,terrain=terrain,slope=slope)

	""" make flight level meteo plot """
	if meteo:
		Plotter.plot_flight_meteo(SYNTH,FLIGHT)

	""" compare synth and flight level """
	if valid:
		Plotter.compare_synth_flight(SYNTH,FLIGHT,level=valid,zoomin=args.zoomin)

	# if turbulence:
	# Plotter.print_covariance(SYNTH,FLIGHT)
	# Plotter.print_correlation(SYNTH,FLIGHT)
	
	# Plotter.plot_wind_comp_var(SYNTH,FLIGHT)

	# Plotter.plot_tke(SYNTH,FLIGHT)

	# Plotter.plot_vertical_heat_flux(SYNTH,FLIGHT)

	Plotter.make_profile_from_field(SYNTH,field='DBZ',location=bby)


	''' use this one with ipython '''
	plt.show(block=False)	

	''' use this one with the shell '''
	# plt.show()

class geolocation(object):
	def __init__(self,lat=None,lon=None,name=None):
		self.lat=lat
		self.lon=lon
		self.name=name

"""call main function """
if __name__ == "__main__":

	args = parser.start()

	config = config.start()

	main(config,args)
