/******************************************************************************
 *
 *  Project:        TDC Control Library
 *
 *  Filename:       tdclifetm.h
 *
 *  Purpose:        Lifetime measurment
 *
 *  Author:         NHands GmbH & Co KG
 */
/*****************************************************************************/
/** @file tdclifetm.h
 *  @brief Lifetime measurement
 *
 *  The header provides functions to calculate a start multistop histogram
 *  for lifetime measurement. A selceted channel provides start events
 *  while events form all other channels act as stop events.
 *  Stop event after are processed until the next start event.
 *
 *  If the start events originate from the dedicated sync input channel
 *  with input divider, the skipped start events can be virtually reconstructed.
 *  Only one histogram is provided; it is calculated on the PC.
 *
 *  Use the functions of @ref tdcbase.h to control the device. Set
 *  parameters with @ref TDC_setLftParams and @ref TDC_setLftStartInput.
 *  Enable the collection of data with @ref TDC_enableLft;
 *  when enabled, all incoming events contribute to the histogram.
 *  Use @ref TDC_getLftHistogram to to retrieve the histogram.
 */
/*****************************************************************************/
/* $Id: tdclifetm.h,v 1.3 2015/07/31 11:57:32 trurl Exp $ */

#ifndef __TDCLIFETM_H
#define __TDCLIFETM_H

#include "tdcdecl.h"


/** Enable Lifetime Calculations
 *
 *  Enables the calculation of the start multistop histogram.
 *  When enabled, all incoming events contribute to the histogram.
 *  When disabled, all Lft functions are unavailable.
 *  The function implicitly clears the histogram.
 *  Use @ref TDC_freezeBuffers to interrupt the accumulation
 *  of events without clearing the histogram and
 *  @ref TDC_resetLftHistogram to clear without interrupt.
 *  @param enable  Enable or disable 
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_enableLft( Bln32 enable );


/** Set Histogram Parameters
 *
 *  Sets parameters for the histogram.
 *  If the function is not called, default values are in place.
 *  When the function is called, all collected data are cleared.
 *  @param binWidth  Width of the bins in units of the TDC Time Base,
 *                   see @ref TDC_getTimebase . Range = 1 ... 8192, default = 1.
 *  @param binCount  Number of bins in the buffers.
 *                   Range = 16 ... 8192, default = 256.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setLftParams( Int32 binWidth,
                                     Int32 binCount );


/** Set TDC Channel for Start Input
 *
 *  Selects the TDC channel that provides the start events.
 *  All events from other channels act as stop events.
 *  The function implicitly clears the histogram.
 *  @param startChan    Channel for start events, Range = 0 ... 7, default = 0
 *                      Ignored for A3 devices that always use the sync channel.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_setLftStartInput( Int32 startChan );


/** Reset Histogram
 *
 *  Clears the accumulated start multistop histogram.
 *  @return  Error code
 */
TDC_API int TDC_CC TDC_resetLftHistogram( void );


/** Retrieve Start Multistop Histogram
 *
 *  Retrieves one of the start multistop histogram accumulated internally.
 *  @param reset     If the histogram should be cleared after retrieving.
 *  @param data      Output: Histogram data. The array must have at least
 *                   binCount (see @ref TDC_setLftParams) elements.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param tooBig    Output: Number of time diffs that were bigger
 *                   than the biggest histogram bin.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param startEvts Output: Number of start events contributing to the histogram.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param stopEvts  Output: Number of stop events contributing to the histogram.
 *                   A NULL pointer is allowed to ignore the data.
 *  @param expTime   Total exposure time for the histogram: the time
 *                   difference between the first and the last event
 *                   that contribute to the histogram. In timebase units.
 *                   A NULL pointer is allowed to ignore the data.
 *  @return  @ref TDC_Ok (never fails)
 */
TDC_API int TDC_CC TDC_getLftHistogram( Bln32 reset,
                                        Int32 * data,
                                        Int32 * tooBig,
                                        Int32 * startEvts,
                                        Int32 * stopEvts,
                                        Int64 * expTime );


#endif
