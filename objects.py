# needs x,y coordinates and probably IDs
from enum import Enum
import numpy as np

class NeuronType(Enum):
    INHIBITORY = 0
    EXCITATORY = 1
    
class Neuron:
    def __init__(self, x, y, id, neuron_type: NeuronType):
        self.id = id
        self.type = neuron_type
        
        self.x = x
        self.y = y
        
        #Izhikevich Modell (a=0.1, b=0.2, c=-65.0, d=2.0)
        self.v = -65.0
        self.u = 0.0

        self.calcium_level = 0
        self.tau_ca = 10000.0
        self.beta = 0.001

        #Ein exzitatorisches Neuron kann nur exzitatorische Stecker bilden, 
        #ein inhibitorisches Neuron nur inhibitorische Stecker.
        
        #Jedes Neuron (egal ob es selbst erregend oder hemmend ist) kann diese exzitatorischen Steckdosen ausbilden, 
        #um erregende Signale von anderen Neuronen zu empfangen.

        #Jedes Neuron (egal ob es selbst erregend oder hemmend ist) kann diese inhebitorische Steckdosen ausbilden, 
        #um erregende Signale von anderen Neuronen zu empfangen.

        #Das sind die Zähler für die absolute Gesamtmenge an synaptischen Elementen, die dieses Neuron aktuell besitzt.
        self.A = 0.0    #Axonale Elemente (Boutons)
        self.D_ex = 0.0 #Exzitatorische dendritische Elemente (Spines)
        self.D_in = 0.0 #Inhibitorische dendritische Elemente
        

        # Vakanzen (Ungebundene Elemente, die für neue Synapsen bereitstehen)
        self.vac_A = 0
        self.vac_D_ex = 0
        self.vac_D_in = 0

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
    
        

class Network:
    def __init__(self, num_neurons: int):
        self.neurons = []
        self.num_neurons = num_neurons
        self.C = np.zeros((num_neurons, num_neurons), dtype=int)
        self.K = np.zeros(num_neurons, num_neurons)







