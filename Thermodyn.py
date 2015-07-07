#
# Thermodynamic functions
#
# Raul Valenzuela
# July, 2015


def relative_humidity(T,Td):

	""" Lawrence, 2005, BAMS"""

	relh=100-5*(T-Td)
	relh[relh>100.0]=100.0

	return relh
