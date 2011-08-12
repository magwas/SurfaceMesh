
import FreeCAD

have_sympy=False
try:
    from sympy import *
except ImportError:
   FreeCAD.Console.PrintMessage("truss calculation needs python-sympy")

class Beam(object):
    def toMatrix(self,v):
        """ converts a freecad vector to a sympy matrix """
        return Matrix([[v.x],[v.y],[v.z]])

    def dirVector(self,p1,p2):
        """ return the direction vector (p2-p1)/|p2-p1| as a sympy matrix """
        v=p2-p1
        l=v.Length
        return self.toMatrix(v)/l

    def __init__(self,edge,truss,addpoints=True):
        l=symbols("%s"%str(edge.Label),real=True, each_char=False)
        self.truss=truss
        self.symbol=l
        self.edge=edge
        p1=edge.Start
        p2=edge.End
        self.eq=self.dirVector(p1.Coordinates,p2.Coordinates)*l
        truss.addForce(p1.Proxy,self.eq,addpoints)
        truss.addForce(p2.Proxy,-self.eq,addpoints)

    def reportForce(self):
        if not getattr(self.edge,"Force",None):
            self.edge.addProperty("App::PropertyFloat","Force","Truss")
        print self.edge.Label
        force=float(self.symbol.subs(self.truss.solution))
        print self.edge.Label,":\t",force
        self.edge.Force=force

class Joint(object):
    def __init__(self,point,truss,eq):
        self.truss=truss
        self.point=point
        self.eq=eq
        tp = getattr(point,"trusspart",None)
        print point.Label,tp
        if tp == "supported":
            self.support = Matrix([[self.eqpart("x")],[self.eqpart("y")],[self.eqpart("z")]])
            self.eq += self.support
            print "supported",point.Label,self.eq
        if tp == "load":
            F = self.point.F
            self.eq += Matrix([[F.x],[F.y],[F.z]])
            
    def eqpart(self,axis):
        return symbols("%s_%s"%(str(self.point.Label),axis),real=True, each_char=False)

    def matrixToVector(self,mx):
        return FreeCAD.Base.Vector(mx[0],mx[1],mx[2])

    def reportForce(self):
        print self.point.Label
        if getattr(self,"support",None):
            if not getattr(self.point,"ForceVector",None):
                self.point.addProperty("App::PropertyVector","ForceVector","Truss")
            if not getattr(self.point,"Force",None):
                self.point.addProperty("App::PropertyFloat","Force","Truss")
            self.point.ForceVector= self.matrixToVector(self.support.subs(self.truss.solution))
            self.point.Force = self.point.ForceVector.Length

            

class Truss(object):
    """
        A Truss is represented with:
            A set of beams:
                The beams are edges identified as having the property of trusspart=beam
                The goal is to calculate the force along the beams
                Note that we assume straight beams even if the edge is not straight.
            A set of joints:
                The joints are the endpoints of the beams.
                The supported joints are marked as trusspart=supported.
                On supported joints we calculate the force on the support.
            A set of loads:
                The loads are points identified by the property trusspart=load
                The force is given in the vector property F
    """

    def __init__(self,mesh):
        """
            initialise our data structures from the given mesh
        """
        self.beams={}
        self.joints={}
        for e in mesh.getEdges():
            tp=getattr(e,"trusspart",None)
            if tp == "beam":
                b = Beam(e,self)
                self.beams[str(b.symbol)]=b

    def addForce(self,point,eq,addpoints=True):
        if not self.joints.has_key(point.Label):
            if addpoints:
                self.joints[point.Label]=Joint(point,self,eq)
        else:
            self.joints[point.Label].eq += eq

    def solve(self):
        self.eqs=[]
        for (k,v) in self.joints.items():
            for eq in v.eq:
                if eq != 0:
                    self.eqs.append(eq)
        self.solution = solve(self.eqs)
        for b in self.beams.values():
            b.reportForce()
        for j in self.joints.values():
            j.reportForce()
        return self.solution

    def listeqs(self):
        for (k,v) in self.joints.items():
            print k
            print "\t%s\n\t%s\n\t%s\n"%tuple(v.eq.tolist())

"""
import truss
reload(truss)
mesh=Gui.getDocument("beam").getObject("Mesh").Proxy
t=truss.Truss(mesh)
t.solve()
t.listeqs()
"""
