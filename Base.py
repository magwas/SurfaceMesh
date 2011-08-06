# coding=UTF-8

import FreeCAD, FreeCADGui 
from pivy import coin
import Part

class Base:
    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

class BaseVP:
    """Basic view provider"""
    def __init__(self,vobj):
        vobj.Proxy=self
        self.Object=vobj.Object
        self.vobj=vobj

    def updateData(self, fp, prop):
        return

    def onChanged(self,vobj,prop):
        return

    def attach(self,obj):
        return

    def getDisplayModes(self,obj):
        modes=[]
        return modes

    def setDisplayMode(self,mode):
        return mode

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def claimChildren(self):
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
        

