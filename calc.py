import math
from typing import Tuple

import scipy
import numpy as np
import matplotlib.pyplot as plt


def step_electrical(self, I: float, dt:float = 1.0) -> bool:
    """Eq. 1/2"""
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
    """Eq. 3"""
    dCa_dt = -(self.calcium_level/self.tau_ca)
    self.calcium_level += dCa_dt*dt

def calculate_growth_rate(self, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
    """The growth rate of synaptic elements is given by the Gaussian function in Eq. 4, where $\eta_z$ is the optimal calcium level for growth and $\epsilon_z$ determines the width of the Gaussian curve."""
    xi_z = (eta + epsilon)/2
    zeta_z = (eta + epsilon)/(2*(-np.log(1/2)))

    dz_dt = v*(2*np.exp(-((self.calcium_level - xi_z)/zeta_z))**2 - 1)
    return dz_dt




def update_structural_elements(self, bound_A: int, bound_D_ex: int, bound_D_in: int, dt: float = 100.0) -> Tuple[float, float, float]:

    #In the numerical integration, $A_j$, $D_i^{ex}$ and $D_i^{in}$ are treated as continuous variables, 
    #but when synaptic elements are deleted or used for synapse formation, the values of $A_j$, $D_i^{ex}$ and $D_i^{in}$ 
    #are rounded off to their smallest integer values.""""
    old_A = math.floor(self.A)
    old_D_ex = math.floor(self.D_ex)
    old_D_in = math.floor(self.D_in)

    #The value of $\eta_z$ depends on the type of synaptic element 
    #Because $\eta_D = 0.1$ and $\eta_A = 0.4$ lead to network recovery, we compare the results
    #obtained with these values with the experimental data.
  
    self.A += self.calculate_growth_rate(self.calcium_level, eta=0.4) * dt
    self.D_ex += self.calculate_growth_rate(self.calcium_level, eta=0.1) * dt
    self.D_in += self.calculate_growth_rate(self.calcium_level, eta=0.1) * dt


    #For example, if neuron j had previously 100 axonal elements bound in 100 outgoing
    #synapses [...] and $A_j$ decreased to e.g. 95.32 due to Eq. 4, $A_j$ is rounded off to 95 and 
    #consequently neuron j has to delete $\Delta A_j$ outgoing synapses at the next update in connectivity.


    #Vacant synaptic elements may come from an increase in synaptic elements due to the activity-dependent growth rules (Eq. 4)...
    if delta_A > 0:
        self.vac_A += delta_A
    if delta_D_ex > 0:
        self.vac_D_ex += delta_D_ex
    if delta_D_in > 0:
        self.vac_D_in += delta_D_in



    #TODO: Gleichung 5 implementieren | Synaptic elements that are not bound in a synapse
    # (vacant elements) decay with time constant  $\tau_{vac} = 10$ connectivity updates.

    delta_A = math.floor(self.A) - old_A
    delta_D_ex = math.floor(self.D_ex) - old_D_ex
    delta_D_in = math.floor(self.D_in) - old_D_in
    
    return delta_A, delta_D_ex, delta_D_in


def calculate_distance_kernel(self, K, neurons, num_neurons: int, sigma: float = 5.0 * 150.0):
        """
        Equ 9:
        """
        
        for i in range(num_neurons):
            for j in range(num_neurons):
                if i == j:
                    continue
                    
                
                dist_sq = (neurons[i].x - neurons[j].x)**2 + (neurons[i].y - neurons[j].y)**2
                # Kernel K_ij berechnen
                K[i, j] = math.exp(-dist_sq / sigma**2)