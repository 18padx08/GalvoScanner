from PyDAQmx import *
import numpy
import random
import time	
from pyflycam import *

#pillow.readthedocs.org/ for image manipulation

#PIL.ImageChops.composite(image1, image2, mask)

#################################################################################
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


#################################################################

class Scanner:
	#scanner class: needs sampleSize (to calculate the max and min angles for the galvo) and 
	#               the distance from the galvo to the lens
	
	#sensitivity of the galvo in volt per rad
	sensitivityRad = 90.0/numpy.pi
	sensitivityDeg = 0.5
	
	# arguments: all units in mm, devicePhi for Xtranslation, devicetheta for Ytranslation
	def __init__(self, sampleSize, sampleDistance,beamDiameter = 5, lens = Lens(1.3,1.5), devicePhi = "Dev2/ao1", deviceTheta = "Dev2/ao0"):
		#local variables rerpresenting the sate of the scanner
		self.currentX = 0
		self.currentY = 0
		self.currentVoltagePhi = 0
		self.currentVoltageTheta = 0
		self.sampleSize = Size(sampleSize.height, sampleSize.width)
		self.sampleDistance = sampleDistance
		self.currentGalvoPhi = 0
		self.currentGalvoTheta = 0
		self.lens = lens
		
		#max and min x are half the sample size since we place the sample in such a way that it is centered arround the
		#origin of lens
		self.maxX = sampleSize.width/2.0
		self.minX = -sampleSize.width/2.0
		
		self.maxY = sampleSize.height / 2.0
		self.minY = -sampleSize.height / 2.0
		
		#prepare the output channels
		self.analog_output = Task()
		self.analog_output.CreateAOVoltageChan(",".join([devicePhi, deviceTheta]),"",-10.0,10.0,DAQmx_Val_Volts,None)
		#self.analog_output.CreateAOVoltageChan(deviceTheta,"",-10.0,10.0,DAQmx_Val_Volts,None)
		self.analog_output.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,100)
		time.sleep(2)
		
		
	#get state of galvo -> return angle in degree
	def getAnglePhiDegree(self):
		return self.currentGalvoPhi * (180./numpy.pi)
	def getAngleThetaDegree(self):
		return self.currentGalvoTheta * (180./numpy.pi)
	
	#setAngles for the galvo (enter values in degree), private: use setX and setY for public access
	def __setPhi(self, phi):
		voltage = self.sensitivityDeg * phi +1.0
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
	def __setPhiRad(self, phiRad):
		self.__setPhi(180./numpy.pi * phiRad)
		
	def __setTheta(self, theta):
		voltage = self.sensitivityDeg * theta
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
	def __setThetaRad(self, thetaRad):
		self.__setTheta(180./numpy.pi * thetaRad)
		
	def ReleaseObjects(self):
		self.analog_output.StopTask()
		self.analog_output.ClearTask()
		
		
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
		
	def scanSample(self):
		#init camera
		self.initCamera()
		#start capturing pictures
		fc2StartCapture(self._context)
		
		#create the two pictures one for getting input the other to save
		rawImage = fc2Image()
		convertedImage = fc2Image()
		fc2CreateImage(rawImage)
		fc2CreateImage(convertedImage)
		
		self.setPoint(self.minX, self.minY)
		for i in numpy.linspace(0,self.maxY, 10):
			for o in numpy.linspace(0, self.maxX, 10):
				#get picture
				fc2RetrieveBuffer(self._context, rawImage)
				ts = fc2GetImageTimeStamp(rawImage)
				#print(ts.cycleCount)	
				self.savePicture("[%f %f].png"%(o, i), rawImage, convertedImage)
				#go one step further			
				self.setPoint(self.minX + o, self.minY + i)


		#after we are done scanning stop Capturing 
		fc2DestroyImage(rawImage)
		fc2DestroyImage(convertedImage)
		fc2StopCapture(self._context)
	
	def savePicture(self, name, rawImage, convertedImage):
		fc2ConvertImageTo(FC2_PIXEL_FORMAT_BGR, rawImage, convertedImage)
		
		fc2SaveImage(convertedImage, name.encode('utf-8'), 6)

		
	
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