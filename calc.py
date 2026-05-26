import scipy
import numpy as np
import matplotlib.pyplot as plt


def step_electrical(self, I: float, dt:float = 1.0) -> bool:
    #I = I^{ext} + I^{syn}
    dv_dt = 0.04*self.v**2 + 5*self.v + 140 - self.u + I

    du_dt = 0.1*(0.2*self.v - self.u)

    self.v += dv_dt*dt
    self.u += du_dt*dt

    has_spiked = False

    if self.v >= 30.0:
        self.v = -65.0
        self.u += 2.0
        self.calcium_level += -self.calcium_level/self.tau_ca + self.beta

    return has_spiked
    
def step_calcium(self, dt: float = 1.0):
    dCa_dt = -(self.calcium_level/self.tau_ca)
    self.calcium_level += dCa_dt*dt

def calculate_growth_rate(self, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
    xi_z = (eta + epsilon)/2
    zeta_z = (eta + epsilon)/(2*(-np.log(1/2)))

    dz_dt = v*(2*np.exp(-((self.calcium_level - xi_z)/zeta_z))**2 - 1)
    return dz_dt

def update_structural_elements(self, dt: float = 100.0):

    dA_dt = self.calculate_growth_rate(eta=0.4)    
    dD_ex_dt = self.calculate_growth_rate(eta=0.1) 
    dD_in_dt = self.calculate_growth_rate(eta=0.1) 

    self.A += dA_dt * dt
    self.D_ex += dD_ex_dt * dt
    self.D_in += dD_in_dt * dt