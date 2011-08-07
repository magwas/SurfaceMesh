# coding=UTF-8

import FreeCAD
import Part

from DocumentObject import DocumentObject

class SMFace(DocumentObject):
    """
        A face is defined by a set of points.
        All edges of the face are created if not already exists.
        The face is stored as a sorted list of edges
        It also have a layer it belongs to
    """
    pytype = "SMFace"
    def __init__(self,layer,points):
            DocumentObject.__init__(self)
            FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Face",self,self)
            self.addProperty("App::PropertyLinkList","Edges","Base","End point")
            self.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.Layer=layer.getobj()
            layer.registerFace(self)
            edges = self.getOrCreateEdges(points)
            if not edges:
                raise UnimplementedError, "Cannot add a face by noncircular edgeset"
            self.Edges = map(lambda x: x.getobj(), edges)
            self.createGeometry()

    def getOrCreateEdges(self,points):
        fp=self.Layer.Mesh.Proxy.getOrCreatePoint(points[0])
        FreeCAD.Console.PrintMessage('p0=%s\n'%fp.Label)
        lastp=fp
        edges=[]
        for pp in points[1:]:
            p=self.Layer.Mesh.Proxy.getOrCreatePoint(pp)
            FreeCAD.Console.PrintMessage('p =%s\n'%p.Label)
            edges.append(self.Layer.Mesh.Proxy.getOrCreateEdge(lastp,p,self.Layer.Label))
            lastp = p
        FreeCAD.Console.PrintMessage('lp=%s\n'%p.Label)
        edges.append(self.Layer.Mesh.Proxy.getOrCreateEdge(lastp,fp,self.Layer.Label))
        return edges

    def getPoints(self):
        points=[]
        edges = self.Edges
        for e in edges:
            points.append(e.Start)
        points.append(edges[-1].End)
        return points
            
    def isOnPoints(self,points):
        myps=self.getPoints()
        if len(points) != len(self.getPoints()):
            return False
        for i in range(len(points)):
            if myps[i] != points[i]:
                return False
        return True
        
            
    def fromfef(self,data):
        # FIXME: it needs to be converted to this framework
            if data:
                data=data.strip().split(' ')
                numpoints=int(data[0])
                self.points=[]
                #print data
                for i in range(numpoints):
                    self.points.append(ship.points[int(data[i+1])])
                #print i
                self.layer=ship.layers[int(data[i+2])]
                self.selected=int(data[i+3])
            if points:
                self.points+=points
            if layer:
                self.layer=layer
            self.plane=Plane(face=self)

    def createGeometry(self):
        fp = self
        plm = fp.Placement
        ps=self.getPoints()
        pvs = map(lambda x: x.Coordinates, ps)
        shape = Part.makePolygon(pvs)
        fp.Shape = Part.Face(shape)
        fp.Placement = plm

