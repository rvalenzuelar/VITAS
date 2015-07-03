#
# Function for handling folders and files
#
# Raul Valenzuela
# July 2015


from os.path import dirname,basename,expanduser,isfile,isdir
import Terrain as tr
import AircraftAnalysis as aa 
import tempfile 


def print_set_working_msg(tmpfile):

	print 'Please set working directories\n'
	synthpath = raw_input("Enter synthesis path: ")
	stdpath = raw_input("Enter stdtape path: ")
	dtmfile = raw_input("Enter DTM path including file: ")

	if synthpath == '.':
		synthpath = getcwd()

	if stdpath == '.':
		stdpath = getcwd()

	home = expanduser("~")
	synthpath=synthpath.replace('~',home)
	stdpath=stdpath.replace('~',home)
	dtmfile=dtmfile.replace('~',home)

	if isdir(synthpath) and isdir(stdpath) and isfile(dtmfile):
		f = open(tmpfile,'w')
		f.write(synthpath+'\n')
		f.write(stdpath+'\n')
		f.write(dtmfile)
		f.close()
	else:
		print '\nPlease try again\n'
		sys.exit()

def set_working_files(**kwargs):

	""" Set working folders/files and
		retrieves object instances
	"""

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
		dtmfile = f.readline().rstrip('\n')
	
	synthfile = synthpath+'/'+cedfile
	flightfile = stdpath+'/'+stdfile

	""" creates a synthesis object """
	try:
		SY=aa.Synthesis(synthfile)
	except RuntimeError:
		print "Input Synth Error: check path or file name\n"
		sys.exit()

	""" creates a std tape object """
	try:
		ST=aa.Stdtape(flightfile)
	except RuntimeError:
		print "Input Flight Error: check path or file name\n"
		sys.exit()

	""" creates terrain object """
	try:
		print dtmfile
		TR=tr.Terrain(dtmfile)
	except RuntimeError:
		print "Input Flight Error: check path or file name\n"
		sys.exit()	

	return SY,ST,TR

def get_working_files():

	tmp='vitas_swd.tmp'
	tmpfile=tempfile.gettempdir()+'/'+tmp

	if not isfile(tmpfile) or swd:
		print_set_working_msg(tmpfile=tmpfile)

	with open(tmpfile, 'r') as f:
		synthpath = f.readline().rstrip('\n')
		stdpath = f.readline().rstrip('\n')
		dtmfile = f.readline().rstrip('\n')	

	print "Synthesis path: "+synthpath
	print "Flight path: "+stdpath
	print "DTM file: "+dtmfile