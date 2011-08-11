# coding=UTF-8

import FreeCAD
import Part

from DocumentObject import DocumentObject, prtb

class SMPoint(DocumentObject):
    """
        A point is defined by a vector.
        It keeps a list of references to edges, so when it moved, the edges can be updated
    """
    pytype = "SMPoint"
    def __init__(self,layer,vect=None):
            DocumentObject.__init__(self)
            FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Point",self,self)
            self.addProperty("App::PropertyVector","Coordinates","Base","Coordinates")
            #self.addProperty("App::PropertyLinkList","Edges","Base", "Edges using this point")
            #self.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            layer.registerPoint(self)
            if vect is None:
                vect=FreeCAD.Base.Vector(0,0,0)
            self.activate()
            self.Coordinates=vect
            self.show()
            self.createGeometry()

    def activate(self):
            self.p0=None

    def __setstate__(self,state):
        self.p0=None
        DocumentObject.__setstate__(self,state)
        self.activate()

    def attach(self,obj=None):
        DocumentObject.attach(self,obj)
            
    @staticmethod
    def fromfef(data):
        x,y,z,vertextype,selected=data.strip().split(' ')
        return SMPoint(FreeCAD.Base.Vector(x,y,z))

    #def __repr__(self):
    #    return "[%s,%s,%s]"%(self.obj.Coordinates.x,self.obj.Coordinates.y,self.obj.Coordinates.z)
    def fefstr(self):
        #vertextype = 1, selected=0
        return "%s %s %s %s %s\r\n"%(self.Coordinates.x,self.Coordinates.y,self.Coordinates.z,1,0)

    def dragStart(self,p0):
        #FreeCAD.Console.PrintMessage("dragStart(%s, %s) %s\n"%(self,p0,self.Coordinates))
        self.p0 = self.Coordinates
    def dragEnd(self,delta):
        #FreeCAD.Console.PrintMessage("dragEnd(%s, %s) %s\n"%(self,delta,self.Coordinates))
        self.Coordinates = self.p0 + delta
        self.p0 = None
    def dragMove(self,delta):
        #FreeCAD.Console.PrintMessage("dragMove(%s, %s) %s\n"%(self,delta,self.Coordinates))
        self.Coordinates = self.p0 + delta
        #self.onChanged("Coordinates")
        #self.mkmarker()

    def getMyEdges(self):
        mesh = self.getParentByType('SMesh')
        l = []
        for e in mesh.getEdges():
            if self in e.getPoints():
                l.append(e)
        return l

    def getMyFaces(self):
        mesh = self.getParentByType('SMesh')
        l = []
        for e in mesh.getFaces():
            if self in e.getPoints():
                l.append(e)
        return l

    def onChanged(self,prop,attach=False):
        #FreeCAD.Console.PrintMessage("onChanged  %s, %s, %s\n"%(self,prop,attach))

        #FIXME workaroud for arg # problem
     try:
        op=prop
        if attach:
            prop=attach

        if prop == "Coordinates":
            self.setCoords()
            for e in self.getMyEdges():
                e.Proxy.createGeometry()
            for f in self.getMyFaces():
                f.Proxy.createGeometry()
        elif prop == "Visibility":
            FreeCAD.Console.PrintMessage("V= %s\n"%(self.Visibility))
            if self.Visibility:
                self.show()
            else:
                self.hide()
        else:
            DocumentObject.onChanged(self,op,attach)
     except:
        prtb()

    def setCoords(self):
        vo=getattr(self,'ViewObject',None)
        if vo:
            self.Placement.Base=self.Coordinates

    def createGeometry(self):
        self.Shape=Part.Vertex(0,0,0)
        self.PointSize=5
        self.Placement.Base=self.Coordinates


