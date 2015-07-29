from functools import partial
import threading
import abc

class Callback:
	def __init__(self,parent):
		self.callback_chain = []
		self.currentIndex = 0
		self.parent = parent
		self.running = threading.Event()
		self.running.clear()
		self.chain_lock = threading.RLock()
	
	def __call__(self):
		self.running.set()
		self.updateThread = threading.Thread(target = self.updateLoop, name="MainUpdateLoop")
		self.updateThread.start()
		return self.updateThread
	
	def stopUpdates(self):
		self.running.clear()
	
	def handleErrors(self, error):
		#handle errors occuring during callback_chain
		pass
	
	def updateLoop(self):
		print("in update loop", self.running.is_set())
		self.threads = {}
		self.currentIndex =0

		with self.chain_lock:
			for functions in self.callback_chain:
				#get threads for each functions
				try:
					self.threads += [self.callObject(functions)]
				except:
					self.handleErrors("Error in calling")
		while self.running.is_set():
			#print("im here")
			flagRunning = False
			self.currentIndex = 0
			del_arr = []
			for thread_name in self.threads:
				thread = self.threads[thread_name]
				if thread.is_alive():
					#check if the thread is dead
					flagRunning = True
				elif self.callback_chain[self.currentIndex][1]:
					#if we have a continues thread restart it
					thread.Run()
					flagRunning = True
				else:
					#thread finished and is not continues so clear it from the list
					currentCallback = self.callback_chain[self.currentIndex]
					del_arr += [currentCallback[2]]
					del self.callback_chain[self.currentIndex]
				if self.currentIndex + 1 < len(self.callback_chain):	
					self.currentIndex += 1
			for name in del_arr:
				#remove the entries from the dictionary
				del self.threads[name]
			if not flagRunning:
				#if callback_chain is empty stop updateLoop
				#we may want to continue the loop
				#self.running.clear()
				pass
			#print("propagateUpdate to master")
			#self.propagateUpdate()
	
	@abc.abstractmethod
	def propagateUpdate(self):
		"""Propagate the updaters to the parent"""
		return
	
	def callObject(self, func):
		localthread = threading.Thread(target=func[0])
		localthread.start()
		return localthread
	
	def getEventPointer(self, func, name):
		return partial(func, self)
	
	def __setitem__(self, key, value):
		with self.chain_lock:
			functions = (value[0], value[1], key)
			self.callback_chain += [functions]
			self.threads[key] = self.callObject(functions)
		
		
class TkInterCallback(Callback):
	def propagateUpdate(self):
		#pass
		self.parent.update()
		