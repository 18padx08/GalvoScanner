/*******************************************************************************
 *
 *  Project:        TDC Custom Programming Library
 *
 *  Filename:       example0.c
 *
 *  Purpose:        Simple example for use of tdcbase lib
 *
 *  Author:         NHands GmbH & Co KG
 *
 *******************************************************************************/
/* $Id: example0.c,v 1.1 2014/02/14 17:46:46 trurl Exp $ */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "tdcbase.h"

#ifdef unix
#include <unistd.h>
#define SLEEP(x) usleep(x*1000)

#else

/* windows.h for Sleep */
#include <windows.h>
#define SLEEP(x) Sleep(x)
#endif

#if defined(__MINGW32__)
#define LLFORMAT "%I64"
#else
#define LLFORMAT "%ll"
#endif


#define HIST_BINCOUNT        40
#define HIST_BINWIDTH       250
#define TIMESTAMP_COUNT   10000


/* Print out return codes */
static const char * printRc( int rc )
{
  switch ( rc ) {
  case TDC_Ok:           return "Success";
  case TDC_Error:        return "Unspecified error";
  case TDC_Timeout:      return "Receive timed out";
  case TDC_NotConnected: return "No connection was established";
  case TDC_DriverError:  return "Error accessing the USB driver";
  case TDC_DeviceLocked: return "Can't connect device because already in use";
  case TDC_Unknown:      return "Unknown error";
  case TDC_NoDevice:     return "Invalid device number used in call";
  case TDC_OutOfRange:   return "Parameter in fct. call is out of range";
  case TDC_CantOpen:     return "Can't open specified file";
  default:                return "????";
  }
}


static void checkRc( const char * fctname, int rc )
{
  if ( rc ) {
    printf( ">>> %s: %s\n", fctname, printRc( rc ) );
    exit( 1 );
  }
}

/*
 * Initialize and start TDC, wait and get some data
 */

int main( int argc, char ** argv )
{
  Int32 rc, count, tooSmall, tooBig, tsValid, eventsA, eventsB, i, j;
  Int64 expTime, lastTimestamp = 0;
  Int32 hist1[HIST_BINCOUNT], hist2[HIST_BINCOUNT];
  Int64 timestamps[TIMESTAMP_COUNT];
  Int8  channels[TIMESTAMP_COUNT];
  int   coincCnt[19];
  double timeBase = TDC_getTimebase();
  double bin2ns = HIST_BINWIDTH * timeBase * 1.e9;     /* Width of a bin in nanoseconds */
  printf( ">>> tdcbase version: %f\n", TDC_getVersion() );
  printf( ">>> timebase: %g ps\n", timeBase * 1.e12 );

  /* Initialize & start */
  rc = TDC_init( -1 );  /* Accept every device */
  checkRc( "TDC_init", rc );
  rc = TDC_enableChannels( 0xff );    /* Use all channels */
  checkRc( "TDC_enableChannels", rc );
  rc = TDC_setHistogramParams( HIST_BINWIDTH, HIST_BINCOUNT );
  checkRc( "TDC_setHistogramParams", rc );
  rc = TDC_setTimestampBufferSize( TIMESTAMP_COUNT );
  checkRc( "TDC_setTimestampBufferSize", rc );
  rc = TDC_setExposureTime( 100 );
  checkRc( "TDC_setExposureTime", rc );
  rc = TDC_setCoincidenceWindow( 100 ); /* 8ns */
  checkRc( "TDC_setCoincidenceWindow", rc );

  if ( argc > 1 && !strcmp( argv[1], "gen" ) ) {
    /* Configure internal signal generator:
     * Ch. 0 + 1, signal period 80ns, bursts of 3 Periods, distance betw. bursts 800ns
     * Expecting peaks at 80ns and 800 - 2*80 = 640ns
     */
    rc = TDC_configureSelftest( 3, 4, 3, 10 );
    checkRc( "TDC_configureSelftest", rc );
  }

  rc = TDC_clearAllHistograms();
  checkRc( "TDC_clearAllHistograms", rc );

  /* wait some seconds and check samples */
  printf( ">>> Collecting...\n" );
  count = 0;
  for ( i = 0; i < 200; ++i ) {
    TDC_getLastTimestamps( 1, timestamps, channels, &tsValid );
    for ( j = 0; j < tsValid; ++j ) {
      if ( channels[j] < 0 || channels[j] > 2 || timestamps[j] < lastTimestamp ) {
        printf( ">>> Channel/Sorting error: round=%d index=%d count=%d\n", i, j, count );
      }
      count++;
      lastTimestamp = timestamps[j];
    }
    SLEEP( 5 );
  }

  /* Ensure consistent histograms */
  TDC_freezeBuffers( 1 );
  /* Retreive and print data */
  TDC_getLastTimestamps( 1, timestamps, channels, &tsValid );
  printf( ">>> Timestamps: buffered=%d\n", tsValid );
  for ( i = 0; i < 10; ++i ) {
    printf( ">>> " );
    for ( j = 0; j < 5; j++ ) {
      printf( LLFORMAT"x (%d)  ", timestamps[5*i+j], channels[5*i+j] );
    }
    printf( "\n" );
  }
  printf( "\n" );

  TDC_getCoincCounters( coincCnt );
  printf( ">>> CoincCounters:  " );
  for ( i = 0; i < 19; ++i ) {
    printf( "%d ", coincCnt[i] );
  }
  printf( "\n" );

  TDC_getHistogram( -1, -1, 1, hist1, &count, &tooSmall, &tooBig, &eventsA, &eventsB, &expTime );
  printf( ">>> Histogram global:  valid=%d tooSmall=%d tooBig=%d\n", count, tooSmall, tooBig );
  printf( ">>>                    ev.A=%d  ev.B=%d expTime=%g s\n", eventsA, eventsB,
          expTime * timeBase );
  TDC_getHistogram( 0, 1, 1, hist2, &count, &tooSmall, &tooBig, &eventsA, &eventsB, &expTime );
  printf( ">>> Histogram 0-1:     valid=%d tooSmall=%d tooBig=%d\n", count, tooSmall, tooBig );
  printf( ">>>                    ev.A=%d  ev.B=%d expTime=%g s\n", eventsA, eventsB,
          expTime * timeBase );
  printf( ">>>       Bin Time   Counter global      Counter 0-1\n" );
  for ( i = 0; i < HIST_BINCOUNT; ++i ) {
    /* "Bin Time" is the lower limit of the bin */
    printf( ">>> %12fns %16d %16d\n", i * bin2ns, hist1[i], hist2[i] );
  }

  /* Stop it and exit */
  TDC_deInit();

  return 0;
}
