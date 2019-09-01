import math
import numpy as np

class HomographyCalculation:

    p1 = []
    p2 = []
    H = None

    def __init__(self, p1, p2):
        self.p1 = self.__set3D(p1)
        self.p2 = self.__set3D(p2)
        self.H = None

    def __set3D(self,ps):
        ps3D = []
        for p in ps:
            ps3D.append([p[0],p[1],1])
        return np.asarray(ps3D).transpose()

    def start_Calculation(self):
        # norm
        T1 = self.__get_Transform_Matrix(self.p1)
        T2 = self.__get_Transform_Matrix(self.p2)
        #transform -> to get tranformed base and attach
        base2 = self.__apply_H(self.p1, T1)
        attach2 = self.__apply_H(self.p2, T2)
        #design matrix -> to get the design matrix A
        A = self.__get_Design_Matrix(base2, attach2)
        #SVD -> solve SVD to get a homography matrix H
        self.H = self.__solve_dlt(A)
        #decondition -> decondition H
        self.H = self.__decondition(T1,T2,self.H)

    def get_H(self):
        return self.H

    def __get_Transform_Matrix(self,ps):
        print("TRANSFORM: input shape "+str(ps.shape))
        px = 0
        py = 0
        sx = 0
        sy = 0
        for p in ps.transpose():
#            print(p.shape)
            px = px + p[0]
            py = py + p[1]
        px = px / ps.shape[1]
        py = py / ps.shape[1]
        for p in ps.transpose():
            x = px-p[0]
            sx = sx + math.sqrt(math.pow(x,2))
            y = py-p[1]
            sy = sy + math.sqrt(math.pow(y,2))
        sx = sx / ps.shape[1]
        sy = sy / ps.shape[1]
        ret = np.eye(3)
        ret[0,0] = 1/sx
        ret[1,1] = 1/sy
        ret[0,2] = -px/sx
        ret[1,2] = -py/sy
        print("output shape "+str(ret.shape))
        return ret

    def __apply_H(self, p, H):
        print("APPLY: input shape "+str(p.shape)+" "+str(H.shape))
        ret = H * np.matrix(p)
        print("output shape "+str(ret.shape))
        return ret

    def __get_Design_Matrix(self, base, attach):
        print("DESIGN MATRIX: input shape "+str(base.shape)+" "+str(attach.shape))
        designMatrix = np.zeros([(base.shape[1]*2),9]) #for random number of points
        for b in range(0,base.shape[1]):
            dMOnePoint = self.__get_Design_Matrix_Of_One_Point(base[:,b], attach[:,b])
            designMatrix[(b*2)] = dMOnePoint[0]
            designMatrix[(b*2)+1] = dMOnePoint[1]
        print("output shape "+str(designMatrix.shape))
        return designMatrix

    def __get_Design_Matrix_Of_One_Point(self, b, a):
        print("DESIGN MATRIX ONE POINT: input shape "+str(b.shape)+" "+str(a.shape))
        designMatrix = np.zeros([2,9])
        for i in range(0,3):
            designMatrix[0,i] = -b[2,0]*a[i,0]# korrekte base and attach
            designMatrix[1,i+3] = -b[2,0]*a[i,0]
            designMatrix[0,i+6] = b[0,0]*a[i,0]
            designMatrix[1,i+6] = b[1,0]*a[i,0]
        print("output shape "+str(designMatrix.shape))
        return designMatrix

    def __solve_dlt(self, A):
        print("SOLVE DLT: "+str(A.shape))
        Aquat = np.zeros([A.shape[1], A.shape[1]])
        if A.shape[0] < A.shape[1]:
            for i in range(0,A.shape[0]):
                Aquat[i] = A[i]
        else:
            Aquat = A
        u,s,vh = np.linalg.svd(Aquat)
        print("SVD shapes: u "+str(u.shape)+", s "+str(s.shape)+", vh "+str(vh.shape))
        index = 0
        min = s[0]
        for i in range(0,len(s)):
            if min>s[i]:
                index = i
                min = s[i]
        column = vh[index].transpose()
        H = np.zeros([3,3])
        for i in range(0,column.shape[0]):
            H[int(i/3),i%3] = column[i]
        print("output shape "+str(H.shape))
        return H

    def __decondition(self, T_base, T_attach, H):
    	return np.linalg.inv(T_base)*H*T_attach
