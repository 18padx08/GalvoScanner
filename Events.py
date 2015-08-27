from functools import partial
import threading
import abc
import time
try:
	import queue
except:
	import Queue
import sys


class ExThread(threading.Thread):
	def __init__(self, target=None,name=None):
		threading.Thread.__init__(self, target=target, name=name)
		self.__status_queue = queue.Queue()
		self.exc_raised = threading.Event()
		self.exc_raised.clear()
		self.target = target
		self.delay = 0
	def run_with_exception(self):
		print("start thread")
		self.target()
	
	def run(self):
		try:
			if self.delay > 0:
				import time
				time.sleep(self.delay)
			self.target()
		except Exception:
			print("omg i got an exception", sys.exc_info())
			self.__status_queue.put(sys.exc_info())
		self.__status_queue.put(None)
	def runWithDelay(self, delay):
		#import time
		#time.sleep(delay)
		self.run(delay)
	
	def wait_for_exc_info(self):
	    return self.__status_queue.get(timeout=0.1)
	
	def join_with_exception(self):
		try:
			ex_info = self.wait_for_exc_info()
		except queue.Empty:
			return
		if ex_info is None:
			return
		else:
			raise ex_info[1]


class Callback:
	def __init__(self,parent):
		self.callback_chain = []
		self.currentIndex = 0
		self.parent = parent
		self.running = threading.Event()
		self.running.clear()
		self.addItem = threading.Event()
		self.addItem.clear()
		self.removeItem = threading.Event()
		self.removeItem.clear()
		self.chain_lock = threading.RLock()
		self.stoppThread = {}
	
	def __call__(self):
		self.running.set()
		self.updateThread = ExThread(target = self.updateLoop, name="MainUpdateLoop")
		self.updateThread.start()
		return self.updateThread
	
	def stopUpdates(self):
		self.running.clear()
	
	def handleErrors(self, error):
		#handle errors occuring during callback_chain
		pass
	
	#find function by name, return functionobject, index
	
	def findFunctionByName(self, name):
		index = 0
		print("array has size: %d"%len(self.callback_chain))
		for fObj in self.callback_chain:
			print(fObj[2])
			if fObj[2] == name:
				print("return @ %d"%index)
				return (fObj, index)
			index += 1
		return(None,0)
			
	
	def updateLoop(self):
		print("in update loop", self.running.is_set())
		if not hasattr(self, "threads"):
			self.threads = {}

		#with self.chain_lock:
		#	for functions in self.callback_chain:
				#get threads for each functions
		#		try:
		#			self.threads += [self.callObject(functions)]
		#		except:
		#			print("ooops")
		#			self.handleErrors("Error in calling")
		while self.running.is_set():
			#print("im here")
			flagRunning = False
			self.currentIndex = 0
			del_arr = []
			with self.chain_lock:
				for thread_name in self.threads:
					thread = self.threads[thread_name]
					print("check thread[%s]"%thread_name)
					myFunctionObject, ind = self.findFunctionByName(thread_name)
					try:
						thread.join_with_exception()
					except:
						#we had an exception, try to rerun the thread
						thread.run()
					if thread.is_alive():
						#check if the thread is dead
						flagRunning = True
						
					elif myFunctionObject[1]:
						try:
							thread.join_with_exception()
						except Exception:
							print("Thread could not recover")
						else:
						#if we have a continues thread restart it with the delay
						#TODO make delay possible
							print("continues task, rerun it, only if not in stoppThreads")
							#thread.delay = self.callback_chain[self.currentIndex][3]
							if not myFunctionObject[2] in self.stoppThread:
								thread.run()
								print("set delay to %d"%myFunctionObject[3])
								flagRunning = True
							else:
								print("thread was requested to stop")
								del_arr += [myFunctionObject[2]]
								del self.callback_chain[ind]
								del self.stoppThread[myFunctionObject[2]]
								self.currentIndex -= 1
							#thread.run()

					else:
						try:
							thread.join_with_exception()
						except Exception:
							print("Fatal error, thread [" + thread_name + "] could not recover state...")
						else:
						#thread finished and is not continues so clear it from the list
							print("remove thread because it has finished", thread_name)
							
							del_arr += [myFunctionObject[2]]
							del self.callback_chain[ind]
							#we removed an item, so everything is adjusteda
							self.currentIndex -= 1
					if self.currentIndex + 1 < len(self.callback_chain):	
						self.currentIndex += 1
				sTD = False
				if len(del_arr) > 0:
					sTD = True
				for name in del_arr:
					#remove the entries from the dictionary
					del self.threads[name]
				if not flagRunning:
					#if callback_chain is empty stop updateLoop
					#we may want to continue the loop
					#self.running.clear()
					pass
				#print("propagateUpdate to master")
				#if we want to use that approach, we have to find a way to send an event to the mainthread
				#self.propagateUpdate()
			if sTD:
				self.removeItem.set()
			self.addItem.wait(10)
			self.addItem.clear()
	
	@abc.abstractmethod
	def propagateUpdate(self):
		"""Propagate the updaters to the parent"""
		return
	
	def callObject(self, func):
		try:
			localthread = ExThread(target=func[0])
			localthread.start()
			return localthread
		except Exception:
			print("could not start thread")
			return None
	
	def getEventPointer(self, func, name):
		return partial(func, self)
	
	def __setitem__(self, key, value):
		print("add thread %s"%key)
		with self.chain_lock:
			#if we have a periodic task save the intervall
			functions = (value[0], value[1], key) if not value[1] else (value[0], value[1], key, value[2])
			if not hasattr(self, "threads"):
				self.threads = {}
			self.threads[key] = self.callObject(functions)
			if key in self.threads:
				self.callback_chain += [functions]
		self.addItem.set()
	
	def remove(self, item):
		#at the moment only periodic tasks can be removed, when they finished execution
		with self.chain_lock:
			if item in self.threads:
				self.stoppThread[item] = True
		print("WAIT FOR REMOVAL, UI IS BLOCKED")
		self.removeItem.wait(20)
		self.removeItem.clear()
	def __contains__(self,key):
		return key in self.threads
class TkInterCallback(Callback):
	def propagateUpdate(self):
		#pass
		self.parent.update()
