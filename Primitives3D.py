#TODO: Make fix EPS weirdness
EPS = 1e-12
EPS_AREPLANAR = 1e-5
M_PI = 3.1415925
import math
from numpy import matrix
import numpy as np
import numpy.linalg as linalg
import matplotlib.pyplot as plt

#############################################################
####                 PRIMITIVE CLASSES                  #####
#############################################################

class Vector3D(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	
	def Dot(self, other):
		return self.x*other.x + self.y*other.y + self.z*other.z
		
	def squaredMag(self):
		return self.x**2.0 + self.y**2.0 + self.z**2.0
	
	def Length(self):
		return self.squaredMag()**0.5
	
	def normalize(self):
		mag = self.squaredMag()**0.5
		mag = float(mag)
		if (mag > EPS):
			self.x = self.x/mag
			self.y = self.y/mag
			self.z = self.z/mag
	
	def Normalize(self):
		self.normalize()
	
	def __add__(self, other):
		if isinstance(other, Point3D):#A Point plus a vector is still a point
			return other + self
		return Vector3D(self.x+other.x, self.y+other.y, self.z+other.z)

	def __sub__(self, other):
		return Vector3D(self.x-other.x, self.y-other.y, self.z-other.z)
	
	def __rmul__(self, a):
		if isinstance(a, float) or isinstance(a, int):
			return Vector3D(a*self.x, a*self.y, a*self.z)
	
	def __mul__(self, a):
		if isinstance(a, float) or isinstance(a, int):
			return Vector3D(a*self.x, a*self.y, a*self.z)
	
	def __neg__(self):
		return Vector3D(-self.x, -self.y, -self.z)
	
	def __eq__(self, other):
		return (self.x == other.x and self.y == other.y and self.z == other.z)
		
	def __ne__(self, other):
		return not (self == other)
	
	#Dot product
	def Dot(self, other):
		return self.x*other.x + self.y*other.y + self.z*other.z
	
	#Use this to implement cross product
	def __mod__(self, other):
		newX = self.y*other.z - other.y*self.z
		newY = -self.x*other.z + other.x*self.z
		newZ = self.x*other.y - other.x*self.y
		return Vector3D(newX, newY, newZ)
		
	#Project V onto this vector
	def proj(self, V):
		thisSqrMag = self.squaredMag()
		scale = 0
		if (thisSqrMag > EPS):
			scale = float(self.Dot(V)) / float(thisSqrMag)
		return Vector3D(self.x*scale, self.y*scale, self.z*scale)
		
	#Do the perpendicular projection of V onto this vector
	def projPerp(self, V):
		ret = Vector3D(V.x, V.y, V.z)
		parProj = self.proj(V)
		return ret - parProj
	
	def Copy(self):
		return Vector3D(self.x, self.y, self.z)
	
	def getPoint(self):
		return Point3D(self.x, self.y, self.z)
	
	def __str__(self):
		return "Vector3D(%g, %g, %g)"%(self.x, self.y, self.z)

class Point3D(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def Dot(self, other):
		return self.x*other.x + self.y*other.y + self.z*other.z

	def __mod__(self, other):
		newX = self.y*other.z - other.y*self.z
		newY = -self.x*other.z + other.x*self.z
		newZ = self.x*other.y - other.x*self.y
		return Vector3D(newX, newY, newZ)

	def squaredMag(self):
		return self.x**2.0 + self.y**2.0 + self.z**2.0
	
	def Length(self):
		return self.squaredMag()**0.5
	
	def normalize(self):
		mag = self.squaredMag()**0.5
		mag = float(mag)
		if (mag > EPS):
			self.x = self.x/mag
			self.y = self.y/mag
			self.z = self.z/mag
	
	def Normalize(self):
		self.normalize()
	
	def __add__(self, other):
		return Point3D(self.x+other.x, self.y+other.y, self.z+other.z)

	def __radd__(self, other):
		return self + other
	
	def __sub__(self, other):
		if isinstance(other, Vector3D): #A point minus a vector is still a point
			return Point3D(self.x-other.x, self.y - other.y, self.z - other.z)
		return Vector3D(self.x-other.x, self.y-other.y, self.z-other.z)	
	
	def __rmul__(self, a):
		if isinstance(a, float) or isinstance(a, int):
			return Point3D(a*self.x, a*self.y, a*self.z)
	
	def __mul__(self, a):
		if isinstance(a, float) or isinstance(a, int):
			return Point3D(a*self.x, a*self.y, a*self.z)
	
	def __neg__(self):
		return Point3D(-self.x, -self.y, -self.z)

	def __eq__(self, other):
		return (self.x == other.x and self.y == other.y and self.z == other.z)
		
	def __ne__(self, other):
		return not (self == other)

	def Copy(self):
		return Point3D(self.x, self.y, self.z)

	def getVector(self):
		return Vector3D(self.x, self.y, self.z)

	def __str__(self):
		return "Point3D(%g, %g, %g)"%(self.x, self.y, self.z)

class PointsCCWComparator(object):
	def __init__(self, C, VFirst):
		self.C = C #Center of reference for comparison
		self.VFirst = VFirst #First vertex in polygon
		self.N = VFirst - C #Normal direction
	
	def compare(self, V1, V2):
		a = V1 - self.VFirst
		b = V2 - self.VFirst
		triNormal = a % b
		dot = triNormal.Dot(self.N)
		if dot > 0:
			return 1
		elif dot == 0:
			return 0
		return -1

class Matrix4(object):
	def __init__(self, args = []):
		if len(args) > 0: #Matrix specified in row-major order in argument
			self.m = args[:]
		else: #Make an identity matrix by default
			self.m = [0]*16 #Zeros
			self.m[0:16:5] = [1, 1, 1, 1] #Ones along diagonal
	
	def Transpose(self):
		return Matrix4([self.m[4*(i%4)+i/4] for i in range(0, 16)])
	
	def getColVector3(self, col):
		if col < 0 or col > 3:
			print "Column %i out of range\n"%(col)
			return
		return Vector3D(self.m[col], self.m[col+4], self.m[col+8])
	
	def __eq__(self, other):
		return sum([abs(self.m[i]-other.m[i]) for i in range(0, 16)]) == 0
	
	def __ne__(self, other):
		return not (self == other)
	
	def __add__(self, other):
		return Matrix4([self.m[i]+other.m[i] for i in range(0, 16)])
	
	def __sub__(self, other):
		return Matrix4([self.m[i]-other.m[i] for i in range(0, 16)])
	
	def __mul__(self, other):
		if isinstance(other, Matrix4):
			#Matrix-Matrix multiplication
			retm = [0]*16
			for i in range(0, 16):
				(row, col) = (i/4, i%4)
				retm[i] = sum([self.m[row*4+k]*other.m[k*4+col] for k in range(0, 4)])
			return Matrix4(retm)
		if isinstance(other, Point3D) or isinstance(other, Vector3D):
			#Point/vector transformation by matrix
			retv = [0]*4
			otherm = [other.x, other.y, other.z, 1] #4D homogenous point/vector
			for row in range(0, 4):
				retv[row] = sum([self.m[row*4+k]*otherm[k] for k in range(0, 4)])
			#Divide by homogenous coordinate
			retv = [float(retv[k]) / float(retv[3]) for k in range(0, 3)] 
			if isinstance(other, Point3D):
				return Point3D(retv[0], retv[1], retv[2])
			else:
				return Vector3D(retv[0], retv[1], retv[2])
	
	def __rmul__(self, a):
		try:
			mulVal = float(a)
			otherm = [a*elem for elem in self.m]
			return Matrix4(otherm)
		except ValueError:
			print "ERROR: Trying to multiply matrix on left by type %s"%type(a)
	
	def __neg__(self):
		return -1*self
	
	#http://stackoverflow.com/questions/1148309/inverting-a-4x4-matrix
	def Inverse(self):
		m = self.m
		numpym = matrix([[m[0], m[1], m[2], m[3]], [m[4], m[5], m[6], m[7]], [m[8], m[9], m[10], m[11]], [m[12], m[13], m[14], m[15]]])
		inv = numpym.I.flatten()
		return Matrix4(inv.tolist()[0])
		
		##There seems to be a bug with the way I did things before so I'm using numpy for now
		inv = [0]*16
		#[a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44] = m
		inv[0] =   m[5]*m[10]*m[15] - m[5]*m[11]*m[14] - m[9]*m[6]*m[15] + m[9]*m[7]*m[14] + m[13]*m[6]*m[11] - m[13]*m[7]*m[10]
		inv[4] =  -m[4]*m[10]*m[15] + m[4]*m[11]*m[14] + m[8]*m[6]*m[15] - m[8]*m[7]*m[14] - m[12]*m[6]*m[11] + m[12]*m[7]*m[10];
		inv[8] =   m[4]*m[9]*m[15] - m[4]*m[11]*m[13] - m[8]*m[5]*m[15]	+ m[8]*m[7]*m[13] + m[12]*m[5]*m[11] - m[12]*m[7]*m[9];
		inv[12] = -m[4]*m[9]*m[14] + m[4]*m[10]*m[13] + m[8]*m[5]*m[14]	- m[8]*m[6]*m[13] - m[12]*m[5]*m[10] + m[12]*m[6]*m[9];
		inv[1] =  -m[1]*m[10]*m[15] + m[1]*m[11]*m[14] + m[9]*m[2]*m[15] - m[9]*m[3]*m[14] - m[13]*m[2]*m[11] + m[13]*m[3]*m[10];
		inv[5] =   m[0]*m[10]*m[15] - m[0]*m[11]*m[14] - m[8]*m[2]*m[15] + m[8]*m[3]*m[14] + m[12]*m[2]*m[11] - m[12]*m[3]*m[10];
		inv[9] =  -m[0]*m[9]*m[15] + m[0]*m[11]*m[13] + m[8]*m[1]*m[15]	- m[8]*m[3]*m[13] - m[12]*m[1]*m[11] + m[12]*m[3]*m[9];
		inv[13] =  m[0]*m[9]*m[14] - m[0]*m[10]*m[13] - m[8]*m[1]*m[14]	+ m[8]*m[2]*m[13] + m[12]*m[1]*m[10] - m[12]*m[2]*m[9];
		inv[2] =   m[1]*m[6]*m[15] - m[1]*m[7]*m[14] - m[5]*m[2]*m[15]	+ m[5]*m[3]*m[14] + m[13]*m[2]*m[7] - m[13]*m[3]*m[6];
		inv[6] =  -m[0]*m[6]*m[15] + m[0]*m[7]*m[14] + m[4]*m[2]*m[15] - m[4]*m[3]*m[14] - m[12]*m[2]*m[7] + m[12]*m[3]*m[6];
		inv[10] =  m[0]*m[5]*m[15] - m[0]*m[7]*m[13] - m[4]*m[1]*m[15] + m[4]*m[3]*m[13] + m[12]*m[1]*m[7] - m[12]*m[3]*m[5];
		inv[14] = -m[0]*m[5]*m[14] + m[0]*m[6]*m[13] + m[4]*m[1]*m[14] - m[4]*m[2]*m[13] - m[12]*m[1]*m[6] + m[12]*m[2]*m[5];
		inv[3] =  -m[1]*m[6]*m[11] + m[1]*m[7]*m[10] + m[5]*m[2]*m[11] - m[5]*m[3]*m[10] - m[9]*m[2]*m[7] + m[9]*m[3]*m[6];
		inv[7] =   m[0]*m[6]*m[11] - m[0]*m[7]*m[10] - m[4]*m[2]*m[11] + m[4]*m[3]*m[10] + m[8]*m[2]*m[7] - m[8]*m[3]*m[6];
		inv[11] = -m[0]*m[5]*m[11] + m[0]*m[7]*m[9] + m[4]*m[1]*m[11]
		inv[15] =  m[0]*m[5]*m[10] - m[0]*m[6]*m[9] - m[4]*m[1]*m[10] + m[4]*m[2]*m[9] + m[8]*m[1]*m[6] - m[8]*m[2]*m[5];
		det = m[0]*inv[0] + m[1]*inv[4] + m[2]*inv[8] + m[3]*inv[12]
		if det == 0:
			print "ERROR: Determinant of matrix is zero; cannot invert"
			return
		det = 1.0/det
		return Matrix4([inv[i]*det for i in range(0, 16)])

	def getUpperLeft3x3(self):
		m = self.m[:]
		m[3] = 0
		m[7] = 0
		m[11] = 0
		return Matrix4(m)

	def __str__(self):
		fmt = "[%g, %g, %g, %g]\n"*4
		return fmt%(tuple(self.m))

class Plane3D(object):
	#P0 is some point on the plane, N is the normal
	#Also store A, B, C, and D, the coefficients of the implicit plane equation
	def __init__(self, P0, N):
		self.P0 = P0
		self.N = N
		self.N.normalize()
		self.resetEquation()

	def resetEquation(self):
		[self.A, self.B, self.C] = [self.N.x, self.N.y, self.N.z]
		self.D = -self.P0.getVector().Dot(self.N)

	def initFromEquation(self, A, B, C, D):
		self.N = Vector3D(A, B, C)
		self.P0 = Point3D(A, B, C)
		self.P0 = (-D/self.N.squaredMag())*self.P0
		self.N.normalize()
		self.resetEquation()

	def distFromPlane(self, P):
		return self.A*P.x + self.B*P.y + self.C*P.z + self.D

	def __str__(self):
		return "Plane3D: %g*x + %g*y + %g*z + %g = 0"%(self.A, self.B, self.C, self.D)

class Line3D(object):
	def __init__(self, P0, V):
		self.P0 = P0
		self.V = V

	def intersectPlane(self, plane):
		P0 = plane.P0
		N = plane.N
		P = self.P0
		V = self.V
		if abs(N.Dot(V)) < EPS:
			return None
		t = (P0.getVector().Dot(N) - N.Dot(P.getVector())) / (N.Dot(V))
		intersectP = P + t*V
		return [t, intersectP]
	
	def intersectOtherLineRet_t(self, other):
		#P0 = Point3D(-2.5, 0, -2.5)
		#V0 = Vector3D(-0, -0, -1)
		#P1 = Point3D(-2.5, -2.5, 0)
		#V1 = Vector3D(0, -1, 0)
		#Solve for (s, t) in the equation P0 + t*V0 = P1+s*V1
		#This is three equations (x, y, z components) in 2 variables (s, t)
		#User cramer's rule and the fact that there is a linear
		#dependence that only leaves two independent equations
		#(add the last two equations together)
		#[a b][t] = [e]
		#[c d][s]	[f]
		P0 = self.P0
		V0 = self.V
		P1 = other.P0
		V1 = other.V
		a = V0.x+V0.z
		b = -(V1.x+V1.z)
		c = V0.y + V0.z
		d = -(V1.y+V1.z)
		e = P1.x + P1.z - (P0.x + P0.z)
		f = P1.y + P1.z - (P0.y + P0.z)
		#print "[%g %g][t] = [%g]\n[%g %g][s]   [%g]"%(a, b, e, c, d, f)
		detDenom = a*d - c*b
		#Lines are parallel or skew
		if abs(detDenom) < EPS:
			return None
		detNumt = e*d - b*f
		detNums = a*f - c*e
		t = float(detNumt) / float(detDenom)
		s = float(detNums) / float(detDenom)
		#print "s = %g, t = %g"%(s, t)
		return (t, P0 + t*V0)
	
	def intersectOtherLine(self, other):
		ret = self.intersectOtherLineRet_t(other)
		if ret:
			return ret[1]
		return None
	
	def __str__(self):
		return "Line3D: %s + t%s"%(self.P0, self.V)


class Ray3D(object):
	def __init__(self, P0, V):
		self.P0 = P0
		self.V = V.Copy()
		self.V.Normalize()
		self.line = Line3D(self.P0, self.V)
	
	def Copy(self):
		return Ray3D(self.P0.Copy(), self.V.Copy())
	
	def Transform(self, matrix):
		self.P0 = matrix*self.P0
		self.V = matrix.getUpperLeft3x3()*self.V
		self.V.normalize()
	
	def intersectPlane(self, plane):
		intersection = self.line.intersectPlane(plane)
		if intersection != None:
			if intersection[0] < 0:
				return None
			return intersection
	
	def intersectMeshFace(self, face):
		facePlane = face.getPlane()
		intersection = self.intersectPlane(facePlane)
		if intersection == None:
			return None
		[t, intersectP] = intersection
		#Now check to see if the intersection is within the polygon
		#Do this by verifying that intersectP is on the same side
		#of each segment of the polygon
		verts = [v.pos for v in face.getVertices()]
		if len(verts) < 3:
			return None
		lastCross = (verts[1] - verts[0]) % (intersectP - verts[1])
		lastCross.normalize()
		for i in range(1, len(verts)):
			v0 = verts[i]
			v1 = verts[(i+1)%len(verts)]
			cross = (v1 - v0) % (intersectP - v1)
			cross.normalize()
			if cross.Dot(lastCross) < EPS: #The intersection point is on the outside of the polygon
				return None
			lastCross = cross
		return [t, intersectP]

	def __str__(self):
		return "Ray3D: %s + t%s"%(self.P0, self.V)
	


#############################################################
####                UTILITY FUNCTIONS                   #####
#############################################################

#Rotate a vector (or point) V by angle "theta" around a line through P0 
#whose direction is specified by V
def rotateAroundAxis(P0, axis, theta, V):
	#print "P0 = %s, axis = %s, V = %s"%(P0, axis, V)
	diffV = V - P0
	parV = axis.proj(diffV) #Part of v along axis unaffected by rotation
	perpV = axis.projPerp(diffV)
	if perpV.Dot(perpV) < EPS: #Hardly any perpendicular component
		return V
	u = perpV.Copy()
	u.normalize()
	w = axis
	w.normalize()
	v = w%u
	#Put perpV into a frame where the rotation is about (0, 0, 1)
	fromFrame = Matrix4([u.x, v.x, w.x, 0, u.y, v.y, w.y, 0, u.z, v.z, w.z, 0, 0, 0, 0, 1])
	toFrame = fromFrame.Inverse()
	perpV = toFrame*perpV
	#Rotate perpV by theta in that frame
	(cosTheta, sinTheta) = (math.cos(theta), math.sin(theta))
	rotMat = Matrix4([cosTheta, -sinTheta, 0, 0, sinTheta, cosTheta, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
	perpV = rotMat*perpV
	#Bring perpV back into world coordinates and compute result
	perpV = fromFrame*perpV
	res = P0 + perpV + parV
	if isinstance(V, Vector3D):
		return Vector3D(res.x, res.y, res.z)
	if isinstance(V, Point3D):
		return Point3D(res.x, res.y, res.z)

#Return True if the vertices in the list "verts" all lie
#in the same plane and False otherwise
def arePlanar(verts):
	if len(verts) <= 3:
		return True
	v0 = verts[1] - verts[0]
	v1 = verts[2] - verts[0]
	n = v0 % v1
	n.normalize()
	for i in range(3, len(verts)):
		v = verts[i] - verts[0]
		v.normalize()
		if abs(v.Dot(n)) > EPS_AREPLANAR:
			return False
	return True

#If the vertices in "verts" form a convex 2D polygon 
#(in the order specified) return True.  Return False otherwise
def are2DConvex(verts):
	if len(verts) <= 3:
		return True
	if not arePlanar(verts):
		return False
	v0 = verts[0]
	v1 = verts[1]
	v2 = verts[2]
	lastCross = (v1-v0) % (v2-v1)
	for i in range(3, len(verts)+1):
		v0 = v1
		v1 = v2
		v2 = verts[i%len(verts)]
		cross = (v1-v0) % (v2-v1)
		if cross.Dot(lastCross) < 0:
			return False
		lastCross = cross
	return True

#General purpose method for returning the normal of a face
#Assumes "verts" are planar and not all collinear
def getFaceNormal(verts):
	#This properly handles the case where three vertices
	#are collinear right after one another
	for i in range(2, len(verts)):
		v1 = verts[i-1] - verts[0]
		v2 = verts[i] - verts[0]
		ret = v1 % v2
		v1L = v1.Length()
		v2L = v2.Length()
		if v1L > 0 and v2L > 0 and ret.Length()/(v1L*v2L) > 1e-10:
			ret.normalize()
			return ret
	return None

#This function assumes the polygon is convex
def getPolygonArea(verts):
	if len(verts) < 3:
		return 0.0
	v1 = verts[1] - verts[0]
	v2 = verts[1] - verts[0]
	area = 0.0
	#Triangulate and add area of each triangle
	for i in range(2, len(verts)):
		v1 = v2
		v2 = verts[i] - verts[0]
		area = area + 0.5*(v1%v2).Length()
	return area

def getTriangleArea(A, B, C):
	return getPolygonArea([A, B, C])

#Get the closest point on the face represented by Vs to P
def getClosestPoint(Vs, P):
	if len(Vs) < 3:
		return
	N = getFaceNormal(Vs)
	dV = P - Vs[0]
	#First find the closest point on the plane to this point
	PPlane = Vs[0] + N.projPerp(P)
	#Now check to see if PPlane is on the interior of the polygon
	ccws = np.zeros((len(Vs), 1))
	for i in range(len(Vs)):
		A = Vs[i]
		B = Vs[(i+1)%len(Vs)]
		v1 = PPlane - A
		v2 = PPlane - B
		M = np.ones((3, 3))
		M[1, :] = np.array([v1.x, v1.y, v1.z])
		M[2, :] = np.array([v2.x, v2.y, v2.z])
		ccw = linalg.det(M)
		if ccw < 0:
			ccws[i] = -1
		elif ccw > 0:
			ccws[i] = 1
		else:
			ccws[i] = 0
	if abs(sum(ccws)) == (ccws != 0).sum():
		return PPlane
	#Otherwise, the point is on the outside of the polygon
	#Check every edge to find the closest point
	minDist = np.inf
	ret = PPlane
	for i in range(len(Vs)):
		A = Vs[i]
		B = Vs[(i+1)%len(Vs)]
		dL = B - A
		PProjRel = dL.proj(PPlane - A)
		PClosest = A + PProjRel
		#Parameter representing where the point is
		#in the interior of the segment AB
		t = dL.Dot(PProjRel)/dL.squaredMag()
		#If the projected point is to the left of A, A is the closest
		if t < 0:
			PClosest = A
		#If the projected point is to the right of B, B is the closest
		elif t > 1:
			PClosest = B
		#Otherwise it is in the interior
		distSqr = (P - PClosest).squaredMag()

		if distSqr < minDist:
			minDist = distSqr
			ret = PClosest
	return ret

#Return the cosine of the angle between P1 and P2 with respect
#to "Vertex" as their common, shared vertex
def COSBetween(Vertex, P1, P2):
	V1 = P1 - Vertex
	V2 = P2 - Vertex
	dot = V1.Dot(V2)
	magProduct = math.sqrt(V1.squaredMag()*V2.squaredMag())
	if (magProduct < EPS):
		return 0
	return float(dot) / float(magProduct)

def PointsEqual(A, B):
	return abs(A.x - B.x) < EPS and abs(A.y - B.y) < EPS and abs(A.z - B.z) < EPS

def printPointsList(L, name):
	print "%s = ["%name,
	for i in range(0, len(L)):
		print "%s"%L[i],
		if i < len(L) - 1:
			print ",",
		else:
			print "]"

if __name__ == '__main__':
	Vs = [Point3D(0.00360787, 0.0590845, -0.0482064), Point3D(0.0396016, 0.0424315, -0.0762202), Point3D(0.0301187, 0.0612541, -0.0644878)]
	P = Point3D(0.0142555, 0.0875641, -0.0460397)
#	Vs = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)]
#	P = Point3D(0.5, 0.6, 2)
	Closest = getClosestPoint(Vs, P)
	
	Axis1 = Vs[1] - Vs[0]
	Axis2 = Vs[2] - Vs[0]
	Axis2 = Axis1.projPerp(Axis2)
	Axis1.normalize()
	Axis2.normalize()
	A = Point3D(0, 0, 0)
	B = Point3D(Axis1.proj(Vs[1] - Vs[0]).Length(), Axis2.proj(Vs[1] - Vs[0]).Length(), 0)
	C = Point3D(Axis1.proj(Vs[2] - Vs[0]).Length(), Axis2.proj(Vs[2] - Vs[0]).Length(), 0)
	X = Point3D(Axis1.proj(Closest - Vs[0]).Length(), Axis2.proj(Closest - Vs[0]).Length(), 0)
	O = Point3D(Axis1.proj(P - Vs[0]).Length(), Axis2.proj(P - Vs[0]).Length(), 0)
	print "O = %s"%O
	print "X = %s"%X
	
	plt.plot([A.x, B.x, C.x, A.x], [A.y, B.y, C.y, A.y], 'r')
	plt.hold(True)
	plt.plot([X.x], [X.y], 'bo')
	plt.plot([O.x], [O.y], 'go')
	plt.plot([X.x, O.x], [X.y, O.y], 'r')
	plt.show()

if __name__ == '__main__3':
	m = Matrix4([0, 1, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 1])
	print m
	print m.Inverse()
	A = Point3D(-1, 0, 0)
	B = Point3D(1, 0, 0)
	C = Point3D(0, 1, 0)
	D = Point3D(0, -1, 0)
	print intersectSegments2D(A, B, C, D)

if __name__ == '__main__2':
#	P0 = Point3D(-2.5, 0, -2.5)
#	V0 = Vector3D(-0, -0, -1)
#	P1 = Point3D(-2.5, -2.5, 0)
#	V1 = Vector3D(0, -1, 0)
#	line1 = Line3D(P0, V0)
#	line2 = Line3D(P1, V1)
#	intersection = line1.intersectOtherLine(line2)
	
	P0 = Point3D(0, 0, 0)#(1, 4, 0)
	P1 = Point3D(1, 1, 0)#(5, 2, 0)
	P2 = Point3D(0, 1, 0)#(2, 0, 0)
	P3 = Point3D(1, 0, 0)#(3, 5, 0)
	PointRot = Point3D(0, 0, 0)
	AxisRot = Vector3D(1, 1, 1)
	Angle = 0.5
	P0 = rotateAroundAxis(PointRot, AxisRot, Angle, P0)
	P1 = rotateAroundAxis(PointRot, AxisRot, Angle, P1)
	P2 = rotateAroundAxis(PointRot, AxisRot, Angle, P2)
	P3 = rotateAroundAxis(PointRot, AxisRot, Angle, P3)
	V0 = P1 - P0
	V1 = P3 - P2
	line1 = Line3D(P0, V0)
	line2 = Line3D(P2, V1)
	intersection = line1.intersectOtherLine(line2)
	intersection = rotateAroundAxis(PointRot, AxisRot, -Angle, intersection)
	print intersection
#	P = Plane3D(Point3D(1, 1, 1), Vector3D(1, 2, 3))
#	print P
#	angle = 30
#	angle = angle*3.141/180.0
#	(cosA, sinA) = [math.cos(angle), math.sin(angle)]
#	A = Matrix4([cosA, -sinA, 0, 0,
#				sinA, cosA, 0, 0,
#				0, 0, 1, 0, 0, 0, 0, 1])
#	verts = [Point3D(0, 0, 0), Point3D(0, 1, 0), Point3D(1, 1, 0), Point3D(2, 0.5, 0), Point3D(3.01, 0, 0), Point3D(1, -1, 0)]
#	verts = [rotateAroundAxis(Point3D(1, 1, 0), Vector3D(1, 0, 0), angle, v) for v in verts]
#	for v in verts:
#		print v
#	print are2DConvex(verts)
