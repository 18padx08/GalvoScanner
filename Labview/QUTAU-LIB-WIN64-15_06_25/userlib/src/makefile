#*******************************************************************************
#*
#*  Project:        Daisy Client Library
#*
#*  Filename:       makefile.win
#*
#*  Purpose:        MSVC makefile for qutaubase example 0
#*
#*  Author:         NHands GmbH & Co KG
#*
#********************************************************************************
# $Id: makefile.win,v 1.1 2014/02/14 17:46:46 trurl Exp $

example0.exe : example0.obj ..\lib\tdcbase.lib
	link /NOLOGO /SUBSYSTEM:CONSOLE example0.obj ..\lib\tdcbase.lib

example0.obj :  example0.c
	cl -nologo -c -W3 -MD -I..\inc example0.c

