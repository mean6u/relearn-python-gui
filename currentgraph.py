from objects import Network
# class which manages every aspect of the current graph (neurons, synapses, transitions, ...) 
class currentgraph():
    def __init__(self, neuron_count: int):
        network = Network(neuron_count)
        self.neurons = network.neurons