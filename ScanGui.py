#conditional module loading python 2/3
try:
	from tkinter import *
	import tkinter.messagebox as messagebox, tkinter.filedialog as filedialog
except ImportError:
	from Tkinter import *
	import tkMessageBox as messagebox, tkFileDialog as filedialog
try:
	import Scanner
except:
	pass
import sys
from functools import partial
import Events
import time

class ScanGui:
	def __init__(self):
		master = Tk()
		
		try:
			self.gs = Scanner.Scanner()
		except(Exception):
			messagebox.showerror("Init Scanner failed", sys.exc_info()[0])
			self.gs = None
		#add our gui to the master Widget
		frame = Frame(master)
		frame.pack()
		
		#we need one slider for focus
		self.scaleLabel = Label(frame, text="Focus: ")
		self.scaleLabel.grid(row=0, column=0)
		self.scale = Scale(frame,from_=0, to=5, resolution=0.001, orient=HORIZONTAL, command=self.ValueChanged)
		self.scale.grid(row=0,column=1)
		#a checkbox for switching autoscale off or on
		self.v = IntVar()
		self.checkbutton = Checkbutton(frame,text="Autoscale", variable=self.v, command=self.checkButtonChanged)
		self.checkbutton.select()
		self.checkbutton.grid(row=3, column=5)
		#add a button to loadConfig
		self.openConfig = Button(frame, text="Open Config File", command=self.openConfigFile)
		self.openConfig.grid(row=1, column=0, columnspan=2)
		
	#add a button to start the scanning
		self.startScan = Button(frame, text="Start Scan", command=lambda: self.startScanning(master=frame))
		self.startScan.grid(row=2,column=0)
	
	#add button to stop scanning
		self.stopScan = Button(frame, text ="Stop Scan", command=self.gs.stopScan)
		self.stopScan.grid(row=2,column=1)
		#button for saving the state
		self.saveStateButton = Button(frame, text="Save state", command=self.saveStateDialog)
		self.saveStateButton.grid(row=3, column=2)
		#button for taking a picture with the ccd
		self.ccdPic = Button(frame, text="Take Picture", command=self.takePictureDialog)
		self.ccdPic.grid(row=3, column=3)
		#button for resetting position
		self.resetPos = Button(frame, text="Goto 0/0", command=partial(self.gs.setPoint,0,0))
		self.resetPos.grid(row=3,column=4)
		
		#Xslider
		self.xsliderLabel = Label(frame, text="Y: ")
		self.xsliderLabel.grid(row=0, column=5)
		self.xslider = Scale(frame,from_=-0.03, to=0.03, resolution=0.00001, orient=HORIZONTAL, command=self.setX)
		self.xslider.grid(row=0,column=6)
		
		#Yslider
		self.xsliderLabel = Label(frame, text="X: ")
		self.xsliderLabel.grid(row=0, column=7)
		self.xslider = Scale(frame,from_=-0.03, to=0.03, resolution=0.00001, orient=HORIZONTAL, command=self.setY)
		self.xslider.grid(row=0,column=8)
		
		self.angleButton = Button(frame, text="Show Angle", command=partial(self.showAngle, master=frame))
		self.angleButton.grid(row=0, column=9)
		#button for showing hbt
		self.hbtButton = Button(frame, text="HBT", command=partial(self.showHBT, master=frame))
		self.hbtButton.grid(row=1, column=5)
		self.hbtStopButton = Button(frame, text="Clear HBT", command=self.hideHBT)
		self.hbtStopButton.grid(row=1,column=6)
		self.hbtUnRunButton = Button(frame, text="Stop HBT", command=self.stopHBT)
		self.hbtUnRunButton.grid(row=1,column=7)
		#checkbox for correction of HBT
		self.corr= IntVar()
		self.correctionCheck = Checkbutton(frame, text="Correction", variable=self.corr, command=self.checkCorrection)
		self.correctionCheck.grid(row=1, column=8)
		self.correctionSigToBack = StringVar()
		self.correctionTextField = Entry(frame, textvariable=self.correctionSigToBack)
		self.correctionTextField.grid(row=1, column=9)
		self.correctionSigToBack.set("0.5")
		#checkbox for normalization
		self.norm = IntVar()
		self.normCheck = Checkbutton(frame, text="Nomralization", variable=self.norm,command=self.checkNormalization)
		self.normCheck.grid(row=2,column=8)
		#entry fields for binWidth and binCount
		self.binWidth = StringVar()
		self.binCount = StringVar()
		self.widthlabel = Label(frame, text="Time Resolution")
		self.countLabel = Label(frame, text="binCount")
		self.widthEntry = Entry(frame, textvariable=self.binWidth)
		self.countEntry = Entry(frame, textvariable=self.binCount)
		self.binCount.set("20")
		self.binWidth.set("1")
		self.widthlabel.grid(row=0, column=3)
		self.widthEntry.grid(row=0, column=4)
		self.countLabel.grid(row=1, column=3)
		self.countEntry.grid(row=1,column=4)
		
		#add menu
		self.menu = Menu(master)
		self.menu.add_command(label="Parse Hook", command=self.loadHookFile)
		
		#add reference to ourself so we have access to the ui thread
		self.gs.refToMain = self
		
		master.config(menu=self.menu)
		#start gui
		#register our eventhandling
		self.mainloop = Events.TkInterCallback(frame)
		#start eventhandling thread
		try:
			self.gs.setPoint(0,0)
			self.gs.setFocus(0)
			self.mainloop["ratePlot"] = (partial(self.gs.plotCurrentRate, frame), False)
			self.mainloop["checkForMax"] = (self.gs.checkForMax, True, 10)
			self.mainloop()
			master.mainloop()
			#start TK main thread for input handling 
			self.mainloop.stopUpdates()
		except RuntimeError:
			print("oooops")
		self.mainloop.stopUpdates()
		self.gs.ReleaseObjects()
		self.gs = None

	
	def createCanvas(self, figure, master):
		from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
		return FigureCanvasTkAgg(figure, master=master)
	def createToolbar(self, canvas, master):
		from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
		return NavigationToolbar2TkAgg(canvas, master)
	def createFrame(self,master):
		return Frame(master)
	def showHBT(self, master=None):
		if "HBT" in self.mainloop:
			#there is a process running, stop it
			self.gs.hbtLoop = False
			time.sleep(0.8)
		self.mainloop["HBT"] = (partial(self.gs.showHBT, binWidth=float(self.binWidth.get()), binCount=int(self.binCount.get()), master=master), False)
	def hideHBT(self):
		self.gs.hbtRunning = False
	def stopHBT(self):
		self.gs.hbtLoop = False
	
	def showAngle(self, master=None):
		messagebox.showinfo("Angles", "Phi: %s, Theta: %s"%(self.gs.currentVoltagePhi,self.gs.currentVoltageTheta))
	
	def checkButtonChanged(self):
		if self.v.get() == 0:
			#offvalue
			self.gs.autoscale = False
		else:
			self.gs.autoscale = True
	
	def checkCorrection(self):
		if self.corr.get() == 0:
			self.gs.signalCorrection = False
		else:
			self.gs.sigToBack = float(self.signalCorrection.get())
			self.gs.signalCorrection = True
	
	def checkNormalization(self):
		if self.norm.get() == 0:
			self.gs.doNormalization = False
		else:
			self.gs.doNormalization = True
	
	def stopScanning(self):
		#self.startScan.config(state=NORMAL)
		#self.stopScan.config(state=DISABLED)
		self.mainloop["stop scanning"] = (self.gs.stopScan, False)
		
	def ValueChanged(self, value):
		print("set slider value", value)
		self.gs.setFocus(float(value))
		
	def setX(self, value):
		try:
			self.gs.setX(float(value), True)
		except(Exception):
			print("X Outside Range")
	def setY(self, value):
		try:
			self.gs.setY(float(value), True)
		except(Exception):
			print("Y Outside Range")
	def startScanning(self, master=None):
		#self.startScan.config(state=DISABLED)
		#self.stopScan.config(state=NORMAL)
		self.mainloop["scanning"] = (partial(self.gs.scanSample, master=master, refToMain=self), False)
		#self.mainloop["stayonmax"] = (self.gs.findMax(), True, 10)
		#self.startScan.config(state=NORMAL)
		#self.stopScan.config(state=DISABLED)
	
	def saveStateDialog(self):
		f = filedialog.asksaveasfilename(filetypes=[("Numpy Binary", "*.npy")])
		if f:
			self.gs.saveState(f)

	def takePictureDialog(self):
		f=filedialog.asksaveasfilename(filetypes=[("PNG", "*.png")], defaultextension=".png")
		if f:
			self.gs.takePicture(f)

	def openConfigFile(self):
		f = filedialog.askopenfile(filetypes=[("ConfigFile", "*.cfg")])
		if f is not None: 
			self.gs.loadConfig(f.name)
	def loadHookFile(self):
		f = filedialog.askopenfile(filetypes=[("HookFile", "*.hk")])
		if f is not None:
			hookName = self.gs.parseHook(f.name)
			self.menu.add_command(label=hookName, command=partial(self.startHook, hookName))
	
	def startHook(self, hookName):
		try:
			print("try to start hook: ", hookName)
			func = getattr(self.gs, hookName)
			func()
		except:
			messagebox.showerror("HookError", sys.exc_info()[0])