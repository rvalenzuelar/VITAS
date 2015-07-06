#
# Function to handle argument parser and help 
# information
#
# Raul Valenzuela
# July 2015


import argparse

def usage():

	desc="""
------------------------------------------------------------------------------	
Script for plotting NOAA-P3 Dual-Doppler analyses derived
from CEDRIC. 
------------------------------------------------------------------------------
"""
	print desc

def start():


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
							required=False,
							help=	"netCDF CEDRIC synthesis with format CaseName/LegName." \
									"\nExample: c03/leg01.cdf")
	group_mandatory.add_argument('--std','-s' ,
							metavar='file',
							required=False,
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
	plot_options.add_argument('--wind', '-w',
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
	group_directory=working_options.add_mutually_exclusive_group()
	group_directory.add_argument('--set_working_directory','-swd',
							action='store_true',
							help="set working directories")
	group_directory.add_argument('--get_working_directory','-gwd',
							action='store_true',
							help="get working directories")

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

	""" Terrain options """
	terrain_options=parser.add_argument_group('Terrain options')
	terrain_options.add_argument('--terrain',
							action='store_true',
							help="plot a terrain map")
	terrain_options.add_argument('--slope',
							action='store_true',
							help="plot a slope map")

	return parser.parse_args()	