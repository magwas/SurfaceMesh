# coding=UTF-8

import FreeCAD
import Part

from DocumentObject import DocumentObject

class SMEdge(DocumentObject):
    """
        An edge is defined by the start and end point.
        It also have a layer it belongs to
    """
    def __init__(self,layer,start,end,crease=None):
            DocumentObject.__init__(self)
            FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Edge",self,self)
            self.addProperty("App::PropertyLink","Start","Base","Start point")
            self.addProperty("App::PropertyLink","End","Base","End point")
            self.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.addProperty("App::PropertyEnumeration","Creased","Base","Creased?").Creased=["Creased","Normal"]
            self.addProperty("App::PropertyLinkList","Faces","Base", "Faces using this edge")
            self.Layer=layer.getobj()
            layer.registerEdge(self)
            self.Start=start.getobj()
            self.End=end.getobj()
            self.setcreased(crease)
            self.Type = "SMEdge"
            self.createGeometry()
            
    def fromfef(self,data):
        #FIXME: the whole fef import stuff should be moved to Mesh
        start,end,crease,selected=data.strip().split(' ')
        startp = self.Layer.Mesh.fefpoint(int(start))
        stopp = self.Layer.Mesh.fefpoint(int(stop))
        start=ship.points[int(start)]
        end=ship.points[int(end)]
        return SMEdge(self.Layer,startp, stopp,crease)

    def setcreased(self,creased):
        if (not creased) or (creased == "Normal"):
            self.Creased = "Normal"
        else:
            self.Creased = "Creased"

    def createGeometry(self):
        o=self
        #FreeCAD.Console.PrintMessage("Edge creategeo %s"%self.Label)
        for e in o.Faces:
            e.createGeometry()
        plm = o.Placement
        #FreeCAD.Console.PrintMessage("%s,%s"%(o.Start.Coordinates,o.End.Coordinates))
        o.Shape=Part.Line(o.Start.Coordinates,o.End.Coordinates).toShape()
        o.Placement = plm

