from enum import Enum
import numpy as np
import calc

class NeuronType(Enum):
    """Enum for neuron types"""
    INHIBITORY = 0
    EXCITATORY = 1
    
class Neuron:
    """Class representing a neuron in the network"""
    def __init__(self, x, y, id, neuron_type: NeuronType):
        self.id = id
        self.type = neuron_type

        self.x = x
        self.y = y
        
        self.v = -65.0  
        self.u = 0.0    

        self.calcium_level = 0  
        self.beta = 0.001      

        # Structural elements
        self.A = 0.0    
        self.D_ex = 0.0 
        self.D_in = 0.0 
        
        self.vac_A = 0     
        self.vac_D_ex = 0   
        self.vac_D_in = 0   

        # Decay accumulators for structural elements
        self.decay_acc_A = 0.0
        self.decay_acc_D_ex = 0.0
        self.decay_acc_D_in = 0.0
        
    def get_id(self):
        """returns the id of the neuron"""
        return self.id
    
    def get_coordinates(self):
        """returns the coordinates of the neuron"""
        return (self.x, self.y)
    
    def get_type(self):
        """returns the type of the neuron"""
        return self.type
    
    def step_electrical(self, I: float, dt:float = 1.0) -> bool:
        return calc.step_electrical(self, I, dt)
    
    def step_calcium(self, dt: float = 1.0):
        calc.step_calcium(self, dt)

    def calculate_growth_rate(self, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
        return calc.calculate_growth_rate(self, eta, epsilon, v)

    def update_structural_elements(self, bound_A: int, bound_D_ex: int, bound_D_in: int, dt: float = 100.0):
        return calc.update_structural_elements(self, bound_A, bound_D_ex, bound_D_in, dt)
    
    def is_excitatory(self):
        """returns True if the neuron is excitatory, False otherwise"""
        return self.type == NeuronType.EXCITATORY
    
    def is_inhibitory(self):
        """returns True if the neuron is inhibitory, False otherwise"""
        return self.type == NeuronType.INHIBITORY

class Network:
    """Class representing a network of neurons"""
    def __init__(self, num_neurons: int, excitatory_probability: float = 0.8, inhibitory_probability: float = 0.2, exact_percentage: bool = True):
        self.neurons = []
        self.num_neurons = num_neurons

        # Parameters for GUI controls
        self.v = 0.0001
        self.I_ext_mean = 5.0
        self.epsilon = 0.7       
        self.tau_ca = 10000.0    
        self.sigma = 750.0
        self.eta_A = 0.4
        self.eta_D = 0.1
        self.k = 1.0

        # Synaptic current array rpresenting the total synaptic input current for each neuron
        self.I_syn = np.zeros(num_neurons, dtype=float) 

        # Caches for excitatory and inhibitory neuron types
        self._is_excitatory_cache = np.zeros(num_neurons, dtype=bool)
        self._is_inhibitory_cache = np.zeros(num_neurons, dtype=bool)

        types = [NeuronType.INHIBITORY, NeuronType.EXCITATORY]
        probabilities = [inhibitory_probability, excitatory_probability]
        
        if exact_percentage:
            num_ex = round(excitatory_probability * num_neurons)
        else:
            neuron_types = np.random.choice(types, size=num_neurons, p=probabilities)
            num_ex = np.sum(neuron_types == NeuronType.EXCITATORY) 

        dynamic_size = 15*num_neurons
        extremes = [dynamic_size, -dynamic_size, dynamic_size, -dynamic_size]

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
            self._is_excitatory_cache[i] = True
        
        # Distributing inhibitory neurons
        for i in range(num_ex, num_neurons):
            x, y = list(remaining_coordinates)[np.random.choice(len(remaining_coordinates))]

            for dx in range(-20, 20):
                for dy in range(-20, 20):
                    remaining_coordinates.discard((x + dx, y + dy))

            neuron: Neuron = Neuron(x, y, i, NeuronType.INHIBITORY)
            self.neurons.append(neuron)
            self._is_inhibitory_cache[i] = True
                
        # Synapses are represented as a 2D array where the value at (i, j) represents the number of synapses from neuron i to neuron j
        self.synapses = np.zeros((num_neurons, num_neurons), dtype=int)
        self.kernel = self.calculate_distance_kernel(sigma=self.sigma)

    def get_neurons(self):
        """returns the list of neurons in the network"""
        return self.neurons
        
    def get_neuron_count(self):
        """returns the number of neurons in the network"""
        return self.num_neurons
    
    def get_synapses(self):
        """returns the list of synapses in the network"""
        return self.synapses
    
    def get_neuron_by_index(self, index: int):
        """returns the neuron at the given index"""
        return self.neurons[index]
    

    def get_amount_of_incoming_synapses(self, neuron_index: int):
        """returns the number of incoming synapses for a given neuron"""
        return self.synapses[:, neuron_index]
    
    def get_amount_of_synapses(self, from_index: int, to_index: int):
        """returns the number of synapses from a given neuron to another"""
        return self.synapses[from_index, to_index]
    
    def get_amount_of_outgoing_synapses(self, neuron_index: int):
        """returns the number of outgoing synapses for a given neuron"""
        return self.synapses[neuron_index, :]
    
    def get_outgoing_synapse_list(self, neuron_index: int) -> list[int]:
        """returns a list of neuron indices that the given neuron has outgoing synapses to"""
        counts = self.get_amount_of_outgoing_synapses(neuron_index)
        return np.repeat(np.arange(self.num_neurons), counts).tolist()

    def get_incoming_synapse_list(self, neuron_index: int) -> list[int]:
        """returns a list of neuron indices that have incoming synapses to the given neuron"""
        counts = self.get_amount_of_incoming_synapses(neuron_index)
        return np.repeat(np.arange(self.num_neurons), counts).tolist()

    def get_incoming_excitatory_source_list(self, neuron_index: int) -> list[int]:
        """returns a list of neuron indices that have incoming excitatory synapses to the given neuron"""
        counts = self.get_amount_of_incoming_synapses(neuron_index)
        ex_counts = counts * self._is_excitatory_cache
        return np.repeat(np.arange(self.num_neurons), ex_counts).tolist()

    def get_incoming_inhibitory_source_list(self, neuron_index: int) -> list[int]:
        """returns a list of neuron indices that have incoming inhibitory synapses to the given neuron"""
        counts = self.get_amount_of_incoming_synapses(neuron_index)
        in_counts = counts * self._is_inhibitory_cache
        return np.repeat(np.arange(self.num_neurons), in_counts).tolist()

    def get_amount_of_bound_dendrites(self, neuron_index: int) -> tuple[int, int]:
        """returns the number of bound dendrites for a given neuron"""
        in_counts = self.get_amount_of_incoming_synapses(neuron_index)
        bound_d_ex = np.sum(in_counts[self._is_excitatory_cache])
        bound_d_in = np.sum(in_counts[self._is_inhibitory_cache])
        return bound_d_ex, bound_d_in
    
    def get_amount_of_bound_axons(self, neuron_index: int) -> int:
        """returns the number of bound axons for a given neuron"""
        bound_a = np.sum(self.get_amount_of_outgoing_synapses(neuron_index))
        return bound_a
    
    def update_synapses(self, _from: int | np.ndarray, to: int | np.ndarray, change_value: int):
        """updates the number of synapses from a given neuron to another"""
        self.synapses[_from, to] += change_value

        # Converting “from” and “to” list to arrays
        from_iter = np.atleast_1d(_from)
        to_iter = np.atleast_1d(to)
        
        # Update vacant counter variable of the respective neurons
        for from_idx, to_idx in zip(from_iter, to_iter):
            sender = self.neurons[from_idx]
            receiver = self.neurons[to_idx]

            # Update for sender
            sender.vac_A -= change_value

            # Update for receiver
            if sender.is_excitatory():
                receiver.vac_D_ex -= change_value
            else:
                receiver.vac_D_in -= change_value

    def calculate_distance_kernel(self, sigma: float = 5.0 * 150.0):
        return calc.calculate_distance_kernel(self, sigma)
        
    def structural_plasticity_step(self):
        calc.structural_plasticity_step(self)
    
    def get_connection_indices(self):
        """returns the (from, to) index of all synapses"""
        return np.argwhere(self.synapses != 0)
    
    def get_undirected_connection_indices(self):
        """returns the (from, to) index of all synapses, but only one direction"""
        combined_matrix = self.synapses + self.synapses.T
        upper_triangle = np.triu(combined_matrix, k=1)
        return np.argwhere(upper_triangle != 0)