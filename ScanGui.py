from Tkinter import *
import tkFileDialog, tkMessageBox
import Scanner
import sys

class ScanGui:
	def __init__(self):
		master = Tk()
		
		try:
			self.gs = Scanner.Scanner()
		except(Exception):
			tkMessageBox.showerror("Init Scanner failed", sys.exc_info()[0])
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
		
		#add a button to start the scanning
			self.startScan = Button(frame, text="Start Scan", command=self.gs.scanSample())
		
		
		#start gui
		master.mainloop()
	
	def openConfigFile(self):
		self.gs.loadConfig(tkFileDialog.askopenfile(filetypes=[("PythonFile", "*.py")]).name)