import numpy as np
from nlp.ls.pymswolfe import StrongWolfeLineSearch

class CG(object):
    """
    Class CGFramework provides a framework for solving unconstrained
    optimization problems by conjugate gradient with different search 
    lines methods
    """
    def __init__(self, model):
        """
        Conjuguate gradient for non linear unconstraint problem 
        """

        self.model = model
        if self.model.m > 0 :
            raise TypeError('This method only works on unconstrained problems')
        
        self.x = kwargs.get("x0", np.copy(model.x0))
        self.f = self.model.obj(self.x)
        self.g = self.model.grad(self.x)
        self.gNorm = np.linalg.norm(self.g)
        self.strategy = kwargs.get("strategy", 'HZ') 
        self.p = -self.g.copy()
        self.cos0 =  np.dot(self.g,self.p)/(self.gNorm*np.linalg.norm(self.p))                              

        self.k = 0
        self.etol = kwargs.get("etol", 1.0e-5)
        self.itermax = kwargs.get("itermax", 10000)

    def solve(self, strategy= None):

        if strategy is not None:
            self.strategy = strategy

        while self.gNorm > self.etol and self.k < self.itermax:
            
            # Search step with Strong Wolfe
            
            SWLS = StrongWolfeLineSearch(self.f,
                                         self.x,
                                         self.g,
                                         self.p,
                                         lambda t: self.model.obj(t),
                                         lambda t: self.model.grad(t),
                                         gtol= 0.1,
                                         ftol = 1.0e-4)
            SWLS.search()
        
            
            if (np.mod(self.k,10)==0):
                print"---------------------------------------"
                print "iter   f       ‖∇f‖    step    cosθ"
                print"---------------------------------------"
            print "%2d  %9.2e  %7.1e %6.4f %9.6f " % (self.k, self.f, self.gNorm, SWLS.stp,self.cos0)
            #Seach line search
            self.x += SWLS.stp * self.p
        
            New_gk = self.model.grad(self.x)
            y = New_gk - self.g

            if self.strategy == 'HZ':
                bk = self.strategy_HZ(New_gk, y)
            elif self.strategy =='FR':
                bk = self.strategy_FR(New_gk)
            elif self.strategy == 'PR':
                bk = self.strategy_PR(New_gk, y)
            elif self.strategy == 'PR+':
                bk = self.strategy_PR_Plus(New_gk, y)
            elif self.strategy == 'PR-FR':
                bk = self.strategy_PR_FR(New_gk, y)
            else:
                raise Exception ('Check your strategy name, used help if you need')

            self.p = -New_gk + bk * self.p
            self.f = self.model.obj(self.x)
            self.g = New_gk
            self.gNorm = np.linalg.norm(self.g)
            self.cos0 =  np.dot(self.g,self.p)/(self.gNorm*np.linalg.norm(self.p)) 
            self.k += 1

        return self.x

    def strategy_FR(self, gk) :
        """
        Flectcher and Reeves strategy 
        """

        return np.dot(gk,gk)/np.dot(self.g, self.g)
   
    def strategy_PR(self, gk, yk):
        """
        Polak and Ribiere strategy
        """

        bk = np.dot(gk, yk)/np.dot(self.g,self.g)
        return bk
   
    def strategy_PR_Plus(self, gk, yk):
        """
        Polak and Ribiere + strategy
        """
            
        bk = self.strategy_PR(gk,yk)
        return max(bk,0)

    def strategy_PR_FR(self, gk, yk):
        """ Mixed between Polak and Ribiere
        and Flectcher and Reeves strategy """
              
        bk_PR = self.strategy_PR(gk,yk)
        bk_FR = self.strategy_FR(gk)
        
        #Check bk
        if bk_PR < -bk_FR:
            return -bk_FR
        elif abs(bk_PR) <= bk_FR:
            return bk_PR
        elif bk_PR > bk_FR:
            return bk_FR

    def strategy_HZ(self, gk, yk, n=0.01):
        """ 
        Hager and Zhang line search 
        """

        nk = -1./(np.linalg.norm(self.p)*min(n, np.linalg.norm(self.g)))
        pk_yk = np.dot(self.p,yk)
        bnk= 1./pk_yk * np.dot(yk - 2.*self.p*np.linalg.norm(yk)/pk_yk, gk)
        return max(bnk, nk)                            
