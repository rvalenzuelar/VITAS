# From:
# http://stackoverflow.com/questions/24702868/python3-pillow-get-all-pixels-on-a-line
# https://github.com/sachinruk/xiaolinwu/blob/master/xiaolinwu.m

def xiaolin(x0, y0, x1, y1,**kwargs):

	width=kwargs['width']

	x=[]
	y=[]
	dx = x1-x0
	dy = y1-y0
	steep = abs(dx) < abs(dy)

	if steep:
		x0,y0 = y0,x0
		x1,y1 = y1,x1
		dy,dx = dx,dy

	if x0 > x1:
		x0,x1 = x1,x0
		y0,y1 = y1,y0

	gradient = float(dy) / float(dx)  # slope

	# print ("points(x0,y0,x1,y1): %s,%s,%s,%s" % (x0,y0,x1,y1))
	# print ("dx,dy: %s,%s" % (dx,dy))
	# print ("gradient: %s" % gradient)

	""" handle first endpoint """
	xend = round(x0)
	yend = y0 + gradient * (xend - x0)
	xpxl0 = int(xend)
	ypxl0 = int(yend)
	x.append(xpxl0)
	y.append(ypxl0)	
	x.append(xpxl0)
	y.append(ypxl0+width)
	intery = yend + gradient

	""" handles the second point """
	xend = round (x1);
	yend = y1 + gradient * (xend - x1);
	xpxl1 = int(xend)
	ypxl1 = int (yend)
	x.append(xpxl1)
	y.append(ypxl1)	
	x.append(xpxl1)
	y.append(ypxl1 + width)

	""" main loop """
	for px in range(xpxl0 + width , xpxl1):
		x.append(px)
		y.append(int(intery))
		x.append(px)
		y.append(int(intery) + width)
		intery = intery + gradient;

	if steep:
		y,x = x,y

	coords=zip(x,y)

	return coords


