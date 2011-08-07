# coding=UTF-8

import FreeCAD
from pivy import coin

from DocumentObject import DocumentObject

class SMPoint(DocumentObject):
    """
        A point is defined by a vector.
        It keeps a list of references to edges, so when it moved, the edges can be updated
    """
    pytype = "SMPoint"
    def __init__(self,layer,vect=None):
            DocumentObject.__init__(self)
            self.p0=None
            self.pt=None
            FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Point",self,self)
            self.addProperty("App::PropertyVector","Coordinates","Base","Coordinates")
            self.addProperty("App::PropertyLinkList","Edges","Base", "Edges using this point")
            self.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.Layer=layer.getobj()
            layer.registerPoint(self)
            if vect is None:
                vect=FreeCAD.Base.Vector(0,0,0)
            self.mkmarker()
            self.Coordinates=vect
            self.show()

    def __setstate__(self,state):
        self.p0=None
        DocumentObject.__setstate__(self,state)
            
    @staticmethod
    def fromfef(data):
        x,y,z,vertextype,selected=data.strip().split(' ')
        return SMPoint(FreeCAD.Base.Vector(x,y,z))

    #def __repr__(self):
    #    return "[%s,%s,%s]"%(self.obj.Coordinates.x,self.obj.Coordinates.y,self.obj.Coordinates.z)
    def fefstr(self):
        #vertextype = 1, selected=0
        return "%s %s %s %s %s\r\n"%(self.Coordinates.x,self.Coordinates.y,self.Coordinates.z,1,0)
    # FreeCad methods

    def endMoveByMouse(self):
        self.p0=None

    def moveByMouse(self,delta):
        FreeCAD.Console.PrintMessage("%s.mBM(%s) p0=%s\n"%(self,delta,self.p0))
        if not self.p0:
            self.p0 = self.Coordinates
        self.Coordinates = self.p0 + delta
        #self.mkmarker()

    def onChanged(self,prop):
        FreeCAD.Console.PrintMessage("onChangedo  %s, %s\n"%(self,prop))
        if prop == "Coordinates":
            self.hide()
            c = self.Coordinates
            self.coords.point.setValue(c.x, c.y, c.z)
            for e in self.Edges:
                e.Proxy.createGeometry()
            self.show()
        elif prop == "Visibility":
            if self.Visibility:
                self.show()
            else:
                self.hide()
        else:
            DocumentObject.onChanged(self,prop)

    def mkmarker(self):
        col = coin.SoBaseColor()
        col.rgb.setValue(self.LineColor[0],
                         self.LineColor[1],
                         self.LineColor[2])
        self.coords = coin.SoCoordinate3()
        c = self.Coordinates
        self.coords.point.setValue(c.x, c.y, c.z)
        self.pt = coin.SoType.fromName("SoFCSelection").createInstance()
        self.pt.documentName.setValue(FreeCAD.ActiveDocument.Name)
        oname=str(self.Label)
        self.pt.objectName.setValue(oname)
        self.pt.subElementName.setValue("0")
        self.pt.addChild(col)
        self.pt.addChild(self.coords)
        marker=coin.SoMarkerSet()
        marker.markerIndex=coin.SoMarkerSet.CIRCLE_FILLED_5_5
        self.pt.addChild(marker)

    def show(self):
        FreeCAD.Console.PrintMessage("showing\n")
        #FIXME this is a workaround
        #self.mkmarker()
        #the bug shown when this is called the second time
        self.RootNode.addChild(self.pt)
        FreeCAD.Console.PrintMessage("showing end\n")
    def hide(self):
        FreeCAD.Console.PrintMessage("hiding %s\n"%self)
        self.RootNode.removeChild(self.pt)
        FreeCAD.Console.PrintMessage("hidden\n")


