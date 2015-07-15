# VITAS
VIsualization Tool for Aircraft Synthesis
--------------------------------------------

VITAS is build to create plots that support the analysis
of dual-Doppler radar synthesis derived from airborne platforms. The code is being developed and therefore is changing constantly. 

The current version is a python script working as command line tool. Hopefully, in 
the future the code will become an installable python module. Also, it is limited to ingest a CEDRIC netCDF synthesis and flight level data in RAF netCDF format. 

Installation
----------------

Copy the repository to your local computer (for example to your home folder). Then, within the vitas folder call `./start_plotting` with the options described in the help menu.

There are several python modules that are required:

- Basemap
- gdal
- matplotlib
- numpy
- netCDF4
- geographiclib
- pandas
- scipy

Installation of [miniconda](1) (python package manager) is highly recommended. Once miniconda is installed, modules can be installed by using:

```code
$ conda install [name of the module]
```

Modules that are not located in the conda database can be installed with binstar.

VITAS is being developed in a Linux (Ubuntu and RedHat 6) environment so Windows/OSX tests are necessary.


Help Menu
-----------------

Help about how to use the script can be obtained by:

```code
$./start_plotting.py -h
```
which prints
```code
usage: start_plotting.py [--help] [--ced file] [--std file] [--panel num]
                         [--zoomin str] [--wind] [--mask]
                         [--all | --field STR [STR ...]] [--print_shapes]
                         [--print_global_atts] [--print_axis STR [STR ...]]
                         [--slicez lat float) [lat (float) ...]]
                         [--slicem lon (float) [lon (float ...]] [--terrain]
                         [--slope] [--meteo]

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

```
Config file
--------

A configuration file named `vitas.config` has to be created in the VITAS folder. This file contains the following parameters that are read by VITAS :

```code
folder_synthesis='~/P3_v2/synth_test'
folder_flight_level='~/Github/correct_dorade_metadata'
filepath_dtm ='~/Github/RadarQC/merged_dem_38-39_123-124_extended.tif'
zoom_center={'offshore':(38.6,-123.5),'onshore':(38.85,-123.25)}
zoom_del={'x':1.2,'y':1.1}
coast_line_color='blue'
flight_line_color='blue'
terrain_contours=[200,600,1000]
terrain_contours_color=[(0,0,0),(0.4,0.4,0.4),(0.6,0.6,0.6)]
synthesis_field_name={'DBZ':'MAXDZ','U':'F2U','V':'F2V','WVA':'WVARF2','WUP':'WUPF2','VOR':'VORT2','CON':'CONM2'}
synthesis_field_cmap={'DBZ':'nipy_spectral','U':'Accent','V':'Accent','WVA':'PRGn','WUP':'PRGn','VOR':'PuOr','CON':'RdBu_r'}
synthesis_field_cmap_range={'DBZ':[-15,45],'U':[-20,20],'V':[-10,30],'WVA':[-2,2],'WUP':[-2,2],'VOR':[-1,1],'CON':[-1,1]}
synthesis_grid_name={'X':'x','Y':'y','Z':'z'}
wind_vector_jump_horizontal={'x':2,'y':2}
wind_vector_jump_vertical={'x':2,'y':1}
figure_size={'single':(8,8),'multi':(8,12),'vertical':(12,10)}
```


Examples
--------

Calling a single panel of DBZ with wind vectors and offshore zoom in (defined within the code):

```code
$ ./start_plotting.py -c c03/leg01.cdf -s 010123I.nc -f DBZ -p 1 --wind -z offshore
```
![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example1.png)

Adding the option `--meteo` produces the following additional plot:

![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example2.png)

Changing the panel number gives different altitudes of analyses. With no panel option `-p`, VITAS plots six default panels:

```code
$ ./start_plotting.py -c c03/leg01.cdf -s 010123I.nc -f DBZ --wind -z offshore
```
![alt tag](https://github.com/rvalenzuelar/vitas/blob/master/figure_example3.png)


[1]:http://conda.pydata.org/miniconda.html
