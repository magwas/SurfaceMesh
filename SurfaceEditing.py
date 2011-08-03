# coding=UTF-8

import FreeCAD, FreeCADGui 

class AddMesh: 
   def Activated(self): 
        FreeCAD.Console.PrintMessage('Hello, World!')
        mesh = SMesh()
        layer = mesh.obj.InList[0]
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            for p in getattr(ob,"Points"):
                sp = SMPoint(layer, p)

   def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Add Mesh', 'ToolTip': 'Adds an empty surface mesh'} 
      

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
    def __init__(self,mesh):
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Layer")
            #self.obj.addProperty("App::PropertyLinkList","Edges","Base", "Edges")
            #self.obj.addProperty("App::PropertyLinkList","Points","Base", "Points")
            #self.obj.addProperty("App::PropertyLinkList","Faces","Base", "Faces")
            self.obj.addProperty("App::PropertyLink","Mesh","Base", "The mesh this point is in")
            self.obj.Mesh=mesh.obj
            self.obj.Proxy = self
            self.Type = "SMLayer"
            SMeshVP(self.obj.ViewObject)

class SMLayerVP (BaseVP):
    """ view provider for points"""
    def __init__(self,vobj):
        BaseVP.__init__(self,vobj)

class SMesh:
    """ A surface mesh """
    def __init__(self):
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Mesh")
            #self.obj.addProperty("App::PropertyLinkList","Layers","Base", "Layers")
            self.obj.Proxy = self
            self.Type = "SMesh"
            SMeshVP(self.obj.ViewObject)
            SMLayer(self)
    
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
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Point")
            self.obj.addProperty("App::PropertyVector","Coordinates","Base","Coordinates")
            self.obj.addProperty("App::PropertyLinkList","Edges","Base", "Edges using this point")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this point is in")
            self.obj.addProperty("App::PropertyLink","Mesh","Base", "The mesh this point is in")
            self.Layer=layer
            self.Mesh=layer.Mesh
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

"""
class Edge:
    def __init__(self,data=None,start=None,end=None,crease=0,selected=0):
            self.obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Edge")
            self.obj.addProperty("App::PropertyLink","StartPoint","Base", "The starting point of the edge")
            self.obj.addProperty("App::PropertyLink","EndPoint","Base", "The endpoint of the edge")
            self.obj.addProperty("App::PropertyLink","Layer","Base", "The layer this edge is in")
            self.obj.addProperty("App::PropertyLink","Mesh","Base", "The mesh this edge is in")
            self.obj.addProperty("App::PropertyLink","Mesh","Base", "The mesh this edge is in")
            self.obj.addProperty("App::PropertyEnumeration","Creased","Base","Creased?").Enum=["Creased","Normal"]
            if data:
                self.start,self.end,self.crease,self.selected=data.strip().split(' ')
                self.start=ship.points[int(self.start)]
                self.end=ship.points[int(self.end)]
            if start:
                self.start=start
            if end:
                self.end=end
                self.selected=1
            self.selected=int(self.selected)

    def setcreased(self,creased):
        if creased:
            self.obj.Creased = "Creased"
        else:
            self.obj.Creased = "Normal"
"""

FreeCADGui.addCommand('Add Mesh', AddMesh())
