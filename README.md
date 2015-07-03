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
which prints the following screen:

```code

```

Modules required:

- basemap
- gdal
- matplotlib
- numpy
- netCDF4
- geographiclib
- pandas

The script is being developed in a Linux (Ubuntu and RedHat 6) environment so Windows/OSX tests are necessary.

Installation of [miniconda](1) (python package manager) is highly recommended.

[1]:http://conda.pydata.org/miniconda.html
