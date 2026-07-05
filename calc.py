import math
import random
from typing import Tuple, List
import numpy as np

def step_electrical(neuron, I: float, dt:float = 1.0) -> bool:
    """updates the electrical activity of a neuron based on the Izhikevich model. 
    Returns True if the neuron spikes."""
 
    #Izhikevich Modell (a=0.1, b=0.2, c=-65.0, d=2.0)

    dv_dt = 0.04*neuron.v**2 + 5*neuron.v + 140 - neuron.u + I
    du_dt = 0.1*(0.2*neuron.v - neuron.u)

    neuron.v += dv_dt*dt
    neuron.u += du_dt*dt
    
    has_spiked = False
    if neuron.v >= 30.0:
        neuron.v = -65.0
        neuron.u += 2.0
        neuron.calcium_level += neuron.beta
        has_spiked = True

    return has_spiked
    
def step_calcium(neuron, tau_ca: float = 10000.0, dt: float = 1.0):
    """Updates the calcium level of a neuron"""

    dCa_dt = -(neuron.calcium_level / tau_ca)
    neuron.calcium_level += dCa_dt*dt

def calculate_growth_rate(neuron, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
    """Calculates the growth rate of synaptic elements.
    Returns the growth rate of synaptic elements."""

    xi_z = (eta + epsilon)/2
    zeta_z = (eta - epsilon) / (2 * np.sqrt(-np.log(0.5)))

    # Avoid division by zero
    if abs(zeta_z) < 1e-12:
        zeta_z = 1e-12

    dz_dt = v * (2.0 * np.exp(-((neuron.calcium_level - xi_z)/zeta_z)**2) - 1.0)
    return dz_dt

def update_structural_elements(neuron, bound_A: int, bound_D_ex: int, bound_D_in: int, v: float, epsilon: float, eta_A: float = 0.4, eta_D: float = 0.1, dt: float = 100.0):
    """Updates the structural elements of a neuron.
    Returns the number of synaptic elements to be deleted."""

    #Update the structural elements based on the growth rate. 
    #max is used to ensure that the number of synaptic elements does not go below zero.
    neuron.A = max(0.0, neuron.A + calculate_growth_rate(neuron, eta=eta_A, epsilon=epsilon,v=v) * dt)
    neuron.D_ex = max(0.0, neuron.D_ex + calculate_growth_rate(neuron, eta=eta_D, epsilon=epsilon, v=v) * dt)
    neuron.D_in = max(0.0, neuron.D_in + calculate_growth_rate(neuron, eta=eta_D, epsilon=epsilon, v=v) * dt)
    
    #Calculates the absolute number of synaptic elements
    new_A = int(neuron.A)
    new_D_ex = int(neuron.D_ex)
    new_D_in = int(neuron.D_in)

    #Updates the number of vacant synaptic elements based on the number of bound synaptic elements. 
    #max is used to ensure that the number of vacant synaptic elements does not go below zero.
    neuron.vac_A = max(0, new_A - bound_A)
    neuron.vac_D_ex = max(0, new_D_ex - bound_D_ex)
    neuron.vac_D_in =  max(0, new_D_in - bound_D_in)

    tau_vac = 10.0

    #Axonal update
    if neuron.vac_A > 0:
        neuron.decay_acc_A += neuron.vac_A / tau_vac
        decayed = int(neuron.decay_acc_A)
        if decayed > 0:
            neuron.decay_acc_A -= decayed 
            neuron.A -= decayed
            neuron.vac_A -= decayed

    #Dendritic excitatory update
    if neuron.vac_D_ex > 0:
        neuron.decay_acc_D_ex += neuron.vac_D_ex / tau_vac
        decayed = int(neuron.decay_acc_D_ex)
        if decayed > 0:
            neuron.decay_acc_D_ex -= decayed
            neuron.D_ex -= decayed
            neuron.vac_D_ex -= decayed

    #Dendritic inhibitory update
    if neuron.vac_D_in > 0:
        neuron.decay_acc_D_in += neuron.vac_D_in / tau_vac
        decayed = int(neuron.decay_acc_D_in)
        if decayed > 0:
            neuron.decay_acc_D_in -= decayed
            neuron.D_in -= decayed
            neuron.vac_D_in -= decayed

    #Calculates the number of synaptic elements to be deleted based on the difference between the bound and new synaptic elements.
    delta_A = max(0, bound_A - new_A)
    delta_D_ex = max(0, bound_D_ex - new_D_ex)
    delta_D_in = max(0, bound_D_in - new_D_in)
    return delta_A, delta_D_ex, delta_D_in

def calculate_kernel_value(neuron_out, neuron_in, sigma: float = 5.0 * 150.0):
    """Returns the kernel value based on the euclidean distance between the two neurons."""

    dist_sq = (neuron_out.x - neuron_in.x)**2 + (neuron_out.y - neuron_in.y)**2
    return math.exp(-dist_sq / sigma**2)


def calculate_distance_kernel(network, sigma: float = 5.0 * 150.0) -> np.ndarray[np.ndarray]:
    """Calculates the distance kernel for the network"""

    num_neurons = network.num_neurons
    value_matrix = np.zeros((num_neurons, num_neurons))
    for n_out in range(num_neurons):
        for n_in in range(num_neurons):
            if n_out == n_in:
                continue
            value_matrix[n_out, n_in] = calculate_kernel_value(network.neurons[n_out], network.neurons[n_in], sigma)
    return value_matrix

def electrical_activity_step(network):
    """Updates the electrical activity of all neurons in the network for one time step.
    This includes updating the membrane potential and calcium level of each neuron."""

    spiked_index = []

    tau_m = 5.0
    network.I_syn *= np.exp(-1.0 / tau_m) 

    for i, neuron in enumerate(network.neurons):
        I_ext = np.random.normal(network.I_ext_mean, 1.0)
        I_total = I_ext + network.k * network.I_syn[i]

        #feuer frei!!!
        if step_electrical(neuron, I_total):
            spiked_index.append(i)
                     
        step_calcium(neuron, network.tau_ca)
        
    for i in spiked_index:
        neuron = network.get_neuron_by_index(i)
        voltage_change = 1.0 if neuron.is_excitatory() else -1.0
        outgoing_synapses_array = network.get_amount_of_outgoing_synapses(i)
        network.I_syn += outgoing_synapses_array * voltage_change
    return spiked_index

def execute_deletions(network, deletion_requests):
    """Executes the deletion of synaptic elements based on the deletion requests.
    Each deletion request is a tuple of (neuron_index, delta_A, delta_D_ex, delta_D_in)""" 

    for neuron_index, dA, dD_ex, dD_in in deletion_requests:
        neuron = network.get_neuron_by_index(neuron_index)
        if dA > 0:
            out_synapses = network.get_outgoing_synapse_list(neuron_index)
            bound_A = len(out_synapses)
            total_A = int(neuron.A) + dA  

            for _ in range(dA):
                if total_A <= 0: break
                probably_bound = bound_A / total_A  
                if random.random() < probably_bound and bound_A > 0:
                    target_index = random.choice(out_synapses)
                    network.update_synapses(neuron_index, target_index, -1)
                    target_neuron = network.get_neuron_by_index(target_index)
                    if neuron.is_excitatory: 
                        target_neuron.vac_D_ex += 1
                    else:
                        target_neuron.vac_D_in += 1
                    neuron.A -= 1
                    out_synapses.remove(target_index)
                    bound_A -= 1
                total_A -= 1      
                
        if dD_ex > 0:
            excitatory_sources = network.get_incoming_excitatory_source_list(neuron_index)
            bound_D_ex = len(excitatory_sources)
            total_D_ex = int(neuron.D_ex) + dD_ex

            for _ in range(dD_ex):
                if total_D_ex <= 0: break
                probably_bound = bound_D_ex / total_D_ex
                if random.random() < probably_bound and bound_D_ex > 0:
                    source_index = random.choice(excitatory_sources)
                    network.update_synapses(source_index, neuron_index, -1)
                    source_neuron = network.get_neuron_by_index(source_index)
                    source_neuron.vac_A += 1
                    neuron.D_ex -= 1
                    excitatory_sources.remove(source_index)
                    bound_D_ex -= 1
                total_D_ex -= 1

        if dD_in > 0:
            inhibitory_sources = network.get_incoming_inhibitory_source_list(neuron_index)
            bound_D_in = len(inhibitory_sources)
            total_D_in = int(neuron.D_in) + dD_in

            for _ in range(dD_in):
                if total_D_in <= 0: break
                probably_bound = bound_D_in / total_D_in
                if random.random() < probably_bound and bound_D_in > 0:
                    source_index = random.choice(inhibitory_sources)
                    network.update_synapses(source_index, neuron_index, -1)
                    source_neuron = network.get_neuron_by_index(source_index)
                    source_neuron.vac_A += 1
                    neuron.D_in -= 1
                    inhibitory_sources.remove(source_index)
                    bound_D_in -= 1
                total_D_in -= 1
             

def structural_plasticity_step(network):
    """Updates the structural plasticity of all neurons in the network for 100 time step.
    This includes updating the number of synaptic elements executing deletions and creating new connections"""

    deletion_requests = []

    for neuron_index, neuron in enumerate(network.neurons):
        bound_A = network.get_amount_of_bound_axons(neuron_index)
        bound_D_ex, bound_D_in = network.get_amount_of_bound_dendrites(neuron_index)
        delta_A, delta_D_ex, delta_D_in = update_structural_elements(neuron, bound_A, bound_D_ex, bound_D_in, network.v, network.epsilon, network.eta_A, network.eta_D)
        deletion_requests.append((neuron_index, delta_A, delta_D_ex, delta_D_in))
    
    execute_deletions(network, deletion_requests)
    create_random_connection(network)
    

def assign_vacant_elements(network) -> list:
    """Assigns vacant synaptic elements to create potential connections between neurons.
    Returns a list of tuples representing the potential connections (outgoing_neuron, incoming_neuron)."""

    # Storing the free synaptic elements for each neuron (index i is the respective number of free element for the i-th neuron)
    free_a_ex = [neuron.vac_A if neuron.is_excitatory() else 0 
                 for neuron in network.neurons]
    free_a_in = [neuron.vac_A if neuron.is_inhibitory() else 0
                 for neuron in network.neurons]
    free_d_ex = [neuron.vac_D_ex for neuron in network.neurons]
    free_d_in = [neuron.vac_D_in for neuron in network.neurons]

    # Storing the total number of axonal / dendritic excitatory / inhibitory elements in a dictionary (four elements)
    # TODO Make more efficient
    sums = {"axonal excitatory": sum(free_a_ex), "axonal inhibitory": sum(free_a_in) , "dendritic excitatory": sum(free_d_ex), "dendritic inhibitory": sum(free_d_in)}
    
    # Creating list of assigned elements: ([outgoing_neuron], [incoming_neuron])
    assigned_excitatory = []
    assigned_inhibitory = []

    # Assigning random elements
    # Assigning excitatory elements (axonal to dendritic)
    while sums["axonal excitatory"] > 0 and sums["dendritic excitatory"] > 0:
        # Find random, vacant, excitatory axonal element and the respective neuron
        chosen_axonal_element: int = random.randint(0, sums["axonal excitatory"] - 1)
        for neuron_index in range(len(free_a_ex)):
            chosen_axonal_element -= free_a_ex[neuron_index]
            if chosen_axonal_element < 0:
                # We got the neuron index (stored in axonal_neuron_index)
                axonal_neuron_index = neuron_index
                break
        # Find random, vacant, excitatory dendritic element and the respective neuron
        chosen_dendritic_element: int = random.randint(0, sums["dendritic excitatory"] - 1)
        for neuron_index in range(len(free_d_ex)):
            chosen_dendritic_element -= free_d_ex[neuron_index]
            if chosen_dendritic_element < 0:
                # We got the neuron index (stored in dendritic_neuron_index)
                dendritic_neuron_index = neuron_index
                break
        # Adding connection to list
        assigned_excitatory.append((axonal_neuron_index, dendritic_neuron_index))
        # Adjusting values
        free_a_ex[axonal_neuron_index] -= 1
        free_d_ex[dendritic_neuron_index] -= 1
        sums["axonal excitatory"] -= 1
        sums["dendritic excitatory"] -= 1
         
    # Assigning inhibitory elements (axonal to dendritic)
    while sums["axonal inhibitory"] > 0 and sums["dendritic inhibitory"] > 0:
        # Find random, vacant, inhibitory axonal element and the respective neuron
        chosen_axonal_element: int = random.randint(0, sums["axonal inhibitory"] - 1)
        for neuron_index in range(len(free_a_in)):
            chosen_axonal_element -= free_a_in[neuron_index]
            if chosen_axonal_element < 0:
                # We got the neuron index (stored in axonal_neuron_index)
                axonal_neuron_index = neuron_index
                break
        # Find random, vacant, inhibitory dendritic element and the respective neuron
        chosen_dendritic_element: int = random.randint(0, sums["dendritic inhibitory"] - 1)
        for neuron_index in range(len(free_d_in)):
            chosen_dendritic_element -= free_d_in[neuron_index]
            if chosen_dendritic_element < 0:
                # We got the neuron index (stored in dendritic_neuron_index)
                dendritic_neuron_index = neuron_index
                break
        # Adding connection to list
        assigned_inhibitory.append((axonal_neuron_index, dendritic_neuron_index))
        # Adjusting values
        free_a_in[axonal_neuron_index] -= 1
        free_d_in[dendritic_neuron_index] -= 1
        sums["axonal inhibitory"] -= 1
        sums["dendritic inhibitory"] -= 1
    
    total_neurons = assigned_excitatory + assigned_inhibitory
    return total_neurons


def check_assignment(network, assignments) -> list:
    """Checks the assigned synaptic elements against the distance kernel 
    Returns the actual synapses that will be created."""
    actual_synapses: list = []
    for neuron_pair in assignments:
        outgoing, incoming = neuron_pair
        if random.uniform(0, 1) < network.kernel[outgoing, incoming]:
            actual_synapses.append(neuron_pair)
    return np.array(actual_synapses)


def create_random_connection(network):
    """Creates a random connection between two neurons."""
    potential_synapses = assign_vacant_elements(network)
    assigments = check_assignment(network, potential_synapses)
    if len(assigments) == 0:
        return
    new_from, new_to = assigments.T
    network.update_synapses(new_from, new_to, 1)