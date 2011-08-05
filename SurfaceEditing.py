# coding=UTF-8

import FreeCAD, FreeCADGui 
from FreeCAD import Gui

from SurfaceMesh.Mesh import SMesh

class AddMesh: 
    def Activated(self): 
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

class Observe:
    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Observe', 'ToolTip': 'Observe'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self): 
        v=Gui.activeDocument().activeView()
        c = v.addEventCallback("SoEvent",self.observe)

    def observe(info):
        """
            mousedown: record position p0
            mosemove if button is down: move all currently selected points with pcurrent-p0
            mouseup: do finalisations if needed
        """
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(info["Type"],))
        FreeCAD.Console.PrintMessage("EVENT %s\n"%(info,))
      

FreeCADGui.addCommand('Add Mesh', AddMesh())
FreeCADGui.addCommand('Observe', Observe())
