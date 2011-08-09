# coding=UTF-8

import FreeCAD
from DocumentObject import DocumentObject

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

class SMesh(DocumentObject):
    """ A surface mesh """
    pytype = "SMesh"
    def __init__(self):
            DocumentObject.__init__(self)
            FreeCAD.ActiveDocument.addObject("App::FeaturePython","Mesh",self,self)
            self.addProperty("App::PropertyLinkList","Layers","Base", "Layers")

    def getOrCreateLayer(self,name=None):
        """
            gets an existing layer, or creates it if does not exists
            arguments:
                name: name of the layer. optional. If omitted, we are looking for the default one
        """
        if name == None:
            name = SMLayer.getDefaultName()
        for layer in self.InList:
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
        for layer in self.InList:
            layer=layer.Proxy
            if layer.pytype == "SMLayer":
                for point in layer.InList:
                    point=point.Proxy
                    if point.pytype == "SMPoint":
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
        for layer in self.InList:
            layer=layer.Proxy
            if layer.pytype == "SMLayer":
                for edge in layer.InList:
                    edge=edge.Proxy
                    if edge.pytype == "SMEdge":
                        if edge.Start==p1 and edge.End==p2:
                            #FreeCAD.Console.PrintMessage('found  %s, %s\n'%(edge.Start.Label,edge.End.Label))
                            return edge
        e=SMEdge(self.getOrCreateLayer(layername),p1,p2)
        p1.Edges += [e.getobj()]
        p2.Edges += [e.getobj()]
        return e

    def getOrCreateFace(self,points,layername=None):
        """
            gets or creates the face with the given points
            arguments:
                points: the points of the face
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        for layer in self.InList:
            layer=layer.Proxy
            if layer.pytype == "SMLayer":
                for face in layer.InList:
                    face = face.Proxy
                    if face.pytype == "SMface":
                        if face.isOnPoints(points):
                            return face
        f = SMFace(self.getOrCreateLayer(layername),points)
        for e in f.Edges:
            e.Faces += [f.getobj()]
        return f
        
    def claimChildren(self):
        #FreeCAD.Console.PrintMessage("claim %s\n"%(self.Object.Label))
        return self.InList


