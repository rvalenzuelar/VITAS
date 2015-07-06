#!/home/rvalenzuela/miniconda/bin/python

# Read netCDF file with pseudo-dual Doppler 
# synthesis and plot variables
#
#
# Raul Valenzuela
# July, 2015



from Plotter import plot_synth
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


	if gwd:
		fh.get_working_directory()
		sys.exit()

	""" retrieves synthesis and flight level objects """
	S,T,DTM=fh.set_working_files(cedfile=cedfile,stdfile=stdfile,swd=swd)

	""" creates a flightpath """
	F=T.Flightpath(S.start, S.end)

	""" print shape of attribute arrays """
	if print_shapes:
		S.print_shapes()
		if not print_global_atts: 
			sys.exit()

	""" print global attirutes of cedric synthesis """
	if print_global_atts:
		S.print_global_atts()
		sys.exit()

	""" print axis values """
	if print_axis:
		for ax in print_axis:
			if ax.isupper():
				ax=ax.lower()
			S.print_axis(ax)
		sys.exit()

	""" print synthesis time """
	print "Synthesis start time :%s" % S.start
	print "Synthesis end time :%s\n" % S.end

	""" make plots """
	for f in plotFields:
		plot_synth(S,F,DTM,
					var=f,
					wind=args.wind,
					panel=args.panel,
					slicem = args.slicem,
					slicez = args.slicez,
					zoomIn=args.zoomin,
					mask = args.mask,
					plot_terrain=args.terrain,
					plot_slope=args.slope)
	
	# plt.show(block=False)	
	plt.show()

"""call main function """
if __name__ == "__main__":

	args = parser.start()

	main(args)
