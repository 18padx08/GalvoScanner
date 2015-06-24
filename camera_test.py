from pyflycam import *

error = fc2Error()
context = fc2Context()
guid = fc2PGRGuid()
numCameras = c_uint()
k_numImages = 100

error = fc2CreateContext(context)
if error != FC2_ERROR_OK.value:
	print("Error in fc2CreateContext: " + str(error))

error = fc2GetNumOfCameras(context, numCameras)
if error != FC2_ERROR_OK.value:
	print("Error in fc2GetNumOfCameras: " + str(error))
if numCameras == 0:
	print("No Cameras detected")

#get the first camera
error = fc2GetCameraFromIndex(context, 0, guid)
if error != FC2_ERROR_OK.value:
	print("Error in fc2GetCameraFromIndex: " + str(error))

error = fc2Connect(context, guid)
if error!= FC2_ERROR_OK.value:
	print("Error in fc2Connect: " + str(error))

fc2StartCapture(context)

rawImage = fc2Image()
convertedImage = fc2Image()

error = fc2CreateImage(rawImage)
fc2CreateImage(convertedImage)

if error != FC2_ERROR_OK.value:
	print("Error in fc2CreateImage rawImage: " + str(error))

error = fc2RetrieveBuffer(context, rawImage)
if error != FC2_ERROR_OK.value:
	print("Error in fc2RetrieveBuffer: " + str(error))

fc2ConvertImageTo(fc2PixelFormat(0x80000008), rawImage, convertedImage)

fc2SaveImage(convertedImage, b'fc2TestImage.png', 6)

fc2DestroyImage(rawImage)
fc2DestroyImage(convertedImage)

fc2StopCapture(context)
fc2DestroyContext(context)