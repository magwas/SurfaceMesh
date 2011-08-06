# coding=UTF-8

import FreeCAD
import Part

from Base import Base, BaseVP

class SMEdge(Base):
    """
        An edge is defined by the start and end point.
        It also have a layer it belongs to
    """
    def __init__(self,layer,start,end,crease=None):
            self.obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Edge")
            self.obj.addProperty("App::PropertyLink","Start","Base","Start point")
            self.obj.addProperty("App::PropertyLink","End","Base","End point")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.obj.addProperty("App::PropertyEnumeration","Creased","Base","Creased?").Creased=["Creased","Normal"]
            self.obj.addProperty("App::PropertyLinkList","Faces","Base", "Faces using this edge")
            self.obj.Layer=layer
            layer.Proxy.registerEdge(self.obj)
            self.obj.Start=start
            self.obj.End=end
            self.setcreased(crease)
            self.obj.Proxy = self
            self.Type = "SMEdge"
            SMEdgeVP(self.obj.ViewObject)
            self.createGeometry()
            
    def fromfef(self,data):
        #FIXME: the whole fef import stuff should be moved to Mesh
        start,end,crease,selected=data.strip().split(' ')
        startp = self.Layer.Mesh.obj.fefpoint(int(start))
        stopp = self.Layer.Mesh.obj.fefpoint(int(stop))
        start=ship.points[int(start)]
        end=ship.points[int(end)]
        return SMEdge(self.Layer,startp, stopp,crease)

    def setcreased(self,creased):
        if (not creased) or (creased == "Normal"):
            self.obj.Creased = "Normal"
        else:
            self.obj.Creased = "Creased"

    def createGeometry(self):
        o=self.obj
        #FreeCAD.Console.PrintMessage("Edge creategeo %s"%self.obj.Label)
        for e in o.Faces:
            e.Proxy.createGeometry()
        plm = o.Placement
        #FreeCAD.Console.PrintMessage("%s,%s"%(o.Start.Coordinates,o.End.Coordinates))
        o.Shape=Part.Line(o.Start.Coordinates,o.End.Coordinates).toShape()
        o.Placement = plm

class SMEdgeVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)
