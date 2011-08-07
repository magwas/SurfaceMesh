# coding=UTF-8

import FreeCAD, FreeCADGui 
from pivy import coin
import Part


class Base(object):
    def __getattribute__(self,name):
        FreeCAD.Console.PrintMessage("%s.%s\n"%(self,name))
        return object.__getattribute__(self,name)
    def __getstate__(self):
        return "nothing"

    def __setstate__(self,state):
        FreeCAD.Console.PrintMessage("setstate%s,%s\n"%(self,state))
        return None

    def onChanged(self,obj,prop):
        if prop == 'Proxy':
            self.obj = obj

class BaseVP:
    """Basic view provider"""
    def __init__(self,vobj):
        vobj.Proxy=self
        self.Object=vobj.Object
        self.vobj=vobj

    #def __getattribute__(self,name):
    #    FreeCAD.Console.PrintMessage("%s.%s\n"%(self,name))
    #    object.__getattribute__(self,name)

    def updateData(self, fp, prop):
        return

    def onChanged(self,vobj,prop):
        return

    def attach(self,obj):
        FreeCAD.Console.PrintMessage("attached %s\n"%(obj.Object.Label))
        self.vobj = obj
        self.Object = obj.Object
        return

    def getDisplayModes(self,obj):
        modes=[]
        return modes

    def setDisplayMode(self,mode):
        return mode

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        self.vobj = None
        self.Object = None
        return None

    def claimChildren(self):
        FreeCAD.Console.PrintMessage("claim \n")
        FreeCAD.Console.PrintMessage("claim %s\n"%(self.Object.Label))
        return []

    def getIcon(self):
        return """
                /* XPM */
                static char * Arch_Wall_xpm[] = {
                "16 16 9 1",
                "       c None",
                ".      c #543016",
                "+      c #6D2F08",
                "@      c #954109",
                "#      c #874C24",
                "$      c #AE6331",
                "%      c #C86423",
                "&      c #FD7C26",
                "*      c #F5924F",
                "                ",
                "                ",
                "       #        ",
                "      ***$#     ",
                "    .*******.   ",
                "   *##$****#+   ",
                " #**%&&##$#@@   ",
                ".$**%&&&&+@@+   ",
                "@&@#$$%&&@@+..  ",
                "@&&&%#.#$#+..#$.",
                " %&&&&+%#.$**$@+",
                "   @%&+&&&$##@@+",
                "     @.&&&&&@@@ ",
                "        @%&&@@  ",
                "           @+   ",
                "                "};
                """
        

