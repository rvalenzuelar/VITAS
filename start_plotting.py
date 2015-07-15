#!/usr/bin/env python

# Read netCDF file with pseudo-dual Doppler 
# synthesis and plot variables
#
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

	""" retrieves synthesis and flight level objects """
	SYNTH,FLIGHT,DTM=fh.set_working_files(cedfile=cedfile,stdfile=stdfile,
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
	for f in plotFields:
		P=Plotter.plot_synth(SYNTH,FLIGHT,DTM,
							var=f,
							wind=args.wind,
							panel=args.panel,
							slicem = args.slicem,
							slicez = args.slicez,
							zoomIn=args.zoomin,
							mask = args.mask,
							config=config)

	""" make terrain plots """
	Plotter.plot_terrain(P,terrain=terrain,slope=slope)

	""" make flight level meteo plot """
	Plotter.plot_flight_meteo(SYNTH,FLIGHT,meteo=meteo)

	""" compare synth and flight level """
	Plotter.compare_synth_flight(SYNTH,FLIGHT,panel=args.panel,zoomin=args.zoomin)

	# plt.show(block=False)	
	plt.show()

"""call main function """
if __name__ == "__main__":

	args = parser.start()

	config = config.start()

	main(config,args)
