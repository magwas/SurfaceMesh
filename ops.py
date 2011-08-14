
"""
Operation classes.

"""

import FreeCAD
from Point import SMPoint

class History(object):
    """
        Mix-in class for Mesh.
        It takes care for the history
    """
    def __init__(self):
        self.history = list()

    def compacthist(self):
        #FIXME
        pass

    def doop(self,operation, sources, **attributes):
        """
        does an operation for the first time
        """
        op=Operation(self,operation,sources,attributes)
        op.play()
        self.history.append(op)

    def redoop(self,op,sources,**attributes):
        """
        Some parameters (either sources or attributes) of the operation have changed,
        so we redo it. Take care of the consequences of the change: some of the operations
        later in the history should be redone, some operations may become invalid, and some
        objects may cease to exist.
        """
        FreeCAD.Console.PrintMessage("redo %s, %s, %s"%(op,sources,attributes))
        histindex = self.history.index(op)
        (changed,deleted,invalid) = op.replay(sources,attributes)
        removedops=list()
        for o in self.history[histindex+1:]:
            if (set(deleted).union(set(invalid))).intersection(set(o.sources)):
                #operation is no longer valid
                invalid = invalid + op.changed + op.new
                removedops.append(op)
            elif set(changed).intersection(set(o.sources)):
                (c2,d2,i2) = o.replay(o.sources,o.attributes)
                changed = changed + c2
                deleted = deleted + d2
                invalid = invalid + i2
        for obj in deleted:
            #here deleteObj is a method of the class we are mixed in
            self.deleteObj(obj)
        for rop in removedops:
            self.history.remove(rop)


class Operation(object):
    """
        operation is an iterface class for idividual operations.
        All kind of operatins are mixins to it, registered by registerOp
    """
    def __init__(self,parent,operation, sources, attributes):
        self.parent = parent
        self.op = operation
        self.sources = sources
        self.attributes = attributes

    @classmethod
    def registerOp(klass,opklass):
        klass.__bases__ += (opklass,)

    def play(self):
        op=getattr(self,"play_"+self.op)
        (self.changed,self.new) = op(self.sources,**self.attributes) #giving self.sources and self.attributes is only a convenience

    def replay(self,sources,attributes):
        """
            replays an operation
            returns (changed,invalid)
            changed is a set of changed elements
            deleted is a set of deleted elements
            invalid is a set of elements became invalid
                e.g. because the redo of the operation went wrong (e.g. make face redone with only two points left)
        """
        op=getattr(self,"replay_"+self.op)
        return op(sources, **attributes)

    def __repr__(self):
        return "Operation(%s,%s,%s)"%(self.op, self.sources, self.attributes)

class AddPoint:
    def play_AddPoint(self,sources,layer=None,x=0,y=0,z=0):
        v = FreeCAD.Base.Vector(x,y,z)
        layerobj = self.parent.getOrCreateLayer(layer)
        p=SMPoint(layerobj,v)
        return list(),[p.Label]

    def replay_AddPoint(self,sources,layer=None,x=0,y=0,z=0):
        v = FreeCAD.Base.Vector(x,y,z)
        p = FreeCAD.ActiveDocument.getObject(self.new[0])
        if p:
            p.Coordinates = v
            #FIXME change layer if needed
            return ( list(self.new), list(), list() )
        else:
            layerobj = self.parent.getOrCreateLayer(layer)
            p = SMPoint(layerobj,v)
            return ( list(), [p.Label], list() )

Operation.registerOp(AddPoint)

class MovePoint:
    def play_MovePoint(self,sources,relative=False,x=0,y=0,z=0):
        FreeCAD.Console.PrintMessage("play_Movepoint(%s)\n"%(sources,))
        for pn in sources:
            print pn
            p = FreeCAD.ActiveDocument.getObject(pn)
            v = FreeCAD.Base.Vector(x,y,z)
            if relative:
                p.Coordinates += v
            else:
                p.Coordinates = v
        return(list(self.sources),list())

    def replay_MovePoint(self,sources,relative=False,x=0,y=0,z=0):
        for pn in sources:
            p = FreeCAD.ActiveDocument.getObject(pn)
            v = FreeCAD.Base.Vector(x,y,z)
            if relative:
                p.Coordinates += v 
            else:
                p.Coordinates = v
        self.attributes['relative'] = relative
        self.attributes['x'] = x
        self.attributes['x'] = y
        self.attributes['x'] = z
        return (list(self.sources),list(),list())

Operation.registerOp(MovePoint)

def test():
    """
import ops
reload(ops)
ops.test()
    """
    FreeCAD.newDocument()
    FreeCAD.setActiveDocument("Unnamed")
    FreeCAD.ActiveDocument=FreeCAD.getDocument("Unnamed")
    FreeCAD.Gui.ActiveDocument=FreeCAD.Gui.getDocument("Unnamed")
    #wb=FreeCAD.Gui.getWorkbench('SurfaceEditingWorkbench')
    import SurfaceEditing
    am=SurfaceEditing.AddMesh()
    am.Activated()
    mesh=FreeCAD.Gui.getDocument("Unnamed").getObject("Mesh").Proxy
    FreeCAD.Gui.Selection.addSelection(mesh.Object)
    FreeCAD.Gui.seEditor.addPoint((400,400))
    FreeCAD.Gui.seEditor.addPoint((410,410))
    FreeCAD.Gui.seEditor.addPoint((415,415))
    p=FreeCAD.ActiveDocument.getObject('Point')
    print p.Coordinates
    mesh.doop('MovePoint',["Point"],relative=True,x=-0.5,y=-0.5,z=10)
    print p.Coordinates
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    h1=mesh.history[0]
    mesh.redoop(h1,[],layer='Default Layer',x=0.3,y=0,z=0)
    print p.Coordinates
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    
