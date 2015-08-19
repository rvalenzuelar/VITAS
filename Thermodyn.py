"""
	Thermodynamic functions

	Raul Valenzuela
	July, 2015
"""

import numpy as np

class meteo(object):

	def __init__(self,**kwargs):

		for key,value in kwargs.iteritems():
			
			if isinstance(value,list) or isinstance(value,int):
				value=np.asarray(value)
			if key == 'T':
				self.T = value
			elif key == 'Tk':
				self.Tk = value
			elif key == 'Dewp':
				self.Dewp = value			
			elif key == 'theta':
				self.theta = value
			elif key == 'mixing_ratio':
				self.mixing_ratio = value
			elif key == 'mb' or key == 'hPa':
				self.pressure = value
			elif key == 'bar':
				self.pressure = value /1000
			elif key == 'Pa':
				self.pressure = value/100

def parse_args(**kwargs):

	return meteo(**kwargs)
	

def relative_humidity(**kwargs):
	""" 	relative_humidity = f(T,Dewp)
		Lawrence, 2005, BAMS
	"""
	meteo=parse_args(**kwargs)	
	try:
		relh = np.asarray(100-5*(meteo.T- meteo.Dewp)) #[%]
		relh[relh>100.0] = 100.0
		return relh	
	except AttributeError:
		print 'Make sure using T instead of Tk'

def theta(**kwargs):
	""" theta = f(T,pressure)
	"""
	p0 = 1000.0 # [hPa]
	c = 0.286
	meteo=parse_args(**kwargs)	
	check_T=hasattr(meteo,'T')
	check_Tk=hasattr(meteo,'Tk')
	quotient=np.divide(p0,meteo.pressure)
	if check_Tk:
		theta = meteo.Tk*np.power(quotient,c) # [K]
		return theta
	elif check_T:
		Tk=meteo.T+273.15
		theta = Tk*np.power(quotient,c) # [K]
		return theta
	else:
		print "Error: check input arguments\n"

def thetav(**kwargs):
	""" thetav = f(T,pressure,mixing_ratio)
	"""
	meteo=parse_args(**kwargs)	
	check_T=hasattr(meteo,'T')
	check_Tk=hasattr(meteo,'Tk')
	check_mixingr=hasattr(meteo,'mixing_ratio')
	check_pressure=hasattr(meteo,'pressure')
	if  check_T and check_pressure and check_mixingr:
		t = theta(T=meteo.T,hPa=meteo.pressure)
		thetav = t*(1+0.61*meteo.mixing_ratio)
		return thetav
	elif check_Tk and check_pressure and check_mixingr:
		t = theta(Tk=meteo.Tk,hPa=meteo.pressure)
		thetav = t*(1+0.61*meteo.mixing_ratio)
		return thetav
	else:
		print "Error: check input arguments\n"
