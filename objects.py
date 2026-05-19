# needs x,y coordinates and probably IDs
class Neuron:
    def __init__(self, calcium_level: float, dendritic: list, axonal: list, inhibitory: bool,):
        self.calcium_level = calcium_level
        # List of dendritic and axonal elements belonging to the neuron
        self.dendritic = dendritic
        self.axonal = axonal
        self.inhibitory = inhibitory


# needs x,y coordinates and probably IDs/attribute which links it to its neuron
class SynapticElement:
    def __init__(self, dendritic: bool, inhibitory: bool, connection: list):
        self.dendritic = dendritic
        self.inhibitory = inhibitory
        # List of connected synaptic elements (should be 0 or 1)
        self.connection = connection
