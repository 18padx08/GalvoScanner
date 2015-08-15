/******************************************************************************
 *
 *  Project:        TDC Control Library
 *
 *  Filename:       tdcbase.h
 *
 *  Purpose:        Control and data acquisition functions for TDC
 *
 *  Author:         NHands GmbH & Co KG
 */
/*****************************************************************************/
/** @mainpage Custom Programming Library for TDC
 *
 *  @ref tdcbase.h "Tdcbase" is a library that allows custom
 *  programming for the TDC time-to-digital converter.
 *  It allows to configure the device, aquire timestamps,
 *  and calculate histograms.
 *
 *  @ref tdcbase.h declares functions for control and data acquisition.
 */
/*****************************************************************************/
/** @file tdcbase.h
 *  @brief Control and data acquisition functions for TDC
 *
 *  The header defines functions that allow to control the TDC time-to-digital
 *  converter and acquire data from it. The received timestamp data can be
 *  retreived programatically or stored in a file. They are also processed
 *  to a set of histograms internally.
 *
 *  Use @ref TDC_init to start and connect to the device and
 *  @ref TDC_deInit to close the connection. Set device parameters with
 *  @ref TDC_setExposureTime etc. and software parameters with
 *  @ref TDC_setHistogramParams etc. . Enable Measurement with
 *  @ref TDC_enableChannels and retreive results with
 *  @ref TDC_getHistogram etc. If a set of data is required that belongs
 *  to the same time, use @ref TDC_freezeBuffers to synchronize.
 */
/*****************************************************************************/
/* $Id: tdcbase.h,v 1.2 2015/06/02 17:35:38 trurl Exp $ */

#ifndef __TDCBASE_H
#define __TDCBASE_H

#ifdef __cplusplus
#define EXTC extern "C"              /**< For use with C++ */
#else
#define EXTC extern                  /**< For use with C */
#endif

#ifdef unix
#define TDC_API EXTC                 /**< Not required for Unix */
#define TDC_CC                       /**< Not required for Unix */
#else
#define TDC_CC     __stdcall         /**< Calling convention */
#ifdef  TDC_EXPORTS
#define TDC_API EXTC __declspec(dllexport)     /**< For internal use */
#else
#define TDC_API EXTC __declspec(dllimport)     /**< For external use */
#endif
#endif


typedef char              Int8;      /**< @brief  8 Bit Integer */
typedef int               Int32;     /**< @brief 32 bit integer */
typedef long long int     Int64;     /**< @brief 64 Bit Integer */
typedef int               Bln32;     /**< @brief Boolean (for documentation) */

#define TDC_INPUT_CHANNELS   8       /**< @brief Number of hardware input channels */
#define TDC_CROSS_CHANNELS   8       /**< @brief Channels used for cross-channel histograms */
#define TDC_COINC_CHANNELS  19       /**< @brief Number of internal coincidence counters */



/** @name Return values of the functions
 *
 *  All functions of this lib - as far as they can fail - return
 *  one of these constants for success control.
 *  @{
 */
#define TDC_Ok               0       /**< @brief Success */
#define TDC_Error          (-1)      /**< @brief Unspecified error */
#define TDC_Timeout          1       /**< @brief Receive timed out */
#define TDC_NotConnected     2       /**< @brief No connection was established */
#define TDC_DriverError      3       /**< @brief Error accessing the USB driver */
#define TDC_DeviceLocked     7       /**< @brief Can't connect device because already in use */
#define TDC_Unknown          8       /**< @brief Unknown error */
#define TDC_NoDevice         9       /**< @brief Invalid device number used in call */
#define TDC_OutOfRange      10       /**< @brief Parameter in fct. call is out of range */
#define TDC_CantOpen        11       /**< @brief Failed to open specified file */
/* @} */



/** @brief Type of the TDC device */
typedef enum {
  DEVTYPE_1A,                        /**< @brief Type 1a - no signal conditioning */
  DEVTYPE_1B,                        /**< @brief Type 1b - 8 channel signal conditioning */
  DEVTYPE_1C,                        /**< @brief Type 1c - 3 channel signal conditioning */
  DEVTYPE_NONE                       /**< @brief No device / invalid */
} TDC_DevType;



/** @brief Get Library Version
 *
 *  Returns the version number of the library.
 *  The integer part of the number denotes main releases, the fractional part
 *  Bugfixes without API change.
 *  @return Version number
 */
TDC_API double TDC_CC TDC_getVersion();


/** @brief Get Time Base
 *
 *  Returns the time base (the resolution) of the TDC device.
 *  It is used as time unit by many other functions.
 *  @return Time base in seconds
 */
TDC_API double TDC_CC TDC_getTimebase();


/** @brief Initialize and Start
 *
 *  The function initializes internal data and starts an event loop for
 *  data acquisition. It discovers devices connected to the computer,
 *  and connects to the first device that matches the given device ID.
 *  (The device ID is an identification number programmed by the user.)
 *
 *  The function should be called before any other TDC functions, except
 *  @ref TDC_getVersion and @ref TDC_getTimebase .
 *
 *  @param   deviceId   Identification number of the device to connect.
 *                      The special value -1 matches all devices.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_init( int deviceId );


/** @brief Disconnect and uninitialize
 *
 *  Disconnects a connected device and stops the internal event loop.
 *  @return  TDC_Ok (never fails)
 */
TDC_API int TDC_CC TDC_deInit();


/** @brief Get type of connected device
 *
 *  Returns the type of the device connected. Requires initialisation.
 *  @return  Type of the connected device; invalid if not connected.
 */
TDC_API TDC_DevType TDC_CC TDC_getDevType();


/** @brief Configure signal conditioning
 *
 *  Configures a channel's signal conditioning. The availability of signal
 *  conditioning electronics depends on the device type (@ref TDC_getDevType);
 *  the function requires an 1B or 1C device. If it isn't present for the
 *  specified channel, @ref TDC_OutOfRange is returned.
 *  @param  channel    Number of the input channel to configure.
 *                     For 1c devices, use 0=Ext0, 1=Ext1, 2=Sync
 *  @param  active     Switches the signal conditioning on (1) or off (0).
 *                     Not relevant for 1C devices.
 *  @param  edge       Selects the signal edge that is processed as an event:
 *                     rising (1) or falling (0)
 *  @param  term       Switches the termination in the signal path on (1) or off (0)
 *  @param  threshold  Voltage threshold that is used to identify events, in V.
 *                     Allowed range is -2 ... 3V; internal resolution is 1.2mV
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_configureSignalConditioning( Int32  channel,
                                                    Bln32  active,
                                                    Bln32  edge,
                                                    Bln32  term,
                                                    double threshold );


/** @brief Configure signal conditioning input divider
 *
 *  Configures the input divider of channel 0 if available.
 *  This function requires an 1B device, otherwise @ref TDC_OutOfRange is returned.
 *  @param  divider  Number of events to skip before one is passed + 1.
 *                   Only the following values are allowed:  1, 8, 16, 32, 64, 128
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_configureSyncDivider( Int32 divider );


/** @brief Configure APD cooling
 *
 *  Configures parameters for the cooling of the internal APDs if available.
 *  This function requires an 1C device, otherwise @ref TDC_OutOfRange is returned.
 *  @param  fanSpeed  Fan speed, unknown scale, Range 0 ... 50000
 *  @param  temp      Temperature control setpoint, range 0 ... 65535
 *                    The temperature scale is nonlinear, some sample points:
 *                    @b 0:     -31°
 *                    @b 16384: -25°
 *                    @b 32768: -18°
 *                    @b 65535:   0°
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_configureApdCooling( Int32 fanSpeed, Int32 temp );


/** @brief Configure APD cooling
 *
 *  Configures parameters for the cooling of the internal APDs if available.
 *  This function requires an 1C device, otherwise @ref TDC_OutOfRange is returned.
 *  @param  apd    Index of adressed APD, 0 or 1
 *  @param  bias   Bias value [V], Range 0 ... 250. Internal resolution is 61mV.
 *  @param  thrsh  Threshold value [V], Range 0 ... 2. Internal resolution is 0.5mV.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_configureInternalApds( Int32  apd,
                                              double bias,
                                              double thrsh );


/** @brief Enable TDC Channels
 *
 *  Selects the channels that contribute to the output stream.
 *  @param  channelMask  Bitfield with activation flag for every TDC channel.
 *                       (e.g. 5 means activate channels 1 and 3)
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_enableChannels( Int32 channelMask );


/** @brief Set Coincidence Window
 *
 *  Sets the coincidence time window for the integrated coincidence counting.
 *  @param  coincWin   Coincidence window in bins, Range = 0 ... 65535,
 *                     see @ref TDC_getTimebase
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setCoincidenceWindow( Int32 coincWin );


/** @brief Set Exposure Time
 *
 *  Sets the exposure time (or integration time) of the internal coincidence
 *  counters.
 *  @param  expTime   Exposure time in ms, Range = 0 ... 65535
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setExposureTime( Int32 expTime );


/** @brief Read Back Device Parameters
 *
 *  Reads the device parameters back from the device. All Parameters are
 *  output parameters but may be NULL-Pointers if the result is not required.
 *  @param  channelMask Enabled channels, see \ref TDC_enableChannels
 *  @param  coincWin    Coincidence window, see \ref TDC_setCoincidenceWindow
 *  @param  expTime     Exposure time, see \ref TDC_setExposureTime
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_getDeviceParams( Int32 * channelMask,
                                        Int32 * coincWin,
                                        Int32 * expTime   );

/** @brief Switch Input Termination
 *
 *  Switches the 50-Ohm termination of input lines on or off.
 *  The function requires an 1A type hardware, otherwise
 *  @ref TDC_OutOfRange is returned.
 *  @param  on   Switch on (1) or off (0)
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_switchTermination( Bln32 on );


/** @brief Configure Selftest
 *
 *  The function enables the internal generation of test signals that are
 *  input to the device. It is mainly used for testing.
 *  @param  channelMask  Bitfield that selects the channels to be fired internally
 *                       (e.g. 5 means signal generation on channels 1 and 3)
 *  @param  period       Period of all test singals in units of 20ns, Range = 2 ... 60
 *  @param  burstSize    Number of periods in a burst, Range = 1 ... 65535
 *  @param  burstDist    Distance between bursts in units of 80ns, Range = 0 ... 10000
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_configureSelftest( Int32 channelMask,
                                          Int32 period,
                                          Int32 burstSize,
                                          Int32 burstDist );

/** @brief Set Histogram Parameters
 *
 *  Sets parameters for the internally generated histograms. If the function is
 *  not called, default values are in place.
 *  When the function is called, all collected histogram data are cleared.
 *  @param binWidth  Width of the histograms bins in units of the TDC Time Base,
 *                   see @ref TDC_getTimebase . Range = 1 ... 1000000, default = 1.
 *  @param binCount  Number of bins in the histogram buffers.
 *                   Range = 2 ... 1000000, default = 10000.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setHistogramParams( Int32 binWidth, Int32 binCount );


/** @brief Read back Histogram Parameters
 *
 *  Reads back the histogram parameters that have been set with
 *  @ref TDC_setHistogramParams or their default values, respectively.
 *  @param binWidth  Output: Width of the histograms bins in TDC Time Base units,
 *                   see @ref TDC_getTimebase .
 *  @param binCount  Number of bins in the histogram buffers.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_getHistogramParams( Int32 * binWidth,
                                           Int32 * binCount );


/** @brief Check for data loss
 *
 *  Timestamps of events detected by the device can get lost if their rate
 *  is too high for the USB interface or if the PC is unable to receive the
 *  data in time. The TDC recognizes this situation and signals it to the
 *  PC (with high priority).
 *
 *  The function checks if a data loss situation is currently detected or if
 *  it has been latched since the last call. If you are only interested in
 *  the current situation, call the function twice; the first call will
 *  delete the latch.
 *  @param lost      Output: Current and latched data loss state.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_getDataLost( Bln32 * lost );


/** @brief Clear Histograms
 *
 *  Clears all internally generated histograms, i.e. all bins are set to 0.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_clearAllHistograms();


/** @brief Set Timestamp Buffersize
 *
 *  Sets the size of a ring buffer that stores the timestamps of the last
 *  detected events. The buffer's contents can be retreived with
 *  TDC_getLastTimestamps. By default, the buffersize is 0.
 *  When the function is called, the buffer is cleared.
 *  @param size      Buffersize; Range = 1 ... 1000000
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setTimestampBufferSize( Int32 size );


/** @brief Freeze internal Buffers
 *
 *  The function can be used to freeze the internal buffers,
 *  allowing to retreive multiple histograms with the same
 *  integration time. When frozen, no more events are added to
 *  the built-in histograms and timestamp buffer. The coincidence
 *  counters are not affected. Initially, the buffers are not frozen.
 *  @param freeze    freeze (1) or activate (0) the buffers
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_freezeBuffers( Bln32 freeze );


/** @brief Retreive Histogram
 *
 *  Retreives one of the histgrams accumulated internally.
 *  One histogram is provided for the time differences of every event
 *  the device has detected (channel independent). 64 histograms are
 *  provided for the time differences of events detected on different
 *  channels. Events on the first channel reset the time counter,
 *  events on the second one integrate the current counter value in
 *  the Histogram.
 *  @param chanA     First TDC channel of the channel pair. Range 0...7
 *                   begins with 0 for channel 1.
 *                   If this parameter is out of range (negative e.g.)
 *                   the channel independent histogram is retreived.
 *  @param chanB     Second TDC channel of the channel pair (0...7).
 *                   If this parameter is out of range (negative e.g.)
 *                   the channel independent histogram is retreived.
 *  @param reset     If the histogram should be cleared after retreiving.
 *  @param data      Output: Histogram data. The array must have at least
 *                   binCount (see @ref TDC_setHistogramParams ) elements.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param count     Total number of valid time diffs in the histogram.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param tooSmall  Number of time diffs that were smaller than the
 *                   smallest histogram bin.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param tooLarge  Number of time diffs that were bigger than the
 *                   biggest histogram bin.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param eventsA   Number of events detected on the first channel that
 *                   contribute to the histogram.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param eventsB   Number of events detected on the second channel that
 *                   contribute to the histogram.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param expTime   Total exposure time for the histogram: the time
 *                   difference between the first and the last event
 *                   that contribute to the histogram. In timebase units.
 *                   A NULL pointer is allowed to ignore the data.
 *  @return  @ref TDC_Ok (never fails)
 */
TDC_API int TDC_CC TDC_getHistogram( Int32 chanA,
                                     Int32 chanB,
                                     Bln32 reset,
                                     Int32 * data,
                                     Int32 * count,
                                     Int32 * tooSmall,
                                     Int32 * tooLarge,
                                     Int32 * eventsA,
                                     Int32 * eventsB,
                                     Int64 * expTime );

/** @brief Retreive Coincidence Counters
 *
 *  Retreives the most recent values of the built-in coincidence counters.
 *  The coincidence counters are not accumulated, i.e. the counter values for
 *  the last exposure (see @ref TDC_setExposureTime ) are returned.
 *
 *  The array contains count rates for all 8 channels, and rates for
 *  two, three, and fourfold coincidences of events detected on different
 *  channels out of the first 4. Events are coincident if they happen
 *  within the coincidence window (see @ref TDC_setCoincidenceWindow ).
 *  @param data      Output: Counter Values. The array must have at least
 *                   19 elements. The Counters come in the following order:
 *                   1, 2, 3, 4, 5, 6, 7, 8, 1/2, 1/3, 1/4, 2/3, 2/4, 3/4,
 *                   1/2/3, 1/2/4, 1/3/4, 2/3/4, 1/2/3/4
 *  @return  @ref TDC_Ok (never fails)
 */
TDC_API int TDC_CC TDC_getCoincCounters( Int32 * data );


/** @brief Retreive Last Timestamp Values
 *
 *  Retreives the timestamp values of the last n detected events on all
 *  TDC channels. The buffer size must have been set with
 *  @ref TDC_setTimestampBufferSize , otherwise 0 data will be returned.
 *  @param reset      If the data should be cleared after retreiving.
 *  @param timestamps Output: Timestamps of the last events in base units,
 *                    see @ref TDC_getTimebase .
 *                    The array must have at least size elements,
 *                    see @ref TDC_setTimestampBufferSize .
 *                    A NULL pointer is allowed to ignore the data.
 *  @param channels   Output: Numbers of the channels where the events have been
 *                    detected. Every array element belongs to the timestamp
 *                    with the same index. Range is 0...7 for channels 1...8.
 *                    The array must have at least size elements,
 *                    see @ref TDC_setTimestampBufferSize .
 *                    A NULL pointer is allowed to ignore the data.
 *  @param valid      Output: Number of valid entries in the above arrays.
 *                    May be less than the buffer size if the buffer has been cleared.
 *  @return  @ref TDC_Ok (never fails)
 */
TDC_API int TDC_CC TDC_getLastTimestamps( Bln32 reset,
                                          Int64 * timestamps,
                                          Int8  * channels,
                                          Int32 * valid );


/** @brief Write Timestamp Values to File
 *
 *  Starts or stops writing the timestamp values to a file continously. 
 *  Timestamps come in base units, see @ref TDC_getTimebase ;
 *  channel Numbers range from 1 to 8.
 *  Two file formats are available:
 *
 *  @li ASCII: Timestamp values (int base units) and channel numbers
 *             as decimal values in two comma separated columns.
 *
 *  @li binary: Records of 10 bytes, 8 bytes for the timestamp, 2 for the channel
 *              number, Stored in little endian (Intel) byte order.
 *
 *  Writing in the ASCII format requires much more CPU power and about twice as much
 *  disk space than using the binary format. If the specified file exists it will be
 *  overwritten. The function checks if the file can be opened; write errors that occur
 *  later in the actual writing process (disk full e.g.) will not be reported.
 *  @param filename   Name of the file to use. To stop writing, call the function with
 *                    an empty or null filename.
 *  @param binary     Use binary (true) or ASCII (false) file format. Meaningless
 *                    if writing is to be stopped.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_writeTimestamps( const char * filename,
                                        Bln32 binary );

#endif
