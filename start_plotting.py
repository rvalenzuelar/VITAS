#!/home/rvalenzuela/miniconda/bin/python

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
import PlotArgParser as parser

def main( args ):
	
	cedfile = args.ced
	stdfile = args.std
	plotFields = args.field 
	print_shapes = args.print_shapes
	print_global_atts = args.print_global_atts
	print_axis = args.print_axis
	swd=args.set_working_directory
	gwd=args.get_working_directory
	terrain=args.terrain
	slope=args.slope
	meteo=args.meteo

	if gwd:
		fh.get_working_directory()
		sys.exit()

	""" retrieves synthesis and flight level objects """
	SYNTH,FLIGHT,DTM=fh.set_working_files(cedfile=cedfile,stdfile=stdfile,swd=swd)

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
							mask = args.mask)

	""" make terrain plots """
	Plotter.plot_terrain(P,terrain=terrain,slope=slope)

	""" make flight level meteo plot """
	Plotter.plot_flight_meteo(SYNTH,FLIGHT,meteo=meteo)

	# plt.show(block=False)	
	plt.show()

"""call main function """
if __name__ == "__main__":

	args = parser.start()

	main(args)
