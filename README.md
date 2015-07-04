# VITAS
VIsualization Tool for Aircraft Synthesis
--------------------------------------------

VITAS is build to create plots that support the analysis
of dual-Doppler radar synthesis derived from airborne platforms. The code is being developed and therefore is changing constantly. 

The current version is limited to a python script. Hopefully, in 
the future the code will become an installable python module. Also, it is limited to ingest a CEDRIC netCDF synthesis and flight level data in RAF netCDF format. 

Help about how to use the script can be obtained by:

```code
$./plot_synth2.py -h
```
which prints
```code
usage: plot_synth2.py [--help] [--ced file] [--std file] [--panel num]
                      [--zoomin str] [--windv] [--mask]
                      [--all | --field STR [STR ...]] [--print_shapes]
                      [--print_global_atts] [--print_axis STR [STR ...]]
                      [--set_working_directory | --get_working_directory]
                      [--slicez lat float) [lat (float) ...]]
                      [--slicem lon (float) [lon (float ...]]

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
  --windv, -w           include wind vectors
  --mask, -m            mask pixels with NaN vertical velocity 
  --all, -a             [default] plot all fields (DBZ,SPD,CON,VOR)
  --field STR [STR ...], -f STR [STR ...]
                        specify radar field(s) to be plotted

Print options:
  --print_shapes        print field variables and arrays with their shapes and exit
  --print_global_atts   print CEDRIC file global attributes and exit
  --print_axis STR [STR ...], -pa STR [STR ...]
                         print axis values (X,Y,Z)

Working directory:
  --set_working_directory, -swd
                        set working directories
  --get_working_directory, -gwd
                        get working directories

Slice options:
  --slicez lat (float) [lat (float) ...], -slz lat (float) [lat (float) ...]
                        latitude coordinates for zonal slices
  --slicem lon (float) [lon (float) ...], -slm lon (float) [lon (float) ...]
                        longitude coordinates for zonal slices
```

Modules required:

- basemap
- gdal
- matplotlib
- numpy
- netCDF4
- geographiclib
- pandas
- scipy

The script is being developed in a Linux (Ubuntu and RedHat 6) environment so Windows/OSX tests are necessary.

Installation of [miniconda](1) (python package manager) is highly recommended.

[1]:http://conda.pydata.org/miniconda.html
