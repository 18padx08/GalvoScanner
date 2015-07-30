from ctypes import *

#map enums

DEVTYPE_1A = 0
DEVTYPE_1A = 1
DEVTYPE_1C = 2
DEVTYPE_NONE = 3

#needed dll functions

#clear histogramm
def TDC_clearAllHistograms():
	return windll.tdcbase.TDC_clearAllHistograms()

def TDC_init (deviceId):
	return windll.tdcbase.TDC_init(deviceId)

def TDC_deInit():
	return windll.tdcbase.TDC_deInit()

def TDC_getHistogram(chanA=-1, chanB=-1, reset=False, data=None, count=None, tooSmall=None, tooLarge=None, eventsA=None, eventsB=None, expTime=None):
	windll.tdcbase.TDC_getHistogram(chanA,chanB, reset, byref(data) if data is not None else None, byref(count)if count is not None else None, byref(tooSmall)if tooSmall is not None else None, byref(tooLarge)if tooLarge is not None else None, byref(eventsA)if eventsA is not None else None, byref(eventsB)if eventsB is not None else None, byref(expTime)if expTime is not None else None)

def TDC_getHistogramParams(binWidth, binCount):
	return windll.tdcbase.TDC_getHistogramParams(byref(binWidth), byref(binCount))
	
def TDC_setHistogramParams(binWidth, binCount):
	return windll.tdcbase.TDC_setHistogramParams(c_int(binWidth), c_int(binCount))

def TDC_getCoincCounters(data):
	return windll.tdcbase.TDC_getCoincCounters(data)
	
def TDC_setExposureTime(time):
	return windll.tdcbase.TDC_setExposureTime(c_int(time))

def TDC_getTimebase():
	return windll.tdcbase.TDC_getTimebase()

#helper functions

#retrieve histogram for current time and sum over all bins to get total count rate
def getCountRate():
	width = int32()
	count = int32()
	TDC_getHistogram_Params(width, count)
	#generate array which holds all bins
	import numpy as np
	histo = np.zeros((count,), dtype=np.int32)
	TDC_getHistogram(0,1,True,histo,None,None,None,None,None,None)
	
	#now sum over all values in the bin
	tcr = np.sum(histo)
	return tcr