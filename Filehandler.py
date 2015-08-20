#
# Function for handling folders and files
#
# Raul Valenzuela
# July 2015


import Terrain as TR
import AircraftAnalysis as AA 
import sys

def set_working_files(**kwargs):

	""" Set working folders/files and
		retrieves object instances
	"""
	cedfile=None
	stdfile=None
	config=None

	for key,value in kwargs.iteritems():
		if key == 'cedfile':
			cedfile=value
		elif key == 'stdfile':
			stdfile=value
		elif key == 'config':
			config=value

	if cedfile and stdfile and config:
		synthpath=config['folder_synthesis']
		stdpath=config['folder_flight_level']
		dtmfile=config['filepath_dtm']

		synthfile = synthpath+'/'+cedfile
		flightfile = stdpath+'/'+stdfile

		""" creates a synthesis instance """
		try:
			SYNTH=AA.Synthesis(synthfile)		
			SYNTH.set_fields(config)
			SYNTH.set_axes(config)
			SYNTH.set_time()
		except RuntimeError:
			print "Input Synth Error: check path or file name\n"
			sys.exit()

		""" creates a std tape instance """
		try:
			FLIGHT=AA.Flight(flightfile)
		except RuntimeError:
			print "Input Flight Error: check path or file name\n"
			sys.exit()

		""" creates terrain instance """
		try:
			TERRAIN=TR.Terrain(dtmfile)
		except RuntimeError:
			print "Input Flight Error: check path or file name\n"
			sys.exit()	

		return SYNTH,FLIGHT,TERRAIN

	elif config:
		return config['folder_synthesis']
	else:
		print "Error in Filehandler.py"
		sys.exit()

