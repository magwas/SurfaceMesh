# coding=UTF-8

import FreeCAD
from Base import BaseVP

from Layer import SMLayer
from Point import SMPoint
from Edge import SMEdge
from Face import SMFace


class SMesh:
    """ A surface mesh """
    def __init__(self):
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Mesh")
            self.obj.addProperty("App::PropertyLinkList","Layers","Base", "Layers")
            self.Type = "SMesh"
            SMeshVP(self.obj.ViewObject)
            self.obj.Proxy = self

    def execute(self,fp):
        pass

    def getOrCreateLayer(self,name=None):
        """
            gets an existing layer, or creates it if does not exists
            arguments:
                name: name of the layer. optional. If omitted, we are looking for the default one
        """
        if name == None:
            name = SMLayer.getDefaultName()
        for layer in self.obj.InList:
            if layer.Proxy.Type == "SMLayer":
                if layer.Label == name:
                    return layer
        l = SMLayer(self,name).obj
        return l
        
    def registerLayer(self,l):
        layers = self.obj.Layers
        layers.append(l)
        self.obj.Layers = layers
        
    def getOrCreatePoint(self,vect,layername=None):
        """
            gets or creates the point with the given vector
            arguments:
                vect: the vector representing the coordinates of the point
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        for layer in self.obj.InList:
            if layer.Proxy.Type == "SMLayer":
                for point in layer.InList:
                    if point.Proxy.Type == "SMPoint":
                        if point.Coordinates == vect:
                            #FIXME maybe some error should be allowed...
                            return point
        return SMPoint(self.getOrCreateLayer(layername),vect).obj

    def getOrCreateEdge(self,p1,p2,layername=None):
        """
            gets or creates the edge with the given endpoints
            arguments:
                pi, p2: the endpoints of the edge
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        FreeCAD.Console.PrintMessage('search %s, %s\n'%(p1.Label,p2.Label))
        for layer in self.obj.InList:
            if layer.Proxy.Type == "SMLayer":
                for edge in layer.InList:
                    if edge.Proxy.Type == "SMEdge":
                        if edge.Start==p1 and edge.End==p2:
                            FreeCAD.Console.PrintMessage('found  %s, %s\n'%(edge.Start.Label,edge.End.Label))
                            return edge
        return SMEdge(self.getOrCreateLayer(layername),p1,p2).obj

    def getOrCreateFace(self,points,layername=None):
        """
            gets or creates the face with the given points
            arguments:
                points: the points of the face
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        for layer in self.obj.InList:
            if layer.Proxy.Type == "SMLayer":
                for face in layer.InList:
                    if face.Proxy.Type == "SMface":
                        if face.isOnPoints(points):
                            return face
        return SMFace(self.getOrCreateLayer(layername),points).obj
        
    
class SMeshVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)
    def claimChildren(self):
        return self.Object.InList


