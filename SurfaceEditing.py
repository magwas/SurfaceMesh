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

class SurfaceEdit:
    def __init__(self):
        self.do=False

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Surface Editing', 'ToolTip': 'Turns on/off the surface editing mode'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self): 
        self.view=Gui.activeDocument().activeView()
        c = self.view.addEventCallback("SoEvent",self.observe)

    def mouseDown(self,pos):
        self.m0=pos
        self.vd0=self.view.getViewDirection()
        self.p0=self.view.getPoint(self.m0)

    def mouseUp(self,pos):
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            mover = None
            if getattr(ob,"Proxy",None):
                mover = getattr(ob.Proxy,"endMoveByMouse",None)
            #FreeCAD.Console.PrintMessage("mover=%s"%mover)
            if mover:
                mover()

    def mouseMove(self,pos):
        vd0 = self.view.getViewDirection()
        if vd0 != self.vd0:
            # the user has changed the viewpoint
            return
        delta = self.view.getPoint(pos) - self.p0
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            mover = None
            if getattr(ob,"Proxy",None):
                mover = getattr(ob.Proxy,"moveByMouse",None)
            if mover:
                mover(delta)

#EVENT {'ShiftDown': False, 'CtrlDown': False, 'Time': 'Friday, 08/05/11 02:11:56 PM', 'Position': (59, 367), 'AltDown': False, 'Type': 'SoLocation2Event'}
#EVENT {'ShiftDown': False, 'Button': 'BUTTON1', 'CtrlDown': False, 'State': 'DOWN', 'Time': 'Friday, 08/05/11 02:12:11 PM', 'Position': (59, 367), 'AltDown': False, 'Type': 'SoMouseButtonEvent'}
#EVENT {'ShiftDown': False, 'Button': 'BUTTON1', 'CtrlDown': False, 'State': 'UP', 'Time': 'Friday, 08/05/11 02:12:20 PM', 'Position': (59, 367), 'AltDown': False, 'Type': 'SoMouseButtonEvent'}
#EVENT {'ShiftDown': False, 'CtrlDown': False, 'State': 'DOWN', 'Key': 'c', 'Time': 'Friday, 08/05/11 02:12:23 PM', 'Position': (59, 367), 'AltDown': False, 'Type': 'SoKeyboardEvent'}
    def observe(self,event):
        """
            mousedown: record position p0
            mosemove if button is down: move all currently selected points with pcurrent-p0
            mouseup: do finalisations if needed
        """
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event["Type"],))
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event,))
        if event["Type"] == 'SoMouseButtonEvent' and event["Button"] == 'BUTTON1':
            if event['State'] == 'DOWN':
                self.do = True
                self.mouseDown(event['Position'])
            else:
                self.do = False
                self.mouseUp(event['Position'])
            return
        if self.do:
            if event["Type"] == 'SoLocation2Event':
                self.mouseMove(event['Position'])
            
      

FreeCADGui.addCommand('Add Mesh', AddMesh())
FreeCADGui.addCommand('SurfaceEdit', SurfaceEdit())
