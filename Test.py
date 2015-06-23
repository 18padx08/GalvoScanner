from PyDAQmx import *
import numpy
import random

# Declaration of variable passed by reference
taskHandle = TaskHandle()
analog_output = Task()
read = int32()
data = numpy.zeros((1000,), dtype=numpy.float64)

try:
    for i in range(1000):
        data[i] = 7.0*numpy.sin(i*2.0*numpy.pi/1000)*random.random()
    # DAQmx Configure Code
    #DAQmxCreateTask("",byref(taskHandle))
    #DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
    analog_output.CreateAOVoltageChan("Dev2/ao1","",-10.0,10.0,DAQmx_Val_Volts,None)
    #DAQmxCfgSampClkTiming(taskHandle,"",10000.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,1000)
    analog_output.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000)
    print(data)
    # DAQmx Start Code
    read = analog_output.WriteAnalogF64(1000,True,-1,DAQmx_Val_GroupByChannel ,data,None,None)        
    #DAQmxStartTask(taskHandle)
    
    # DAQmx Read Code
    #DAQmxReadAnalogF64(taskHandle,1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)
    
    t = input("tets")
    print("Acquired %d points"%read)
except DAQError as err:
    print("DAQmx Error: %s"%err)
finally:
    if taskHandle:
        # DAQmx Stop Code
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)