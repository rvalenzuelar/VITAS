#
# Function for parsing vitas.config file
#
# Raul Valenzuela
# July, 2015

def start():
	f = open("vitas.config")
	data = f.readlines()
	for line in data:
	# parse input, assign values to variables
	key, value = line.split(":")
	player[key.strip()] = value.strip()
	f.close()