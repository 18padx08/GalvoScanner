from PyDAQmx import *
import numpy
import random

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
		self.currentVoltage = 0
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
		self.analog_outputPhi = Task()
		self.analog_outputPhi.CreateAOVoltageChan(devicePhi,"",-10.0,10.0,DAQmx_Val_Volts,None)
		self.analog_outputPhi.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,100)
		
		self.analog_outputTheta = Task()
		self.analog_outputTheta.CreateAOVoltageChan(deviceTheta,"",-10.0,10.0,DAQmx_Val_Volts,None)
		self.analog_outputTheta.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,100)
		
		
	#get state of galvo -> return angle in degree
	def getAnglePhiDegree(self):
		return self.currentGalvoPhi * (180./numpy.pi)
	def getAngleThetaDegree(self):
		return self.currentGalvoTheta * (180./numpy.pi)
	
	#setAngles for the galvo (enter values in degree), private: use setX and setY for public access
	def __setPhi(self, phi):
		voltage = self.sensitivityDeg * phi
		data = numpy.zeros((100,), dtype=numpy.float64)
		data[0:100] = voltage
		
		#set the state of the object
		self.currentVoltage = voltage
		self.currentGalvoPhi = phi
		
		#write to the output channel
		self.analog_outputPhi.WriteAnalogF64(100,True,-1,DAQmx_Val_GroupByChannel ,data,None,None)
	def __setPhiRad(self, phiRad):
		self.__setPhi(180./numpy.pi * phiRad)
		
	def __setTheta(self, theta):
		voltage = self.sensitivityDeg * theta
		data = numpy.zeros((100,), dtype=numpy.float64)
		data[0:100] = voltage
		
		#set the state of the object
		self.currentVoltage = voltage
		self.currentGalvoTheta = theta
		
		#write to the output channel
		self.analog_outputTheta.WriteAnalogF64(100,True,-1,DAQmx_Val_GroupByChannel ,data,None,None)
	def __setThetaRad(self, thetaRad):
		self.__setTheta(180./numpy.pi * thetaRad)
		
	def ReleaseObjects(self):
		self.analog_outputPhi.StopTask()
		self.analog_outputPhi.ClearTask()
		self.analog_outputTheta.StopTask()
		self.analog_outputTheta.ClearTask()
		
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