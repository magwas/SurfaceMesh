# coding=UTF-8

import FreeCAD, FreeCADGui 
from FreeCAD import Gui

from SurfaceMesh.Mesh import SMesh

from draftGui import translate, getMainWindow, DraftDockWidget, DraftLineEdit

from DocumentObject import prtb

from PyQt4 import QtCore,QtGui,QtSvg    


"""
import SurfaceEditing
reload (SurfaceEditing)
FreeCADGui.seToolbar.baseWidget.hide()
FreeCADGui.seToolbar=SurfaceEditing.SEToolbar()
FreeCADGui.seToolbar.baseWidget.show()
FreeCADGui.seToolbar.w1.show()
FreeCADGui.seToolbar.seWidget.setVisible(True)
"""
class SEToolbar:
    def __init__(self):
            # create the se Toolbar
            self.mw = getMainWindow()
            self.seWidget = QtGui.QDockWidget()
            self.baseWidget = DraftDockWidget()
            self.seWidget.setObjectName("seToolbar")
            self.seWidget.setTitleBarWidget(self.baseWidget)
            self.seWidget.setWindowTitle(translate("se", "Surface Editor Command Bar"))
            self.mw.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.seWidget)
            self.baseWidget.setVisible(False)
            self.seWidget.setVisible(False)
            #self.seWidget.toggleViewAction().setVisible(False)
            #self.sourceCmd = None
            #self.taskmode = Draft.getParam("UiMode")
            self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight,self.baseWidget)
            self.layout.setDirection(QtGui.QBoxLayout.LeftToRight)
            self.layout.setObjectName("layout")

            self.l1 = self.label("l1","current command: ")
            self.lcommand = self.label("lcommand", "None")
            self.w1 = self.lineedit("w1",width=100)
            self.l2 = self.label("l1","value:")
            self.w2 = self.lineedit("w2",width=100)
            self.q1 = self.combo("q1",[("String","App::PropertyString"),("Float","App::PropertyFloat"),("Vector","App::PropertyVector")])
            self.b1 = self.button("b1","OK")

            self.layout.addStretch(100)

    def show(self,text=None):
        self.l1.show()
        self.lcommand.show()
        self.baseWidget.show()
        self.seWidget.setVisible(True)
        if text:
            self.lcommand.setText(text)

    def hide(self):
        self.seWidget.setVisible(False)
        self.reset()
        
    def showPropEntry(self,callback):
        """
        Shows the widgets for property entry
        """
        self.show()
        self.lcommand.setText("Add Property")
        self.w1.show()
        self.l2.show()
        self.w2.show()
        self.q1.show()
        self.b1.show()

    def reset(self):
        self.w1.hide()
        self.l2.hide()
        self.w2.hide()
        self.q1.hide()
        self.b1.hide()
        self.lcommand.setText('None')
        

    def button (self,name, text, hide=True, icon=None, width=66, checkable=False):
        button = QtGui.QPushButton(self.baseWidget)
        button.setObjectName(name)
        button.setText(text)
        button.setMaximumSize(QtCore.QSize(width,26))
        if hide:
            button.hide()
        if checkable:
            button.setCheckable(True)
            button.setChecked(False)
        self.layout.addWidget(button)
        return button

    def combo(self, name, choices, hide=True):
        combo = QtGui.QComboBox(self.baseWidget)
        combo.setObjectName(name)
        if hide: combo.hide()
        for (name,userdata) in choices:
            combo.addItem(name,userdata)
        self.layout.addWidget(combo)
        return combo

    def label (self,name, text=None, hide=True):
        label = QtGui.QLabel(self.baseWidget)
        label.setObjectName(name)
        if hide: label.hide()
        if text: label.setText(text)
        self.layout.addWidget(label)
        return label

    def lineedit (self, name, hide=True, width=None):
        lineedit = DraftLineEdit(self.baseWidget)
        lineedit.setObjectName(name)
        if hide: lineedit.hide()
        if not width: width = 800
        lineedit.setMaximumSize(QtCore.QSize(width,22))
        self.layout.addWidget(lineedit)
        return lineedit
        
class ToggleCrease:
    def Activated(self):
        FreeCADGui.seEditor.callSelected('toggleCrease')

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Toggle Crease', 'ToolTip': 'Toggles creasedbess of selected edges'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class AddProp:
    def Activated(self):
        FreeCADGui.seToolbar.showPropEntry(FreeCADGui.seEditor.addProp)

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Add/Edit property', 'ToolTip': 'Adds/edits user defined property of selected objects'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class AddEdge:
    def Activated(self):
        FreeCADGui.seEditor.addEdge()

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Add Edge', 'ToolTip': 'Adds edge between selected points'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class AddFace:
    def Activated(self):
        FreeCADGui.seEditor.addFace()

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Add Face', 'ToolTip': 'Adds face with selected points'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class ClearSelection:
    def Activated(self):
        FreeCADGui.Selection.clearSelection()

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Clear Selection', 'ToolTip': 'Clears the selection'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

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
                sp = self.mesh.getOrCreatePoint(p,"points")
                points.append(sp)
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

class MovePoints:
    def Activated(self):
        FreeCADGui.seEditor.activateMover()

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Move Points', 'ToolTip': 'Moves points around'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class InsertPoints:
    def Activated(self):
        FreeCADGui.seEditor.activateInserter()

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Insert Points', 'ToolTip': 'Inserts points'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class SurfaceEdit:
    def __init__(self):
        self.obj=None
        QtCore.QObject.connect(FreeCADGui.seToolbar.b1,QtCore.SIGNAL("pressed()"),self.addProp)

    def activateMover(self):
        self.mode='Move Points'
        self.activated()

    def activateInserter(self):
        self.mode='Insert Points'
        self.activated()

    def activated(self): 
        #FreeCAD.Console.PrintMessage("activate\n")
        self.obj=None
        self.view=Gui.activeDocument().activeView()
        self.call = self.view.addEventCallback("SoEvent",self.observe)
        FreeCADGui.seToolbar.show(self.mode)

    def deactivate(self):
        FreeCAD.Console.PrintMessage("deactivate\n")
        self.view.removeEventCallback("SoEvent",self.call)
        FreeCADGui.seToolbar.hide()
        self.do = False

    def dummycb(self,p):
        pass

    def callSelected(self,methname):
        #FreeCAD.Console.PrintMessage("cs %s\n"%methname)
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            #FreeCAD.Console.PrintMessage("ob %s\n"%ob)
            if getattr(ob,"Proxy",False):
                #FreeCAD.Console.PrintMessage("ob %s\n"%ob.Proxy)
                meth = getattr(ob.Proxy,methname,None)
                if meth:
                    #FreeCAD.Console.PrintMessage("calling %s\n"%meth)
                    meth()


    def addProp(self):
        #FreeCAD.Console.PrintMessage("addprop %s\n"%(self,))
        tb = FreeCADGui.seToolbar
        name = str(tb.w1.text())
        value = str(tb.w2.text())
        proptype = str(tb.q1.itemData(tb.q1.currentIndex()).toString())
        if proptype == "App::PropertyFloat":
            value=float(value)
        elif proptype == "App::PropertyVector":
            value=FreeCAD.Base.Vector(eval(value))
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            #FreeCAD.Console.PrintMessage("addprop %s, %s\n"%(self,ob))
            ob.addProperty(proptype,name,"Custom",name)
            try:
                setattr(ob,name,value)
            except TypeError:
                FreeCAD.Console.PrintMessage("invalid type for %s.%s: %s\n"%(ob.Label,name,proptype))
        tb.hide()
        FreeCAD.ActiveDocument.recompute()
        
    def addPoint(self,pos):
        p=self.getPoint(pos)
        sel = FreeCADGui.Selection.getSelection()
        FreeCAD.Console.PrintMessage("sel= %s\n"%(sel))
        FreeCAD.Console.PrintMessage("sel= %s\n"%(map(lambda x: x.Proxy,sel)))
        FreeCAD.Console.PrintMessage("sel= %s\n"%(map(lambda x: x.Proxy.pytype,sel)))
        FreeCAD.Console.PrintMessage("sel= %s\n"%(map(lambda x: x.Proxy.pytype.__class__,sel)))
        for s in sel:
            FreeCAD.Console.PrintMessage("s= %s\n"%(s))
            #try:
            if s.Proxy.pytype == 'SMesh': 
                s.Proxy.getOrCreatePoint(p)
                return
            elif s.Proxy.pytype == 'SMLayer':
                s.Proxy.getParentByType('SMesh').getOrCreatePoint(p,s.Label) 
                return
            #except AttributeError:
            #    pass
        FreeCAD.Console.PrintMessage("You should select a Mesh or Layer to create a point in it\n")
        
    def getSelectedPoints(self):
        sel = FreeCADGui.Selection.getSelection()
        points=[]
        mesh=None
        for s in sel:
            pt = False
            try:
                pt = (s.Proxy.pytype == 'SMPoint')
            except AttributeError:
                continue
            if pt:
                if not mesh:
                    mesh = s.Proxy.getParentByType('SMesh')
                elif mesh != s.Proxy.getParentByType('SMesh'):
                    FreeCAD.Console.PrintMessage("You should select points in the same mesh to create edges/faces!\n")
                    return mesh,[]
                points.append(s.Proxy) 
        return mesh,points

    def addEdge(self):
        mesh,points = self.getSelectedPoints()
        if len(points) < 2:
            FreeCAD.Console.PrintMessage("You should select at least 2 points in the same mesh to create edges!\n")
            return

        p0 = points[0]
        for p in points[1:]:
            mesh.getOrCreateEdge(p0,p)
            p0 = p

    def addFace(self):
        mesh,points = self.getSelectedPoints()
        if len(points) < 3:
            FreeCAD.Console.PrintMessage("You should select at least 3 points in the same mesh to create a face!\n")
            return
        mesh.getOrCreateFace(points)

    def observe(self,event):
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event["Type"],))
        if event["Type"] == 'SoKeyboardEvent' and event['State']=='DOWN':
            if event['Key'] == 'ESCAPE':
                self.deactivate()
            else:
                FreeCAD.Console.PrintMessage("unhandled keypress %s\n"%(event['Key'],))
        elif event["Type"] == 'SoLocation2Event':
            if not self.obj:
                return
            #FreeCAD.Console.PrintMessage("moving\n")
            delta = self.getPoint(event['Position']) - self.p0
            #self.mesh.getOrCreatePoint(self.p0+delta,"points")
            cb = getattr(self.obj,'dragMove',self.dummycb)
            cb(delta)
        elif event["Type"] == 'SoMouseButtonEvent':
            FreeCAD.Console.PrintMessage("EVENT %s\n"%(event,))
            if event['State'] == 'DOWN':
                pos = event['Position']
                if self.mode == 'Insert Points':
                    FreeCAD.Console.PrintMessage("inserting at %s\n"%(pos,))
                    self.addPoint(pos)
                    return
                objs = Gui.ActiveDocument.ActiveView.getObjectsInfo(pos)
                if objs:
                    for obj in objs:
                        try:
                            ob=FreeCAD.ActiveDocument.getObject(obj['Object']).Proxy
                        except AttributeError:
                            continue
                        if getattr(ob,'pytype',False) and ob.pytype == 'SMPoint':
                            self.obj=ob
                self.p0 = self.getPoint(pos)
                #self.mesh = SMesh()
                #self.mesh.getOrCreatePoint(self.p0,"points")
                    
                #FreeCAD.Console.PrintMessage("drag %s from %s\n"%(self.obj,self.p0))
                cb = getattr(self.obj,'dragStart',self.dummycb)
                cb(self.p0)
            elif event['State'] == 'UP':
                pos = event['Position']
                if not self.obj:
                    return
                delta = self.getPoint(pos) - self.p0
                #self.mesh.getOrCreatePoint(self.p0+delta,"points")
                #FreeCAD.Console.PrintMessage("dragend %s from %s\n"%(self.obj,delta))
                cb = getattr(self.obj,'dragEnd',self.dummycb)
                cb(delta)
                self.obj=None
        #else:
        #    FreeCAD.Console.PrintMessage("unhandled event %s\n"%(event,))
          
    def getPoint(self,pos):
        return Gui.ActiveDocument.ActiveView.getPoint(pos)

"""
import SurfaceEditing

reload(SurfaceEditing)
se = SurfaceEditing.SurfaceEdit()
se.Activated()


"""

FreeCADGui.seToolbar = SEToolbar()
FreeCADGui.seEditor = SurfaceEdit()
FreeCADGui.addCommand('Add Mesh', AddMesh())
FreeCADGui.addCommand('Insert Points', InsertPoints())
FreeCADGui.addCommand('Move Points', MovePoints())
FreeCADGui.addCommand('Toggle Crease', ToggleCrease())
FreeCADGui.addCommand('Add Property', AddProp())
FreeCADGui.addCommand('Add Edge', AddEdge())
FreeCADGui.addCommand('Add Face', AddFace())
FreeCADGui.addCommand('Clear Selection', ClearSelection())

