#!//home/raul/miniconda/bin/python

# Read netCDF file with pseudo-dual Doppler 
# synthesis and plot variables
#
# Check:
# http://matplotlib.org/examples/axes_grid/demo_axes_grid2.html
# http://stackoverflow.com/questions/7878398/how-to-extract-an-arbitrary-line-of-values-from-a-numpy-array
#
# Raul Valenzuela
# July, 2015

from os import getcwd
from os.path import dirname, basename, expanduser
import sys
import matplotlib.pyplot as plt
import argparse
import AircraftAnalysis as aa 
import AircraftPlot as ap

def usage():

	desc="""
------------------------------------------------------------------------------	
Script for plotting NOAA-P3 Dual-Doppler analyses derived
from CEDRIC. 
------------------------------------------------------------------------------
"""
	print desc

def main( args ):
	
	filepath = args.ced
	stdfile = args.std
	plotFields = args.field 
	print_shapes = args.print_shapes
	print_global_atts = args.print_global_atts
	print_axis = args.print_axis

	home = expanduser("~")

	"""base directory """
	basedirectory = home+"/P3_v2/synth_test/"
	stdtapedir = home+"/Github/correct_dorade_metadata/"

	"""input folder """
	mypath=dirname(filepath)
	myfile=basename(filepath)

	
	if mypath ==".":
		mypath=getcwd()
		filepath=mypath+filepath
	else:
		mypath=basedirectory
		filepath=mypath+filepath

	if not myfile:
		print "Please include filename in path"
		sys.exit()

	""" creates a synthesis """
	try:
		S=aa.Synthesis(filepath)
	except RuntimeError:
		print "Input Error: check file names\n"
		sys.exit()

	""" creates a std tape """
	T=aa.Stdtape(stdtapedir+stdfile)

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
		plot_synth(S,F,
					var=f,
					windb=args.windv,
					panel=args.panel,
					slicem = args.slicem,
					slicez = args.slicez,
					zoomIn=args.zoomin,
					mask = args.mask)
	
	# plt.show(block=False)	
	plt.show()

def plot_synth(S , F, **kwargs):

	"""creates synthesis plot instance """
	P=ap.SynthPlot()

	"""set variables """
	P.var = kwargs['var']
	P.windb = kwargs['windb']
	P.panel = kwargs['panel']
	P.zoomOpt = kwargs['zoomIn']
	P.mask = kwargs['mask']

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
	array=getattr(S , P.var)		

	""" set common variables """
	P.axesval['x']=S.X
	P.axesval['y']=S.Y
	P.axesval['z']=S.Z
	P.u_array=S.U
	P.v_array=S.V
	P.w_array=S.WVA
	# P.w_array=S.WUP

	""" general  geographic domain boundaries """
	P.set_geographic(S)

	""" flight path from standard tape """
	P.set_flight_level(F)

	""" coast line """
	P.set_coastline()

	""" make horizontal plane plot """
	P.horizontal_plane(field=array)
	
	""" make vertical plane plots """		
	if P.slicem:
		if P.var == 'SPH' :
			P.vertical_plane_velocity(	fieldM=S.SPM, # meridional component
										fieldZ=S.SPZ,
										sliceo='meridional') # zonal component)
		else:
			P.vertical_plane(field=array,sliceo='meridional')	

	if P.slicez:
		if P.var == 'SPH' :
			P.vertical_plane_velocity(	fieldM=S.SPM, # meridional component
										fieldZ=S.SPZ,
										sliceo='zonal') # zonal component)
		else:
			P.vertical_plane(field=array,sliceo='zonal')	

	# if P.dtm:
	# 	P.dtm_with_flightpath()
		

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
