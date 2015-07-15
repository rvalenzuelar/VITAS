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
