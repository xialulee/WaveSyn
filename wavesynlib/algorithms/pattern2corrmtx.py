# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 22:19:30 2014

@author: Tao Zhang, Feng-cong Li (xialulee@sina.com)
"""

from numpy import exp, kron, mat, pi, r_, real, sin, vstack, zeros
import cvxpy as cp




def Jmat(M):
    'Create a complex M^2 * M^2 matrix which satisfies vec(R) == Jr'
    ret = zeros((M**2, M**2), complex)
    
    k   = 0
    addr_table  = {}
    for q in range(M):
        for p in range(q, M):
            addr_table[(p,q)]   = k
            k += 1 if p==q else 2
    
    for q in range(M):
        for p in range(M):
            row = q*M + p
            if p == q:
                ret[row, addr_table[(p,q)]]   = 1
            else:
                addr    = addr_table[(p,q)] if p > q else addr_table[(q,p)]
                ret[row, addr]    = 1
                ret[row, addr+1]  = 1j if p > q else -1j
    return mat(ret)
    
    
def Amat(M, angles):
    'The steering matrix'
    ret = zeros((M, len(angles)), complex)
    for col, theta in enumerate(angles):
        ret[:, col] = exp(1j * pi * r_[0:M] * \
        sin(pi * theta / 180.))
    return mat(ret)
    
#def unnamed():
#    theta   = r_[-90:90.1:0.1]
def ideal_pattern(angles, beamangle, beamwidth):
    ret = zeros(len(angles))  
    for k in range(len(beamangle)):
        for idx, theta in enumerate(angles):
            if abs(theta - beamangle[k]) < beamwidth[k]/2.0:
                ret[idx]    = 1
    return ret
    
def Gmat(M, angles, idealpattern):
    G1  = mat(zeros((M**2+1, M**2+1)))
    #G2  = mat(zeros((M**2+1, M**2+1)))
    A   = mat(Amat(M, angles))
    J   = mat(Jmat(M))
    #w   = mat(np.ones((len(angles), 1)))
    for idx, theta in enumerate(angles):
        g   = -(kron(A[:,idx].T, A[:,idx].H) * J).T
        #G1  += vstack((idealpattern[idx], g)) * np.hstack((idealpattern[idx], g.T))
        #vstack((idealpattern[idx], g))
        #print idealpattern[idx].shape
        t   = mat(vstack((idealpattern[idx], g)));
        #G1  += np.outer(*([vstack((idealpattern[idx], g))]*2))
        G1  += real(t * t.T)
    G1  = 1.0/len(angles) * G1
    G1  = real(G1)
    return mat(G1)
    
                
              
def corrmtx2pattern(R, angles):
    M   = R.shape[0]
    ret = zeros(len(angles))    
    A   = Amat(M, angles)
    for k in range(len(angles)):
        #print (A[:,k].H * R * A[:,k])[0,0]
        ret[k]  = real((A[:, k].H * R * A[:, k])[0,0])
    ret /= max(ret)
    return ret
#####################################################
# test
#M   = 10                
#angles  = r_[-90:90.1:0.1]
#idealp  = ideal_pattern(angles, [-20], [20])
#Gamma   = Gmat(M, angles, idealp)    
#print Gamma            
#####################################################  
class Problem(object):
    def __init__(self):
        self.__M    = None
        self.__idealp   = None
        self.angles = None
        self.__Gamma    = None
    
    @property
    def M(self):
        return self.__M 

    @M.setter
    def M(self, val):
        val = int(val)
        if val != self.__M:
            #self.__Gamma    = cp.Parameter(M**2+1, M**2+1)
            self.__M    = val            
            #self.__setup()
            
    @property
    def idealpattern(self):
        return self.__idealp
        
    @idealpattern.setter
    def idealpattern(self, val):
        Gamma   = Gmat(self.M, self.angles, val)
        #self.__Gamma(Gamma)
        self.__Gamma    = Gamma
            
    def solve(self, *args, **kwargs):
        self.__setup()
        self.__problem.solve(*args, **kwargs)
        R   = (self.__ReR.value + 1j * self.__ImR.value)
        return R        
        

    def __setup(self):  
        M   = self.__M           
        Rreal = cp.semidefinite(2*M, 'Rreal')
# Rreal = [B1 B3
#          B2 B4 ]
#       = [ReR -ImR
#          ImR  ReR]    
        B1 = Rreal[0:M, 0:M]
        B2 = Rreal[M:(2*M), 0:M]
        B3 = Rreal[0:M, M:(2*M)]
        B4 = Rreal[M:(2*M), M:(2*M)]
        rho = cp.Variable(1+M**2, 1, 'rho')

        constraints = [] # the list of the constraint equations and inequations
        constraints.append(0 <= rho[0])
        k   = 1
        for q in range(M):
            for p in range(M):
                if p == q:
                    constraints.append(rho[k] == B1[p, q])
                    k += 1
                elif p > q:
                    constraints.append(rho[k] == B1[p, q])
                    k += 1
                    constraints.append(rho[k] == B2[p, q])
                    k += 1
            
        constraints.append(B1 == B4)
        constraints.append(B1 == B1.T)
        constraints.append(B3 == -B2)
        constraints.append(B3 == -B3.T)
        
        constraints.extend([B1[k,k]==1 for k in range(M)])


        objective   = cp.Minimize(cp.quad_form(rho, self.__Gamma))

#objective = cp.Minimize(cp.norm(R))
#objective = quad_form()

        problem     = cp.Problem(objective, constraints)
        self.__problem  = problem
        self.__ReR      = B1
        self.__ImR      = B2
#problem.solve()



#R = (B1.value + 1j * B2.value).todense()
#print complexR
#savemat('complexR.mat', {'R':complexR})
#pattern = corrmtx2pattern(R, angles)
#plot(angles, pattern)
#hold(True)
#plot(angles, idealp, 'r')
