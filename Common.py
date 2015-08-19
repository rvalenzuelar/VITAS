
'''
***************************************
	Common functions used
	by Radardata.py and Flightdata.py

	Raul Valenzuela
	August, 2015
*************************************** 
'''

import numpy as np
import matplotlib.pyplot as plt

from geographiclib.geodesic import Geodesic
from collections import Sequence


def find_index_recursively(**kwargs):

	''' array and value have to have
			the same number of decimals
			positions
	'''
	array=kwargs['array']
	value=kwargs['value']
	decimals=kwargs['decimals'] #decimals of each element

	idx= np.where(array == value)
	array_new=array
	value_new=value
	while len(idx[0])==0:

		decimals-=1
		if decimals <0:
			return None
		array_new = np.asarray(around(array_new,decimals))
		value_new = round(value_new,decimals)
		idx= np.where(array_new == value_new)
	
	if len(idx[0])>1:
		idxx=find_nearest(array[idx[0]],value)
		return idx[0][idxx]
	else:
		return idx[0][0]
							 						
def around(array,decimals):

	rounded=[]
	for val in array:
		rounded.append(round(val,decimals))
	return rounded

def find_nearest(array,value):

	idx = (np.abs(array-value)).argmin()
	return idx

def find_nearest2(array,targetArray):

	""" See stackoverflow answer from Bi Rico """

	''' array must be sorted '''
	idx = array.searchsorted(targetArray)
	idx = np.clip(idx, 1, len(array)-1)
	left = array[idx-1]
	right = array[idx]
	idx -= targetArray - left < right - targetArray
	return idx

def chop_horizontal(self, array):

	zvalues=self.axesval['z']

	''' set  vertical level in a list of arrays '''
	if self.panel:
		choped_array = [array[:,:,self.panel[0]] for i in range(6)]
		self.zlevels = [zvalues[self.panel[0]] for i in range(6)]	
	else:
		choped_array = [array[:,:,i+1] for i in range(6)]
		self.zlevels = [zvalues[i+1] for i in range(6)]
		
	return choped_array

def chop_vertical(self,array):

	array=np.squeeze(array)

	slices=[]
	if self.sliceo=='zonal':		
		for coord in self.slicez:
			idx=find_nearest(self.lats,coord)
			slices.append(array[:,idx,:])
	elif self.sliceo=='meridional':
		for coord in self.slicem:
			idx=find_nearest(self.lons,-coord)
			slices.append(array[idx,:,:])
	# elif self.sliceo=='cross':
	# elif self.sliceo=='along:

	return slices	

def resample(array,**kwargs):

	if len(kwargs)==1:
		array=array[::kwargs['res']]

	elif len(kwargs)==2:
		yjump=kwargs['yres']
		xjump=kwargs['xres']
		array= array[::yjump,::xjump]

	return array

def all_same(array):
	b= all(x == array[0] for x in array)

	return b

def zoom_in(synthplot,in_extent,center_point):

	y,x=center_point
	inext=in_extent
	outext=[None,None,None,None]
	delx=synthplot.zoomDelta['x'] #[deg]
	dely=synthplot.zoomDelta['y'] #[deg]

	if x<inext[0] or x>inext[1] or y<inext[2] or y>inext[3]:
		print "Zoom center point out of geographic extention boundaries"
		sys.exit()

	outext[0]=x-delx/2
	outext[1]=x+delx/2
	outext[2]=y-dely/2
	outext[3]=y+dely/2

	if outext[0]<inext[0]:outext[0]=inext[0]
	if outext[1]>inext[1]:outext[1]=inext[1]
	if outext[2]<inext[2]:outext[2]=inext[2]
	if outext[3]>inext[3]:outext[3]=inext[3]
		
	return outext	

def adjust_extent(self,ori_extent,orient,type_extent):

	out_extent=[None,None,None,None]
	if orient == 'meridional':
		out_extent[0]=ori_extent[2] *self.scale
		out_extent[1]=ori_extent[3] *self.scale
	elif orient == 'zonal':
		out_extent[0]=ori_extent[0] *self.scale
		out_extent[1]=ori_extent[1] *self.scale
		
	if type_extent=='data':
		zvalues=self.axesval['z']		
		out_extent[2]=min(zvalues)
		out_extent[3]=max(zvalues)
	elif type_extent=='detail':
		out_extent[2]=0.0
		out_extent[3]=5.0			
	
	return out_extent

def get_distance_along_flight_track(**kwargs):
	
	x=kwargs['lon']
	y=kwargs['lat']
	
	distance_from_p0=[0]
	first=True
	for lon,lat in zip(x,y):
		p1=[lat,lon]
		if first:
			p0=p1
			first=False
		else:
			value=Geodesic.WGS84.Inverse(p0[0], p0[1],p1[0], p1[1])
			distance_from_p0.append(value['s12']/1000) #[km]
			
	if kwargs['ticks_every']:
		frequency=kwargs['ticks_every'] #[km]
		endsearch=int(distance_from_p0[-1]) #[km]
		target=range(0,endsearch,frequency)
		search=np.asarray(distance_from_p0)
		idxs=find_nearest2(search,target)
		return [distance_from_p0,idxs]
	else:
		return distance_from_p0

def round_to_closest_int(value,base):

	if isinstance(value,Sequence):
		r=[]
		for v in value:
			if v%base < 1:
				r.append(int(v - v%base))
			else:
				r.append(int(v + (base - v%base)))
		return r
	else:
		if value%base < 1:
			r = value - value%base
		else:
			r = value + (base - value%base)
		return int(r)