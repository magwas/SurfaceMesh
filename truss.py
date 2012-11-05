
import FreeCAD

try:
    from sympy import *
except ImportError:
   FreeCAD.Console.PrintMessage("truss calculation needs python-sympy\n")

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
        self.vect=self.dirVector(p1.Coordinates,p2.Coordinates)
        self.eq=self.vect*self.symbol
        truss.addForce(p1.Proxy,self.vect,self.symbol,addpoints)
        truss.addForce(p2.Proxy,-self.vect,self.symbol,addpoints)

    def reportForce(self):
        if None is getattr(self.edge,"Force",None):
            self.edge.addProperty("App::PropertyFloat","Force","Truss")
        force=float(self.symbol.subs(self.truss.solution))
        self.edge.Force=force

class Joint(object):
    def __init__(self,point,truss,vect,symbol):
        self.truss=truss
        self.point=point
        self.eq = Matrix([[0],[0],[0]])
        self.mlines = [{},{},{}]
        self.addEq(vect,symbol)
        tp = getattr(point,"trusspart",None)
        if tp == self.truss.supportedname:
            px = self.eqpart("x")
            py = self.eqpart("y")
            pz = self.eqpart("z")
            self.support = Matrix([[px],[py],[pz]])
            self.mlines[0][px] = 1.0
            self.mlines[1][py] = 1.0
            self.mlines[2][pz] = 1.0
            self.truss.syms.add(px)
            self.truss.syms.add(py)
            self.truss.syms.add(pz)
            self.truss.supportsyms = self.truss.supportsyms.union(self.support)
            self.eq += self.support
        if tp == self.truss.loadname:
            F = self.point.F
            self.mlines[0][0] = - F.x
            self.mlines[1][0] = - F.y
            self.mlines[2][0] = - F.z
            self.eq += Matrix([[F.x],[F.y],[F.z]])
            
    def addEq(self,vect,symbol):
        self.eq += vect*symbol
        self.mlines[0][symbol] = vect[0]
        self.mlines[1][symbol] = vect[1]
        self.mlines[2][symbol] = vect[2]
        self.truss.syms.add(symbol)

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
        self.syms = set()
        for e in mesh.getEdges():
            tp=getattr(e,"trusspart",None)
            if tp == self.beamname:
                b = Beam(e,self)
                self.beams[str(b.symbol)]=b

    def addForce(self,point,vect,symbol,addpoints=True):
        self.syms.add(symbol)
        if not self.joints.has_key(point.Label):
            if addpoints:
                self.joints[point.Label]=Joint(point,self,vect,symbol)
        else:
            self.joints[point.Label].addEq(vect,symbol)

    def solve(self):
       return self.solve_matrix()

    def solve_matrix(self):
        # first make a list of the symbols. they will be the columns of the matrix 0 forthe constant column
        slist = sorted(self.syms)
        slist.append(0)
        FreeCAD.Console.PrintMessage("syms= %s\n"%(slist,))
        #build the rows of the matrix. we use a hash so we can later identify the rows by label
        mx = {}
        for (k,v) in self.joints.items():
            FreeCAD.Console.PrintMessage("building lines for %s\n"%k)
            for n in 0,1,2:
                kk = "%s_%s"%(k,n)
                row = []
                for s in slist:
                    if v.mlines[n].has_key(s):
                      row.append(v.mlines[n][s])
                    else:
                      row.append(0.0)
                mx[kk] = row
        self.mx = mx
        #the rows are in alphabetical order of their label
        self.rlabels = sorted(mx.keys())
        mxv = []
        for l in self.rlabels:
            mxv.append(mx[l])
        self.matrix = Matrix(mxv)
        # and now we solve it
        FreeCAD.Console.PrintMessage("slist = %s\n"%(slist,))
        FreeCAD.Console.PrintMessage("rlabels = %s\n"%(self.rlabels,))
        FreeCAD.Console.PrintMessage("matrix = %s\n"%(self.matrix,))
        self.solution = solve_linear_system(self.matrix,*slist[:-1])
        self._compileEqs()
        self._doReport()

    def _compileEqs(self):
        self.eqs=[]
        for (k,v) in self.joints.items():
            for eq in v.eq:
                if eq != 0:
                    self.eqs.append(eq)

    def solve_symbolic(self):
        self._compileEqs()
        solution = solve(self.eqs)
        if solution is None:
        	FreeCAD.Console.PrintMessage("No solution for this truss\n")
        	return

        #if a support component makes the truss indeterminate, we fix that component to 0
        missings = set()
        for k,v in solution.items():
            syms = v.atoms(Symbol)
            if not syms:
                continue
            if syms - self.supportsyms:
                FreeCAD.Console.PrintMessage("syms=%s\n"%(syms,))
                FreeCAD.Console.PrintMessage("self.supportsysms=%s\n"%(self.supportsysms,))
                raise ValueError("This truss is unsolvable")
            missings = missings.union(syms)
        for s in missings:
            self.eqs.append(s)
            FreeCAD.Console.PrintMessage("%s is missing, fixed\n"%s)
        self.missing = missings
        self.solution = solve(self.eqs)
        self._doReport()

    def _doReport(self):
        for eq in self.eqs:
          if eq.subs(self.solution) > 0.0001:
            self.valid = False
        if self.valid:
            self.report()
        else:
            FreeCAD.Console.PrintMessage("Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493\n")
            

    def report(self):
        if None is self.valid:
            FreeCAD.Console.PrintMessage( "solve it first\n")
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
            FreeCAD.Console.PrintMessage( "solve it first\n")
            return
        for (k,v) in self.joints.items():
            FreeCAD.Console.PrintMessage("#%s\n"%k)
            FreeCAD.Console.PrintMessage( "\t%s,\n\t%s,\n\t%s,\n"%tuple(v.eq.tolist()))
        FreeCAD.Console.PrintMessage( "--------------\n")
        for i in self.missing:
            FreeCAD.Console.PrintMessage( "%s\tzeroed\n"%i )
        FreeCAD.Console.PrintMessage( "--------------\n" )
        for (k,v) in sorted(self.solution.items()):
            FreeCAD.Console.PrintMessage( "%s:\t%s\n"%(k,v))
        if False is self.valid:
            FreeCAD.Console.PrintMessage( "Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493\n" )
    def printraweqs(self):
        if None is self.valid:
            FreeCAD.Console.PrintMessage( "solve it first\n")
            return
        e=set()
        for i in self.eqs:
           e = e.union(map(lambda x: str(x),i.atoms(Symbol)))
        FreeCAD.Console.PrintMessage( "syms = %s\n" %(", ".join(map(lambda x: "'" + x + "'",e)),))
        FreeCAD.Console.PrintMessage( "%s = symbols(syms)\n"%(", ".join(e)))
        FreeCAD.Console.PrintMessage( "eqs = %s\n"%( self.eqs,))
        FreeCAD.Console.PrintMessage( "len(eqs) = %u\n"%len(self.eqs))
        FreeCAD.Console.PrintMessage( "len(syms) = %u\n" % len(e))
        if False is self.valid:
            FreeCAD.Console.PrintMessage( "Solution is invalid. See http://code.google.com/p/sympy/issues/detail?id=3493\n" )


"""
import truss
reload(truss)
mesh=Gui.getDocument("truss").getObject("Mesh").Object.Proxy
t=truss.Truss(mesh,beamname="beam",supportedname="sup",loadname="load")
t.solve()
t.printraweqs()
"""
