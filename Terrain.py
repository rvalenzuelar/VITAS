#
# Functions for digital terrain model
#
# Raul Valenzuela
# July 2015

class Terrain(object):
	def __init__(self,filepath):
		if filepath:
			self.file=filepath
		else:
			self.file=None

# def plot_level():

# def plot_profile():


def make_terrain_array(Terrain):

		''' working folders '''
		home = expanduser("~")
		dem_file=home+'/Github/RadarQC/merged_dem_38-39_123-124_extended.tif'
		temp_file=home+'/Github/pythonx/temp.tif'
		out_file=home+'/Github/pythonx/temp_resamp.tif'

		''' same boundaries as synthesis'''
		ulx = min(self.lons)
		uly = max(self.lats)		
		lrx = max(self.lons)
		lry = min(self.lats)

		''' number of verical gates '''
		zvalues=self.axesval['z']		
		levels=len(zvalues)

		''' vertical gate resolution'''
		res=(zvalues[1]-zvalues[0])*1000 # [m] 
		
		''' downsample DTM using synthesis axes '''
		xvalues=self.axesval['x']
		yvalues=self.axesval['y']
		resampx_to=len(xvalues)
		resampy_to=len(yvalues)

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

		''' store dtm in data '''
		datafile = gdal.Open(out_file)
		geotransform=datafile.GetGeoTransform()
		cols=datafile.RasterXSize
		rows=datafile.RasterYSize
		band=datafile.GetRasterBand(1)		
		data=band.ReadAsArray(0,0,cols,rows)
		datafile=None

		# ''' creates 3D terrain mask array '''
		# mask=np.zeros((rows,cols,levels))

		# '''Loop through each pixel of DTM and 
		# corresponding vertical column of mask'''
		# for ij in np.ndindex(mask.shape[:2]):

		# 	'''indices'''
		# 	i,j=ij
			
		# 	'''index of maximum vertical gate to
		# 	filled with ones (e.g. presence of terrain);
		# 	works like floor function; altitude of mask 
		# 	is zlevel[n-1] for n>0'''
		# 	n = int(np.ceil(data[i,j]/float(res)))
			
		# 	''' fills verical levels '''
		# 	mask[i,j,0:n] = 1

		mask=[]

		''' geographic axes '''
		originX=geotransform[0]
		originY=geotransform[3]
		pixelW=geotransform[1]
		pixelH=geotransform[5]

		# print originX,originY,pixelW,pixelH

		endingX=originX+cols*pixelW
		endingY=originY+rows*pixelH

		# print endingX, endingY

		xg=np.linspace(originX,endingX,cols)
		yg=np.linspace(originY,endingY,rows)

		dtm={	'data':data,
				'mask':mask,
				'extent':[ulx, lrx, lry,uly],
				'xg':xg,
				'yg':yg,}

		return dtm