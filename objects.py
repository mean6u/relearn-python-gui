# needs x,y coordinates and probably IDs
from enum import Enum
import numpy as np
import calc

class NeuronType(Enum):
    INHIBITORY = 0
    EXCITATORY = 1
    
class Neuron:
    def __init__(self, x, y, id, neuron_type: NeuronType):
        # Unique id and type (exhibitory or inhibitory)
        self.id = id
        self.type = neuron_type

        # Synapses the neuron posseses
        self.synapses = []
        
        # Position of neuron
        self.x = x
        self.y = y
        
        #TODO add explanation 
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
        self.A = 0.0    # Axonale Elemente 
        self.D_ex = 0.0 # Exzitatorische dendritische Elemente
        self.D_in = 0.0 # Inhibitorische dendritische Elemente
        

        # Vakanzen (Ungebundene Elemente, die für neue Synapsen bereitstehen)
        self.vac_A = 0
        self.vac_D_ex = 0
        self.vac_D_in = 0

        # Akkumulatoren für deterministischen Verfall (Equ. 5)
        self.decay_acc_A = 0.0
        self.decay_acc_D_ex = 0.0
        self.decay_acc_D_in = 0.0

        # TODO gebundene Elemente nur in Matrix (self.C in Network)?

    def get_id(self):
        return self.id
    
    def get_coordinates(self):
        return (self.x,self.y)
    
    def get_type(self):
        return self.type

    # should maybe be divided into "inward" and "outward" synapses
    def get_synapses(self):
        return self.synapses

    # TODO import calc.py and use its formula

    def step_electrical(self, I: float, dt:float = 1.0) -> bool:
        return calc.step_electrical(self, I, dt)
    
    def step_calcium(self, dt: float = 1.0):
        calc.step_calcium(self, dt)

    def calculate_growth_rate(self, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
        return calc.calculate_growth_rate(self, eta, epsilon, v)

    def update_structural_elements(self, dt: float = 100.0):
        calc.update_structural_elements(self, dt)
    
        

class Synapse:
    def __init__(self, from_neuron: Neuron, to_neuron: Neuron, weight, id:int = 0):
        self.source_neuron = from_neuron
        self.goal_neuron = to_neuron
        self.weight = weight
        self.id = id

class Network:
    def __init__(self, num_neurons: int, excitatory_probability: float = 0.8, inhibitory_probability: float = 0.2, exact_percentage: bool = True):
        self.neurons = []
        self.excitatory = []
        self.inhibitory = []
        self.num_neurons = num_neurons

        types = [NeuronType.INHIBITORY, NeuronType.EXCITATORY]
        probabilities = [inhibitory_probability, excitatory_probability]
        # types = [NeuronType.EXCITATORY, NeuronType.INHIBITORY]
        neuron_types = np.zeros(num_neurons)
        num_ex = -1
        if exact_percentage:
            num_ex = round(excitatory_probability * num_neurons)
            neuron_types[:num_ex] = 1
            neuron_types[num_ex:] = 0
        else:
            probabilities = [excitatory_probability, inhibitory_probability]
            neuron_types = np.random.choice(types, size=num_neurons, p=probabilities)
            num_ex = neuron_types.count(NeuronType.EXCITATORY)

        neuron_types.sort()
        # TODO Distribute inhibitory neurons among excitatory ones (“within limits of excitatory”)
        # TODO Comply to guidelines regarding excitatory / inhibitory spacing (see discord screenshot)
        # TODO 
        for i in range(num_neurons):
            x = np.random.randint(-100, 100)
            y = np.random.randint(-100, 100)
            type = neuron_types[i]
            _temp = Neuron(x, y, i, type)
            self.neurons.append(_temp)
            #_temp ist ein pointer der auf die erstelten Objekte zeit
            if type == NeuronType.EXCITATORY:
                self.excitatory.append(_temp)
            else:
                self.inhibitory.append(_temp)

        # Extremes of x and y ([x_min, x_max, y_min, y_max])
        extremes = [100, -100, 100, -100]
        # Distributing excitatory neurons
        for i in range(num_ex):
            x = np.random.randint(-100, 100)
            y = np.random.randint(-100, 100)
            if x < extremes[0]:
                x_min = x
            if x > extremes[1]:
                x_max = x
            if y < extremes[2]:
                y_min = y
            if y > extremes[3]:
                y_max = y
            self.neurons.append(Neuron(x, y, i, NeuronType.EXCITATORY))
        
        # Distributing inhibitory neurons
        for i in range(num_ex, num_neurons):
            x = np.random.randint(extremes[0], extremes[1])
            y = np.random.randint(extremes[2], extremes[3])
        

        # Probability Kernel
        self.K = np.zeros((num_neurons, num_neurons), dtype=float)
        # functions as "from-to graph", entry equals count of synapses from this neuron to the other one
        # TODO matrix of boolean values / 0s and 1s?
        self.synapses = np.zeros((num_neurons, num_neurons), dtype=int)

    def get_neurons(self):
        return self.neurons
    
    def get_excitatory_neurons(self):
        return self.excitatory
    
    def get_inhibitory_neurons(self):
        return self.inhibitory
    
    def get_neuron_count(self):
        return self.num_neurons
    
    def get_synapses(self):
        return self.synapses
    
    # should maybe only add 1 to the current value?
    def update_synapses(self, x: int, y: int, value):
        self.synapses[x, y] += value

    # 
    def reset_synapse(self, x: int, y: int):
        self.synapses[x, y] = 0
        