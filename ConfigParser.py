#
# Function for parsing vitas.config file
#
# Raul Valenzuela
# July, 2015


import ast

def start():
	f = open("vitas.config")
	input_config = f.readlines()
	config={}
	for line in input_config:
		key, value = line.split("=")
		config[key.strip()] = ast.literal_eval(value.strip())

	f.close()

	a= config['folder_synthesis']
	b= config['folder_flight_level']
	c= config['zoom_center']

	print a
	print b
	print c['onshore']