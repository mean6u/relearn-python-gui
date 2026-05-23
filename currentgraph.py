import objects
# class which manages every aspect of the current graph (neurons, synapses, transitions, ...) 
class currentgraph():
    def __init__(self, neuron_count: int):
        network = objects.Network(neuron_count)