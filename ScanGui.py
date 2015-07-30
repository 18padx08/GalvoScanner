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
		self.checkbutton.grid(row=3, column=4)
		if self.gs is not None:
		#add a button to loadConfig
			self.openConfig = Button(frame, text="Open Config File", command=self.openConfigFile)
			self.openConfig.grid(row=1, column=0, columnspan=2)
		
		#add a button to start the scanning
			self.startScan = Button(frame, text="Start Scan", command=lambda: self.startScanning(master=frame))
			self.startScan.grid(row=2,column=0)
		
		#add button to stop scanning
			self.stopScan = Button(frame, text ="Stop Scan", command=self.gs.stopScan)
			self.stopScan.grid(row=2,column=1)
		
		#button for showing hbt
		self.hbtButton = Button(frame, text="HBT", command=partial(self.showHBT, master=frame))
		self.hbtButton.grid(row=8, column=4)
		
		#entry fields for binWidth and binCount
		self.binWidth = StringVar()
		self.binCount = StringVar()
		widthlabel = Label(frame, text="Time Resolution")
		countLabel = Label(frame, text="binCount")
		self.widthEntry = Entry(frame, variable=binWidth)
		self.countEntry = Entry(frame, variable=binCount)
		self.binCount.set("20")
		self.binWidth.set("21")
		self.widthlabel.grid(row=0, column=3)
		self.widthEntry.grid(row=0, column=4)
		self.countLabel.grid(row=1, column=3)
		self.countEntry.grid(row=1,column=4)
		
		#add menu
		self.menu = Menu(master)
		self.menu.add_command(label="Parse Hook", command=self.loadHookFile)
		
		
		master.config(menu=self.menu)
		#start gui
		#register our eventhandling
		self.mainloop = Events.TkInterCallback(frame)
		#start eventhandling thread
		self.mainloop()
		self.mainloop["ratePlot"] = (partial(self.gs.plotCurrentRate, frame), False)
		#start TK main thread for input handling 
		master.mainloop()
		self.mainloop.stopUpdates()
		self.gs.ReleaseObjects()
		self.gs = None
	
	def showHBT(self, master=None):
		self.mainloop["HBT"] = (partial(self.gs.showHBT, master=master), False)
	
	def checkButtonChanged(self, event):
		if self.v.get() == 0:
			#offvalue
			self.gs.autoscale = False
		else:
			self.gs.autoscale = True
	
	def stopScanning(self):
		#self.startScan.config(state=NORMAL)
		#self.stopScan.config(state=DISABLED)
		self.mainloop["stop scanning"] = (self.gs.stopScan, False)
		
	def ValueChanged(self, value):
		print("set slider value", value)
		self.gs.setFocus(float(value))
	def startScanning(self, master=None):
		#self.startScan.config(state=DISABLED)
		#self.stopScan.config(state=NORMAL)
		self.mainloop["scanning"] = (partial(self.gs.scanSample, master=master), False)
		
		#self.startScan.config(state=NORMAL)
		#self.stopScan.config(state=DISABLED)
	
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