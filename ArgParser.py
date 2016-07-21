#
# Function to handle argument parser and help 
# information
#
# Raul Valenzuela
# July 2015


import argparse
#import sys

def usage():

    desc="""
------------------------------------------------------------------------------    
Script for plotting NOAA-P3 Dual-Doppler analyses derived
from CEDRIC. 
------------------------------------------------------------------------------
"""
#    print desc

def coords(s):
    try:
        s = s.translate(None,'()')
        x, y, az, dist = map(float, s.split(','))
        return x, y, az, dist
    except:
        raise argparse.ArgumentTypeError("Coordinates must be (lat,lon,az,dist)")

def coords_prof(s):
    try:
        s = s.translate(None,'()')
        x, y = map(float, s.split(','))
        return x, y
    except:
        raise argparse.ArgumentTypeError("Coordinates must be (lat,lon)")


def start(params=None):

    parser = argparse.ArgumentParser(description=usage(),
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     add_help=False)

    help_option=parser.add_argument_group('Help')
    help_option.add_argument('--help', '-h',
                            action='help',
                            help='shows this help message and exit')

    """ Input files """
    group_input=parser.add_argument_group('Input files')
    group_input.add_argument('--ced','-c',
                            metavar='file',
                            required=False,
                            help=    "netCDF CEDRIC synthesis with format CaseName/LegName." \
                                    "\nExample: c03/leg01.cdf")
    group_input.add_argument('--std','-s' ,
                            metavar='file',
                            required=False,
                            help=    "netCDF NOAA-P3 standard tape file using RAF format." \
                                    "\nExample: 010123I.nc")
    group_input.add_argument('--print_list_synth',
                            action='store_true',
                            help="print list with synthesis availables")
    
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
                            help="zoom-in over an area specified in vitas.config zoom_center")    
    plot_options.add_argument('--wind', '-w',
                            action='store_true',
                            help="include wind vectors")    
    plot_options.add_argument('--mask','-m',
                            action='store_true',
                            help="mask pixels with NaN vertical velocity ")
    plot_options.add_argument('--multi','-ml',
                            action='store_true',
                            default=False,
                            help="disable plotting functions and return an array; used for processing multiple legs")        
    plot_options.add_argument('--no_plot','-np',
                            action='store_true',
                            default=False,
                            help="disable plotting profile")        


    """ Field Arguments """
    group_fields = plot_options.add_mutually_exclusive_group()
    group_fields.add_argument('--all', '-a',
                            action='store_true',
                            help="[default] plot all fields (DBZ,SPD,CON,VOR)")
    group_fields.add_argument('--field', '-f',
                            metavar='STR',
                            nargs='+',
                            choices=['DBZ','SPD','CON','VOR','U','V','WVA','WUP'],
                            default=None,
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
                            metavar='(float)',
                            type=float, 
                            nargs='+',
                            required=False,
                            help="latitude coordinates for zonal slices")
    slice_options.add_argument('--slicem', '-slm',
                            metavar='(float)',
                            type=float, 
                            nargs='+',
                            required=False,
                            help="longitude coordinates for meridional slices")
    slice_options.add_argument('--slice', '-sl',
                            metavar='(lat,lon,az,dist)',
                            type=coords, 
                            nargs=1,
                            required=False,
                            help=" initial coordinate, azimuth [degrees], and \
                                    distance [km] for cross section")

    """ Terrain options """
    terrain_options=parser.add_argument_group('Terrain options')
    terrain_options.add_argument('--terrain',
                            action='store_true',
                            help="plot a terrain map")
    terrain_options.add_argument('--slope',
                            action='store_true',
                            help="plot a slope map")

    """ Flight level options """
    flight_options=parser.add_argument_group('Flight level options')
    flight_options.add_argument('--meteo',
                            action='store_true',
                            help="plot meteo data from flight level")

    """ Validation options """
    flight_options=parser.add_argument_group('Validation options')
    flight_options.add_argument('--valid','-v',
                            metavar='level (int)',
                            type=int, 
                            nargs='+',
                            required=False,
                            help="plot validation info for a given level between 0 \
                                    and max num of vertical levels")
    flight_options.add_argument('--prof',
                            metavar='(lat,lon)',
                            type=coords_prof, 
                            nargs='+',
                            required=False,
                            help="plot wind profile at given coordinates")


#    sl = parser.parse_args().slice
#    az = parser.parse_args().azimuth
#    di = parser.parse_args().distance
#
#    if sl and not az and not di:
#        parser.error('--slice option needs --azimuth and --distance values\n')

    if params is None:
        return parser.parse_args()
    else:
        return parser.parse_args(params.split())