#!//home/raul/miniconda/bin/python

# Read netCDF file with pseudo-dual Doppler 
# synthesis and plot variables
#
#
# Raul Valenzuela
# July, 2015


from Filehandler import set_working_files
from Plotter import plot_synth
import sys
import matplotlib.pyplot as plt
import argparse


def usage():

	desc="""
------------------------------------------------------------------------------	
Script for plotting NOAA-P3 Dual-Doppler analyses derived
from CEDRIC. 
------------------------------------------------------------------------------
"""
	print desc

def main( args ):
	
	cedfile = args.ced
	stdfile = args.std
	plotFields = args.field 
	print_shapes = args.print_shapes
	print_global_atts = args.print_global_atts
	print_axis = args.print_axis
	swd=args.set_working_directory


	gwd=args.get_working_directory # <-----LEFT HERE



	""" retrieves synthesis and flight level objects """
	S,T,DTM=set_working_files(cedfile=cedfile,stdfile=stdfile,swd=swd)

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
					windb=args.windv,
					panel=args.panel,
					slicem = args.slicem,
					slicez = args.slicez,
					zoomIn=args.zoomin,
					mask = args.mask)
	
	# plt.show(block=False)	
	plt.show()


		

"""call main function """
if __name__ == "__main__":

	parser = argparse.ArgumentParser(	description=usage(),
											formatter_class=argparse.RawTextHelpFormatter,
											add_help=False)

	help_option=parser.add_argument_group('Help')
	help_option.add_argument('--help', '-h',
							action='help',
							help='shows this help message and exit')

	""" Mandatory Arguments """
	group_mandatory=parser.add_argument_group('Input files')
	group_mandatory.add_argument('--ced','-c',
							metavar='file',
							required=True,
							help=	"netCDF CEDRIC synthesis with format CaseName/LegName." \
									"\nExample: c03/leg01.cdf")
	group_mandatory.add_argument('--std','-s' ,
							metavar='file',
							required=True,
							help=	"netCDF NOAA-P3 standard tape file using RAF format." \
									"\nExample: 010123I.nc")
	
	""" Plot Options """
	plot_options=parser.add_argument_group('Plot options')
	plot_options.add_argument('--panel', '-p',
							metavar='num',
							type=int, 
							nargs=1,
							default=None,
							help="choose a panel (1-6); otherwise plots a figure with 6 panles")
	plot_options.add_argument('--zoomin', '-z',
							metavar='str',
							nargs=1,
							default=None,
							choices=['offshore','onshore'],
							help="zoom-in over a offshore|onshore flight leg")	
	plot_options.add_argument('--windv', '-w',
							action='store_true',
							help="include wind vectors")	

	plot_options.add_argument('--mask','-m',
							action='store_true',
							help="mask pixels with NaN vertical velocity ")	

	""" Field Arguments """
	group_fields = plot_options.add_mutually_exclusive_group()
	group_fields.add_argument('--all', '-a',
							action='store_true',
							help="[default] plot all fields (DBZ,SPD,CON,VOR)")
	group_fields.add_argument('--field', '-f',
							metavar='STR',
							nargs='+',
							choices=['DBZ','SPD','CON','VOR','U','V','WVA','WUP'],
							default=['DBZ','SPD','CON','VOR'],
							help="specify radar field(s) to be plotted")	

	""" Print Options """
	print_options=parser.add_argument_group('Print options')
	print_options.add_argument('--print_shapes',
							action='store_true',
							help="print field variables and arrays with their shapes and exit")
	print_options.add_argument('--print_global_atts',
							action='store_true',
							help="print CEDRIC file global attributes and exit")	
	print_options.add_argument('--print_axis','-pa',
							metavar='STR',
							nargs='+',
							choices=['X','x','Y','y','Z','z'],
							help=" print axis values (X,Y,Z)")	

	""" Working directory Options """
	working_options=parser.add_argument_group('Working directory')
	working_options.add_argument('--set_working_directory','-swd',
							action='store_true',
							help="set working directory")
	working_options.add_argument('--get_working_directory','-gwd',
							action='store_true',
							help="get working directory")

	""" Slice options """
	slice_options=parser.add_argument_group('Slice options')
	slice_options.add_argument('--slicez', '-slz',
							metavar='lat (float)',
							type=float, 
							nargs='+',
							required=False,
							help="latitude coordinates for zonal slices")
	slice_options.add_argument('--slicem', '-slm',
							metavar='lon (float)',
							type=float, 
							nargs='+',
							required=False,
							help="longitude coordinates for zonal slices")

	args = parser.parse_args()	

	main(args)
