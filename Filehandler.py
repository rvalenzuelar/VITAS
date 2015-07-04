#
# Function for handling folders and files
#
# Raul Valenzuela
# July 2015


from os.path import dirname,basename,expanduser,isfile,isdir
import Terrain as tr
import AircraftAnalysis as aa 
import tempfile 
import sys


pr1="Enter synthesis path: "
pr2="Enter stdtape path: "
pr3="Enter DTM path including file: "

def print_set_working_msg(tmpfile):

	print 'Please enter working directories\n'
	synthpath = raw_input(pr1)
	stdpath = raw_input(pr2)
	dtmfile = raw_input(pr3)

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
		print '\nSome of the input information seems wrong.'
		print 'Please try again\n'
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

	if not isfile(tmpfile):
		print_set_msg(tmpfile=tmpfile)
	
	with open(tmpfile, 'r') as f:
		synthpath = f.readline().rstrip('\n')
		stdpath = f.readline().rstrip('\n')
		dtmfile = f.readline().rstrip('\n')

	if swd:		
		synthpath=input_with_prefill(pr1,synthpath)
		stdpath=input_with_prefill(pr2,stdpath)
		dtmfile=input_with_prefill(pr3,dtmfile)
	
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

def get_working_directory():

	tmp='vitas_swd.tmp'
	tmpfile=tempfile.gettempdir()+'/'+tmp

	if not isfile(tmpfile):
		print "\nDirectories have not been set."
		print "Use --set_working_directories or -swd option "
		sys.exit()

	with open(tmpfile, 'r') as f:
		synthpath = f.readline().rstrip('\n')
		stdpath = f.readline().rstrip('\n')
		dtmfile = f.readline().rstrip('\n')	

	print "Synthesis path: "+synthpath
	print "Stdtape path: "+stdpath
	print "DTM file: "+dtmfile
	print ""

def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = raw_input(prompt)
    readline.set_pre_input_hook()
    return result	