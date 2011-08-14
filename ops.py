
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
        FreeCAD.ActiveDocument.openTransaction(operation)
        op=Operation(self,operation,sources,attributes)
        op.play()
        self.history.append(op)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        return op

    def redoop(self,op,sources,**attributes):
        """
        Some parameters (either sources or attributes) of the operation have changed,
        so we redo it. Take care of the consequences of the change: some of the operations
        later in the history should be redone, some operations may become invalid, and some
        objects may cease to exist.
        """
        #FreeCAD.Console.PrintMessage("redo %s, %s, %s\n"%(op,sources,attributes))
        if not op in self.history:
            return
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
            returns (changed,deleted,invalid)
            changed is a set of changed elements
            deleted is a set of deleted elements
            invalid is a set of elements became invalid
                e.g. because the redo of the operation went wrong (e.g. make face redone with only two points left)
        """
        op=getattr(self,"replay_"+self.op)
        return op(sources, **attributes)

    def __repr__(self):
        return "Operation(%s,%s,%s)"%(self.op, self.sources, self.attributes)

class ToggleCrease:
    def play_ToggleCrease(self,sources,**attributes):
        for obj in sources:
            ob = FreeCAD.ActiveDocument.getObject(obj)
            ob.Proxy.toggleCrease()
        return (list(sources),list())
    def replay_ToggleCrease(self,sources,**attributes):
        for obj in sources:
            ob = FreeCAD.ActiveDocument.getObject(obj)
            ob.Proxy.toggleCrease()
        return (list(sources),list(),list())

Operation.registerOp(ToggleCrease)

class AddOb:
    def replay_AddOb(self,sources,**attributes):
        """
        recreate the list of points, edges and faces from self.attributes
        for each new mesh element we reparametrize the next one on the list
        if there is no more in the list, the we create a new one
        the mesh elements left on the list after that will be deleted
        """
        firstp=None
        lastp=None
        points=map(lambda n: FreeCAD.ActiveDocument.getObject(n), self.attributes['points'])
        edges=map(lambda n: FreeCAD.ActiveDocument.getObject(n), self.attributes['edges'])
        faces=map(lambda n: FreeCAD.ActiveDocument.getObject(n), self.attributes['faces'])
        npoints=[]
        nedges=[]
        nfaces=[]
        shape = FreeCAD.ActiveDocument.getObject(sources[0]).Shape
        for p in shape.Vertexes:
            if len(points):
                sp = points[0]
                points.remove(sp)
                sp.Coordinates=FreeCAD.Base.Vector(p.Point)
            else:
                sp = self.parent.getOrCreatePoint(p.Point,"points")
                sp.addBirth(self)
            npoints.append(sp)
        for se in shape.Edges:
            if len(edges):
                e = edges[0]
                edges.remove(e)
            else:
                if len(se.Vertexes)<2:
                    continue
                sp1 = self.parent.getOrCreatePoint(se.Vertexes[0].Point,"points")
                sp2 = self.parent.getOrCreatePoint(se.Vertexes[1].Point,"points")
                e=self.parent.getOrCreateEdge(sp1,sp2,"edges")
                e.addBirth(self)
            nedges.append(e)
        for sf in shape.Faces:
            if len(faces):
                f = faces[0]
                faces.remove(f)
            else:
                if len(sf.Vertexes)<3:
                    continue
                fps=[]
                for p in sf.Vertexes:
                    fps.append(self.parent.getOrCreatePoint(p.Point,"points"))
                f=self.parent.getOrCreateFace(fps,"faces")
                f.addBirth(self)
            nfaces.append(f)
                
        npoints = map(lambda x: x.Label,npoints)
        nedges = map(lambda x: x.Label,nedges)
        nfaces = map(lambda x: x.Label,nfaces)
        changed = nedges+npoints+nfaces
        deleted = points+edges+faces
        self.attributes['points'] = npoints
        self.attributes['edges'] = nedges
        self.attributes['faces'] = nfaces
        return (changed,deleted,list())

    def play_AddOb(self,sources):
        FreeCAD.Console.PrintMessage("play_AddOb(%s)\n"%(sources,))
        firstp=None
        lastp=None
        npoints=[]
        nedges=[]
        nfaces=[]
        ob = FreeCAD.ActiveDocument.getObject(sources[0])
        ob.ViewObject.hide()
        shape = ob.Shape
        for p in shape.Vertexes:
            sp = self.parent.getOrCreatePoint(p.Point,"points")
            sp.addBirth(self)
            npoints.append(sp)
        for se in shape.Edges:
            if len(se.Vertexes)<2:
                continue
            sp1 = self.parent.getOrCreatePoint(se.Vertexes[0].Point,"points")
            sp2 = self.parent.getOrCreatePoint(se.Vertexes[1].Point,"points")
            e=self.parent.getOrCreateEdge(sp1,sp2,"edges")
            e.addBirth(self)
            nedges.append(e)
        for sf in shape.Faces:
            if len(sf.Vertexes)<2:
                continue
            fps=[]
            for p in sf.Vertexes:
                fps.append(self.parent.getOrCreatePoint(p.Point,"points"))
            f=self.parent.getOrCreateFace(fps,"faces")
            f.addBirth(self)
            nfaces.append(f)
        npoints = map(lambda x: x.Label,npoints)
        nedges = map(lambda x: x.Label,nedges)
        nfaces = map(lambda x: x.Label,nfaces)
        self.attributes['points'] = npoints
        self.attributes['edges'] = nedges
        self.attributes['faces'] = nfaces
        return ([],npoints+nedges+nfaces)

Operation.registerOp(AddOb)

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
        self.attributes['y'] = y
        self.attributes['z'] = z
        return (list(self.sources),list(),list())

Operation.registerOp(MovePoint)

def test():
    """
import ops
reload(ops)
ops.test()
    """
    import Draft
    FreeCAD.newDocument()
    FreeCAD.setActiveDocument("Unnamed")
    FreeCAD.ActiveDocument=FreeCAD.getDocument("Unnamed")
    FreeCAD.Gui.ActiveDocument=FreeCAD.Gui.getDocument("Unnamed")
    #wb=FreeCAD.Gui.getWorkbench('SurfaceEditingWorkbench')
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
    w1=FreeCAD.Base.Vector(0,0,0)
    w2=FreeCAD.Base.Vector(0,1,0)
    wire=Draft.makeWire([w1,w2]) 
    op=mesh.doop('AddWire',[wire.Label])
    pname=op.attributes['points'][1]
    mesh.doop('MovePoint',[pname],relative=True,x=-0.2,y=0.2)
    ob=FreeCAD.Gui.getDocument("Unnamed").getObject("Line")
    ps=ob.Object.Points
    ps[1]=FreeCAD.Base.Vector(0.5,0.5,0)
    ob.Object.Points=ps
    mesh.redoop(op,op.sources,**op.attributes)
    mesh.redoop(op,op.sources,**op.attributes)
    mesh.doop('AddPoint',[],x=0.5,y=0.5,z=1)
        
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")

