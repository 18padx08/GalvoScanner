import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import os

#smoothing function
def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


def plot3dmap(data, maskvalue=50000, plotid=111, title=""):
	global fig
	if len(data) <= 0:
		return
	zlayers = []
	for entry in data:
		#read each file and load it
		zlayers += [numpy.load(entry)]
	#prepare the x-axes (since we have a rectangle we have height times the same x value)
	
	xdim = zlayers[0].shape[0]
	ydim = zlayers[0].shape[1]
	zdim = len(zlayers)
	x_ = numpy.linspace(1,xdim, xdim)
	y_ = numpy.linspace(1,ydim, ydim)
	z_ = numpy.linspace(1,zdim, zdim)
	x,y,z = numpy.meshgrid(x_,y_,z_, indexing='ij')
	vol = xdim * ydim * zdim
	x = x.reshape(vol,)
	y = y.reshape(vol,)
	z = z.reshape(vol,)
	print(x,y,z)
	#for xval in numpy.linspace(1,xdim,xdim):
	#	print(len(ydim* zdim *[xval]))
	#	x = numpy.append(x,ydim* zdim *[xval])
	#for yval in numpy.linspace(1,ydim,ydim):
#		y = numpy.append(y,xdim *zdim * [yval])
#		for zval in numpy.linspace(1,zdim,zdim):
#			z = numpy.append(z,xdim *ydim * [zval])
		
	c = numpy.array(zlayers)
	c = c.reshape(xdim*ydim*zdim,order='F')
	c = numpy.ma.masked_less(c, maskvalue)
	
	print("shapes", x.shape, y.shape,z.shape, c.shape)
	#now we have prepared our data lets plot
	ax = fig.add_subplot(plotid, projection='3d')
	sc = ax.scatter(x,y,z,c=c, cmap=plt.hot())
	try:
		plt.colorbar(sc)
	except:
		pass

fig = plt.figure(1)

#create a combined 3d plot
plt.title("3D Plot of Photon counts X/Y/Z")
plot3dmap([os.path.join(root,name) for root, top, file in os.walk(".") for name in file if "npy" in name and not "csv" in name and "x" in name], plotid=311, title="X-Direction")
plot3dmap([os.path.join(root,name) for root, top, file in os.walk(".") for name in file if "npy" in name and not "csv" in name and "yline" in name], plotid=312, title="Y-Direction")
plot3dmap([os.path.join(root,name) for root, top, file in os.walk(".") for name in file if "npy" in name and not "csv" in name and "z" in name], maskvalue=5000, plotid=313, title="Z-Direction")
#plt.show()
fig.set_size_inches(10,25)
fig.savefig("combinedPlot.png", dpi=100)

#try to calculate the gausian fits

#load data for xline
dataArray = numpy.load("xline.npy")

#invert the dataArray such that we get a peak for a intensity (remember negative Voltage means high intensity)
rotatedDataArray = dataArray


#shift the dataArray so we have our gausians around 0
intens = rotatedDataArray[0,:] 
intens = [x for x in intens if x > 0]
smoothDataArray = savitzky_golay(intens, 51, 5)

#now calculate the derivative
diffRotatedDataArray = numpy.diff(smoothDataArray)
diffRotatedUnSmoothDataArray = numpy.diff(intens)

mask = numpy.r_[True, diffRotatedDataArray[1:] < diffRotatedDataArray[:-1]] & numpy.r_[diffRotatedDataArray[:-1] < diffRotatedDataArray[1:], True]


#show smooth data array
fig = plt.figure()
plt.plot(smoothDataArray)
plt.plot(intens)
plt.title("Xdata smoothend count function")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts")
#plt.show()
fig.set_size_inches(10,10)
fig.savefig("xdataS.png", dpi=100)

#show derivative
fig = plt.figure()
plt.plot(diffRotatedDataArray, linewidth=2)
plt.plot(diffRotatedUnSmoothDataArray)
plt.title("XData derivative")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts / Pseudo distance")
#plt.show()
fig.set_size_inches(10,10)
fig.savefig("xdataSD.png", dpi=100)

#load data for yline
dataArray = numpy.load("yline.npy")
print(dataArray.shape)
#invert the dataArray such that we get a peak for a intensity (remember negative Voltage means high intensity)
rotatedDataArray = dataArray


#shift the dataArray so we have our gausians around 0
intens = rotatedDataArray[:,0]
print(intens)
intens = [x for x in intens if x > 0]
print(intens)
smoothDataArray = savitzky_golay(intens, 51, 5)

#now calculate the derivative
diffRotatedDataArray = numpy.diff(smoothDataArray)
diffRotatedUnSmoothDataArray = numpy.diff(intens)

mask = numpy.r_[True, diffRotatedDataArray[1:] < diffRotatedDataArray[:-1]] & numpy.r_[diffRotatedDataArray[:-1] < diffRotatedDataArray[1:], True]


#show smooth data array
fig = plt.figure()
plt.plot(smoothDataArray)
plt.plot(intens)
plt.title("Ydata smoothend count function")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts")
#plt.show()

fig.set_size_inches(10,10)
fig.savefig("ydataS.png", dpi=100)

#show derivative
fig = plt.figure()
plt.plot(diffRotatedDataArray, linewidth=2)
plt.plot(diffRotatedUnSmoothDataArray)
plt.title("YData derivative")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts / Pseudo distance")
#plt.show()
fig.set_size_inches(10,10)
fig.savefig("ydataSD.png", dpi=100)

dataArray = []
#load data for zline
for dataFile in [os.path.join(root,name) for root, top, file in os.walk(".") for name in file if "npy" in name and not "csv" in name and "z" in name]:
    dataArray += [numpy.load(dataFile)[0,0]]

#invert the dataArray such that we get a peak for a intensity (remember negative Voltage means high intensity)
rotatedDataArray = dataArray
print(dataArray)


#shift the dataArray so we have our gausians around 0
intens = rotatedDataArray[:] 
intens = [x for x in intens if x > 0]
smoothDataArray = savitzky_golay(intens, 51, 5)

#now calculate the derivative
diffRotatedDataArray = numpy.diff(smoothDataArray)
diffRotatedUnSmoothDataArray = numpy.diff(intens)

mask = numpy.r_[True, diffRotatedDataArray[1:] < diffRotatedDataArray[:-1]] & numpy.r_[diffRotatedDataArray[:-1] < diffRotatedDataArray[1:], True]


#show smooth data array
fig = plt.figure()
plt.plot(smoothDataArray)
plt.plot(intens)
plt.title("Zdata smoothend count function")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts")
#plt.show()
fig.set_size_inches(10,10)
fig.savefig("zdataS.png", dpi=100)

#show derivative
fig = plt.figure()
plt.plot(diffRotatedDataArray, linewidth=2)
plt.plot(diffRotatedUnSmoothDataArray)
plt.title("ZData derivative")
plt.xlabel("Pseudo distance")
plt.ylabel("Photon counts / Pseudo distance")
#plt.show()
fig.set_size_inches(10,10)
fig.savefig("zdataSD.png", dpi=100)
#plot the dependency of peaks to voltage

#peaks = [72, 278, 415, 552]
#peaksVoltage = [66, 160, 248, 339]
#fit = np.polyfit(peaksVoltage, peaks, 1)
#fitCurve = np.poly1d(fit)
#plt.plot(peaksVoltage, peaks , linestyle="", marker="*")
#plt.plot(peaksVoltage, fitCurve(peaksVoltage))
#plt.show()
