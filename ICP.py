from Primitives3D import *
from PolyMesh import *
from LaplacianMesh import *
from PointCloud import *
from sys import exit, argv
import random
import numpy as np
import numpy.linalg as linalg
import scipy.spatial as spatial

ICP_MAXITER = 100
ICP_NPOINTSAMPLES = 100

def getRigidTransformationSVD(Points, TargetPoints):
	P = Points.copy()
	T = TargetPoints.copy()
	#Subtract off centroids
	meanP = P.mean(0)
	meanT = T.mean(0)
	P = P - meanP
	T = T - meanT
	H = P.transpose().dot(T)
	U, S, Vh = linalg.svd(H)
	R = np.eye(4)
	R[0:3, 0:3] = Vh.transpose().dot(U.transpose())
	#Transformation order:
	#1: Move the point set so it's centered on the centroid
	#2: Rotate the point set by the calculated rotation
	#3: Move the point set so it's centered on the target centroid
	T1 = np.eye(4)
	T1[0:3, 3] = -meanP
	T2 = np.eye(4)
	T2[0:3, 3] = meanT
	#In other words, T2*R*T1
	return T2.dot(R.dot(T1))

def getSquaredError(PPointsThis, MPointsThis):
	diff = PPointsThis - MPointsThis
	diff = diff*diff
	return diff.sum()

def transformPoints(T, P):
	#Put points into homogenous coordinates and multiply
	PTemp = P.copy()
	PTemp = np.concatenate((PTemp, np.ones((PTemp.shape[0], 1))), axis = 1)
	PTemp = PTemp.transpose()
	PTemp = T.dot(PTemp)
	PTemp = PTemp.transpose()
	return PTemp[:, 0:3]

#update: Update the points to reflect the best found transformation?
def ICP_PointsToMesh(P, M, update = False):
	MCentroid = M.getCentroid()
	NM = len(M.vertices)
	MPoints = np.zeros((NM, 3))
	for i in range(NM):
		pos = M.vertices[i].pos
		MPoints[i, 0] = pos.x
		MPoints[i, 1] = pos.y
		MPoints[i, 2] = pos.z
	(MAxis1, MAxis2, MAxis3, maxProj, minProj, MAxes) = M.getPrincipalAxes()
	
	PCentroid = P.getCentroid()
	NP = len(P.points)
	OrigPoints = np.zeros((NP, 3))
	for i in range(NP):
		pos = P.points[i]
		OrigPoints[i, 0] = pos.x
		OrigPoints[i, 1] = pos.y
		OrigPoints[i, 2] = pos.z
	(PAxis1, PAxis2, PAxis3, maxProj, minProj, PAxes) = P.getPrincipalAxes()
	
	#Randomly subsample points in the point sets for speed
	PIndices = np.random.permutation(OrigPoints.shape[0])
	PPoints = OrigPoints[PIndices[0:min(ICP_NPOINTSAMPLES, OrigPoints.shape[0])], :]
	MIndices = np.random.permutation(MPoints.shape[0])
	MPoints = MPoints[MIndices[0:min(ICP_NPOINTSAMPLES, MPoints.shape[0])], :]
	MKDTree = spatial.KDTree(MPoints)
	
	AllTransformations = []
	minError = np.infty
	minIndex = 0 #Index of the best permuation/flip
	
	[flip1, flip2, flip3] = [1, 1, 1]

		
	for perm1 in range(3):
		for perm2 in range(3):
			if perm2 == perm1:
				continue
			for perm3 in range(3):
				if perm3 == perm2 or perm3 == perm1:
					continue
				for flip1 in [-1, 1]:
					for flip2 in [-1, 1]:
						for flip3 in [-1, 1]:
							print "perm1, perm2, perm3 = %i, %i, %i"%(perm1, perm2, perm3)
							print "flip1, flip2, flip3 = %i, %i, %i"%(flip1, flip2, flip3)
							thisaxis = PAxes[:, np.array([perm1, perm2, perm3])]
							thisaxis[:, 0] = flip1*thisaxis[:, 0]
							thisaxis[:, 1] = flip2*thisaxis[:, 1]
							thisaxis[:, 2] = flip3*thisaxis[:, 2]
							#Initial Guess Transformation steps
							#1. Translate point set so that it's centered at the origin
							#2. Rotate point set so that it's aligned with the chosen axes
							#3. Rotate again to align with the axes of the mesh
							#4. Translate to center at the centroid of the mesh
							T1 = np.eye(4)
							T1[0:3, 3] = np.array([-PCentroid.x, -PCentroid.y, -PCentroid.z])
							R1 = np.eye(4)
							R1[0:3, 0:3] = thisaxis
							R1 = R1.transpose()
							T2 = np.eye(4)
							T2[0:3, 3] = np.array([MCentroid.x, MCentroid.y, MCentroid.z])
							R2 = np.eye(4)
							R2[0:3, 0:3] = MAxes
							#In other words, T = R2*T2*R1*T1
							T = R2.dot( T2.dot( R1.dot( T1 ) ) )
							converged = False
							lastidx = np.zeros(ICP_NPOINTSAMPLES)
							#Find closest points and re-align until the closest points
							#do not change
							transformations = []
							numIter = 0
							while not converged and numIter < ICP_MAXITER:
								transformations.append(T)
								PPointsThis = transformPoints(T, PPoints)
								dists, idx = MKDTree.query(PPointsThis)
								MPointsThis = MPoints[idx, :]
								#TODO: Use this to do point to plane ICP getting closest
								#points on supporting planes
								diffFromLast = np.abs(idx - lastidx)
								if diffFromLast.sum() == 0:
									converged = True
								lastidx = idx
								T = getRigidTransformationSVD(PPoints, MPointsThis)
								numIter = numIter + 1
								print ".",
							print ""
							AllTransformations.append(transformations)
							err = getSquaredError(PPointsThis, MPointsThis)
							print "err = %g"%err
							if err < minError:
								minError = err;
								minIndex = len(AllTransformations) - 1
	
	T = AllTransformations[minIndex][-1]
	print "T = %s"%T
	if update:
		#Update the points in the point set
		OrigPoints = transformPoints(T, OrigPoints)
		for i in range(OrigPoints.shape[0]):
			P.points[i] = Point3D(OrigPoints[i, 0], OrigPoints[i, 1], OrigPoints[i, 2])
	return AllTransformations, minIndex, error

def ICP_MeshToMesh(M1, M2, update = False):
	P = PointCloud()
	for i in range(len(M1.vertices)):
		P.points.append(M1.vertices[i].pos)
		P.colors.append([1, 0, 0])
	AllTransformations, minIndex, error = ICP_PointsToMesh(P, M2, update)
	for i in range(len(M1.vertices)):
		M1.vertices[i].pos = P.points[i]
	return AllTransformations, minIndex, error