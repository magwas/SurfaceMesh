#!/usr/bin/python
# -*- coding: utf-8 -*-

from sympy import *
from SurfaceEditing import SMesh
# t1 = felső, t2= alsó , t3 = hátsó

CR='\r\n'

class Layer:
		def __init__(self,ship,name,data=None):
						self.ship=ship
						self.name=name.strip()
						if not data:
								data = "0 32768 1 1 1 1 1 1 0.50000000 4.00000000"
						self.id,self.color,self.visible,self.developable,self.symmetric,self.useforintersection,self.useinhydrostatic,self.showinlinesplan,self.density,self.thickness=data.strip().split(' ')
		def __repr__(self):
				return "%s"%self.name
		def fefstr(self):
				r=self.name+CR+self.id+' '+self.color+' '+self.visible+' '+self.developable+' '+self.symmetric+' '+self.useforintersection+' '+self.useinhydrostatic+' '+self.showinlinesplan+' '+self.density+' '+self.thickness+CR
				return r
				
class Point(Matrix):
		def __init__(self,ship,data=None,x=None,y=None,z=None,selected=0,vertextype=1):
						self.ship=ship
						self.selected=selected
						self.vertextype=vertextype
						if data:
								self.x,self.y,self.z,self.vertextype,self.selected=data.strip().split(' ')
						if x is not None:
								self.x=x
						if y is not None:
								self.y=y
						if z is not None:
								self.z=z
						self.x=float(self.x)
						self.x=float(self.x)
						self.x=float(self.x)
						self.y=float(self.y)
						self.z=float(self.z)
						self.selected=int(self.selected)
						Matrix.__init__(self,[self.x,self.y,self.z])
						self.vertextype=int(self.vertextype)
		def __repr__(self):
				return "(%s,%s,%s) %s"%(self.x,self.y,self.z,self.vertextype)
		def fefstr(self):
				return "%s %s %s %s %s %s"%(self.x,self.y,self.z,self.vertextype,self.selected,CR)
				return str(self.x)+' '+str(self.y)+' '+str(self.z)+' '+str(self.vertextype)+self.selected+CR

class Edge:
		def __init__(self,ship,data=None,start=None,end=None,crease=0,selected=0):
						self.ship=ship
						self.crease=crease
						self.selected=selected
						if data:
								self.start,self.end,self.crease,self.selected=data.strip().split(' ')
								self.start=ship.points[int(self.start)]
								self.end=ship.points[int(self.end)]
						if start:
								self.start=start
						if end:
								self.end=end
								self.selected=1
						self.selected=int(self.selected)
		def __repr__(self):
				return "%s,%s,%s,%s"%(self.start.__repr__(),self.end.__repr__(),self.crease,id(self))
		def fefstr(self):
				return "%s %s %s %s %s"% (
						self.ship.points.index(self.start),
						self.ship.points.index(self.end),
						self.crease,
						self.selected,
						CR)
		def connected(self,other):
				return (self.end==other.start) or (self.start==other.end) or (self.end==other.end) or (self.start==other.start)
		def contains(self,point):
				return (point == self.start) or (point == self.end)
		def normwith(self,vector):
				"""normal to the plan created by self and vector"""
				a=self.start
				b=self.end
				#print self.start,vector
				c=self.start+vector
				n= (b-a).cross(c-a)
				return n/abs(n)

class Face:
		def __init__(self,ship,data=None,points=None,layer=None,selected=0):
						self.ship=ship
						self.selected=selected
						self.points=[]
						if data:
								data=data.strip().split(' ')
								numpoints=int(data[0])
								self.points=[]
								#print data
								for i in range(numpoints):
										self.points.append(ship.points[int(data[i+1])])
								#print i
								self.layer=ship.layers[int(data[i+2])]
								self.selected=int(data[i+3])
						if points:
								self.points+=points
						if layer:
								self.layer=layer
						self.plane=Plane(face=self)
		def norm(self):
				"""normal to the face"""
				a,b,c=self.points[:3]
				n= (a-b).cross(c-b)
				#print n/abs(n)
				n= (b-a).cross(c-a)
				return n/n.norm()
		def __repr__(self):
				return "%s: %s"%(self.layer.name,self.points)
		def fefstr(self):
				data=[]
				data.append(len(self.points))
				for i in self.points:
						data.append(self.ship.points.index(i))
				data.append(self.ship.layers.index(self.layer))
				data.append(self.selected)
				r=[]
				for d in data:
						r.append(str(d))
				return " ".join(r)+CR
		def triangulate(self):
				"""not as the name suggest, it breakes the face into triangles"""
				if len(self.points) == 3:
						return [self]
				f1=self.ship.newface(self.points[:3],layername=self.layer.name)
				f2=self.ship.newface(self.points[1:],layername=self.layer.name)
				self.ship.faces.remove(self)
				return([f1]+f2.triangulate())
		def getedges(self):
				edges=[]
				for p in self.points:
						for e in self.ship.edges:
								if e.contains(p):
										if p==e.start:
												if e.end in self.points:
														edges.append(e)
				return edges
		def commonedge(self,other):
				for i in self.getedges():
						for j in other.getedges():
								if i == j:
										return i
				return None
				

class Plane:
		def __init__(self,face=None,point=None,norm=None):
				if face:
						self.norm=face.norm()
						self.point=face.points[0]
				else:
						self.norm=norm
						self.point=point
				self.denom=-self.norm[0]**2-self.norm[1]**2-self.norm[2]**2
		def intersectline(self,point,vector):
				"find the intersection of the plane with the line defined by point and vector"
				x,y,z,u=symbols("xyzu",real=True)
				newp=Matrix([x,y,z])
				line=point+vector*u-newp
				fn=self.norm
				r0=self.point
				plane=fn.dot(r0-newp)
				res=solve(list(line)+[plane],[x,y,z,u])
				print res
				if res is None:
						return (point,oo)
				if not res.has_key(u):
						return (point,0.0)
				return (Matrix([res[x],res[y],res[z]]),res[u])
		def project(self,point):
				x,y,z,u=symbols("xyzu",real=True)
				newp=Matrix([x,y,z])
				line=point+self.norm.transpose()*u-newp
				plane=self.norm.dot(self.point-newp)
				res=solve(list(line)+[plane],[x,y,z,u])
				return res[u]
		def project2(self,point):
				u=(self.norm[0]*(point[0]-self.point[0])+self.norm[1]*(point[1]-self.point[1])+self.norm[2]*(point[2]-self.point[2]) )/self.denom
				return u
		def intersectline2(self,point,vector):
				denom= - self.norm[0]*vector[0] - self.norm[1]*vector[1] - self.norm[1]*vector[1]
				px0=point[0]-self.point[0]
				py0=point[1]-self.point[1]
				pz0=point[2]-self.point[2]
				top=self.norm[1]*py0+self.norm[2]*pz0+self.norm[0]*px0
				top2=self.norm[0]*vector[0]+self.norm[1]*vector[1]+self.norm[2]*vector[2]
				x= (vector[0]*top - point[0]*top2)/denom
				y= (vector[1]*top - point[1]*top2)/denom
				z= (vector[2]*top - point[2]*top2)/denom
				u= top/denom
				return Matrix([x,y,z]),u
				
class Ship:
		def __init__(self,feffile=None):
				self.projname=""
				self.designer=""
				self.createdby=""
				self.comment=""
				self.length="1.0"
				self.beam="1.0"
				self.draft="1.0"
				self.waterdensity="1.0"
				self.appendagecoeff="1.0"
				self.units="0"
				self.mainparticular="1"
				self.precision="1"
				if feffile:
						self.fefread(feffile)
				else:
						self.layers=[]
						self.points=[]
						self.edges=[]
						self.faces=[]

		def fefread(self,feffile):
				f=open(feffile)
				self.projname=f.readline().strip()
				self.designer=f.readline().strip()
				self.createdby=f.readline().strip()
				self.comment=f.readline().strip()
				(self.length,self.beam,self.draft,self.waterdensity,self.appendagecoeff,self.units,self.mainparticular,self.precision)=f.readline().strip().split(' ')
				numlayers=int(f.readline().strip())
				self.layers=[]
				for i in range(numlayers):
						name=f.readline()
						data=f.readline()
						l = Layer(self,name,data)
						self.layers.append(l)
				numpoints=int(f.readline().strip())
				self.points=[]
				for i in range(numpoints):
						data=f.readline()
						p = Point(self,data)
						self.points.append(p)
				numedges=int(f.readline().strip())
				self.edges=[]
				for i in range(numedges):
						data=f.readline()
						p = Edge(self,data)
						self.edges.append(p)
				numfaces=int(f.readline().strip())
				self.faces=[]
				for i in range(numfaces):
						data=f.readline()
						p = Face(self,data)
						self.faces.append(p)
				f.close()

		def addToDoc(self,doc):
			"""
			Adds the ship to the FreeCad doc
			"""
			m = SMesh()
			for layer in self.layers:
				m.getOrCreateLayer(layer.name)
			print "# of points=%d"%len(self.points)
			shippoints = {}
			for point in self.points:
				"ship,x,y,z,selected,vertextype"
				p = m.getOrCreatePoint((point.x,point.y,point.z)) #no layer!
				shippoints[(point.x,point.y,point.z)] = p
			#for edge in self.edges:
			#	"ship,start,end,crease,selected"
			#	start = shippoints[(edge.start.x,edge.start.y,edge.start.z)]
			#	end = shippoints[(edge.end.x,edge.end.y,edge.end.z)]
			#	m.getOrCreateEdge(start,end)
			for face in self.faces:
				"ship,points,layer,selected"
				points=[]
				for p in face.points:
					fp = shippoints[(p.x,p.y,p.z)]
					points.append(fp)
				f = m.getOrCreateFace(points,face.layer.name)
				f.claimChildren()
		

		def fefwrite(self,fname):
				f=open(fname,"w") 
				f.write(self.projname+CR)
				f.write(self.designer+CR)
				f.write(self.createdby+CR)
				f.write(self.comment+CR)
				f.write(self.length+' '+self.beam+' '+self.draft+' '+self.waterdensity+' '+self.appendagecoeff+' '+self.units+' '+self.mainparticular+' '+self.precision+CR)
				f.write(str(len(self.layers))+CR)
				for i in self.layers:
						f.write(i.fefstr())
				f.write(str(len(self.points))+CR)
				for i in self.points:
						f.write(i.fefstr())
				f.write(str(len(self.edges))+CR)
				for i in self.edges:
						f.write(i.fefstr())
				f.write(str(len(self.faces))+CR)
				for i in self.faces:
						f.write(i.fefstr())
				f.close()
				
		def getpointsoflayer(self,name,vertextype=None):
				points=[]
				for face in self.faces:
						if face.layer.name == name:
								for p in face.points:
										if not p in points:
												if not vertextype or (p.vertextype==vertextype):
														points.append(p)
				return points
		def getedgewithpoints(self,s,e):
				for edge in self.edges:
						if (edge.start==s) and (edge.end==e):
								return edge
				return None
		def getfacesoflayer(self,name):
				fs=[]
				for f in self.faces:
						if f.layer.name==name:
								fs.append(f)
				return fs
		def getedgesoflayer(self,name):
				p=self.getpointsoflayer(name)
				edges=[]
				for s in p:
						for e in p:
								edges.append(self.getedgewithpoints(s,e))
				while None in edges:
						edges.remove(None)
				return edges
		def selectededges(self):
				sel=[]
				for e in self.edges:
						if e.selected:
								sel.append(e)
				return sel
		def getlayer(self,name):
				for l in self.layers:
						if l.name == name:
								return l
				#not found, creating one
				l=Layer(self,name)
				self.layers.append(l)
				return l
		def newpointif(self,point):
				if point in self.points:
						return self.points[self.points.index(point)]
				p=Point(self,x=point[0],y=point[1],z=point[2])
				self.points.append(p)
				return p
		def newedgeif(self,point1,point2,crease=None):
				for i in self.edges:
						if i.contains(point1) and i.contains(point2):
								return i
				e=Edge(self,start=point1,end=point2,crease=crease)
				self.edges.append(e)
				print "new edge",e
				return e
		def newface(self,points,layername):
				layer=self.getlayer(layername)
				f=Face(self,points=points,layer=layer)
				self.faces.append(f)
				return f
		def grow(self,p,vect,stopper):
				print "growing with",stopper
				if stopper is None:
						return p+vect.end-vect.start
				return stopper.stopping(p,vect)
				
		def addmesh(ship,mesh,strakename):
				newmesh=[]
				for line in mesh:
						newline=[]
						for point in line:
								point=ship.newpointif(point)
								newline.append(point)
						newmesh.append(newline)
				
				for i in range(len(newmesh)-1):
						for j in range(len(newmesh[0])-1):
								p1=newmesh[i][j]
								p2=newmesh[i][j+1]
								p3=newmesh[i+1][j+1]
								p4=newmesh[i+1][j]
								ship.newedgeif(p1,p2,crease=1)
								ship.newedgeif(p2,p3,crease=0)
								ship.newedgeif(p3,p4,crease=1)
								ship.newedgeif(p4,p1,crease=0)
								ship.newface([p1,p2,p3,p4],'%s%s'%(strakename,i))
		
class Line:
		"""
				A continous line of edges
		"""
		def __init__(self,edges):
				laste=edges[0]
				self.line=[laste]
				edges=sorted(edges[1:])
				found = True
				while found:
						found = None
						for e in edges:
								if laste.end == e.start:
										self.line.append(e)
										laste=e
										found = laste
										edges.remove(e)
								elif laste.end == e.end:
										e.end=e.start
										e.start=laste.end
										self.line.append(e)
										laste=e
										found = laste
										edges.remove(e)
				laste = self.line[0]
				found = True
				while found:
						found = None
						for e in edges:
								if laste.start == e.end:
										self.line.insert(0,e)
										laste=e
										found = laste
										edges.remove(e)
								elif laste.start == e.start:
										e.start=e.end
										e.end=laste.start
										self.line.insert(0,e)
										laste=e
										found = laste
										edges.remove(e)
				self.unconnected=edges
				if len(edges):
						print "found unconnected selected stuff"
				self.points=[]
				for e in self.line:
						self.points.append(e.start)
				self.points.append(e.end)

class Planeset:
		def __init__(self,faces):
				"""
						faces should be connected in graph theory sense
						where faces are vertices and edges between connecting faces are ... edges
				"""
				self.boundaries={}
				self.fbs={}
				nf=[]
				for f in faces:
						nf += f.triangulate()
				self.faces=nf
				for f1 in nf:
						for f2 in nf:
								if f1 == f2:
										break
								ce = f1.commonedge(f2)
								if ce:
										# we have a common edge
										if not self.fbs.has_key(f1):
												self.fbs[f1]=[]
										self.fbs[f1].append(f2)
										n1=f1.norm()
										n2=f2.norm()
										dir=1
										if abs(n1-n2) > abs(n1+n2):
												dir=-1
										bv=(n1+dir*n2)/2
										norm=ce.normwith(bv.transpose())
										#I should think about which one is positive
										pf1=None
										for p in f1.points:
												if not ce.contains(p):
														pf1=p
														break
										pl=Plane(norm=norm,point=ce.start)
										u=pl.project(pf1)
										self.boundaries[(f1,f2)]=Plane(norm=norm*sign(u),point=ce.start)

		def stopping(self,point,vector):
				"the point where the line defined by point and vector cuts the planeset"
				print "stopping",point,vector
				vector=vector.end-vector.start
				seemsgood=[]
				for f in self.faces:
						np,u0=f.plane.intersectline(point,vector)
						found=True
						if self.fbs.has_key(f):
								for f1 in self.fbs[f]:
										u=self.boundaries[(f,f1)].project(np)
										if u <0:
												found=False
												break
						if found:
								if u0<0:
										np=point-vector*u0
								seemsgood.append((f,np))
				if len(seemsgood) == 0:
						print self
						raise 'ojaj'
				l=oo
				f=None
				np=None
				for f0,np0 in seemsgood:
						l0=abs(f0.points[0]-np0)
						if l0 < l: 
								f=f0
								np=np0
				return np
				
								
