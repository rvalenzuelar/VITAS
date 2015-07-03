#
# Function plotter
#
# Raul Valenzuela
# July 2015

from os import getcwd
from os.path import dirname, basename, expanduser
import sys
import tempfile
import AircraftPlot as ap
import AircraftAnalysis as aa 



def set_working_files(**kwargs):

	cedfile=kwargs['cedfile']
	stdfile=kwargs['stdfile']

	home = expanduser("~")

	"""base directory """
	# basedirectory = home+"/P3_v2/synth_test/"
	# stdtapedir = home+"/Github/correct_dorade_metadata/"
	basedirectory = home+"/P3/synth/"
	stdtapedir = home+"/Github/correct_dorade_metadata/"

	"""input folder """
	mypath=dirname(cedfile)
	myfile=basename(cedfile)

	
	if mypath ==".":
		mypath=getcwd()
		cedfile=mypath+cedfile
	else:
		mypath=basedirectory
		cedfile=mypath+cedfile

	if not myfile:
		print "Please include filename in path"
		sys.exit()

	""" creates a synthesis """
	print cedfile
	try:
		S=aa.Synthesis(cedfile)
	except RuntimeError:
		print "Input Error: check file names\n"
		sys.exit()

	""" creates a std tape """
	T=aa.Stdtape(stdtapedir+stdfile)

	return S,T


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