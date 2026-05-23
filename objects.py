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

        self.synapses = []
        
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

class Synapse:
    def __init__(self, from_neuron: Neuron, to_neuron: Neuron, weight, id:int = 0):
        self.source_neuron = from_neuron
        self.goal_neuron = to_neuron
        self.weight = weight
        self.id = id

class Network:
    def __init__(self, num_neurons: int):
        self.neurons = []
        self.num_neurons = num_neurons
        for i in range(0, num_neurons):
            x = np.random.randint(-10, 10)
            y = np.random.randint(-10, 10)
            type = np.random.randint(0,1)
            self.neurons.append(Neuron(x,y,i,type))
        self.C = np.zeros((num_neurons, num_neurons), dtype=int)
        self.K = np.zeros(num_neurons, num_neurons) # funktioniert nicht oder?
        self.synapses = np.zeros((num_neurons, num_neurons), dtype=int) # functions as "from-to graph", entry equals count of synapses from this neuron to the other one







