from ctypes import *


#GLOBAL constants 

FULL_32BIT_VALUE = 0x7fffff

#define MAXSTRINGLENGTH
MAX_STRING_LENGTH = 512


##############################################################################################
#ENUMS

#define fc2Error enum
fc2Error = c_int
FC2_ERROR_UNDEFINED = fc2Error(-1)
FC2_ERROR_OK = fc2Error(0)
FC2_ERROR_FAILED= fc2Error(1)
FC2_ERROR_NOT_IMPLEMENTED = fc2Error(2)
FC2_ERROR_FAILED_BUS_MASTER_CONNECTION = fc2Error(3)
FC2_ERROR_NOT_CONNECTED = fc2Error(4)
FC2_ERROR_INIT_FAILED = fc2Error(5)
FC2_ERROR_NOT_INTITIALIZED = fc2Error(6)
FC2_ERROR_INVALID_PARAMETER = fc2Error(7)
FC2_ERROR_INVALID_SETTINGS = fc2Error(8)      
FC2_ERROR_INVALID_BUS_MANAGER = fc2Error(9)
FC2_ERROR_MEMORY_ALLOCATION_FAILED = fc2Error(10)
FC2_ERROR_LOW_LEVEL_FAILURE = fc2Error(11)
FC2_ERROR_NOT_FOUND = fc2Error(12)
FC2_ERROR_FAILED_GUID = fc2Error(13)
FC2_ERROR_INVALID_PACKET_SIZE = fc2Error(14)
FC2_ERROR_INVALID_MODE = fc2Error(15)
FC2_ERROR_NOT_IN_FORMAT7 = fc2Error(16)
FC2_ERROR_NOT_SUPPORTED = fc2Error(17)
FC2_ERROR_TIMEOUT = fc2Error(18)
FC2_ERROR_BUS_MASTER_FAILED = fc2Error(19)
FC2_ERROR_INVALID_GENERATION = fc2Error(20)
FC2_ERROR_LUT_FAILED = fc2Error(21)
FC2_ERROR_IIDC_FAILED= fc2Error(22)
FC2_ERROR_STROBE_FAILED= fc2Error(23)
FC2_ERROR_TRIGGER_FAILED = fc2Error(24)
FC2_ERROR_PROPERTY_FAILED = fc2Error(25)
FC2_ERROR_PROPERTY_NOT_PRESENT = fc2Error(26)
FC2_ERROR_REGISTER_FAILED = fc2Error(27)
FC2_ERROR_READ_REGISTER_FAILED = fc2Error(28)
FC2_ERROR_WRITE_REGISTER_FAILED = fc2Error(29)
FC2_ERROR_ISOCH_FAILED = fc2Error(30)
FC2_ERROR_ISOCH_ALREADY_STARTED = fc2Error(31)
FC2_ERROR_ISOCH_NOT_STARTED = fc2Error(32)
FC2_ERROR_ISOCH_START_FAILED = fc2Error(33)
FC2_ERROR_ISOCH_RETRIEVE_BUFFER_FAILED = fc2Error(34)
FC2_ERROR_ISOCH_STOP_FAILED = fc2Error(35)
FC2_ERROR_ISOCH_SYNC_FAILED = fc2Error(36)
FC2_ERROR_ISOCH_BANDWIDTH_EXCEEDED = fc2Error(37)
FC2_ERROR_IMAGE_CONVERSION_FAILED = fc2Error(38)
FC2_ERROR_IMAGE_LIBRARY_FAILURE = fc2Error(39)
FC2_ERROR_BUFFER_TOO_SMALL = fc2Error(40)
FC2_ERROR_IMAGE_CONSISTENCY_ERROR = fc2Error(41)
FC2_ERROR_INCOMPATIBLE_DRIVER = fc2Error(42)
FC2_ERROR_FORCE_32BITS = fc2Error(43)

#define fc2InterfaceType enum
fc2InterfaceType = c_int
FC2_INTERFACE_IEEE1394 = fc2InterfaceType(0)
FC2_INTERFACE_USB_2 = fc2InterfaceType(1)
FC2_INTERFACE_USB_3 = fc2InterfaceType(2)
FC2_INTERFACE_GIGE = fc2InterfaceType(3)
FC2_INTERFACE_UNKNOWN = fc2InterfaceType(4)
FC2_INTERFACE_TYPE_FORCE_32BITS = FULL_32BIT_VALUE

#define enum for fc2DriverType
fc2DriverType = c_int
FC2_DRIVER_1394_CAM = fc2DriverType(0)
FC2_DRIVER_1394_PRO = fc2DriverType(1)
FC2_DRIVER_1394_JUJU = fc2DriverType(2)
FC2_DRIVER_1394_VIDEO1394 = fc2DriverType(3)
FC2_DRIVER_1394_RAW1394 = fc2DriverType(4)
FC2_DRIVER_USB_NONE = fc2DriverType(5)
FC2_DRIVER_USB_CAM = fc2DriverType(6)
FC2_DRIVER_USB3_PRO = fc2DriverType(7)
FC2_DRIVER_GIGE_NONE = fc2DriverType(8)
FC2_DRIVER_GIGE_FILTER = fc2DriverType(9)
FC2_DRIVER_GIGE_PRO = fc2DriverType(10)
FC2_DRIVER_UNKNOWN  = fc2DriverType(-1)
FC2_DRIVER_FORCE_32BITS = FULL_32BIT_VALUE

#define enum for fc2BusSpeed
fc2BusSpeed = c_int

#define enum for fc2PCIeBusSpeed
fc2PCIeBusSpeed = c_int

#define enum for fc2BayerTileFormat
fc2BayerTileFormat = c_int


#define enum for fc2PixelFormat
fc2PixelFormat = c_int



##############################################################################################################
#typedefs

#fc2Context is a void pointer (see c api)
fc2Context = c_void_p

#fc2ImageImpl is a void pointer
fc2ImageImpl = c_void_p

##############################################################################################################
#Structs

#define fc2TimeStamp
class fc2TimeStamp(Structure):
	_fields_ = [("seconds", c_longlong), ("microSeconds", c_uint), ("cycleSeconds", c_uint), ("cycleCount", c_uint), ("cycleOffset", c_uint), ("reserved", c_uint*8)]

#define struct ipaddress
class fc2IPAddress(Structure):
	_fields_ = [("octets", c_ubyte*4)]

#define struct for macaddress
class fc2MACAddress(Structure):
	_fields_ = [("octets", c_ubyte*6)]

#define fc2ConfigRom struct
class fc2ConfigROM(Structure):
	_fields_ = [("nodeVendorId", c_uint),("chipIdHi", c_uint),("chipIdLo", c_uint),("unitSpecId", c_uint),("unitSWVer", c_uint),
				("unitSubSWVer", c_uint),("vendorUniqueInfo_0", c_uint),("vendorUniqueInfo_1", c_uint),("vendorUniqueInfo_2", c_uint),("vendorUniqueInfo_3", c_uint),
				("pszKeyword", c_char*MAX_STRING_LENGTH),("nodeVendorId", c_uint)]

#CameraInfo Struct
class fc2CameraInfo(Structure):
	_fields_ = [("serialNumber", c_uint), ("interfaceType", fc2InterfaceType), ("driverType", fc2DriverType), ("isColorCamera", c_int),
				("modelName", c_char*MAX_STRING_LENGTH), ("vendorName", c_char*MAX_STRING_LENGTH), ("sensorInfo", c_char*MAX_STRING_LENGTH), ("sensorResolution", c_char*MAX_STRING_LENGTH),
				("driverName", c_char*MAX_STRING_LENGTH), ("firmwareVersion", c_char*MAX_STRING_LENGTH), ("firmwareBuildTime", c_char*MAX_STRING_LENGTH), ("maximumBusSpeed", fc2BusSpeed),
				("pcieBusSpeed", fc2PCIeBusSpeed), ("bayerTileFormat", fc2BayerTileFormat), ("busNumber", c_ushort), ("nodeNumber", c_ushort),
				("iidcVer", c_uint), ("configROM", fc2ConfigROM), ("gigEMajorVersion", c_uint), ("gigEMinorVersion", c_uint), ("userDefinedName", c_char*MAX_STRING_LENGTH),
				("xmlURL1", c_char*MAX_STRING_LENGTH), ("xmlURL2", c_char*MAX_STRING_LENGTH), ("macAddress", fc2MACAddress), ("ipAddress", fc2IPAddress), ("subnetMask", fc2IPAddress),
				("defaultGateway", fc2IPAddress), ("ccpStatus", c_uint), ("applicationIPAddress", c_uint), ("applicationPort", c_uint), ("reserved", c_uint*16)]
	
class fc2PGRGuid(Structure):
	_fields_ = [("value", c_uint*4)]
	
#fc2Image struct
class fc2Image(Structure):
	_fields_ = [("rows", c_uint), ("cols", c_uint), ("stride", c_uint), ("pData", POINTER(c_ubyte)), ("dataSize", c_uint),
				("receivedDataSize", c_uint), ("format", fc2PixelFormat), ("bayerFormat", fc2BayerTileFormat), ("imageImpl", fc2ImageImpl)]

###############################################################################################################

#function definitions

def fc2CreateContext(context):
	return windll.FlyCapture2_C.fc2CreateContext(byref(context))
	
def fc2GetNumOfCameras(context, numCameras):
	return windll.FlyCapture2_C.fc2GetNumOfCameras(context, byref(numCameras))

def fc2GetCameraFromIndex(context, index, guid):
	return windll.FlyCapture2_C.fc2GetCameraFromIndex(context, index, byref(guid))
	
def fc2Connect(context, guid):
	return windll.FlyCapture2_C.fc2Connect(context, byref(guid))

def fc2StartCapture(context):
	return windll.FlyCapture2_C.fc2StartCapture(context)
	
def fc2StopCapture(context):
	return windll.FlyCapture2_C.fc2StopCapture(context)

def fc2DestroyContext(context):
	return windll.FlyCapture2_C.fc2DestroyContext(context)

def fc2GetCameraInfo(context, camInfo):
	return windll.FlyCapture2_C.fc2GetCameraInfo(context, byref(camInfo))
	
def fc2CreateImage(image):
	return windll.FlyCapture2_C.fc2CreateImage(byref(image))

def fc2RetrieveBuffer(context, image):
	return windll.FlyCapture2_C.fc2RetrieveBuffer(context, byref(image))
	
def fc2GetImageTimeStamp(image):
	return windll.FlyCapture2_C.fc2GetImageTimeStamp(byref(image))
	
def fc2ConvertImageTo(pixelFormat, srcImage, destImage):
	return windll.FlyCapture2_C.fc2ConvertImageTo(pixelFormat, byref(srcImage), byref(destImage))
	
def fc2SaveImage(image, filename, fileFormat):
	return windll.FlyCapture2_C.fc2SaveImage(byref(image), filename, fileFormat)

def fc2DestroyImage(image):
	return windll.FlyCapture2_C.fc2DestroyImage(byref(image))