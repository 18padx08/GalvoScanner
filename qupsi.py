from ctypes import *
import ctypes as ct
from Enum import *
	

tdcbase = windll.tdcbase
#tdcbase.h

#constants
TDC_INPUT_CHANNELS = 8
TDC_COINC_CHANNELS = 19

#enums
TDC_DevType = Enum("DEVTYPE_1A", "DEVTYPE_1B", "DEVTYPE_1C", "DEVTYPE_NONE")
TDC_FileFormat = Enum("FORMAT_ASCII", "FORMAT_BINARY", "FORMAT_COMPRESSED", "FORMAT_NONE")
TDC_SignalCond = Enum("SCOND_TTL", "SCOND_LVTTL", "SCOND_NIM", "SCOND_MISC", "SCOND_NONE")
TDC_SimType = Enum("SIM_F:AT", "SIM_NORMAL", "SIM_NONE")

#functions

tdcbase.TDC_getVersion.restype = c_double
def TDC_getVersion():
	return tdcbase.TDC_getVersion()

tdcbase.TDC_perror.argtypes = [c_int]
tdcbase.TDC_perror.restype = c_char_p
def TDC_perror(rc):
	return tdcbase.TDC_perror()

tdcbase.TDC_getTimebase.restype = c_double
def TDC_getTimebase():
	return tdcbase.TDC_getTimebase()

tdcbase.TDC_init.argtypes = [c_int]
tdcbase.TDC_init.restype = c_int
def TDC_init (deviceId):
	return tdcbase.TDC_init(deviceId)

tdcbase.TDC_deInit.restype = c_int
def TDC_deInit():
	return tdcbase.TDC_deInit()

tdcbase.TDC_getDevType.restype = c_int #TDC_DevType
def TDC_getDevType():
	return tdcbaseTDC_getDevType()

tdcbase.TDC_checkFeatureHbt.restype = c_bool
def TDC_checkFeatureHbt():
	return tdcbase.TDC_checkFeatureHbt()
	
tdcbase.TDC_checkFeatureLifeTime.restype = c_bool
def TDC_checkFeatureLifeTime():
	return tdcbase.TDC_checkFeatureLifeTime()

tdcbase.TDC_configureSignalConditioning.argtypes = [c_int, c_int, c_bool, c_bool, c_double]
tdcbase.TDC_configureSignalConditioning.restype = c_int
def TDC_configureSignalConditioning(channel, conditioning, edge, term, threshold):
	return tdcbase.TDC_configureSignalConditioning(channel, conditioning, edge, term, threshold)

tdcbase.TDC_configureSyncDivider.argtypes = [c_int, c_bool]
tdcbase.TDC_configureSyncDivider.restype = c_int
def TDC_configureSyncDivider(divider, reconstruct):
	return tdcbase.TDC_configureSyncDivider(divider, reconstruct)

tdcbase.TDC_configureApdCooling.argtypes = [c_int, c_int]
tdcbase.TDC_configureApdCooling.restype = c_int
def TDC_configureApdCooling(fanSpeed, temp):
	return tdcbase.TDC_configureApdCooling(fanSpeed, temp)

tdcbase.TDC_configureInternalApds.argtypes = [c_int, c_double, c_double]
tdcbase.TDC_configureInternalApds.restype = c_int
def TDC_configureInternalApds(apd, bias, thrsh):
	return tdcbase.TDC_configureInternalApds(apd, bias, thrsh)

tdcbase.TDC_enableChannels.argtypes = [c_int]
tdcbase.TDC_enableChannels.restype = c_int
def TDC_enableChannels(channelMask):
	return tdcbase.TDC_enableChannels(channelMask)

tdcbase.TDC_setChannelDelays.argtypes = [POINTER(c_int)]
tdcbase.TDC_setChannelDelays.restype = c_int
def TDC_setChannelDelays(delays):
	return tdcbase.TDC_setChannelDelays(delays)

tdcbase.TDC_setCoincidenceWindow.argtypes = [c_int]
tdcbase.TDC_setCoincidenceWindow.restype = c_int
def TDC_setCoincidenceWindow(coincWin):
	return tdcbase.TDC_setCoincidenceWindow(coincWin)

tdcbase.TDC_setExposureTime.argtypes = [c_int]
tdcbase.TDC_setExposureTime.restype = c_int
def TDC_setExposureTime(time):
	return tdcbase.TDC_setExposureTime(c_int(time))

tdcbase.TDC_getDeviceParams.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int)]
tdcbase.TDC_getDeviceParams.restype = c_int
def TDC_getDeviceParams(channelMask, coincWin, expTime):
	return tdcbase.TDC_getDeviceParams(byref(channelMask), byref(coincWin), byref(expTime))

tdcbase.TDC_switchTermination.argtypes = [c_bool]
tdcbase.TDC_switchTermination.restype = c_int
def TDC_switchTermination(on):
	return tdcbase.TDC_switchTermination(on)
	
tdcbase.TDC_configureSelftest.argtypes = [POINTER(c_int), c_int, c_int, c_int]
tdcbase.TDC_configureSelftest.restype = c_int
def TDC_configureSelftest(channelMask, period, burstSize, burstDist):
	return tdcbase.TDC_configureSelftest(channelMask, period, burstDist)

tdcbase.TDC_getDataLost.argtypes = [POINTER(c_bool)]
tdcbase.TDC_getDataLost.restype = c_int
def TDC_getDataLost(lost):
	return tdcbase.TDC_getDataLost(byref(lost))

tdcbase.TDC_setTimestampBufferSize.argtypes = [c_int]
tdcbase.TDC_setTimestampBufferSize.reset = c_int
def TDC_setTimestampBufferSize(size):
	return TDC_setTimestampBufferSize(size)
	
tdcbase.TDC_freezeBuffers.argtypes = [c_bool]
tdcbase.TDC_freezeBuffers.restype = c_int
def TDC_freezeBuffers(freeze):
	return tdcbase.TDC_freezeBuffers(freeze)

tdcbase.TDC_getCoincCounters.argtypes = [POINTER(c_int), POINTER(c_int)]
tdcbase.TDC_getCoincCounters.restype = c_int
def TDC_getCoincCounters(data, updates=None):
	return tdcbase.TDC_getCoincCounters(data, (updates) if updates is not None else None)

tdcbase.TDC_getLastTimestamps.argtypes = [c_bool, POINTER(c_long), POINTER(c_short),POINTER(c_int)]
tdcbase.TDC_getLastTimestamps.restype = c_int
def TDC_getLastTimestamps(reset, timestamps, channels, valid):
	return tdcbase.TDC_getLastTimestamps(reset, byref(timestamps), byref(channels), byref(valid))

tdcbase.TDC_writeTimestamps.argtypes = [c_char_p, c_int]
tdcbase.TDC_writeTimestamps.restype = c_int
def TDC_writeTimestamps(filename, f):
	return tdcbase.TDC_writeTimestamps(filename,f)

tdcbase.TDC_inputTimestamps.argtypes = [POINTER(c_long), POINTER(c_short), POINTER(c_int)]
tdcbase.TDC_inputTimestamps.restype = c_int
def TDC_inputTimestamps(timestamps, channels, count):
	return tdcbase.TDC_inputTimestamps(byref(timestamps), byref(channels), count)

tdcbase.TDC_readTimestamps.argtypes = [c_char_p, c_int]
tdcbase.TDC_readTimestamps.restype = c_int
def TDC_readTimestamps(filename, f):
	return tdcbase.TDC_readTimestamps(filename,f)

tdcbase.TDC_generateTimestamps.argtypes = [c_int, POINTER(c_double), c_int]
tdcbase.TDC_generateTimestamps.restype = c_int
def TDC_generateTimestamps(t, par, count):
	return TDC_generateTimestamps(t, byref(par), count)

#######################################################
#tdcstartstop.h
#######################################################

#constants

TDC_CROSS_CHANNELS = 8

tdcbase.TDC_enableStartStop.argtypes = [c_bool]
tdcbase.TDC_enableStartStop.restype = c_int
def TDC_enableStartStop(enable):
	return tdcbase.TDC_enableStartStop(enable)

tdcbase.TDC_setHistogramParams.argtypes = [c_int, c_int]
tdcbase.TDC_setHistogramParams.restype = c_int
def TDC_setHistogramParams(binWidth, binCount):
	return tdcbase.TDC_setHistogramParams(binWidth, binCount)


tdcbase.TDC_getHistogramParams.argtypes = [POINTER(c_int), POINTER(c_int)]
tdcbase.TDC_getHistogramParams.restype = c_int
def TDC_getHistogramParams(binWidth, binCount):
	return TDC_getHistogramParams(byref(binWidth), byref(binCount))

tdcbase.TDC_getHistogram.argtypes = [c_int, c_int, c_bool, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
def TDC_getHistogram(chanA=-1, chanB=-1, reset=False, data=None, count=None, tooSmall=None, tooLarge=None, eventsA=None, eventsB=None, expTime=None):
	windll.tdcbase.TDC_getHistogram(chanA,chanB, reset, byref(data) if data is not None else None, byref(count)if count is not None else None, byref(tooSmall)if tooSmall is not None else None, byref(tooLarge)if tooLarge is not None else None, byref(eventsA)if eventsA is not None else None, byref(eventsB)if eventsB is not None else None, byref(expTime)if expTime is not None else None)

######################################################################################
#tdcdecl.h
#################################################################################################
TDC_OK = 0
TDC_Error = -1
TDC_Timeout = 1
TDC_NotConnected = 2
TDC_DriverError = 3
TDC_DeviceLocked = 7
TDC_Unkown = 8
TDC_NoDevice = 9
TDC_OutOfRange = 10
TDC_CantOpen = 11
TDC_NotInitialized = 12
TDC_NotEnabled = 13
TDC_NotAvailable = 14


#########################################################################################################
#tdchbt.h
#########################################################################################################
#constants
HBT_PARAM_SIZE = 5

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

#Enum
HBT_FctType = Enum("FCTTYPE_NONE", "FCTTYPE_COHERENT", "FCTTYPE_THERMAL", "FCTTYPE_SINGLE", 
   "FCTTYPE_ANTIBUNCH", "FCTTYPE_THERM_JIT", "FCTTYPE_SINGLE_JIT", "FCTTYPE_ANTIB_JIT", 
   "FCTTYPE_THERMAL_OFS", "FCTTYPE_SINGLE_OFS", "FCTTYPE_ANTIB_OFS", "FCTTYPE_THERM_JIT_OFS", 
   "FCTTYPE_SINGLE_JIT_OFS", "FCTTYPE_ANTIB_JIT_OFS")
#needed dll functions

tdcbase.TDC_enableHbt.argtypes = [c_bool]
tdcbase.TDC_enableHbt.restype = c_int
def TDC_enableHbt(enable):
	return tdcbase.TDC_enableHbt(enable)

tdcbase.TDC_setHbtParams.argtypes = [c_int, c_int]
tdcbase.TDC_setHbtParams.restype = c_int
def TDC_setHbtParams(binWidth, binCount):
	return tdcbase.TDC_setHbtParams(c_int(binWidth), c_int(binCount))

tdcbase.TDC_setHbtDetectorParams.argtypes = [c_double]
tdcbase.TDC_setHbtDetectorParams.restype = c_int
def TDC_setHbtDetectorParams(jitter):
	return tdcbase.TDC_setHbtDetectorParams(jitter)

tdcbase.TDC_setHbtInput.argtypes = [c_int,c_int]
tdcbase.TDC_setHbtInput.restype = c_int
def TDC_setHbtInput(channel1, channel2):
	return tdcbase.TDC_setHbtInput(channel1,channel2)

tdcbase.TDC_switchHbtInternalApds.argtypes = [c_bool]
tdcbase.TDC_switchHbtInternalApds.restype = c_int
def TDC_switchHbtInternalApds(internal):
	return tdcbase.TDC_switchHbtInternalApds(internal)
	
tdcbase.TDC_resetHbtCorrelations.restype = c_int
def TDC_resetHbtCorrelations():
	return tdcbase.TDC_resetHbtCorrelations()

tdcbase.TDC_getHbtEventCount.argtypes = [POINTER(c_long), POINTER(c_long), POINTER(c_double)]
tdcbase.TDC_getHbtEventCount.restype = c_int
def TDC_getHbtEventCount(totalCount, lastCount, lastRate):
	return tdcbase.TDC_getHbtEventCount(byref(totalCount), byref(lastCount), byref(lastRate))

tdcbase.TDC_getHbtIntegrationTime.argtypes = [POINTER(c_double)]
tdcbase.TDC_getHbtIntegrationTime.restype = c_int
def TDC_getHbtIntegrationTime(intTime):
	return tdcbase.TDC_getHbtIntegrationTime(byref(intTime))

tdcbase.TDC_getHbtCorrelations.argtypes = [c_bool, POINTER(TDC_HbtFunction)]
tdcbase.TDC_getHbtCorrelations.restype = c_int
def TDC_getHbtCorrelations(forward, fct):
	return tdcbase.TDC_getHbtCorrelations(forward, fct)

tdcbase.TDC_calcHbtG2.argtypes = [POINTER(TDC_HbtFunction)]
tdcbase.TDC_calcHbtG2.restype = c_int
def TDC_calcHbtG2(fct):
	return tdcbase.TDC_calcHbtG2(fct)

tdcbase.TDC_fitHbtG2.argtypes = [POINTER(TDC_HbtFunction), c_int, POINTER(c_double), POINTER(c_double), POINTER(c_int)]
tdcbase.TDC_fitHbtG2.restype = c_int
def TDC_fitHbtG2(fct, fitType, startParams, fitParams, iterations):
	return tdcbase.TDC_fitHbtG2(byref(fct), fitType, startParams, fitParams, iterations)

tdcbase.TDC_getHbtFitStartParams.argtypes = [c_int]
tdcbase.TDC_getHbtFitStartParams.restype = POINTER(c_double)
def TDC_getHbtFitStartParams(fctType):
	return tdcbase.TDC_getHbtFitStartParams(fctType)

tdcbase.TDC_calcHbtModelFct.argtypes = [c_int, POINTER(c_double), POINTER(TDC_HbtFunction)]
tdcbase.TDC_calcHbtModelFct.restype = c_int
def TDC_calcHbtModelFct(fctType, params, fct):
	return tdcbase.TDC_calcHbtModelFct(fctType, params, fct)

tdcbase.TDC_generateHbtDemo.argtypes = [c_int, POINTER(c_double), c_double]
tdcbase.TDC_generateHbtDemo.restype = c_int
def TDC_generateHbtDemo(fctType, params, noiseLv):
	return tdcbase.TDC_generateHbtDemo(fctType, params, noiseLv)

#returns a TDC_HbtFunction
tdcbase.TDC_createHbtFunction.restype = ct.POINTER(TDC_HbtFunction)
def TDC_createHbtFunction():
	return tdcbase.TDC_createHbtFunction()

tdcbase.TDC_releaseHbtFunction.argtypes = [POINTER(TDC_HbtFunction)]
tdcbase.TDC_releaseHbtFunction.restype = c_void_p
def TDC_releaseHbtFunction(fct):
	return tdcbase.TDC_releaseHbtFunction(fct)
	
tdcbase.TDC_analyseHbtFunction.argtypes = [POINTER(TDC_HbtFunction), POINTER(c_int),POINTER(c_int),POINTER(c_int),POINTER(c_int),POINTER(c_double), c_int]
tdcbase.TDC_analyseHbtFunction.restype = c_void_p
def TDC_analyseHbtFunction(fct, capacity, size, binWidth, iOffset, values, bufSize):
	return tdcbase.TDC_analyseHbtFunction(fct, capacity, byref(size), byref(binWidth), byref(iOffset), values, bufSize)

################################################################################################################################################
#tdclifetm.h
##########################################################################################################################################

tdcbase.TDC_enableLft.argtypes = [c_bool]
tdcbase.TDC_enableLft.restype = c_int
def TDC_enableLft(enable):
	return tdcbase.TDC_enableLft(enable)

tdcbase.TDC_setLftParams.argtypes = [c_int, c_int]
tdcbase.TDC_setLftParams.restype = c_int
def TDC_setLftParams(binWidth, binCount):
	return tdcbase.TDC_setLftParams(binWidth, binCount)

tdcbase.TDC_setLftStartInput.argtypes = [c_int]
tdcbase.TDC_setLftStartInput.restype = c_int
def TDC_setLftStartInput(startChan):
	return tdcbase.TDC_setLftStartInput(startChan)
	
tdcbase.TDC_resetLftHistogram.restype = c_int
def TDC_resetLftHistogram():
	return tdcbase.TDC_resetLftHistogram()

tdcbase.TDC_getLftHistogram.argtypes = [c_bool, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_long)]
tdcbase.TDC_getLftHistogram.restype = c_int
def TDC_getLftHistogram(reset, data, tooBig, startEvts, stopEvts, expTime):
	return tdcbase.TDC_getLftHistogram(reset, data, tooBig, startEvts, stopEvts, expTime)


#clear histogramm
def TDC_clearAllHistograms():
	return tdcbase.TDC_clearAllHistograms()

def TDC_getHistogramParams(binWidth, binCount):
	return tdcbase.TDC_getHistogramParams(byref(binWidth), byref(binCount))
	

