from objects import Network
# class which manages every aspect of the current graph (neurons, synapses, transitions, ...) 
class currentgraph():
    def __init__(self, neuron_count: int, excitatory_probability: float = 0.8, inhibitory_probability: float = 0.2, exact_percentage: bool = True):
        network = Network(neuron_count, excitatory_probability, inhibitory_probability, exact_percentage)
        self.neurons = network.neurons