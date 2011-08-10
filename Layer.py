# coding=UTF-8

import FreeCAD

from DocumentObject import DocumentObject

class SMLayer(DocumentObject):
    """ A layer """
    pytype = "SMLayer"
    def __init__(self,mesh,name=None):
            DocumentObject.__init__(self)
            if name == None:
                name = self.getDefaultName()
            FreeCAD.ActiveDocument.addObject("App::FeaturePython","Layer",self,self)
            self.addProperty("App::PropertyLinkList","Edges","Base", "Edges")
            self.addProperty("App::PropertyLinkList","Points","Base", "Points")
            self.addProperty("App::PropertyLinkList","Faces","Base", "Faces")
            self.addProperty("App::PropertyLinkList","Layers","Base", "Faces")
            #self.addProperty("App::PropertyLink","Mesh","Base", "The mesh this point is in")
            #self.Mesh=mesh.getobj()
            mesh.registerLayer(self)
            self.Label = name

    def getEdges(self):
        ret = map(lambda x: x.Proxy,self.Edges)
        for l in self.Layers:
            ret.extend(l.Proxy.getEdges())
        return ret

    def getLayers(self):
        ret = map(lambda x: x.Proxy,self.Layers)
        for l in self.Layers:
            ret.extend(l.Proxy.getLayers())
        return ret

    def getFaces(self):
        ret = map(lambda x: x.Proxy,self.Faces)
        for l in self.Layers:
            ret.extend(l.Proxy.getFaces())
        return ret

    def getPoints(self):
        ret = map(lambda x: x.Proxy,self.Points)
        for l in self.Layers:
            ret.extend(l.Proxy.getFaces())
        return ret

    def registerPoint(self,p):
        self.Points += [p.getobj()]

    def registerEdge(self,p):
        self.Edges += [p.getobj()]

    def registerFace(self,p):
        self.Faces += [p.getobj()]

    @staticmethod
    def getDefaultName():
        return "Default Layer"

    def claimChildren(self):
        #FreeCAD.Console.PrintMessage("claim %s\n"%(self.Object.Label))
        return self.Object.Edges + self.Object.Points + self.Object.Faces

