from ctypes import *
import ctypes as ct

#map enums

DEVTYPE_1A = 0
DEVTYPE_1A = 1
DEVTYPE_1C = 2
DEVTYPE_NONE = 3

#function struct
class TDC_HbtFunction(Structure):
	_fields_ = [
		("capacity", c_int32),
		("size", c_int32),
		("binWidth", c_int32),
		("indexOffset", c_int32),
		("values", c_double*0)
	]
	
	def __getitem__(self, key):
		theaddr = cast(self.values, POINTER(c_double))
		self.vals = (c_double * self.capacity)(*theaddr[0:self.capacity])
		return self.vals[key]

#needed dll functions

tdcbase = windll.tdcbase

#clear histogramm
def TDC_clearAllHistograms():
	return windll.tdcbase.TDC_clearAllHistograms()

def TDC_init (deviceId):
	return windll.tdcbase.TDC_init(deviceId)

def TDC_deInit():
	return windll.tdcbase.TDC_deInit()

def TDC_enableHbt(enable):
	return windll.tdcbase.TDC_enableHbt(enable)
#returns a TDC_HbtFunction

def TDC_createHbtFunction():
	helperFunction =  windll.tdcbase.TDC_createHbtFunction
	helperFunction.restype = ct.POINTER(TDC_HbtFunction)
	return helperFunction()

def TDC_freezeBuffers(freeze):
	return windll.tdcbase.TDC_freezeBuffers(freeze)
def TDC_resetHbtCorrelations():
	return windll.tdcbase.TDC_resetHbtCorrelations()

def TDC_getHbtCorrelations(forward, fct):
	return windll.tdcbase.TDC_getHbtCorrelations(forward, fct)

def TDC_calcHbtG2(fct):
	return windll.tdcbase.TDC_calcHbtG2(fct)

#def TDC_getHistogram(chanA=-1, chanB=-1, reset=False, data=None, count=None, tooSmall=None, tooLarge=None, eventsA=None, eventsB=None, expTime=None):
#	windll.tdcbase.TDC_getHistogram(chanA,chanB, reset, byref(data) if data is not None else None, byref(count)if count is not None else None, byref(tooSmall)if tooSmall is not None else None, byref(tooLarge)if tooLarge is not None else None, byref(eventsA)if eventsA is not None else None, byref(eventsB)if eventsB is not None else None, byref(expTime)if expTime is not None else None)

def TDC_getHistogramParams(binWidth, binCount):
	return windll.tdcbase.TDC_getHistogramParams(byref(binWidth), byref(binCount))
	
def TDC_setHbtParams(binWidth, binCount):
	return windll.tdcbase.TDC_setHbtParams(c_int(binWidth), c_int(binCount))

def TDC_getCoincCounters(data, updates=None):
	return windll.tdcbase.TDC_getCoincCounters(data, (updates) if updates is not None else None)
	
def TDC_setExposureTime(time):
	return windll.tdcbase.TDC_setExposureTime(c_int(time))

def TDC_getTimebase():
	helper =windll.tdcbase.TDC_getTimebase
	helper.restype = c_double
	return helper()

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