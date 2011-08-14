# coding=UTF-8

import FreeCAD
from DocumentObject import DocumentObject
from ops import History

from Layer import SMLayer
from Point import SMPoint
from Edge import SMEdge
from Face import SMFace

"""
App.newDocument()
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")
import SurfaceEditing
mesh=SurfaceEditing.SMesh()
mesh.getOrCreateLayer()
mesh.__object__.Layers
mesh.Layers
"""

class SMesh(DocumentObject,History):
    """ A surface mesh """
    pytype = "SMesh"
    def __init__(self):
            DocumentObject.__init__(self)
            History.__init__(self)
            FreeCAD.ActiveDocument.addObject("App::FeaturePython","Mesh",self,self)
            self.addProperty("App::PropertyLinkList","Layers","Base", "Layers")

    def getEdges(self):
        ret = []
        for l in self.Layers:
            ret.extend(l.Proxy.getEdges())
        return ret

    def getLayers(self):
        ret = self.Layers
        for l in self.Layers:
            ret.extend(l.Proxy.getLayers())
        return ret

    def getFaces(self):
        ret = []
        for l in self.Layers:
            ret.extend(l.Proxy.getFaces())
        return ret

    def getPoints(self):
        ret = []
        for l in self.Layers:
            ret.extend(l.Proxy.getPoints())
        return ret

    def getOrCreateLayer(self,name=None):
        """
            gets an existing layer, or creates it if does not exists
            arguments:
                name: name of the layer. optional. If omitted, we are looking for the default one
App.newDocument()
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")
import SurfaceEditing
mesh=SurfaceEditing.SMesh()
mesh.getOrCreateLayer()
mesh.__object__.Layers
mesh.getOrCreateLayer()
mesh.__object__.Layers
mesh.Layers

        """
        if name == None:
            name = SMLayer.getDefaultName()
        for layer in self.getLayers():
            layer=layer.Proxy
            if layer.pytype == "SMLayer":
                if layer.Label == name:
                    return layer
        l = SMLayer(self,name)
        return l
        
    def registerLayer(self,l):
        layers = self.Layers
        layers.append(l.getobj())
        self.Layers = layers
        
    def getOrCreatePoint(self,vect,layername=None):
        """
            gets or creates the point with the given vector
            arguments:
                vect: the vector representing the coordinates of the point
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        for point in self.getPoints():
            if point.Coordinates == vect:
                #FIXME maybe some error should be allowed...
                return point
        return SMPoint(self.getOrCreateLayer(layername),vect)

    def getOrCreateEdge(self,p1,p2,layername=None):
        """
            gets or creates the edge with the given endpoints
            arguments:
                pi, p2: the endpoints of the edge
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        #FreeCAD.Console.PrintMessage('search %s, %s\n'%(p1.Label,p2.Label))
        for edge in self.getEdges():
            if edge.Start.Proxy==p1 and edge.End.Proxy==p2:
                #FreeCAD.Console.PrintMessage('found  %s, %s\n'%(edge.Start.Label,edge.End.Label))
                return edge
        e=SMEdge(self.getOrCreateLayer(layername),p1,p2)
        return e

    def getOrCreateFace(self,points,layername=None):
        """
            gets or creates the face with the given points
            arguments:
                points: the points of the face
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        f = SMFace(self.getOrCreateLayer(layername),points)
        return f
        
    def claimChildren(self):
        #FreeCAD.Console.PrintMessage("claim %s\n"%(self.Object.Label))
        return self.Layers


