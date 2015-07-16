#
# Function for handling folders and files
#
# Raul Valenzuela
# July 2015


import Terrain as tr
import AircraftAnalysis as AA 
import sys

def set_working_files(**kwargs):

	""" Set working folders/files and
		retrieves object instances
	"""

	cedfile=kwargs['cedfile']
	stdfile=kwargs['stdfile']
	config=kwargs['config']

	synthpath=config['folder_synthesis']
	stdpath=config['folder_flight_level']
	dtmfile=config['filepath_dtm']

	synthfile = synthpath+'/'+cedfile
	flightfile = stdpath+'/'+stdfile

	""" creates a synthesis object """
	try:
		SY=AA.Synthesis(synthfile)		
		SY.set_fields(config)
		SY.set_axes(config)
		SY.set_time()
	except RuntimeError:
		print "Input Synth Error: check path or file name\n"
		sys.exit()

	""" creates a std tape object """
	try:
		ST=AA.Stdtape(flightfile)
	except RuntimeError:
		print "Input Flight Error: check path or file name\n"
		sys.exit()

	""" creates terrain object """
	try:
		TR=tr.Terrain(dtmfile)
	except RuntimeError:
		print "Input Flight Error: check path or file name\n"
		sys.exit()	

	return SY,ST,TR
