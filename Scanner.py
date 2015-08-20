from PyDAQmx import *
import numpy
import matplotlib.pyplot as plt
import random
import time	
from pyflycam import *
from qupsi import *

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
		self.testData = []
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
		self.autoscale = True
		self.hbtLoop = False
		self.baseVoltage = 5
		TDC_init(-1)
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

		self.dataArray = numpy.ones((len(self.ysteps),len(self.xsteps)), dtype=numpy.float64)
		
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
		self.initCamera()
				#if we have a focus point set it
		#init the piezo to full focal 
		self.setFocus(0)
		if hasattr(self, "focus"):
			self.setFocus(self.focus)
		if(hasattr(self, "imageSettings")):
			self.setImageProperties(self.imageSettings['gain'], self.imageSettings['shutter'])	
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
		self.dataArray = numpy.ones((len(self.ysteps),len(self.xsteps)), dtype=numpy.float64)

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
	
	def findMaximumX(self, oldMax, step=0.0002):
		#we try to find the new maximum in all three dims
		#first move in x
		tmpB = c_int *19
		tmpBuffer = tmpB()
		tmpX = self.currentX
		max = oldMax
		self.setX(tmpX + step)
		TDC_getCoincCounters(tmpBuffer)
		countsA = numpy.sum(tmpBuffer)/0.032
		#try to go a step back
		self.setX(tmpX - step)
		TDC_getCoincCounters(tmpBuffer)
		countsB = numpy.sum(tmpBuffer)/0.032
		diff = countsA-countsB
		print("diff is: ", diff)
		if abs(diff) >  1.5 *numpy.sqrt(oldMax):
			#so go half the step size to the right
			if diff < 0:
				self.setX(tmpX - step/2.0)
			else:
				self.setX(tmpX + step / 2.0)
		else:
			return oldMax
		time.sleep(0.032)
		TDC_getCoincCounters(tmpBuffer)
		counts = numpy.sum(tmpBuffer)/0.032
		max = self.findMaximumX(counts, step=step/2.0)
		#we did not find any maximum go back to origin
		tmpB = None
		tmpBuffer = None
		return max
	def findMaximumY(self, oldMax, step=0.0002):
		#we try to find the new maximum in all three dims
		#first move in x
		tmpB = c_int *19
		tmpBuffer = tmpB()
		tmpY = self.currentY
		max = oldMax
		self.setY(tmpY + step)
		TDC_getCoincCounters(tmpBuffer)
		countsA = numpy.sum(tmpBuffer)/0.032
		#try to go a step back
		self.setY(tmpY - step)
		TDC_getCoincCounters(tmpBuffer)
		countsB = numpy.sum(tmpBuffer)/0.032
		diff = countsA-countsB
		if abs(diff) > 1.5 *numpy.sqrt(oldMax):
			#so go half the step size to the right
			if diff < 0:
				self.setY(tmpY - step/2.0)
			else:
				self.setY(tmpY + step / 2.0)
		else:
			return oldMax
		time.sleep(0.032)
		TDC_getCoincCounters(tmpBuffer)
		counts = numpy.sum(tmpBuffer)/0.032
		max = self.findMaximumY(counts, step=step/2.0)
		#we did not find any maximum go back to origin
		tmpB = None
		tmpBuffer = None
		return max				
		#we did not find any maximum go back to origin
		
		self.setY(tmpY)
		print("max and oldmax are the same", oldMax, max)
		tmpB = None
		tmpBuffer = None
		return oldMax

	def findMax(self):
		#lets start finding the maximum
		tmpB = c_int *19
		tmpBuffer = tmpB()
		TDC_getCoincCounters(tmpBuffer)
		counts = numpy.sum(tmpBuffer)
		newmax = self.findMaximumX(counts)
		newmax = self.findMaximumY(newmax)
		tmpB = None
		tmpBuffer = None

	def callbackFactory(self, callback, args):
		return lambda: getattr(self, callback.strip())(args)
	
	def parseHook(self, hookFile):
		keywords = { }
		tmpHookName = hookFile
		#compile a regular expression, so that we have fname(**args) and then call the appropriate function
		#or match variable declarations var = value
		import re
		functionCallPattern = re.compile("\w+\s*\([\s\w\/\,\.\_\-\!\$\?]*\)")
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
							if functionName == "plot3dmap":
								body += [self.callbackFactory(functionName, args)]
							else:
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
			return tmpHookName
	#get state of galvo -> return angle in degree
	def getAnglePhiDegree(self):
		return self.currentGalvoPhi * (180./numpy.pi)
	def getAngleThetaDegree(self):
		return self.currentGalvoTheta * (180./numpy.pi)
	
	def stopScan(self):
		self.interrupt = True
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
		if self.baseVoltage - voltage < 0:
			raise(VoltageCannotBeNegativeException)
		v = self.baseVoltage - voltage
		data = numpy.zeros((300,), dtype=numpy.float64)
		data[:100] = self.currentVoltagePhi
		data[100:200] = self.currentVoltageTheta
		data[200:] = v
		#set the state of the object
		self.currentPiezoVoltage = v
		
		#write to the output channel
		self.analog_output.WriteAnalogF64(100,False,-1,DAQmx_Val_GroupByChannel ,data,None,None)
		self.analog_output.StartTask()
		
		self.analog_output.StopTask()
		
	#setAngles for the galvo (enter values in degree), private: use setX and setY for public access
	def __setPhi(self, phi):
		voltage = self.sensitivityDeg * phi + self.calibrationPhi
		data = numpy.zeros((300,), dtype=numpy.float64)
		data[:100] = voltage
		data[100:200] = self.currentVoltageTheta
		data[200:] = self.currentPiezoVoltage
		self.testData = data
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
		data[:100] = self.currentVoltagePhi
		data[100:200] = voltage
		data[200:] = self.currentPiezoVoltage
		self.testData = data
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
		TDC_deInit()
		
		
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
		numpy.savetxt(name+".csv", self.dataArray, delimiter=',')
	
	def goTo(self, x, y):
		self.setPoint( self.xsteps[int(x)], self.ysteps[int(y)])
	
	def showHistogram(self):
		plt.clf()
		plt.scatter(self.dataArray)
		plt.hist2d(self.dataArray)
		
	def plot3dmap(self, data, maskvalue=50000, multiple=False, fig=None):
		plt.clf()
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
	
		c = numpy.array(zlayers)
		c = c.reshape(xdim*ydim*zdim,order='F')
		c = numpy.ma.masked_less(c, maskvalue)
		
		print("shapes", x.shape, y.shape,z.shape, c.shape)
		#now we have prepared our data lets plot
		from mpl_toolkits.mplot3d import Axes3D 
		import matplotlib.pyplot as plt 
		import numpy as np 
		
		#if not multiple we get a figure object so add our plot as a add_subplot
		if not multiple:	
			fig = plt.figure(1)
		ax = fig.add_subplot(111, projection='3d') 
		sc = ax.scatter(x,y,z,c=c, cmap=plt.hot())
		plt.colorbar(sc)
		
		#if we have multiple ones, we dont want to show the plot
		if not multiple:
			plt.show()
			plt.savefig("3dplot.jpeg")
	
	def processMouseClick(self, event):
		print("Mouse clicked at, ", event.xdata, event.ydata)
		if self.interrupt and event.xdata is not None and event.ydata is not None:
			print(self.currentX)
			self.goTo(int(event.xdata) if event.xdata > 0 else 0, int(event.ydata) if event.ydata > 0 else 0)
			#self.findMax()
			print(self.currentX)
			
	def plotCurrentRate(self, master=None, refToMain=None):
		if master is not None:
			try:
				import tkinter as Tk
			except ImportError:
				import Tkinter as Tk
			from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
		from matplotlib.figure import Figure
		f = Figure(figsize=(3,1.5), dpi=100)
		f.subplots_adjust(left=0.2)
		fplt = f.add_subplot(111)
		for item in ([fplt.title, fplt.xaxis.label, fplt.yaxis.label] +fplt.get_xticklabels() + fplt.get_yticklabels()):
			item.set_fontsize(8)
		try:
				import Tkinter as tk
		except ImportError:
				import tkinter as tk
		if refToMain is not None:
			toolbar_frame = refToMain.createFrame(master)
		else:
			toolbar_frame = tk.Frame(master)
		toolbar_frame.grid(row=4,column=4, columnspan=3, rowspan=3)
		if refToMain is not None:
			ratePlot = refToMain.createCanvas(f, toolbar_frame)
		else:
			ratePlot = FigureCanvasTkAgg(f, master=toolbar_frame)
		ratePlot.show()
		ratePlotWidget =ratePlot.get_tk_widget()
		#register mouse callback to be able to navigate to
		#f.canvas.mpl_connect('pick_event', self.processMouseClick)
		ratePlotWidget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		#add the toolbar 
		currentRate = []
		t = []
		tmpB = c_int *19
		tmpBuffer = tmpB()
		ratep  = fplt.plot(t, currentRate)
		fplt.set_xlim([0,100])
		i=0
		filled = False
		import threading
		while True:
			ret = TDC_getCoincCounters(tmpBuffer)
			if len(currentRate) > 100:
				currentRate = currentRate[1:]
				filled = True
			currentRate += [numpy.sum(tmpBuffer)/0.032]
			if not filled:
				t += [i]
				i+=1
			ratep[0].set_data(t,currentRate)
			if not self.autoscale:
				fplt.set_ylim([0, 200000])
			else:
				fplt.set_ylim([0, numpy.max(currentRate)])
			
			f.canvas.draw()
			#ratep[0].set_clim(numpy.min(currentRate), numpy.max(currentRate))
	def showHBT(self, binWidth=1, binCount=20, master=None, refToMain=None):
		self.hbtRunning = True
		self.hbtLoop = True
		#its irritating, binwidth is actually the TDC_timeBase Resolution, that means binWidth corresponds to the time in ns 
		if master is not None:
			#import according to python version (2 or 3)
			try:
				import tkinter as Tk
			except ImportError:
				import Tkinter as Tk
			from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
			TDC_enableHbt(True)
			#we need to set binWidth according to TDC_timeBase
			timeBase = TDC_getTimebase()
			#time base is the resolution in seconds, so 
			rightBinWidth = int((binWidth*1.0e-9) / timeBase)
			#first set histogram parameter
			print(timeBase, rightBinWidth, binCount)
			TDC_setHbtParams(rightBinWidth,binCount)
			#set up array with at least binCount elements

			from matplotlib.figure import Figure
			histFig = Figure(figsize=(5,3), dpi=100)
			histFig.subplots_adjust(left=0.2)
			histAx = histFig.add_subplot(111)
			for item in ([histAx.title, histAx.xaxis.label, histAx.yaxis.label] +histAx.get_xticklabels() + histAx.get_yticklabels()):
				item.set_fontsize(8)
			dataArray = numpy.zeros((binCount*2-1,))
			t = numpy.linspace(-(binCount), binCount-1, 2*binCount-1)
			if master is None:
				plt.clf()
				plt.ion()
				print("I WANT DATA", len(t), len(dataArray))
				self.histo = histAx.bar(t,dataArray)#, norm=LogNorm(vmin=100, vmax=1000000))
			else:
				print("I WANT DATA", len(t), len(dataArray))
			#if the canvas exists just set the data
				self.histo = histAx.bar(t,dataArray)#, norm=LogNorm(vmin=100, vmax=1000000))
			#self.imgplot.set_data(self.dataArray)
		
		if master is not None and not hasattr(self,"histoCanvas"):
			#if the canvas is not allready shown show it
			try:
				import Tkinter as tk
			except ImportError:
				import tkinter as tk
			if refToMain is not None:
				toolbar_frame = refToMain.createFrame(master)
			else:
				toolbar_frame = tk.Frame(master)
			toolbar_frame.grid(row=7,column=4, columnspan=5, rowspan=3)
			if refToMain is not None:
				histoCanvas = refToMain.createCanvas(histFig, toolbar_frame)
			else:
				histoCanvas = FigureCanvasTkAgg(histFig, master=toolbar_frame)
			histoCanvas.show()
			histoWidget =histoCanvas.get_tk_widget()
			
			histoWidget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
			
			#for normalization we need the integration time
			startTime = time.time()
			hbtFunction = TDC_createHbtFunction()
			self.signalCorrection = False
			while self.hbtLoop:
				#retrieve histogram
				print("in loop", self.hbtRunning)
				if not self.hbtRunning:
					#reset the histogram
					print("reset TDC_getHbtCorrelations")
					#TDC_resetHbtCorrelations()
					TDC_calcHbtG2(hbtFunction)
					startTime = time.time()
					#be sure to not have a time diff of 0 seconds... (otherwise we divide by zero)
					endTime = time.time()+1
					self.hbtRunning = True
					print("clear data")
				else:
					TDC_calcHbtG2(hbtFunction)
					endTime = time.time()
				dataArray = numpy.array(hbtFunction[0][:], dtype=numpy.float64)
				datalen = len(dataArray)
				print(hbtFunction[0].indexOffset)
				histAx.cla()
				#normalize data (we assume to have a probabilty of one at large taus, so take the midvalue of the last 5 elements on each side)
				#print(numpy.concatenate((dataArray[:5], dataArray[-5:])))
				normConst = numpy.mean(numpy.concatenate((dataArray[:5], dataArray[-5:])))
				#if normConst > 0:
					#dataArray /= normConst
				
				#TODO make correction not static
				#we assume a poor signal to background noise of 0.5
				if self.signalCorrection:
					dataArray = (dataArray-(1-0.5**2))/0.5**2
					b = dataArray<0
					dataArray[b] = 0
				histAx.set_ylim([numpy.min(dataArray), numpy.max(dataArray)])
				self.histo = histAx.plot(t,dataArray)
				histFig.canvas.draw()
				#only update every second
				time.sleep(1)
			
			dataArray = None
			
	
		
	def scanSample(self, master=None, refToMain=None):
		#at start we clearly have no interrupt
		self.interrupt = False
		#clear data array
		self.dataArray = numpy.ones((len(self.ysteps),len(self.xsteps)), dtype=numpy.float64)
		try:
			import tkinter as Tk
		except ImportError:
			import Tkinter as Tk
		from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
		countX = 0
		countY = 0
		from matplotlib.colors import LogNorm
		from matplotlib.figure import Figure
		f = Figure(figsize=(8,4), dpi=100)
		f.subplots_adjust(left=0.2)
		self.fplt = f.add_subplot(111)
		#f.tight_layout()
		self.imgplot = self.fplt.imshow(self.dataArray, animated=True)#, norm=LogNorm(vmin=100, vmax=1000000))
		self.imgplot.set_interpolation('none')
		if hasattr(self,"canvas"):
			self.canvas.get_tk_widget().grid_forget()
			self.canvas = None
		#if the canvas is not allready shown show it
		try:
			import Tkinter as tk
		except ImportError:
			import tkinter as tk
		if refToMain is not None:
			toolbar_frame = refToMain.createFrame(master)
		elif hasattr(self, "refToMain"):
			toolbar_frame = self.refToMain.createFrame(master)
		else:
			toolbar_frame = tk.Frame(master)
		toolbar_frame.grid(row=4,column=0, columnspan=4, rowspan=6)
		#if we have a ref to main try to execute the gui generation on the main thread
		if refToMain is not None:
			self.canvas = refToMain.createCanvas(f, toolbar_frame)
		elif hasattr(self, "refToMain"):
			self.canvas = self.refToMain.createCanvas(f, toolbar_frame)
		else:
			self.canvas = FigureCanvasTkAgg(f, master=toolbar_frame)
		self.canvas.show()
		canvasWidget =self.canvas.get_tk_widget()
		#register mouse callback to be able to navigate to
		f.canvas.mpl_connect('button_press_event', self.processMouseClick)
		canvasWidget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		
		tmpB = c_int *19
		tmpBuffer = tmpB()
		sleepTime = 0.032
		exposureTime = int(sleepTime *1000)
		TDC_setExposureTime(exposureTime)
		for i in self.ysteps:
			countX = 0
			for o in self.xsteps:
				#navigate to location
				self.setPoint( o, i)
				#retrieve count rate from adp
				ret = TDC_getCoincCounters(tmpBuffer)
				
				#set the count rate (the value we get is the pure count number, so divide by exposure time)
				self.dataArray[countY][countX] = numpy.sum(tmpBuffer) / sleepTime
							
				countX += 1
				#set data and new limits for better color plotting
				self.imgplot.set_data(self.dataArray)
				self.imgplot.set_clim(numpy.min(self.dataArray), numpy.max(self.dataArray))
				
				#update the canvas with the new data
				f.canvas.draw()
				
				if self.interrupt:
					#if we have an interrupt stop scanning and clean the resources
					#update the master (we only can get interrupts from the gui, so its save to assume that master is not None)
					master.update()
					
					#clear the buffer, otherwise we get memory leaks and issues which let the python interpreter crash)
					tmpBuffer = None
					tmpB = None
					
					#navigate back to origin
					self.setPoint(0,0)
					return
			countY += 1
		if master is None:
			#only save the sample scan if we are not from gui (otherwise we see it there...)
			plt.savefig("sampleScan.jpeg")
			plt.ioff()	

		#same as for the interrupt
		tmpB = None
		tmpBuffer = None
	
	def takePicture(self, name):
		if not hasattr(self, "_context"):
			self.initCamera()
		
		fc2StartCapture(self._context)
		#create the two pictures one for getting input the other to save
		rawImage = fc2Image()
		convertedImage = fc2Image()
		fc2CreateImage(rawImage)
		fc2CreateImage(convertedImage)
		
		fc2RetrieveBuffer(self._context, rawImage)
		self.savePicture(name, rawImage, convertedImage)
		
		fc2DestroyImage(rawImage)
		fc2DestroyImage(convertedImage)
		fc2StopCapture(self._context)
		
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