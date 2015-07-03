#
# Function plotter
#
# Raul Valenzuela
# July 2015

from os import getcwd
from os.path import dirname,basename,expanduser,isfile,isdir
import sys
import tempfile
import AircraftPlot as ap
import AircraftAnalysis as aa 


def print_set_working_msg(tmpfile):

	print 'Please set working directories\n'
	synthpath = raw_input("Enter synthesis path: ")
	stdpath = raw_input("Enter stdtape path: ")

	if synthpath == '.':
		synthpath = getcwd()

	if stdpath == '.':
		stdpath = getcwd()

	home = expanduser("~")
	synthpath=synthpath.replace('~',home)
	stdpath=stdpath.replace('~',home)

	if isdir(synthpath) and isdir(stdpath):
		f = open(tmpfile,'w')
		f.write(synthpath+'\n')
		f.write(stdpath)
		f.close()
	else:
		print '\nPlease try again\n'
		sys.exit()

def set_working_files(**kwargs):

	cedfile=kwargs['cedfile']
	stdfile=kwargs['stdfile']
	swd=kwargs['swd']

	tmp='vitas_swd.tmp'
	tmpfile=tempfile.gettempdir()+'/'+tmp

	if not isfile(tmpfile) or swd:
		print_set_working_msg(tmpfile=tmpfile)

	with open(tmpfile, 'r') as f:
		synthpath = f.readline().rstrip('\n')
		stdpath = f.readline().rstrip('\n')
	
	synthfile = synthpath+'/'+cedfile
	flightfile = stdpath+'/'+stdfile


	""" creates a synthesis """
	try:
		S=aa.Synthesis(synthfile)
	except RuntimeError:
		print "Input Synth Error: check path or file name\n"
		sys.exit()

	""" creates a std tape """
	try:
		T=aa.Stdtape(flightfile)
	except RuntimeError:
		print "Input Flight Error: check path or file name\n"
		sys.exit()

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