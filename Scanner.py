from PyDAQmx import *
import numpy
import matplotlib.pyplot as plt
import random
import time	
from pyflycam import *

#pillow.readthedocs.org/ for image manipulation

#PIL.ImageChops.composite(image1, image2, mask)

#################################################################################

#container class for holding attributes
class EmptyObject:
	pass

#helper class for callable list
class CallableList(list):
	def __call__(self):
		for entry in self:
			entry()
	

#helper class for Sample size
class Size:
	def __init__(self, height, width):
		self.height = height
		self.width = width
		
	#override multiplication
	def __mul__(self, other):
		self.width *= other
		self.height *= other
		return self
		
	#override division
	def __div__(self, other):
		self.width /=other
		self.height /=other
		return self
	
#Helper class for storing Lens informatios and to calculate the focal length corresponding to the NA
class Lens:
	def __init__(self, NA, n):
		self.NA = NA
		self.n = n
	
	def LensNumber(self):
		return 1/numpy.tan(numpy.arcsin(self.NA/self.n))
#########################################################################################

################################################################
#Exceptions which occur while scanning	
class AngleOutsideOfRangeException(Exception):
	pass

class VoltageCannotBeNegativeException(Exception):
	pass

class ConfigFileNotFoundException(Exception):
	pass
#################################################################
def scannerObjects(dct):
	if "_sample_size_" in dct:
		return Size(dct["height"], dct["width"])
	if "_eval_" in dct:
		if "libraries" in dct:
			for lib in dct["libraries"]:
				exec("import " + str(lib))
		return eval(dct["expression"])
	return dct

class Scanner:
	#scanner class: needs sampleSize (to calculate the max and min angles for the galvo) and 
	#               the distance from the galvo to the lens
	
	#sensitivity of the galvo in volt per rad
	sensitivityRad = 90.0/numpy.pi
	sensitivityDeg = 0.5
	
	# arguments: all units in mm, devicePhi for Xtranslation, devicetheta for Ytranslation
	def __init__(self, sampleSize = None,beamDiameter = 5, lens = Lens(1.3,1.5),inputDevice="Dev2/ai1", devicePhi = "Dev2/ao1", deviceTheta = "Dev2/ao0", configFile = "scanner_config.cfg"):
		#local variables rerpresenting the sate of the scanner
		self.currentX = 0
		self.currentY = 0
		self.currentVoltagePhi = 0
		self.currentVoltageTheta = 0
		self.currentPiezoVoltage = 0
		self.sampleSize = sampleSize
		self.currentGalvoPhi = 0
		self.currentGalvoTheta = 0
		self.lens = lens
		self.calibrationPhi = 0
		self.calibrationTheta = 0
		self.devicePhi = devicePhi
		self.deviceTheta = deviceTheta
		self.inputDevice = inputDevice
		#the calibration values, read them from the config file
		import json
		import os.path
		if os.path.isfile(configFile):
			self._config = json.loads(open(configFile).read(), object_hook=scannerObjects)
		else:
			self._config = {}
			self._config["settings"] = {}
		if "settings" in  self._config:
			#foreach import config load the variables (same names get overwritten)
			if "imports" in self._config:
				for cfgfile in self._config["imports"]:
					self.loadConfig(cfgfile)
			for key in self._config["settings"]:
				setattr(self, key, self._config["settings"][key])
		
		#max and min x are half the sample size since we place the sample in such a way that it is centered arround the
		#origin of lens
		self.maxX = self.sampleSize.width/2.0
		self.minX = -self.sampleSize.width/2.0
		
		self.maxY = self.sampleSize.height / 2.0
		self.minY = -self.sampleSize.height / 2.0
		
		if not hasattr(self, 'xsteps'):
			self.xsteps = numpy.linspace(0, 0.05, 500)
		if not hasattr(self, 'ysteps'):
			self.ysteps = numpy.linspace(0,0.05, 500)

		self.dataArray = numpy.zeros((len(self.ysteps),len(self.xsteps)), dtype=numpy.float64)
		
		#prepare the output channels
		try:
			self.analog_output = Task()
			self.analog_output.CreateAOVoltageChan(",".join([self.devicePhi, self.deviceTheta, self.piezoDevice]),"",-10.0,10.0,DAQmx_Val_Volts,None)
			#self.analog_output.CreateAOVoltageChan(deviceTheta,"",-10.0,10.0,DAQmx_Val_Volts,None)
			self.analog_output.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,100)
			
			self.analog_input = Task()
			self.analog_input.CreateAIVoltageChan(self.inputDevice, "", DAQmx_Val_Cfg_Default, -10.0,10.0,DAQmx_Val_Volts, None)
			self.analog_input.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,100)	
		except(Exception):
			print("Could not init DaqMX")
		#self.initCamera()
				#if we have a focus point set it
		if hasattr(self, "focus"):
			self.setFocus(self.focus)
		#if(hasattr(self, "imageSettings")):
		#	self.setImageProperties(self.imageSettings['gain'], self.imageSettings['shutter'])	
		time.sleep(2)
	
	#load config file
	def loadConfig(self, configFile="scanner_config.cfg"):
		import json
		import os.path
		if os.path.isfile(configFile):
			self._config = json.loads(open(configFile).read(), object_hook=scannerObjects)
		else:
			raise(ConfigFileNotFoundException)
		if "settings" in  self._config:
			for key in self._config["settings"]:
				setattr(self, key, self._config["settings"][key])
		if hasattr(self, "focus"):
			self.setFocus(self.focus)
		self.dataArray = numpy.zeros((len(self.ysteps),len(self.xsteps)), dtype=numpy.float64)

	#setImage properties
	def setImageProperties(self, gain=0.0, shutter=10.0):
		gainProp = fc2Property()
		shutterProp = fc2Property()
		gainProp.type = FC2_GAIN
		shutterProp.type = FC2_SHUTTER
		
		#retrieve current settings
		fc2GetProperty(self._context, gainProp)
		fc2GetProperty(self._context, shutterProp)
		
		gainProp.absValue = gain
		shutterProp.absValue = shutter
		
		fc2SetProperty(self._context, gainProp)
		fc2SetProperty(self._context, shutterProp)
	def startScanhook(self, hook):
		getattr(self, hook)()
	
	def callbackFactory(self, callback, args):
		return lambda: getattr(self, callback.strip())(args)
	
	def parseHook(self, hookFile):
		keywords = {"print" : lambda args: print(args) }
		tmpHookName = hookFile
		#compile a regular expression, so that we have fname(**args) and then call the appropriate function
		#or match variable declarations var = value
		import re
		functionCallPattern = re.compile("\w+\s*\([\s\w\,\.\_\-\!\$\?]*\)")
		assignPattern = re.compile("\w+\s*=\s*\w+")
		tmpObject = EmptyObject()
		body = CallableList()
		for line in open(hookFile).readlines():
			match = functionCallPattern.search(line)
			if match is not None:
				#we got a function call, so split at the first bracket
				index = match.group().find("(") 
				if  index > -1:
					functionName = match.group()[:index]
					if hasattr(self, functionName):
						arguments = match.group()[index+1:-1]
						#call function if it is a class funcion
						if(arguments == ""):
							args = None
						else:
							args = arguments.split(",")
						#print(arguments)
						if args is not None:
							body += [self.callbackFactory(functionName, *args)]
						else:
							body += [getattr(self, functionName)]
					else:
						#see if we have defined a own call
						print(functionName)
						if functionName in keywords:
							print("custom function")
							arguments = match.group()[index+1:-1]
							#call function if it is a class funcion
							args = ",".join(arguments)
							body += [lambda: keywords[functionName](args)]
			match = assignPattern.search(line)
			print(match)
			if match is not None:
				#we have a assignment
				name, value = match.group().split("=")
				setattr(tmpObject, name.strip(), value.strip())
			
			if hasattr(tmpObject, "name"):
				tmpHookName = getattr(tmpObject, "name")
			setattr(self, tmpHookName, body)
				
	#get state of galvo -> return angle in degree
	def getAnglePhiDegree(self):
		return self.currentGalvoPhi * (180./numpy.pi)
	def getAngleThetaDegree(self):
		return self.currentGalvoTheta * (180./numpy.pi)
	
	#set Voltage directly
	def setVoltagePhi(voltage):
		data = numpy.zeros((200,), dtype=numpy.float64)
		data[:99] = voltage
		data[99:] = self.currentVoltageTheta
		#set the state of the object
		self.currentVoltagePhi = voltage
		self.currentGalvoPhi = phi
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		time.sleep(0.0001)
		self.analog_output.StopTask()
	
	def setVoltageTheta(voltage):
		data = numpy.zeros((200,), dtype=numpy.float64)
		data[:99] = self.currentVoltagePhi
		data[99:] = voltage
		
		#set the state of the object
		self.currentVoltageTheta = voltage
		self.currentGalvoTheta = theta
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		#time.sleep(0.0001)
		self.analog_output.StopTask()
		
	def calibrate():
		self.calibrationPhi = self.currentVoltagePhi
		self.currentVoltagePhi = 0
		self.calibrationTheta = self.currentVoltageTheta
		self.currentVoltageTheta = 0
		self.currentGalvoTheta = 0
		self.currentGalvoPhi = 0
		self.currentX = 0
		self.currentY = 0		
	
	def setFocus(self, voltage):
		if voltage < 0:
			raise(VoltageCannotBeNegativeException)
		data = numpy.zeros((300,), dtype=numpy.float64)
		data[:99] = self.currentVoltagePhi
		data[99:199] = self.currentVoltageTheta
		data[199:] = voltage
		#set the state of the object
		self.currentPiezoVoltage = voltage
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		
		self.analog_output.StopTask()
		
	#setAngles for the galvo (enter values in degree), private: use setX and setY for public access
	def __setPhi(self, phi):
		voltage = self.sensitivityDeg * phi + self.calibrationPhi
		data = numpy.zeros((300,), dtype=numpy.float64)
		data[:99] = voltage
		data[99:199] = self.currentVoltageTheta
		data[199:] = self.currentPiezoVoltage
		#set the state of the object
		self.currentVoltagePhi = voltage
		self.currentGalvoPhi = phi
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		
		self.analog_output.StopTask()
	def __setPhiRad(self, phiRad):
		self.__setPhi(180./numpy.pi * phiRad)
		
	def __setTheta(self, theta):
		voltage = self.sensitivityDeg * theta + self.calibrationTheta
		data = numpy.zeros((300,), dtype=numpy.float64)
		data[:99] = self.currentVoltagePhi
		data[99:199] = voltage
		data[199:] = self.currentPiezoVoltage
		
		#set the state of the object
		self.currentVoltageTheta = voltage
		self.currentGalvoTheta = theta
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		#time.sleep(0.0001)
		self.analog_output.StopTask()
	def __setThetaRad(self, thetaRad):
		self.__setTheta(180./numpy.pi * thetaRad)
		
	def ReleaseObjects(self):
		self.analog_output.StopTask()
		self.analog_output.ClearTask()
		self.analog_input.StopTask()
		self.analog_input.ClearTask()
		self.uninitCamera()
		
		
	#units are mm: set x and y according to angle and sampledistance x and y is relative to the sample, so it is the
	#where the laser beam will hit the target
	#-the incident angle on the lens will be phi as well
	#-the formula for s(alpha_i) = (beamDiameter/2.) *
	def setX(self, X):
		#check if we are on the sample 
		if X < self.minX or X > self.maxX:
			raise(AngleOutsideOfRangeException)
		#set the angle of  the galvo
		self.__setPhiRad(numpy.arctan(X * self.lens.LensNumber()))
		#set the state of the situation
		self.currentX = X
		
	def setY(self, Y):
		#check if we are on the sample 
		if Y < self.minY or Y > self.maxY:
			raise(AngleOutsideOfRangeException)
		#set the angle of  the galvo
		self.__setThetaRad(numpy.arctan(Y * self.lens.LensNumber()))
		#set the state of the situation
		self.currentY = Y
	
	def setPoint(self, x, y):
		self.setX(x)
		self.setY(y)
	
	def saveState(self, name="tmpArray"):
		numpy.save(name, self.dataArray)
	
	def scanSample(self):
		#start capturing pictures
		#fc2StartCapture(self._context)
		
		#create the two pictures one for getting input the other to save
		#rawImage = fc2Image()
		#convertedImage = fc2Image()
		#fc2CreateImage(rawImage)
		#fc2CreateImage(convertedImage)
		
		self.setPoint(self.minX, self.minY)
		countX = 0
		countY = 0
		plt.ion()
		imgplot = plt.imshow(self.dataArray, animated=True)
		imgplot.set_interpolation('none')
		plt.colorbar()
		for i in self.ysteps:
			countX = 0
			for o in self.xsteps:
				#get picture
				#fc2RetrieveBuffer(self._context, rawImage)
				#ts = fc2GetImageTimeStamp(rawImage)
				#print(ts.cycleCount)	
				#self.savePicture("[%f %f].png"%(o, i), rawImage, convertedImage)
				tmpBuffer = numpy.zeros((100,), dtype=numpy.float64)
				read32 = int32()
				self.analog_input.StartTask()
				self.analog_input.ReadAnalogF64(100,0.1,DAQmx_Val_GroupByChannel, tmpBuffer, 100, byref(read32), None)
				self.analog_input.StopTask()
				#print(numpy.mean(tmpBuffer)) if abs(numpy.mean(tmpBuffer)) > 5.0e-4 else 0
				self.dataArray[countY][countX] = numpy.mean(tmpBuffer) if abs(numpy.mean(tmpBuffer)) > 5.0e-5 else 0
				#go one step further			
				countX += 1
				self.setPoint( o, i)
				imgplot.set_data(self.dataArray)
				imgplot.set_clim(numpy.min(self.dataArray), numpy.max(self.dataArray))
				
				plt.pause(0.000005)
				plt.draw()
			countY += 1
		plt.show()
		plt.savefig("sampleScan.jpeg")


		#after we are done scanning stop Capturing 
		#fc2DestroyImage(rawImage)
		#fc2DestroyImage(convertedImage)
		#fc2StopCapture(self._context)
	
	def savePicture(self, name, rawImage, convertedImage):
		fc2ConvertImageTo(FC2_PIXEL_FORMAT_BGR, rawImage, convertedImage)
		
		fc2SaveImage(convertedImage, name.encode('utf-8'), 6)

		
	def uninitCamera(self):
		fc2StopCapture(self._context)
		fc2DestroyContext(self._context)
	
	def initCamera(self):
		error = fc2Error()
		self._context = fc2Context()
		self._guid = fc2PGRGuid()
		self._numCameras = c_uint()
		
		error = fc2CreateContext(self._context)
		if error != FC2_ERROR_OK.value:
			print("Error in fc2CreateContext: " + str(error))
		
		error = fc2GetNumOfCameras(self._context, self._numCameras)
		if error != FC2_ERROR_OK.value:
			print("Error in fc2GetNumOfCameras: " + str(error))
		if self._numCameras == 0:
			print("No Cameras detected")
		
		#get the first camera
		error = fc2GetCameraFromIndex(self._context, 0, self._guid)
		if error != FC2_ERROR_OK.value:
			print("Error in fc2GetCameraFromIndex: " + str(error))
		
		error = fc2Connect(self._context, self._guid)
		if error!= FC2_ERROR_OK.value:
			print("Error in fc2Connect: " + str(error))		