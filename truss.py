
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
        if None is getattr(self.edge,"Force",None):
            self.edge.addProperty("App::PropertyFloat","Force","Truss")
        #print self.edge.Label
        force=float(self.symbol.subs(self.truss.solution))
        print self.edge.Label,":\t",force
        self.edge.Force=force

class Joint(object):
    def __init__(self,point,truss,eq):
        self.truss=truss
        self.point=point
        self.eq=eq
        tp = getattr(point,"trusspart",None)
        #print point.Label,tp
        if tp == self.truss.supportedname:
            self.support = Matrix([[self.eqpart("x")],[self.eqpart("y")],[self.eqpart("z")]])
            self.truss.supportsyms = self.truss.supportsyms.union(self.support)
            self.eq += self.support
            #print "supported",point.Label,self.eq
        if tp == self.truss.loadname:
            F = self.point.F
            self.eq += Matrix([[F.x],[F.y],[F.z]])
            
    def eqpart(self,axis):
        return symbols("%s_%s"%(str(self.point.Label),axis),real=True, each_char=False)

    def matrixToVector(self,mx):
        """It also converts from stadard FreeCAD mm to SI m"""
        return FreeCAD.Base.Vector(mx[0]/1000.0,mx[1]/1000.0,mx[2]/1000.0)

    def reportForce(self):
        if None is not getattr(self,"support",None):
            if None is getattr(self.point,"ForceVector",None):
                self.point.addProperty("App::PropertyVector","ForceVector","Truss")
            if None is getattr(self.point,"Force",None):
                self.point.addProperty("App::PropertyFloat","Force","Truss")
            fv = self.matrixToVector(self.support.subs(self.truss.solution))
            self.point.ForceVector = fv
            self.point.Force = fv.Length
            print self.point.Label,":\t", fv,"\t", fv.Length
        else:
            print self.point.Label, ":\t inner joint"
				

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

    def __init__(self,mesh,beamname="beam",supportedname="supported",loadname="load"):
        """
            initialise our data structures from the given mesh
        """
        self.mesh = mesh
        self.beams={}
        self.joints={}
        self.supportsyms=set()
        self.beamname = beamname
        self.supportedname = supportedname
        self.loadname = loadname
        self.valid=None
        for e in mesh.getEdges():
            tp=getattr(e,"trusspart",None)
            if tp == self.beamname:
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
        solution = solve(self.eqs)
        if solution is None:
        	print "No solution for this truss"
        	return

        #if a support component makes the truss indeterminate, we fix that component to 0
        missings = set()
        for k,v in solution.items():
            syms = v.atoms(Symbol)
            if not syms:
                continue
            if syms - self.supportsyms:
                print syms
                print self.supportsyms
                raise ValueError("This truss is unsolvable")
            missings = missings.union(syms)
        for s in missings:
            self.eqs.append(s)
            print s," is missing, fixed"
        self.missing = missings
        self.solution = solve(self.eqs)
        for eq in self.eqs:
          if eq.subs(self.solution) > 0.0001:
            self.valid = False
        if self.valid:
            self.report()
        else:
            print "Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493"
            

    def report(self):
        if None is self.valid:
            print "solve it first"
            return
        doc = self.mesh.getobj().Document
        doc.openTransaction("Truss calculation")
        for b in self.beams.values():
            b.reportForce()
        for j in self.joints.values():
            j.reportForce()
        doc.commitTransaction()

    def listeqs(self):
        if None is self.valid:
            print "solve it first"
            return
        for (k,v) in self.joints.items():
            print "#",k
            print "\t%s,\n\t%s,\n\t%s,\n"%tuple(v.eq.tolist())
        print "--------------"
        for i in self.missing:
            print i,"\tzeroed"
        print "--------------"
        for (k,v) in sorted(self.solution.items()):
            print k,":\t",v
        if False is self.valid:
            print "Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493"
    def printraweqs(self):
        if None is self.valid:
            print "solve it first"
            return
        e=set()
        for i in self.eqs:
           e = e.union(map(lambda x: str(x),i.atoms(Symbol)))
        print "syms = " + ", ".join(map(lambda x: "'" + x + "'",e))
        print "%s = symbols(syms)"%(", ".join(e))
        print "eqs = ", self.eqs
        print "len(eqs) = %u"%len(self.eqs)
        print "len(syms) = %u" % len(e)
        if False is self.valid:
            print "Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493"


"""
import truss
reload(truss)
mesh=Gui.getDocument("truss").getObject("Mesh").Object.Proxy
t=truss.Truss(mesh,beamname="beam",supportedname="sup",loadname="load")
t.solve()
t.printraweqs()
"""
