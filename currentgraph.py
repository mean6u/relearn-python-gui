from objects import Network
import numpy as np
import calc
# class which manages every aspect of the current graph (neurons, synapses, transitions, ...) 
class currentgraph():
    def __init__(self, neuron_count: int, excitatory_probability: float = 0.8, inhibitory_probability: float = 0.2, exact_percentage: bool = True):
        self.network = Network(neuron_count, excitatory_probability, inhibitory_probability, exact_percentage)
        self.neurons = self.network.neurons


    

    def generate_synaptic_positions(self, neuron, axon_count, exc_count, inh_count, radius = 6):
        ax_x = []
        ax_y = []

        exc_x = []
        exc_y = []

        inh_x = []
        inh_y = []

        total_count = (axon_count + exc_count + inh_count)

        remaining_ax = axon_count
        remaining_exc = exc_count
        remaining_inh = inh_count


        if total_count == 0:
            return (ax_x, ax_y,
                    exc_x, exc_y,
                    inh_x, inh_y)


        # Random Rotation Offset
        offset = np.random.uniform(0, 2 * np.pi)


        # Angles for Synaptic Elements of one Neuron
        angles = np.linspace(offset, offset + 2*np.pi, total_count, endpoint=False)

        axon_angles = []

        exc_angles = []

        inh_angles = []

        # Split Angles between Synapse Types

        i = 0

        while i < total_count:
            if (remaining_ax > 0):
                axon_angles.append(angles[i])
                i += 1
                remaining_ax -= 1

            if (i < total_count and remaining_exc > 0):
                exc_angles.append(angles[i])
                i += 1
                remaining_exc -= 1
            
            if (i < total_count and remaining_inh > 0):
                inh_angles.append(angles[i])
                i += 1
                remaining_inh -= 1


        for angle in axon_angles:

            x = neuron.x + np.cos(angle) * radius
            y = neuron.y + np.sin(angle) * radius

            ax_x.append(x)
            ax_y.append(y)


        for angle in exc_angles:

            x = neuron.x + np.cos(angle) * radius
            y = neuron.y + np.sin(angle) * radius

            exc_x.append(x)
            exc_y.append(y)


        for angle in inh_angles:

            x = neuron.x + np.cos(angle) * radius
            y = neuron.y + np.sin(angle) * radius

            inh_x.append(x)
            inh_y.append(y)

        return (ax_x, ax_y,
                exc_x, exc_y,
                inh_x, inh_y)



    def update_synaptic_elements(self):
        all_ax_x = []
        all_ax_y = []
        
        all_exc_x = []
        all_exc_y = []

        all_inh_x = []
        all_inh_y = []

        for neuron in self.neurons:
            axon_count = int(neuron.vac_A)
            exc_count = int(neuron.vac_D_ex)
            inh_count = int(neuron.vac_D_in)

            (ax_x, ax_y,
             exc_x, exc_y,
             inh_x, inh_y) = self.generate_synaptic_positions(neuron, axon_count, exc_count, inh_count, 12)

            all_ax_x.extend(ax_x)
            all_ax_y.extend(ax_y)

            all_exc_x.extend(exc_x)
            all_exc_y.extend(exc_y)

            all_inh_x.extend(inh_x)
            all_inh_y.extend(inh_y)
        
        return (all_ax_x, all_ax_y,
                all_exc_x, all_exc_y,
                all_inh_x, all_inh_y)

    def update_slow_processes(self, steps):
        for _ in range(steps):
            calc.structural_plasticity_step(self.network)
        
    def update_fast_processes(self, steps):
        for _ in range(steps):
            calc.electrical_activity_step(self.network)