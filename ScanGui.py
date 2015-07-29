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
		self.scale = Scale(frame,from_=0, to=5, resolution=0.001, orient=HORIZONTAL)
		self.scale.grid(row=0,column=1)
		
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
			
		
		#add menu
		self.menu = Menu(master)
		self.menu.add_command(label="Parse Hook", command=self.loadHookFile)
		
		master.config(menu=self.menu)
		#start gui
		self.mainloop = Events.TkInterCallback(frame)
		self.mainloop()
		master.mainloop()
		self.mainloop.stopUpdates()
		self.gs.ReleaseObjects()
		self.gs = None
	
	def stopScanning(self):
		#self.startScan.config(state=NORMAL)
		#self.stopScan.config(state=DISABLED)
		self.mainloop["stop scanning"] = (self.gs.stopScan, False)
		
	
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
			func = getattr(self.gs, hookName)
			func()
		except:
			messagebox.showerror("HookError", sys.exc_info()[0])