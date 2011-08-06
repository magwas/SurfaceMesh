# coding=UTF-8

import FreeCAD
from pivy import coin

from Base import Base, BaseVP


class SMPoint(Base):
    """
        A point is defined by a vector.
        It keeps a list of references to edges, so when it moved, the edges can be updated
    """
    def __init__(self,layer,vect=None):
            self.obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Point")
            self.obj.addProperty("App::PropertyVector","Coordinates","Base","Coordinates")
            self.obj.addProperty("App::PropertyLinkList","Edges","Base", "Edges using this point")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.obj.Layer=layer
            layer.Proxy.registerPoint(self.obj)
            if vect is None:
                vect=FreeCAD.Base.Vector(0,0,0)
            self.obj.Coordinates=vect
            self.obj.Proxy = self
            self.Type = "SMPoint"
            SMPointVP(self.obj.ViewObject)
            self.p0=None
            
    @staticmethod
    def fromfef(data):
        x,y,z,vertextype,selected=data.strip().split(' ')
        return SMPoint(FreeCAD.Base.Vector(x,y,z))

    def __repr__(self):
        return "[%s,%s,%s]"%(self.obj.Coordinates.x,self.obj.Coordinates.y,self.obj.Coordinates.z)
    def fefstr(self):
        #vertextype = 1, selected=0
        return "%s %s %s %s %s\r\n"%(self.Coordinates.x,self.Coordinates.y,self.Coordinates.z,1,0)
    # FreeCad methods
    def execute(self,obj):
        pass
        
    def endMoveByMouse(self):
        self.p0=None

    def moveByMouse(self,delta):
        if not self.p0:
            self.p0 = self.obj.Coordinates
        self.obj.Coordinates = self.p0 + delta
        #self.ViewObject.mkmarker()

    def onChanged(self,obj,prop):
        #FreeCAD.Console.PrintMessage("onChangedo  %s, %s\n"%(obj,prop))
        if prop in ["Coordinates"]:
            self.obj.ViewObject.hide()
            self.obj.ViewObject.show()
            for e in self.obj.Edges:
                e.Proxy.createGeometry()


class SMPointVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)
        self.mkmarker()
        self.show()

    def onChanged(self,vobj,prop):
        #FreeCAD.Console.PrintMessage("onChanged  %s, %s\n"%(vobj,prop))
        if prop == "Visibility":
            if vobj.Visibility:
                self.show()
            else:
                self.hide()
        #FreeCAD.Console.PrintMessage("onChanged end\n")
        return

    def mkmarker(self):
        vobj=self.vobj
        col = coin.SoBaseColor()
        col.rgb.setValue(vobj.LineColor[0],
                         vobj.LineColor[1],
                         vobj.LineColor[2])
        self.coords = coin.SoCoordinate3()
        c = vobj.Object.Coordinates
        self.coords.point.setValue(c.x, c.y, c.z)
        self.pt = coin.SoType.fromName("SoFCSelection").createInstance()
        self.pt.documentName.setValue(FreeCAD.ActiveDocument.Name)
        oname=str(vobj.Object.Label)
        self.pt.objectName.setValue(oname)
        self.pt.subElementName.setValue("0")
        self.pt.addChild(col)
        self.pt.addChild(self.coords)
        marker=coin.SoMarkerSet()
        marker.markerIndex=coin.SoMarkerSet.CIRCLE_FILLED_5_5
        self.pt.addChild(marker)

    def show(self):
        #FreeCAD.Console.PrintMessage("showing\n")
        #FIXME this is a workaround
        self.mkmarker()
        #the bug shown when this is called the second time
        self.vobj.RootNode.addChild(self.pt)
        #FreeCAD.Console.PrintMessage("showing end\n")
    def hide(self):
        #FreeCAD.Console.PrintMessage("hiding\n")
        self.vobj.RootNode.removeChild(self.pt)
        #FreeCAD.Console.PrintMessage("hidden\n")


