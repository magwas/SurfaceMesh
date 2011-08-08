# coding=UTF-8

import FreeCAD, FreeCADGui 
from FreeCAD import Gui

from SurfaceMesh.Mesh import SMesh

from pivy import coin

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
        FreeCAD.ActiveDocument.recompute()


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

"""
import SurfaceEditing

se = SurfaceEditing.SurfaceEdit()
se.Activated()

"""
class SurfaceEdit:
    def __init__(self):
        self.obj=None

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Surface Editing', 'ToolTip': 'Turns on/off the surface editing mode'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self): 
        FreeCAD.Console.PrintMessage("activate\n")
        self.obj=None
        self.view=Gui.activeDocument().activeView()
        self.call = self.view.addEventCallback("SoKeyboardEvent",self.observe)
        self.callp = self.view.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),self.getMouseClick) 
        self.callm = self.view.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(),self.getMouseMove) 

    def getPoint(self):
        return Gui.ActiveDocument.ActiveView.getPoint(tuple(self.event.getPosition().getValue()))

    def getMouseMove(self,event_cb):
        if not self.obj:
            return
        FreeCAD.Console.PrintMessage("moving\n")
        self.event=event_cb.getEvent()
        self.p0 = self.getPoint()
        cb = getattr(self.obj,'dragMove',self.dummycb)
        cb(self.p0)
        
    def dummycb(self,p):
        pass

    def getMouseClick(self,event_cb):
        self.ev=event_cb
        event=self.ev.getEvent()
        self.event = event
        if event.isButtonPressEvent(event,1):
            try:
                self.po = self.ev.getPickedPoint().getPath()
                oname = self.ev.getPickedPoint().getPath().getNodeFromTail(1).objectName.getValue()
                FreeCAD.Console.PrintMessage("picking %s\n"%oname)
                self.obj = Gui.ActiveDocument.getObject(str(oname)).Proxy
            except AttributeError:
                FreeCAD.Console.PrintMessage("Not picked anything\n")
                return
            self.p0 = self.getPoint()
            #FreeCAD.Console.PrintMessage("drag %s from %s\n"%(self.obj,self.p0))
            cb = getattr(self.obj,'dragStart',self.dummycb)
            cb(self.p0)
        elif event.isButtonReleaseEvent(event,1):
            FreeCAD.Console.PrintMessage("dragend %s from %s\n"%(self.obj,self.p0))
            self.p0 = self.getPoint()
            cb = getattr(self.obj,'dragEnd',self.dummycb)
            cb(self.p0)
            self.obj=None

    def deactivate(self):
        FreeCAD.Console.PrintMessage("deactivate\n")
        self.view.removeEventCallback("SoKeyboardEvent",self.call)
        self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),self.callp)
        self.view.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(),self.callm)
        FreeCAD.Console.PrintMessage("removed callbacks\n")
        self.do = False


    def observe(self,event):
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event["Type"],))
        FreeCAD.Console.PrintMessage("EVENT %s\n"%(event,))
        if event["Type"] == 'SoKeyboardEvent':
            if event['Key'] == 'ESCAPE':
                self.deactivate()
      

FreeCADGui.addCommand('Add Mesh', AddMesh())
FreeCADGui.addCommand('SurfaceEdit', SurfaceEdit())
