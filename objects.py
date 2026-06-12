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

        # Position of neuron
        self.x = x
        self.y = y
        
        #Izhikevich Modell (a=0.1, b=0.2, c=-65.0, d=2.0)
        self.v = -65.0  # Membrane potential
        self.u = 0.0    # Membrane recovery variable

        self.calcium_level = 0  # Calcium level of neuron
        self.tau_ca = 10000.0   # Decay time of calcium level (decreases exponentially to zero)
        self.beta = 0.001       # Increase in calcium every time the neuron fires

        #Ein exzitatorisches Neuron kann nur exzitatorische Stecker bilden, 
        #ein inhibitorisches Neuron nur inhibitorische Stecker.
        
        #Jedes Neuron (egal ob es selbst erregend oder hemmend ist) kann diese exzitatorischen Steckdosen ausbilden, 
        #um erregende Signale von anderen Neuronen zu empfangen.

        #Jedes Neuron (egal ob es selbst erregend oder hemmend ist) kann diese inhebitorische Steckdosen ausbilden, 
        #um erregende Signale von anderen Neuronen zu empfangen.

        #Das sind die Zähler für die absolute Gesamtmenge an synaptischen Elementen, die dieses Neuron aktuell besitzt.
        self.A = 0.0    # Axonal elements
        self.D_ex = 0.0 # Dendritic elements (excitatory)
        self.D_in = 0.0 # Dendritic elements (inhibitory)
        

        # Vakanzen (Ungebundene Elemente, die für neue Synapsen bereitstehen)
        self.vac_A = 0      # Axonal elements
        self.vac_D_ex = 0   # Dendritic elements (excitatory)
        self.vac_D_in = 0   # Dendritic elements (inhibitory)

        # Akkumulatoren für deterministischen Verfall (Paper Eq. 5)
        # Nu (“v”): Growth factor (is set to 0.001 in the paper)
        # z_i: Number of synaptic elements of a neuron (not explicitly computed)
        # dz_i / dt: Growth rate of synaptic elements (calculated by multiplying nu with term that depends on calcium level)

        self.decay_acc_A = 0.0
        self.decay_acc_D_ex = 0.0
        self.decay_acc_D_in = 0.0
        
        #gesamte mänge anliegender Spannung
        

    def get_id(self):
        return self.id
    
    def get_coordinates(self):
        return (self.x, self.y)
    
    def get_type(self):
        return self.type

    # TODO import calc.py and use its formula

    def step_electrical(self, I: float, dt:float = 1.0) -> bool:
        return calc.step_electrical(self, I, dt)
    
    def step_calcium(self, dt: float = 1.0):
        calc.step_calcium(self, dt)

    def calculate_growth_rate(self, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
        return calc.calculate_growth_rate(self, eta, epsilon, v)

    def update_structural_elements(self, bound_A: int, bound_D_ex: int, bound_D_in: int, dt: float = 100.0):
        return calc.update_structural_elements(self, bound_A, bound_D_ex, bound_D_in, dt)
    
    def is_excitatory(self):
        return self.type == NeuronType.EXCITATORY
    
    def is_inhibitory(self):
        return self.type == NeuronType.INHIBITORY
    
        

class Synapse:
    def __init__(self, from_neuron: Neuron, to_neuron: Neuron, weight, id:int = 0):
        self.source_neuron = from_neuron
        self.goal_neuron = to_neuron
        self.weight = weight
        self.id = id

class Network:
    def __init__(self, num_neurons: int, excitatory_probability: float = 0.8, inhibitory_probability: float = 0.2, exact_percentage: bool = True, sigma_dist: float = 5.0 * 150.0):
        self.neurons = []
        self.excitatory = []
        self.inhibitory = []
        self.num_neurons = num_neurons

        #gesamt anliegende spannung aller Neuronen
        self.I_syn = np.zeros(num_neurons, dtype=float) 


        types = [0, 1]
        probabilities = [inhibitory_probability, excitatory_probability]
        # types = [NeuronType.EXCITATORY, NeuronType.INHIBITORY]

        # was previously a float array (without dtype=int)
        neuron_types = np.zeros(num_neurons, dtype=int)
        num_ex = -1
        if exact_percentage:
            num_ex = round(excitatory_probability * num_neurons)
            neuron_types[:num_ex] = 1 # crashed with Enum Types -> therefore used int values instead
            neuron_types[num_ex:] = 0 # same here
        else:
            probabilities = [excitatory_probability, inhibitory_probability]
            neuron_types = np.random.choice(types, size=num_neurons, p=probabilities)
            num_ex = np.sum(neuron_types == 1) # numpy summing = more efficient (ig)

        neuron_types.sort()
        
        # TODO Distribute inhibitory neurons among excitatory ones (“within limits of excitatory”)
        # TODO Comply to guidelines regarding excitatory / inhibitory spacing (see discord screenshot)
        """
        From the paper: Excitatory neurons were placed with a spatial variance of on a 20×16 grid with
        a distance between two grid points of . More precisely, the x,y-coordinates of each neuron were
        derived from a normal distribution (with the chosen spatial variance as standard deviation) that
        was centered at an individual grid point. For the 80 inhibitory neurons we defined a second 10×8
        grid positioned in such a way that the inhibitory neurons become equally distributed among the
        excitatory ones; the precise x,y coordinates were determined as was done for the excitatory neurons.
        Given that neurons in the adult cortex of rodents [54] are capable of rewiring their axonal branches
        over a couple of hundred micrometers, the expected distance between neurons of in the model is a
        plausible choice.
        """
        """
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
        """

        # Extremes of x and y ([x_min, x_max, y_min, y_max])
        extremes = [150, -150, 150, -150]

        # Building a collision avoiding grid to store remaining coordinates
        remaining_x = np.arange(extremes[1], extremes[0] + 1)
        remaining_y = np.arange(extremes[1], extremes[0] + 1)

        X,Y = np.meshgrid(remaining_x, remaining_y)

        coordinates = np.stack([X.ravel(), Y.ravel()], axis=-1)
        remaining_coordinates = set(tuple(c) for c in coordinates)

        # Distributing excitatory neurons
        for i in range(num_ex):
            x, y = list(remaining_coordinates)[np.random.choice(len(remaining_coordinates))]
            if x < extremes[0]:
                extremes[0] = x
            if x > extremes[1]:
                extremes[1] = x
            if y < extremes[2]:
                extremes[2] = y
            if y > extremes[3]:
                extremes[3] = y
            
            for dx in range(-20, 20):
                for dy in range(-20, 20):
                    remaining_coordinates.discard((x + dx, y + dy))
            
            neuron: Neuron = Neuron(x, y, i, NeuronType.EXCITATORY)
            self.neurons.append(neuron)
            self.excitatory.append(neuron)
        
        # Distributing inhibitory neurons
        for i in range(num_ex, num_neurons):
            x, y = list(remaining_coordinates)[np.random.choice(len(remaining_coordinates))]

            for dx in range(-20, 20):
                for dy in range(-20, 20):
                    remaining_coordinates.discard((x + dx, y + dy))

            neuron: Neuron = Neuron(x, y, i, NeuronType.INHIBITORY)
            self.neurons.append(neuron)
            self.inhibitory.append(neuron)
        

        # Probability Kernel
        self.K = np.zeros((num_neurons, num_neurons), dtype=float)
        # functions as "from-to graph", entry equals count of synapses from this neuron to the other one
        

        self.synapses = np.zeros((num_neurons, num_neurons), dtype=bool)
        self.kernel = calc.calculate_distance_kernel(self, sigma=sigma_dist)


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
    
    def get_neuron_by_index(self, index: int):
        return self.neurons[index]
    

    def get_outgoing_synapses(self, neuron_index: int):
        return self.synapses[:, neuron_index]
    
    def get_incoming_synapses(self, neuron_index: int):
        return self.synapses[neuron_index, :]
    
    
    # should maybe only add 1 to the current value?
    def update_synapses(self, x: int, y: int, value):
        self.synapses[x, y] += value

    def reset_synapse(self, x: int, y: int):
        self.synapses[x, y] = 0
        
    def calculate_distance_kernel(self, sigma: float = 5.0 * 150.0):
        calc.calculate_distance_kernel(self, sigma)
        
    def structural_plasticity_step(self):
        calc.structural_plasticity_step(self)
    

    
    def get_connection_indices(self):
        """returns the (from, to) index of all synapses"""
        return np.argwhere(self.synapses)
        
        

        


        