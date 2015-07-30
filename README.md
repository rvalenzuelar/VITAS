# VITAS
VIsualization Tool for Aircraft Synthesis
--------------------------------------------

`VITAS` is aimed to create plots that support the analysis
of dual-Doppler radar synthesis derived from airborne platforms. The code is being developed and therefore is changing constantly. 

The current version is a python script working as command line tool. Hopefully, in 
the future the code will become an installable python module. Also, it is limited to ingest a CEDRIC netCDF synthesis and flight level data in RAF netCDF format. 

Installation
----------------

Copy the repository to your local computer (for example to your home folder). Then, within the `VITAS` folder call `./vitas.py` with the options described in the help menu.

There are several python modules that are required:

- Basemap
- gdal
- matplotlib
- numpy
- netCDF4
- geographiclib
- pandas
- scipy

Installation of [miniconda](http://conda.pydata.org/miniconda.html) (python package manager) is highly recommended. Once miniconda is installed, modules can be installed by using:

```code
$ conda install [name of the module]
```

Modules that are not located in the conda database can be installed with binstar.

`VITAS` is being developed in a Linux (Ubuntu and RedHat 6) environment so Windows/OSX tests are necessary.


Help Menu
-----------------

Help about how to use the script can be obtained by:

```code
$./vitas.py -h
```
which prints
```code
usage: vitas.py [--help] [--ced file] [--std file] [--panel num]
                         [--zoomin str] [--wind] [--mask]
                         [--all | --field STR [STR ...]] [--print_shapes]
                         [--print_global_atts] [--print_axis STR [STR ...]]
                         [--slicez lat float) [lat (float) ...]]
                         [--slicem lon (float) [lon (float ...]] [--terrain]
                         [--slope] [--meteo]
                         [--valid level (int) [level (int ...]]

Help:
  --help, -h            shows this help message and exit

Input files:
  --ced file, -c file   netCDF CEDRIC synthesis with format CaseName/LegName.
                        Example: c03/leg01.cdf
  --std file, -s file   netCDF NOAA-P3 standard tape file using RAF format.
                        Example: 010123I.nc

Plot options:
  --panel num, -p num   choose a panel (1-6); otherwise plots a figure with 6 panles
  --zoomin str, -z str  zoom-in over a offshore|onshore flight leg
  --wind, -w            include wind vectors
  --mask, -m            mask pixels with NaN vertical velocity 
  --all, -a             [default] plot all fields (DBZ,SPD,CON,VOR)
  --field STR [STR ...], -f STR [STR ...]
                        specify radar field(s) to be plotted

Print options:
  --print_shapes        print field variables and arrays with their shapes and exit
  --print_global_atts   print CEDRIC file global attributes and exit
  --print_axis STR [STR ...], -pa STR [STR ...]
                         print axis values (X,Y,Z)

Slice options:
  --slicez lat (float) [lat (float) ...], -slz lat (float) [lat (float) ...]
                        latitude coordinates for zonal slices
  --slicem lon (float) [lon (float) ...], -slm lon (float) [lon (float) ...]
                        longitude coordinates for zonal slices

Terrain options:
  --terrain             plot a terrain map
  --slope               plot a slope map

Flight level options:
  --meteo               plot meteo data from flight level

Validation options:
  --valid level (int) [level (int) ...], -v level (int) [level (int) ...]
                        plot validation info for a given level between 0 and max num 
                        of vertical levels

```
Config file
--------

A configuration file named `vitas.config` has to be created in the `VITAS` folder. This file is meant to personalize VITAS and contains the following parameters that are read by VITAS :

```code
folder_synthesis='~/folder_1/folder_2/.../folder_n'
folder_flight_level='~/folder_1/folder_2/.../folder_n'
filepath_dtm ='~/folder_1/folder_2/.../folder_n/DTMfile.tif'
figure_size={'single':(8,8),'multi':(8,12),'vertical':(12,10)}
zoom_center={'offshore':(38.6,-123.5),'onshore':(38.85,-123.25)}
zoom_del={'x':1.2,'y':1.1}
coast_line_color='black'
coast_line_width=4
coast_line_style='--'
flight_line_color=(0,0,0)
flight_line_width=1
flight_line_style='none'
flight_dot_on=False
flight_dot_color='red'
flight_dot_size=15
terrain_contours=[200,600,1000]
terrain_contours_color=[(0,0,0),(0.4,0.4,0.4),(0.6,0.6,0.6)]
terrain_profile_facecolor='none'
terrain_profile_edgecolor=(0,0,0)
wind_vector_vertical_component='WVA'
wind_vector_jump={'x':2,'y':2,'z':1}
wind_vector_color='white'
wind_vector_edgecolor='black'
wind_vector_linewidth=1
wind_vector_magnitude=10 # [m/s]
wind_vector_scale=0.5
section_slice_line_color=(0,0,0.5)
section_slice_line_width=2
section_slice_line_style='--'
synthesis_field_name={'DBZ':'MAXDZ', 'U':'F2U','V':'F2V','WVA':'WVARF2','WUP':'WUPF2','VOR':'VORT2','CON':'CONM2'}
synthesis_field_cmap_name={'DBZ':'gist_ncar', 'U':'RdBu_r', 'V':'RdBu_r', 'WVA':'RdBu_r', 'WUP':'PRGn', 'VOR':'PuOr', 'CON':'RdBu_r', 'SPD':'Accent'}
synthesis_field_cmap_range={'DBZ':[0,45],   'U':[-8,8],   'V':[-15,15], 'WVA':[-2,2],   'WUP':[-2,2], 'VOR':[-1,1], 'CON':[-1,1],   'SPD':[0,20]}
synthesis_grid_name={'X':'x','Y':'y','Z':'z'}
synthesis_horizontal_gridmajor_on=False
synthesis_horizontal_gridminor_on=False
synthesis_vertical_gridmajor_on=False
synthesis_vertical_gridminor_on=False
```
Each variable contains a valid python object (string, integer, tuple, list, or dictionary) that agrees with the input argument of the [matplotlib](http://matplotlib.org) object being modified. For example:

```code
flight_line_color='red'
```
or 
```code
flight_line_color=(0.3, 0.1, 0.4)
```
are both valid, but:

```code
flight_line_color=2
```

is not.


Examples
--------

Calling a single panel of DBZ with wind vectors and offshore zoom in (defined within the code):

```code
$ ./vitas.py -c c03/leg01.cdf -s 010123I.nc -f DBZ -p 1 --wind -z offshore
```
![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example1.png)

Adding the option `--meteo` produces the following additional plot:

![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example2.png)

Changing the panel number gives different altitudes of analyses. With no panel option `-p`, VITAS plots six default panels:

```code
$ ./vitas.py -c c03/leg01.cdf -s 010123I.nc -f DBZ --wind -z offshore
```
![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example3.png)

