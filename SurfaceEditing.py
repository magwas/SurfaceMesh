# coding=UTF-8

import FreeCAD, FreeCADGui 
from pivy import coin
import Part


class AddMesh: 
    def Activated(self): 
        FreeCAD.Console.PrintMessage('Hello, World!')
        FreeCAD.ActiveDocument.openTransaction("Adding Mesh")
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
            for p in ob.Points:
                sp = self.mesh.getOrCreatePoint(p,"points")
                if firstp is None:
                    firstp=sp
                if lastp is not None:
                    self.mesh.getOrCreateEdge(lastp,sp,"edges")
                lastp = sp
            if len(ob.Points) > 2 and ob.Closed:
                self.mesh.getOrCreateEdge(lastp,firstp,"edges")

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
            gets or creates the point with the given vector
            arguments:
                vect: the vector representing the coordinates of the point
                layername: name of the layer where to put a new point. Optional. If omitted, the default layer is used.
        """
        for edge in self.obj.InList:
            if edge.Proxy.Type == "SMEdge":
                if edge.Start==p1 and edge.End==p2:
                    return edge
        return SMEdge(self.getOrCreateLayer(layername),p1,p2).obj
        
    
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
        return "[%s,%s,%s]"%(self.Coordinates.x,self.Coordinates.y,self.Coordinates.z)
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
        self.attach(vobj)

    def attach(self,vobj):
        col = coin.SoBaseColor()
        col.rgb.setValue(vobj.LineColor[0],
                         vobj.LineColor[1],
                         vobj.LineColor[2])
        self.coords = coin.SoCoordinate3()
        c = self.Object.Coordinates
        self.coords.point.setValue(c.x, c.y, c.z)
        self.pt = coin.SoAnnotation()
        self.pt.addChild(col)
        self.pt.addChild(self.coords)
        marker=coin.SoMarkerSet()
        marker.markerIndex=coin.SoMarkerSet.CIRCLE_FILLED_5_5
        self.pt.addChild(marker)
        vobj.RootNode.addChild(self.pt)


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
        FreeCAD.Console.PrintMessage('adding shape to %s (%s,%s) self=%s'%(fp,fp.Start.Coordinates,fp.End.Coordinates,self))
        for e in fp.Faces:
            e.createGeometry()
        plm = fp.Placement
        fp.Shape=Part.Line(fp.Start.Coordinates,fp.End.Coordinates).toShape()
        fp.Placement = plm
        """
>>> edge=App.getDocument("a").getObject("Edge")
>>> edge.Proxy.createGeometry(edge)
"""

class SMEdgeVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)


FreeCADGui.addCommand('Add Mesh', AddMesh())
