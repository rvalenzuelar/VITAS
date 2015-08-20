# -*- coding: utf-8 -*-
"""
	Thermodynamic functions

	Raul Valenzuela
	July, 2015
"""

import numpy as np
from numpy.polynomial.polynomial import polyval

class meteo(object):
	def __init__(self,**kwargs):
		for key,value in kwargs.iteritems():
			if isinstance(value,list) or isinstance(value,int):
				value=np.asarray(value)
			if key == 'C':
				self.C = value # [°C]
			elif key == 'K':
				self.K = value # [K]
			elif key == 'theta':
				self.theta = value # [K]			
			elif key == 'Dewp':
				self.Dewp = value	# [°C]
			elif key == 'mixing_ratio':
				self.mixing_ratio = value # [kg/kg]
			elif key == 'mb' or key == 'hPa':
				self.pressure = value # [mb] or [hPa]
			elif key == 'bar':
				self.pressure = value /1000 # [mb]
			elif key == 'Pa':
				self.pressure = value/100 # [hPa]

def parse_args(**kwargs):

	return meteo(**kwargs)

def sat_wv_press(**kwargs):
	"""  sat water vapor pressure = f(T) [mb]
		valid for liquid water and -50°C<T<50°C
		error within 1%
		Lowe, 1977, JAM
	"""
	meteo=parse_args(**kwargs)	
	check_C=hasattr(meteo,'C')
	check_K=hasattr(meteo,'K')
	if check_C:
		coef=[	6.107799961,
				4.436518521E-1,
				1.428945805E-2,
				2.650648471E-4,
				3.031240396E-6,
				2.034080948E-8,
				6.136820929E-11]
		return polyval(meteo.C,coef)				
	elif check_K:
		coef =[	6984.505294,
				-188.9039310,
				2.133357675,
				-1.288580973E-2,
				4.393587233E-5,
				-8.023923082E-8,
				6.136820929E-11]
		return polyval(meteo.K,coef)
	else:
		print "Error: check input arguments\n"

def sat_mix_ratio(**kwargs):
	"""  sat mixing ratio = f(T,pressure) [kg/kg]
		Saucier, 1989, p.11
		Bohren and Albrecht, 1998, p.186
	"""
	meteo=parse_args(**kwargs)	
	check_C=hasattr(meteo,'C')
	check_p=hasattr(meteo,'pressure')	
	if check_C and check_p:
		es = sat_wv_press(C=meteo.C)
		p=meteo.pressure 
		return (0.622*es)/(p - es ) # [kg/kg]
	else:
		print "Error: check input arguments\n"

def relative_humidity(**kwargs):
	""" 	relative_humidity = f(T,Dewp) 
		Lawrence, 2005, BAMS
	"""
	meteo=parse_args(**kwargs)	
	try:
		relh = np.asarray(100-5*(meteo.C- meteo.Dewp)) #[%]
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
	check_C=hasattr(meteo,'C')
	check_K=hasattr(meteo,'K')
	quotient=np.divide(p0,meteo.pressure)
	if check_K:
		return meteo.K*np.power(quotient,c) # [K]
	elif check_C:
		Tk=meteo.C+273.15
		return Tk*np.power(quotient,c) # [K]
	else:
		print "Error: check input arguments\n"

def virtual_temp(**kwargs):
	"""  Tv = f(C, mixing_ratio) [°C]
		Tv = f(K, mixing_ratio) [K]
		Thetav = f(theta, mixing_ratio) [K]
		Saucier, 1989, p.12
	"""
	meteo=parse_args(**kwargs)	
	check_C=hasattr(meteo,'C')
	check_K=hasattr(meteo,'K')
	check_theta=hasattr(meteo,'theta')
	check_mixingr=hasattr(meteo,'mixing_ratio')
	if  check_C and check_mixingr:
		return meteo.C*(1+0.61*meteo.mixing_ratio)
	elif check_K and check_mixingr:
		return meteo.K*(1+0.61*meteo.mixing_ratio)
	elif check_theta and check_mixingr:
		return meteo.theta*(1+0.61*meteo.mixing_ratio)
	else:
		print "Error: check input arguments\n"
