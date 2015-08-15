/*******************************************************************************
 *
 *  Project:        QKD Custom Programming Library
 *
 *  Filename:       example0.c
 *
 *  Purpose:        Trivial example
 *
 *  Author:         NHands GmbH & Co KG
 *
 *******************************************************************************/
/* $Id: example1.c,v 1.1 2015/06/02 17:35:38 trurl Exp $ */

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

#define TIMESTAMP_COUNT 10000

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
  default:               return "????";
  }
}


static const char * printHwType( TDC_DevType type )
{
  switch ( type ) {
  case DEVTYPE_1A:  return "1A";
  case DEVTYPE_1B:  return "1B";
  case DEVTYPE_1C:  return "1C";
  default:          return "--";
  }
}


static void checkRc( const char * fctname, int rc )
{
  if ( rc ) {
    printf( ">>> %s: %s\n", fctname, printRc( rc ) );
    if ( rc != TDC_OutOfRange ) {
      exit( 1 );
    }
  }
}


int main( int argc, char ** argv )
{
  int   i, j, rc, tsValid, evtCount[8];
  Int64 timestamps[TIMESTAMP_COUNT];
  Int8  channels[TIMESTAMP_COUNT];
  TDC_DevType type;
  rc = TDC_init( -1 );                    /* Accept every device */
  checkRc( "TDC_init", rc );
  type = TDC_getDevType();
  printf( "Hardware found: %s\n", printHwType( type ) );
  rc = TDC_configureSignalConditioning( 0, 1, 1, 0, 1.1 );
  checkRc( "TDC_configureSignalConditioning(0,...)", rc );
  rc = TDC_configureSignalConditioning( 6, 1, 1, 0, 1.1 );
  checkRc( "TDC_configureSignalConditioning(6,...)", rc );
  rc = TDC_configureSyncDivider( 32 );
  checkRc( "TDC_configureSyncDivider(32)", rc );
  rc = TDC_configureSyncDivider( 4 );
  checkRc( "TDC_configureSyncDivider(4)", rc );
  rc = TDC_configureApdCooling( 10000, 20000 );
  checkRc( "TDC_configureApdCooling", rc );
  rc = TDC_configureInternalApds( 0, 150., 1.5 );
  checkRc( "TDC_configureInternalApds(0,...)", rc );
  rc = TDC_configureInternalApds( 1, 150., 1.5 );
  checkRc( "TDC_configureInternalApds(1,...)", rc );
  rc = TDC_enableChannels( 0xff );
  checkRc( "TDC_enableChannels", rc );
  rc = TDC_setTimestampBufferSize( TIMESTAMP_COUNT );
  checkRc( "TDC_setTimestampBufferSize", rc );

  for ( j = 0; j < 8; ++j ) {
    evtCount[j] = 0;
  }
  for ( i = 0; i < 50; ++i ) {
    TDC_getLastTimestamps( 1, timestamps, channels, &tsValid );
    for ( j = 0; j < tsValid; ++j ) {
      evtCount[channels[j]]++;
    }
    for ( j = 0; j < 8; ++j ) {
      printf( "%8i", evtCount[j] );
      evtCount[j] = 0;
    }
    printf( "\n" );
    SLEEP( 100 );
  }

  TDC_deInit();                           /* Stop it and exit */
  return 0;
}
