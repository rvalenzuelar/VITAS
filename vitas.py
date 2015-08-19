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

def main( config, args ):
	
	cedfile = args.ced
	stdfile = args.std
	plotFields = args.field 
	print_shapes = args.print_shapes
	print_global_atts = args.print_global_atts
	print_axis = args.print_axis
	terrain=args.terrain
	slope=args.slope
	meteo=args.meteo
	valid=args.valid


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
								config=config)

	""" make terrain plots """
	if terrain or slope:
		Plotter.plot_terrain(P,terrain=terrain,slope=slope)

	""" make flight level meteo plot """
	if meteo:
		Plotter.plot_flight_meteo(SYNTH,FLIGHT)

	""" compare synth and flight level """
	if valid:
		Plotter.compare_synth_flight(SYNTH,FLIGHT,level=valid,zoomin=args.zoomin)

	# plt.show(block=False)	
	plt.show()

"""call main function """
if __name__ == "__main__":

	args = parser.start()

	config = config.start()

	main(config,args)
