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

def TDC_getHistogram(chanA, chanB, reset, data, count, tooSmall, tooLarge, eventsA, eventsB, expTime):
	windll.tdcbase.TDC_getHistogram(chanA,chanB, reset, byref(data), byref(count), byref(tooSmall), byref(tooLarge), byref(eventsA), byref(eventsB), byref(expTime))

def TDC_getHistogram_Params(binWidth, binCount):
	return windll.tdcbase.TDC_getHistogram_Params(byref(binWidth), byref(binCount))

def TDC_getCoincCounters(data):
	return windll.tdcbase.TDC_getCoincCounters(data)

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