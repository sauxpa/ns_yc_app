import numpy as np
import scipy
from scipy import optimize

class NelsonSiegel():
    def __init__(self,
                 b0=0.0,
                 b1=0.0,
                 b2=0.0,
                 tau=1.0
                ):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.tau = tau
        self.constraints = dict()

    def ytm(self, t):
        return self.ytm_NS(t, self.b0, self.b1, self.b2, self.tau)

    def ytm_NS(self, t, b0, b1, b2, tau):
        return b0 \
    + b1 * (1-np.exp(-t/tau)) / (t/tau) \
    + b2 * ((1-np.exp(-t/tau))/(t/tau) + np.exp(-t/tau))

    def constraints_func(self, params):
        errors = []
        for t, y in self.constraints.items():
            errors.append(
                (self.ytm_NS(t, params[0], params[1], params[2], params[3]) - y) ** 2
            )
        return errors

    def calibrate(self, constraints):
        """constraints: dict of (maturity, yield)
        """
        params_init = [0.0, 0.0, 0.0, 1.0]
        self.constraints = constraints
        sol = scipy.optimize.root(self.constraints_func, params_init, method='lm')

        if sol.success:
            params = sol.x
            self.b0 = params[0]
            self.b1 = params[1]
            self.b2 = params[2]
            self.tau = params[3]
        else:
            raise Exception('Cannot fit yield curve')
