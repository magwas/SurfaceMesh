# coding=UTF-8

import FreeCAD, FreeCADGui 
from pivy import coin
import Part


class AddMesh: 
    def Activated(self): 
        FreeCAD.Console.PrintMessage('Hello, World!\n')
        FreeCAD.ActiveDocument.openTransaction("Adding Mesh\n")
        self.mesh = SMesh()
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            tipe = self.obtype(ob)
            if tipe == "Wire":
                self.meshWire(ob)
            else:
                FreeCAD.Console.PrintMessage('Cannot mesh object %s(%s)\n'%(ob.Label,tipe))
        FreeCAD.ActiveDocument.commitTransaction()


    def meshWire(self,ob):
            firstp=None
            lastp=None
            points=[]
            for p in ob.Points:
                points.append(p)
                sp = self.mesh.getOrCreatePoint(p,"points")
                if firstp is None:
                    firstp=sp
                if lastp is not None:
                    self.mesh.getOrCreateEdge(lastp,sp,"edges")
                lastp = sp
            if len(ob.Points) > 2 and ob.Closed:
                self.mesh.getOrCreateEdge(lastp,firstp,"edges")
            if ob.ViewObject.DisplayMode == "Flat Lines" and ob.Closed:
                self.mesh.getOrCreateFace(points,"faces")

    @staticmethod
    def obtype(ob):
        p = getattr(ob,"Proxy",None)
        if p:
            ob = p
        return getattr(ob,"Type",None)

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Add Mesh', 'ToolTip': 'Adds an empty surface mesh'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None
      

class BaseVP:
    """Basic view provider"""
    def __init__(self,vobj):
        vobj.Proxy=self
        self.Object=vobj.Object
        self.vobj=vobj

    def updatedata():
        return

    def onChanged(self,vobj,prop):
        return

    def attach(self,obj):
        return

    def getDisplayModes(self,obj):
        modes=[]
        return modes

    def setDisplayMode(self,mode):
        return mode

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def claimChildren(self):
        return []

    def getIcon(self):
        return """
                /* XPM */
                static char * Arch_Wall_xpm[] = {
                "16 16 9 1",
                "       c None",
                ".      c #543016",
                "+      c #6D2F08",
                "@      c #954109",
                "#      c #874C24",
                "$      c #AE6331",
                "%      c #C86423",
                "&      c #FD7C26",
                "*      c #F5924F",
                "                ",
                "                ",
                "       #        ",
                "      ***$#     ",
                "    .*******.   ",
                "   *##$****#+   ",
                " #**%&&##$#@@   ",
                ".$**%&&&&+@@+   ",
                "@&@#$$%&&@@+..  ",
                "@&&&%#.#$#+..#$.",
                " %&&&&+%#.$**$@+",
                "   @%&+&&&$##@@+",
                "     @.&&&&&@@@ ",
                "        @%&&@@  ",
                "           @+   ",
                "                "};
                """
        

"""
    Abstractions
    We have
        - points
        - edges
        - faces
        - layers
        - mesh

    An edge is defined by two points in the same mesh.
    A face is defined by a topologically closed set of edges in the same mesh.
    A layer is a set of faces, edges and points.
    A mesh is a set of layers.
"""

class SMLayer:
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
        return self.Object.Edges + self.Object.Points + self.Object.Faces

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


class SMPoint:
    """
        A point is defined by a vector.
        It keeps a list of references to edges, so when it moved, the edges can be updated
    """
    def __init__(self,layer,vect=None):
            self.obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Point")
            self.obj.addProperty("App::PropertyVector","Coordinates","Base","Coordinates")
            self.obj.addProperty("App::PropertyLinkList","Edges","Base", "Edges using this point")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.obj.Layer=layer
            layer.Proxy.registerPoint(self.obj)
            if vect is None:
                vect=FreeCAD.Base.Vector(0,0,0)
            self.obj.Coordinates=vect
            self.obj.Proxy = self
            self.Type = "SMPoint"
            SMPointVP(self.obj.ViewObject)
            
    @staticmethod
    def fromfef(data):
        x,y,z,vertextype,selected=data.strip().split(' ')
        return SMPoint(FreeCAD.Base.Vector(x,y,z))

    def __repr__(self):
        return "[%s,%s,%s]"%(self.obj.Coordinates.x,self.obj.Coordinates.y,self.obj.Coordinates.z)
    def fefstr(self):
        #vertextype = 1, selected=0
        return "%s %s %s %s %s\r\n"%(self.Coordinates.x,self.Coordinates.y,self.Coordinates.z,1,0)
    # FreeCad methods
    def execute(self,obj):
        pass
        
    def onChanged(self,obj,prop):
        if prop in ["Coordinates"]:
            for e in self.Edges:
                e.createGeometry()


class SMPointVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)
        self.mkmarker()
        self.show()

    def onChanged(self,vobj,prop):
        #FreeCAD.Console.PrintMessage("onChanged  %s, %s\n"%(vobj,prop))
        if prop == "Visibility":
            if vobj.Visibility:
                self.show()
            else:
                self.hide()
        return

    def mkmarker(self):
        vobj=self.vobj
        col = coin.SoBaseColor()
        col.rgb.setValue(vobj.LineColor[0],
                         vobj.LineColor[1],
                         vobj.LineColor[2])
        self.coords = coin.SoCoordinate3()
        c = vobj.Object.Coordinates
        self.coords.point.setValue(c.x, c.y, c.z)
        self.pt = coin.SoAnnotation()
        self.pt.addChild(col)
        self.pt.addChild(self.coords)
        marker=coin.SoMarkerSet()
        marker.markerIndex=coin.SoMarkerSet.CIRCLE_FILLED_5_5
        self.pt.addChild(marker)

    def show(self):
        self.vobj.RootNode.addChild(self.pt)
    def hide(self):
        self.vobj.RootNode.removeChild(self.pt)


class SMEdge:
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
            self.createGeometry(self.obj)
            
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

    def createGeometry(self,fp):
        for e in fp.Faces:
            e.createGeometry()
        plm = fp.Placement
        fp.Shape=Part.Line(fp.Start.Coordinates,fp.End.Coordinates).toShape()
        fp.Placement = plm

class SMEdgeVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)

class SMFace:
    """
        A face is defined by a set of points.
        All edges of the face are created if not already exists.
        The face is stored as a sorted list of edges
        It also have a layer it belongs to
    """
    def __init__(self,layer,points):
            self.obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython","Face")
            self.obj.addProperty("App::PropertyLinkList","Edges","Base","End point")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.obj.Layer=layer
            layer.Proxy.registerFace(self.obj)
            edges = self.getOrCreateEdges(points)
            if not edges:
                raise UnimplementedError, "Cannot add a face by noncircular edgeset"
            self.obj.Edges=edges
            self.Type = "SMFace"
            self.obj.Proxy = self
            SMFaceVP(self.obj.ViewObject)
            self.createGeometry(self.obj)

    def getOrCreateEdges(self,points):
        fp=self.obj.Layer.Mesh.Proxy.getOrCreatePoint(points[0])
        FreeCAD.Console.PrintMessage('p0=%s\n'%fp.Label)
        lastp=fp
        edges=[]
        for pp in points[1:]:
            p=self.obj.Layer.Mesh.Proxy.getOrCreatePoint(pp)
            FreeCAD.Console.PrintMessage('p =%s\n'%p.Label)
            edges.append(self.obj.Layer.Mesh.Proxy.getOrCreateEdge(lastp,p,self.obj.Layer.Label))
            lastp = p
        FreeCAD.Console.PrintMessage('lp=%s\n'%p.Label)
        edges.append(self.obj.Layer.Mesh.Proxy.getOrCreateEdge(lastp,fp,self.obj.Layer.Label))
        return edges

    def getPoints(self):
        points=[]
        edges = self.obj.Edges
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

    def createGeometry(self,fp):
        plm = fp.Placement
        ps=self.getPoints()
        pvs = map(lambda x: x.Coordinates, ps)
        shape = Part.makePolygon(pvs)
        fp.Shape = Part.Face(shape)
        fp.Placement = plm

class SMFaceVP (BaseVP):
    """ view provider for Faces"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)


FreeCADGui.addCommand('Add Mesh', AddMesh())
