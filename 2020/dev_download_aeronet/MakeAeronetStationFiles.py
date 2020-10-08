#!/usr/bin/env python3
# Script for downloading Aeronet Data
# Created by: Jan Griesfeller (jang@met.no)

################################################################

import pdb
import sys
import os

####################################################################

def Html2Txt(infile, outfile, VerboseFlag=False, DebugFlag=False):
	#routine to do the actual conversion
	from bs4 import BeautifulSoup

	#read file
	if VerboseFlag is True:
		sys.stderr.write('reading HTML file: '+infile+'\n')
	with open(infile) as FHandle:
		Html=FHandle.read()

	#convert to txt using BeautifulSoup
	if VerboseFlag is True:
		sys.stderr.write('converting HTML to text...\n')
	Txt = BeautifulSoup(Html,"lxml")

	#write outfile
	if VerboseFlag is True:
		sys.stderr.write('writing text file: '+outfile+'\n')
	with open(outfile, 'w') as FHandle:
		FHandle.write(Txt.get_text())

	return 0

####################################################################

def WriteAeronetFiles(FileName, Outdir, VerboseFlag=False, DebugFlag=False, LongHeaderFlag=False):
	#routine to write Aeronet output files, one per station

	if LongHeaderFlag:
		HeaderLineNo = 7
	else:
		HeaderLineNo = 6

	if os.path.isdir(Outdir):
		if os.path.isfile(FileName):
			header=[]
			with open(FileName) as FHandle:
				FileString=FHandle.read()
			FHandle.close()

			OldFile=''
			for line in FileString.split('\n'):
				#print(line)
				if len(header) < HeaderLineNo:
					header.append(line.strip())
				else:
					DummyArr=line.split(',')
					if len(DummyArr[0]) < 2:
						continue
					Outfile=os.path.join(Outdir, DummyArr[0]+'.lev30')

					if not os.path.isfile(Outfile):
						if VerboseFlag is True:
							sys.stderr.write('writing new file: '+Outfile+'\n')
						OutHandle=open(Outfile, 'w')
						OutHandle.write('\n'.join(header)+'\n')
					else:
						if VerboseFlag is True:
							sys.stderr.write('appending to file: '+Outfile+'\n')
						try:
							if OutHandle.name != Outfile:
								OutHandle.close()
								OutHandle=open(Outfile, 'a')
						except NameError:
							#this handles the 1st file
							OutHandle=open(Outfile, 'a')
					OutHandle.write(','.join(DummyArr[:])+'\n')

			OutHandle.close()
			if DebugFlag is True:
				pdb.set_trace()
				
		else:
			sys.stderr.write("Error: file not found: "+FileName+" \n")
			sys.stderr.write('Exiting.\n')
			sys.exit(2)
		
	else:
		sys.stderr.write("Error: path does not exist: \n")
		sys.stderr.write('Exiting.\n')
		sys.exit(1)

	


######################################################################################

if __name__ == '__main__':
	import argparse

	dict_Param={}
	parser = argparse.ArgumentParser(description='MakeAeronetStationFiles: convert via the Aeronet web tools downloaded files to statiosn files used by the aerocom-tools\n\n')
	#epilog='RI#eturns some general statistics')
	parser.add_argument("infile", help="Input file as downloaded from AERONET")
	#parser.add_argument("infilehigh", help="infile")
#
	parser.add_argument("outdir", help="output directory; will be filled with one file per station")
	parser.add_argument("-v","--info", help="print some info since the operations may take some time", action='store_true')
	parser.add_argument("-d","--debug", help="debug mode; stop into python debug mode after the data reading", action='store_true')
	parser.add_argument("--textfile", help="switch off conversion html -> text file", action='store_true')
	#parser.add_argument("-l", help="")

	args = parser.parse_args()

	if args.debug:
		dict_Param['debug']=args.debug
	else:
		dict_Param['debug']=False

	if args.info:
		dict_Param['info']=args.info
	else:
		dict_Param['info']=False

	if args.infile:
		dict_Param['infile']=args.infile
	else:
		dict_Param['infile']=False

	if args.outdir:
		dict_Param['outdir']=args.outdir
	else:
		dict_Param['outdir']=False

	if args.textfile:
		dict_Param['textfile']=args.textfile
	else:
		dict_Param['textfile']=False
	
	if not dict_Param['textfile']:
		TmpFile='./Convert.txt'
		Success=Html2Txt(dict_Param['infile'], TmpFile, DebugFlag=dict_Param['debug'], VerboseFlag=dict_Param['info'])
		success=WriteAeronetFiles(TmpFile, dict_Param['outdir'], VerboseFlag=dict_Param['info'])
	else:
		TmpFile=dict_Param['infile']
		success=WriteAeronetFiles(TmpFile, dict_Param['outdir'], VerboseFlag=dict_Param['info'],LongHeaderFlag = True)




