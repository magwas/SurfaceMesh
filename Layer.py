# coding=UTF-8

import FreeCAD

from Base import Base,BaseVP

class SMLayer(Base):
    """ A layer """
    def __init__(self,mesh,name=None):
            if name == None:
                name = self.getDefaultName()
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Layer")
            self.obj.addProperty("App::PropertyLinkList","Edges","Base", "Edges")
            self.obj.addProperty("App::PropertyLinkList","Points","Base", "Points")
            self.obj.addProperty("App::PropertyLinkList","Faces","Base", "Faces")
            self.obj.addProperty("App::PropertyLink","Mesh","Base", "The mesh this point is in")
            self.obj.Mesh=mesh.obj
            mesh.registerLayer(self.obj)
            self.obj.Label = name
            self.Type = "SMLayer"
            SMLayerVP(self.obj.ViewObject)
            self.obj.Proxy = self

    def registerPoint(self,p):
        l = self.obj.Points
        l.append(p)
        self.obj.Points = l

    def registerEdge(self,p):
        l = self.obj.Edges
        l.append(p)
        self.obj.Edges = l

    def registerFace(self,p):
        l = self.obj.Faces
        l.append(p)
        self.obj.Faces = l

    @staticmethod
    def getDefaultName():
        return "Default Layer"

    def execute(self,fp):
        pass

class SMLayerVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)
    def claimChildren(self):
        FreeCAD.Console.PrintMessage("claim %s\n"%(self.Object.Label))
        return self.Object.Edges + self.Object.Points + self.Object.Faces

