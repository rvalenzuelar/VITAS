#
# Functions for digital terrain model
#
# Raul Valenzuela
# July 2015


from os.path import isfile
import tempfile
import os
import gdal
import numpy as np
import matplotlib.pyplot as plt

class Terrain(object):
	def __init__(self,filepath):
		if filepath:
			self.file=filepath
		else:
			self.file=None

		self.array=None

# def plot_level():

# def plot_profile():

def add_contour(axis,Plot):

	if not Plot.terrain.array:
		dtm=make_array(Plot.terrain.file,Plot)
		Plot.terrain.array=dtm
	else:
		dtm=Plot.terrain.array

	cont=axis.contour(dtm['xg'],dtm['yg'],dtm['data'],
					levels=[200,600],
					colors=( (0,0,0) , (0.4,0.4,0.4) ),
					linewidths=2)
	
	axis.clabel(cont,[200,600],fmt='%.0f',fontsize=12,inline_spacing=2)	

def plot_altitude_mask(axis,S,dtm):

	extent=S.get_extent()

	axis.figure()
	axis.plot(S.coast['lon'], S.coast['lat'], color='r')
	axis.plot(S.flight_lon, S.flight_lat,color='r')		
	axis.imshow(dtm['data'],
					interpolation='none',
					cmap='terrain_r',
					vmin=500,
					vmax=501,
					extent=dtm['extent'])
	axis.colorbar()
	axis.xlim(extent[0], extent[1])
	axis.ylim(extent[2], extent[3])				
	axis.draw()

def plot_slope_map(SynthPlot):

	extent=SynthPlot.get_extent()

	dem_file=tempfile.gettempdir()+'/terrain2.tmp'
	out_file=tempfile.gettempdir()+'/terrain3.tmp'
	input_param = (dem_file, out_file)
	run_gdal = 'gdaldem slope %s %s -p -s 111120' % input_param
	os.system(run_gdal)

	data=get_data(out_file)

	plt.figure()
	plt.plot(SynthPlot.coast['lon'], SynthPlot.coast['lat'], color='r')
	plt.plot(SynthPlot.flight_lon, SynthPlot.flight_lat,color='r')		
	plt.imshow(data['array'],
					interpolation='none',
					vmin=0,
					vmax=20,
					extent=data['extent'])
	plt.colorbar()	
	plt.xlim(extent[0], extent[1])
	plt.ylim(extent[2], extent[3])		
	plt.draw()

def plot_terrain_map(SynthPlot):

	extent=SynthPlot.get_extent()

	dem_file=tempfile.gettempdir()+'/terrain2.tmp'
	data=get_data(dem_file)

	plt.figure()
	plt.plot(SynthPlot.coast['lon'], SynthPlot.coast['lat'], color='r')
	plt.plot(SynthPlot.flight_lon, SynthPlot.flight_lat,color='r')		
	plt.imshow(data['array'],
					interpolation='none',
					vmin=0,
					vmax=600,
					cmap='terrain',
					extent=data['extent'])
	plt.colorbar()	
	plt.xlim(extent[0], extent[1])
	plt.ylim(extent[2], extent[3])		
	plt.draw()

def get_data(dtmfile):

	''' store dtm in data '''
	datafile = gdal.Open(dtmfile)
	geotransform=datafile.GetGeoTransform()
	cols=datafile.RasterXSize
	rows=datafile.RasterYSize
	band=datafile.GetRasterBand(1)		
	array=band.ReadAsArray(0,0,cols,rows)
	datafile=None

	''' geographic axes '''
	originX=geotransform[0]
	originY=geotransform[3]
	pixelW=geotransform[1]
	pixelH=geotransform[5]
	
	endingX=originX+cols*pixelW
	endingY=originY+rows*pixelH

	xg=np.linspace(originX,endingX,cols)
	yg=np.linspace(originY,endingY,rows)

	''' data extent '''
	ulx=min(xg)
	lrx=max(xg)
	lry=min(yg)
	uly=max(yg)

	''' return dictionary '''
	data={}
	data['array']=array
	data['extent']=[ulx,lrx,lry,uly]
	data['xg']=xg
	data['yg']=yg

	return data

def make_3d_mask(data,levels,res):

	rows=data['rows']
	cols=data['cols']
	array=data['array']

	''' creates 3D terrain mask array '''
	mask=np.zeros((rows,cols,levels))

	'''Loop through each pixel of DTM and 
	corresponding vertical column of mask'''
	for ij in np.ndindex(mask.shape[:2]):

		'''indices'''
		i,j=ij

		'''index of maximum vertical gate to
		filled with ones (e.g. presence of terrain);
		works like floor function; altitude of mask 
		is zlevel[n-1] for n>0'''
		n = int(np.ceil(array[i,j]/float(res)))

		''' fills verical levels '''
		mask[i,j,0:n] = 1

	return mask

def make_array(dem_file, Plot):

	temp_file=tempfile.gettempdir()+'/terrain1.tmp'
	out_file=tempfile.gettempdir()+'/terrain2.tmp'

	''' same boundaries as synthesis'''
	ulx = min(Plot.lons)
	uly = max(Plot.lats)		
	lrx = max(Plot.lons)
	lry = min(Plot.lats)

	''' number of verical gates '''
	zvalues=Plot.axesval['z']		
	levels=len(zvalues)

	''' vertical gate resolution'''
	res=(zvalues[1]-zvalues[0])*1000 # [m] 

	''' downsample DTM using synthesis axes '''
	xvalues=Plot.axesval['x']
	yvalues=Plot.axesval['y']
	resampx_to=len(xvalues)*1
	resampy_to=len(yvalues)*1

	if isfile(temp_file):
		os.remove(temp_file)

	if isfile(out_file):
		os.remove(out_file)

	''' shrink original dtm '''
	input_param = (ulx, uly, lrx, lry, dem_file, temp_file)
	run_gdal = 'gdal_translate -projwin %s %s %s %s %s %s' % input_param
	os.system(run_gdal)

	''' resample shrinked dtm '''
	input_param = (resampy_to,resampx_to,temp_file, out_file)
	run_gdal = 'gdalwarp -ts %s %s -r near -co "TFW=YES" %s %s' % input_param
	os.system(run_gdal)

	data=get_data(out_file)

	# mask=make_3d_mask(data,levels,res)
	mask=[]

	
	''' return dictionary '''
	dtm={}
	dtm['data']=data['array']
	dtm['mask']=mask
	dtm['extent']=data['extent']
	dtm['xg']=data['xg']
	dtm['yg']=data['yg']

	return dtm