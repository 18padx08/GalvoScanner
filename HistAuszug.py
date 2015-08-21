while self.hbtLoop:
	#retrieve histogram
	if not self.hbtRunning:
		#reset the histogram
		TDC_clearAllHistograms()
		TDC_getHistogram(data=bufferArray,eventsA=eventsA, eventsB=eventsB)
		startTime = time.time()
		#be sure to not have a time diff of 0 seconds... (otherwise we divide by zero)
		endTime = time.time()+1
		self.hbtRunning = True
		print("clear data")
	else:
		TDC_getHistogram(chanA=4, chanB=5,data=bufferArray, eventsA=eventsA, eventsB=eventsB)
		endTime = time.time()
	dataArray = numpy.array(bufferArray, dtype=numpy.float64)
	datalen = len(dataArray)
	if datalen % 2 == 0:
		left, right = (dataArray[0::2], dataArray[1::2])
	else:
		left, right = (dataArray[0::2], dataArray[1::2])
	print(left, right)
	dataArray = numpy.hstack((numpy.flipud(left),right))
	histAx.cla()
	#normalize data (we assume to have a probabilty of one at large taus, so take the midvalue of the last 5 elements on each side)
	#print(numpy.concatenate((dataArray[:5], dataArray[-5:])))
	normConst = numpy.mean(numpy.concatenate((dataArray[:5], dataArray[-5:])))
	if normConst > 0:
		dataArray /= normConst
				