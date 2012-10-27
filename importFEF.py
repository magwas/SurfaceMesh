# -*- coding: utf-8 -*-

__title__="FreeCAD Draft Workbench - Airfoil data importer"
__author__ = "Heiko Jakob <heiko.jakob@gediegos.de>"

import re, FreeCAD, FreeCADGui, Part, cProfile, os, string
from FreeCAD import Vector, Base
from fef import Ship
import sys, traceback

def open(filename):
	"called when freecad opens a file"
	docname = os.path.splitext(os.path.basename(filename))[0]
	doc = FreeCAD.newDocument(docname)
	doc.Label = docname[:-4]
	process(doc,filename)

def insert(filename,docname):
	"called when freecad imports a file"
	groupname = os.path.splitext(os.path.basename(filename))[0]
	try:
		doc=FreeCAD.getDocument(docname)
	except:
		doc=FreeCAD.newDocument(docname)
	importgroup = doc.addObject("App::DocumentObjectGroup",groupname)
	importgroup.Label = groupname
	process(doc,filename)

def process(doc,filename):    
	try:
		ship=Ship(filename)
	except:
		traceback.print_exc(file=sys.stdout)
		return
	ship.addToDoc(doc)

