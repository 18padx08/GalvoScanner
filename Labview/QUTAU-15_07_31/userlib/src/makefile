############################################################
#
#  Project:        TDC User Library
#
#  Filename:       makefile
#
#  Purpose:        MSVC makefile for tdcbase examples
#
#  Author:         NHands GmbH & Co KG
#
############################################################
# $Id: makefile.win,v 1.4 2015/07/17 14:37:33 trurl Exp $

INCDIR=..\inc
LIBDIR=..\lib

.c.exe:
	cl -nologo -W3 -MD -wd4996 -I$(INCDIR) $(LIBDIR)\tdcbase.lib %s

all : example0.exe example1.exe example2.exe example3.exe \
      example4.exe example5.exe example6.exe tdcbase.dll

clean:
	del *.exe *.obj *.manifest *.dll

tdcbase.dll : $(LIBDIR)\tdcbase.dll
	copy $(LIBDIR)\tdcbase.dll .