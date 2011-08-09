# coding=UTF-8

import FreeCAD
import Part

from DocumentObject import DocumentObject

class SMEdge(DocumentObject):
    """
        An edge is defined by the start and end point.
        It also have a layer it belongs to
    """
    pytype="SMEdge"
    def __init__(self,layer,start,end,crease=None):
            DocumentObject.__init__(self)
            FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Edge",self,self)
            self.addProperty("App::PropertyLink","Start","Base","Start point")
            self.addProperty("App::PropertyLink","End","Base","End point")
            #self.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.addProperty("App::PropertyEnumeration","Creased","Base","Creased?").Creased=["Creased","Normal"]
            #self.addProperty("App::PropertyLinkList","Faces","Base", "Faces using this edge")
            #self.Layer=layer.getobj()
            layer.registerEdge(self)
            self.Start=start.getobj()
            self.End=end.getobj()
            self.setCreased(crease)
            self.createGeometry()
            
    def fromfef(self,data):
        #FIXME: the whole fef import stuff should be moved to Mesh
        mesh = self.getParentByType('SMesh')
        start,end,crease,selected=data.strip().split(' ')
        startp = mesh.fefpoint(int(start))
        stopp = mesh.fefpoint(int(stop))
        start=ship.points[int(start)]
        end=ship.points[int(end)]
        return SMEdge(self.Layer,startp, stopp,crease)

    def toggleCrease(self):
        #FreeCAD.Console.PrintMessage("toggleCrease %s %s\n"%(self.Label,self.Creased))

        if self.Creased == "Creased":
            self.Creased = "Normal"
        else:
            self.Creased = "Creased"
        #FreeCAD.Console.PrintMessage("toggleCrease end %s %s\n"%(self.Label,self.Creased))
        self.creaseColor()


    def onChanged(self,prop,attach=False):
        if prop == "Creased":
            self.creaseColor()
        else:
            DocumentObject.onChanged(self,prop,attach)
            
    def creaseColor(self):
        creased = self.Creased
        if (not creased) or (creased == "Normal"):
            self.LineColor = (0.0,0.0,0.0,0.0)
        else:
            self.LineColor = (1.0,0.0,0.0,0.0)

    def setCreased(self,creased):
        if (not creased) or (creased == "Normal"):
            self.Creased = "Normal"
        else:
            self.Creased = "Creased"

    def getPoints(self):
        return [self.Start.Proxy,self.End.Proxy]

    def getMyFaces(self):
        mesh = self.getParentByType('SMesh')
        l = []
        for e in mesh.getFaces():
            if self in e.getEdges():
                l.append(e)
        return l

    def createGeometry(self):
        #FreeCAD.Console.PrintMessage("Edge creategeo %s"%self.Label)
        for e in self.getMyFaces():
            e.Proxy.createGeometry()
        plm = self.Placement
        #FreeCAD.Console.PrintMessage("%s,%s"%(self.Start.Coordinates,self.End.Coordinates))
        self.Shape=Part.Line(self.Start.Coordinates,self.End.Coordinates).toShape()
        self.Placement = plm

