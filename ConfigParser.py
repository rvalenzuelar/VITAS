#
# Function for parsing vitas.config file
#
# Raul Valenzuela
# July, 2015


from os.path import expanduser,isfile,isdir
import ast
import sys

def start():
	f = open("vitas.config")
	input_config = f.readlines()
	f.close()

	config={}
	for line in input_config:
		key, value = line.split("=")
		if not value:
			print "Please set the value of: "+key
		else:
			config[key.strip()] = ast.literal_eval(value.strip())

	synthpath=config['folder_synthesis']
	stdpath=config['folder_flight_level']
	dtmfile=config['filepath_dtm']

	if synthpath == '.':
		synthpath = getcwd()

	if stdpath == '.':
		stdpath = getcwd()

	home = expanduser("~")

	synthpath=synthpath.replace('~',home)
	stdpath=stdpath.replace('~',home)
	dtmfile=dtmfile.replace('~',home)

	if not isdir(synthpath):
		print "Please check input folder_synthesis"
		sys.exit()

	if not isdir(stdpath):
		print "Please check input folder_flight_level"
		sys.exit()

	if not isfile(dtmfile):
		print "Please check input filepath_dtm"
		sys.exit()


	config['folder_synthesis']=synthpath
	config['folder_flight_level']=stdpath
	config['filepath_dtm']=dtmfile


	return config

