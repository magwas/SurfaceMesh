# coding=UTF-8

import FreeCAD, FreeCADGui 
from FreeCAD import Gui

from SurfaceMesh.Mesh import SMesh

from draftGui import translate, getMainWindow, DraftDockWidget, DraftLineEdit


from pivy import coin

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
            self.q1 = self.combo("q1",[("String","App::PropertyString"),("Float","App::PropertyFloat")])
            self.b1 = self.button("b1","OK")

            self.layout.addStretch(100)

    def show(self):
        self.l1.show()
        self.lcommand.show()
        self.baseWidget.show()
        self.seWidget.setVisible(True)

    def hide(self):
        self.seWidget.setVisible(False)
        self.reset()
        
    def showPropEntry(self,callback):
        """
        Shows the widgets for property entry
        """
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

reload(SurfaceEditing)

"""
class SurfaceEdit:
    def __init__(self):
        self.obj=None
        QtCore.QObject.connect(FreeCADGui.seToolbar.b1,QtCore.SIGNAL("pressed()"),self.addProp)

    def GetResources(self): 
       return {'Pixmap' : '', 'MenuText': 'Surface Editing', 'ToolTip': 'Turns on/off the surface editing mode'} 

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self): 
        #FreeCAD.Console.PrintMessage("activate\n")
        self.obj=None
        self.view=Gui.activeDocument().activeView()
        self.call = self.view.addEventCallback("SoKeyboardEvent",self.observe)
        self.callp = self.view.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),self.getMouseClick) 
        self.callm = self.view.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(),self.getMouseMove) 
        FreeCADGui.seToolbar.show()

    def getPoint(self):
        return Gui.ActiveDocument.ActiveView.getPoint(tuple(self.event.getPosition().getValue()))

    def getMouseMove(self,event_cb):
        if not self.obj:
            return
        #FreeCAD.Console.PrintMessage("moving\n")
        self.event=event_cb.getEvent()
        delta = self.getPoint() - self.p0
        cb = getattr(self.obj,'dragMove',self.dummycb)
        cb(delta)
        
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
            delta = self.getPoint() - self.p0
            #FreeCAD.Console.PrintMessage("dragend %s from %s\n"%(self.obj,delta))
            cb = getattr(self.obj,'dragEnd',self.dummycb)
            cb(delta)
            self.obj=None

    def deactivate(self):
        FreeCAD.Console.PrintMessage("deactivate\n")
        self.view.removeEventCallback("SoKeyboardEvent",self.call)
        self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),self.callp)
        self.view.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(),self.callm)
        #FreeCAD.Console.PrintMessage("removed callbacks\n")
        FreeCADGui.seToolbar.hide()
        self.do = False

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
        sel = FreeCADGui.Selection.getSelection()
        for ob in sel:
            #FreeCAD.Console.PrintMessage("addprop %s, %s\n"%(self,ob))
            ob.addProperty(proptype,name,"Custom",name)
            try:
                setattr(ob,name,value)
            except TypeError:
                FreeCAD.Console.PrintMessage("invalid type for %s.%s: %s\n"%(ob.Label,name,proptype))
        tb.reset()
        FreeCAD.ActiveDocument.recompute()
        
    def observe(self,event):
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event["Type"],))
        #FreeCAD.Console.PrintMessage("EVENT %s\n"%(event,))
        if event["Type"] == 'SoKeyboardEvent' and event['State']=='DOWN':
            if event['Key'] == 'ESCAPE':
                if event['ShiftDown']:
                    self.deactivate()
                else:
                    FreeCADGui.Selection.clearSelection()
            elif event['Key'] == 'c':
                self.callSelected('toggleCrease')
            elif event['Key'] == 'a':
                    FreeCADGui.seToolbar.showPropEntry(self.addProp)
      

FreeCADGui.seToolbar = SEToolbar()
FreeCADGui.addCommand('Add Mesh', AddMesh())
FreeCADGui.addCommand('SurfaceEdit', SurfaceEdit())
