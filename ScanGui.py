from tkinter import *
import tkinter.messagebox as messagebox, tkinter.filedialog as filedialog
import Scanner
import sys

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
		self.scaleLabel.pack()
		self.scale = Scale(frame,from_=0, to=5, resolution=0.001, orient=HORIZONTAL)
		self.scale.pack()
		
		if self.gs is not None:
		#add a button to loadConfig
			self.openConfig = Button(frame, text="Open Config File", command=self.openConfigFile)
			self.openConfig.pack()
		
		#add a button to start the scanning
			self.startScan = Button(frame, text="Start Scan", command=self.gs.scanSample)
			self.startScan.pack()
		
		
		#start gui
		master.mainloop()
		self.gs.ReleaseObjects()
		self.gs = None
	
	def openConfigFile(self):
		f = filedialog.askopenfile(filetypes=[("ConfigFile", "*.cfg")])
		if f is not None: 
			self.gs.loadConfig(f.name)