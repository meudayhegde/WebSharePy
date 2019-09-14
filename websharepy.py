#!/usr/bin/python3

import sys
import argparse
from os import environ
from app import PyExplorer
import platform


HOME = 'HOME'
if platform.system().upper()=='WINDOWS':
	HOME = 'USERPROFILE'

parser = argparse.ArgumentParser(description="a flask based web server to explore storage")
parser.add_argument("--port", "-p",type=int,help="Port to listen on",default=8080)
parser.add_argument("--dir", "-d",type=str,help="Directory from the machine to serve",default=environ.get(HOME))
parser.add_argument("--host", "-H",type=str,help="Client address to accept request from",default='0.0.0.0')
args = parser.parse_args()


if __name__ == '__main__':
	app=PyExplorer(port=args.port,path=args.dir,host=args.host)
	app.start()
