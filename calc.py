import math
import random
from typing import Tuple, List
import numpy as np

# from objects import NeuronType, Neuron


def step_electrical(neuron, I: float, dt:float = 1.0) -> bool:
    """
    Equation 1 and 2
    Calculates the membrane potential Izhikevich Modell (with dv_dt and du_dt)
    I describes the total electrical impulse a neuron receives? Impulses from other neurons and the background activity / noise?
    """

    """
    Each neuron receives input that comprises synaptic input I = I^ext + I^syn from other neurons in the network (horizontal input
    from adjacent and distant cortical neurons) and external input I^ext (vertical input from the eye via the thalamus).
    """
 
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
    
def step_calcium(neuron, dt: float = 1.0):
    """Eq. 3"""
    dCa_dt = -(neuron.calcium_level / neuron.tau_ca)
    neuron.calcium_level += dCa_dt*dt

def calculate_growth_rate(neuron, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
    """The growth rate of synaptic elements is given by the Gaussian function in Eq. 4, where $eta_z$ is the optimal calcium level for growth and $epsilon_z$ determines the width of the Gaussian curve."""
    xi_z = (eta + epsilon)/2
    zeta_z = (eta - epsilon) / (2 * np.sqrt(-np.log(0.5)))

    dz_dt = v*(2.0*np.exp(-((neuron.calcium_level - xi_z)/zeta_z)**2) - 1.0)
    return dz_dt




def update_structural_elements(neuron, bound_A: int, bound_D_ex: int, bound_D_in: int, dt: float = 100.0) -> Tuple[float, float, float]:
    """
    This method models the slow processes.
    """
    #In the numerical integration, $A_j$, $D_i^{ex}$ and $D_i^{in}$ are treated as continuous variables, 
    #but when synaptic elements are deleted or used for synapse formation, the values of $A_j$, $D_i^{ex}$ and $D_i^{in}$ 
    #are rounded off to their smallest integer values.""""
    old_A = int(neuron.A)
    old_D_ex = int(neuron.D_ex)
    old_D_in = int(neuron.D_in)

    #The value of $\eta_z$ depends on the type of synaptic element 
    #Because $\eta_D = 0.1$ and $\eta_A = 0.4$ lead to network recovery, we compare the results
    #obtained with these values with the experimental data.
  
    neuron.A += calculate_growth_rate(neuron, eta=0.4) * dt
    neuron.D_ex += calculate_growth_rate(neuron, eta=0.1) * dt
    neuron.D_in += calculate_growth_rate(neuron, eta=0.1) * dt


    #Equ. 8: 
    vac_A = old_A - bound_A
    vac_D_ex = old_D_ex - bound_D_ex
    vac_D_in = old_D_in - bound_D_in

    #Equ. 5: Deterministischer Zerfall ungenutzter Vakanzen
    tau_vac = 10.0  
    if vac_A > 0:
        neuron.decay_acc_A += vac_A / tau_vac
        decayed = int(neuron.decay_acc_A)
        if decayed > 0:
            neuron.decay_acc_A -= decayed
            neuron.A -= decayed

    if vac_D_ex > 0:
        neuron.decay_acc_D_ex += vac_D_ex / tau_vac
        decayed = int(neuron.decay_acc_D_ex)
        if decayed > 0:
            neuron.decay_acc_D_ex -= decayed
            neuron.D_ex -= decayed

    if vac_D_in > 0:
        neuron.decay_acc_D_in += vac_D_in / tau_vac
        decayed = int(neuron.decay_acc_D_in)
        if decayed > 0:
            neuron.decay_acc_D_in -= decayed
            neuron.D_in -= decayed

    
    #For example, if neuron j had previously 100 axonal elements bound in 100 outgoing
    #synapses [...] and $A_j$ decreased to e.g. 95.32 due to Eq. 4, $A_j$ is rounded off to 95 and 
    #consequently neuron j has to delete $\Delta A_j$ outgoing synapses at the next update in connectivity.
    delta_A = int(neuron.A) - old_A
    delta_D_ex = int(neuron.D_ex) - old_D_ex
    delta_D_in = int(neuron.D_in) - old_D_in
    
    return delta_A, delta_D_ex, delta_D_in

# TODO change all occurrences of sigma to 5.0 * 150 * 10^-6? Because it's micrometers
def calculate_kernel_value(neuron_out, neuron_in, sigma: float = 5.0 * 150.0):
    dist_sq = (neuron_out.x - neuron_in.x)**2 + (neuron_out.y - neuron_in.y)**2
    return math.exp(-dist_sq / sigma**2)


def calculate_distance_kernel(network, sigma: float = 5.0 * 150.0):
    """Equ 9"""
    num_neurons = network.num_neurons
    for i in range(num_neurons):
        for j in range(num_neurons):
            if i == j:
                continue
            # dist_sq = (network.neurons[i].x - network.neurons[j].x)**2 + (network.neurons[i].y - network.neurons[j].y)**2
            # network.K[i, j] = math.exp(-dist_sq / sigma**2)
            network.K[i, j] = calculate_kernel_value(network.neurons[i], network.neurons[j], sigma)


def structural_plasticity_step(network):
    """Slow process: Wird alle 100 ms aufgerufen."""
    # Deletion of synaptic elements?
    deletions = []

    for i, neuron in enumerate(network.neurons):
        #Herausfinden, wie viele Elemente aktuell gebunden sind
        bound_A = np.sum(network.get_outgoing_synapses(i)) # Ausgehende Synapsen (Spalte i)
        bound_D_ex = np.sum(int(network.is_excitatory(i)) * network.get_incoming_synapses(i)) # Eingehend von exzitatorischen
        bound_D_in = np.sum(int(network.is_inhibitory(i)) * network.get_incoming_synapses(i)) # Eingehend von inhibitorischen

            # Das Neuron aktualisieren
        deltas = update_structural_elements(neuron, bound_A, bound_D_ex, bound_D_in)
            
            #Abbau-Aufträge merken
        if any(val > 0 for val in deltas):
            deletions.append((i, deltas))

    # den tatsächlichen Abbau im Netzwerk durchführen
    network.execute_deletions(deletions)

    all_vacA = []
    all_D_ex = []
    all_D_in = []
    for i, neuron in enumerate(network.neurons):
        #Herausfinden, wie viele Elemente aktuell gebunden sind
        bound_A = np.sum(network.get_outgoing_synapses(i)) # Ausgehende Synapsen (Spalte i)
        bound_D_ex = np.sum(int(network.is_excitatory(i)) * network.get_incoming_synapses(i)) # Eingehend von exzitatorischen
        bound_D_in = np.sum(int(network.is_inhibitory(i)) * network.get_incoming_synapses(i)) # Eingehend von inhibitorischen

            # Das Neuron aktualisieren
        deltas = update_structural_elements(neuron, bound_A, bound_D_ex, bound_D_in)
            
            #Abbau-Aufträge merken
        if any(val > 0 for val in deltas):
            deletions.append((i, deltas))
        
    # TODO Add creation of new synapses (via assign_vacant_elements and check_assignment)
    

# Calculates synaptic connections among the neurons based on free synaptic elements and the
# euclidean distance of the respective neurons
def assign_vacant_elements(network) -> list:
    """
    Takes a network and returns a list of tuples. A tuple for a synapse from neuron a to neuron b is (a, b).
    """
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
    while sums["axonal excitatory"] != 0 and sums["dendritic excitatory"] != 0:
        # Find random, vacant, excitatory axonal element and the respective neuron
        chosen_axonal_element: int = random.randint(0, sums["axonal excitatory"] - 1)
        for neuron_index in range(len(free_a_ex)):
            chosen_axonal_element -= free_a_ex[neuron_index]
            if chosen_axonal_element < 1:
                # We got the neuron index (stored in axonal_neuron_index)
                axonal_neuron_index = neuron_index
                break
        # Find random, vacant, excitatory dendritic element and the respective neuron
        chosen_dendritic_element: int = random.randint(0, sums["dendritic excitatory"] - 1)
        for neuron_index in range(len(free_d_ex)):
            chosen_dendritic_element -= free_d_ex[neuron_index]
            if chosen_dendritic_element < 1:
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
    while sums["axonal inhibitory"] != 0 and sums["dendritic inhibitory"] != 0:
        # Find random, vacant, inhibitory axonal element and the respective neuron
        chosen_axonal_element: int = random.randint(0, sums["axonal inhibitory"] - 1)
        for neuron_index in range(len(free_a_ex)):
            chosen_axonal_element -= free_a_ex[neuron_index]
            if chosen_axonal_element < 1:
                # We got the neuron index (stored in axonal_neuron_index)
                axonal_neuron_index = neuron_index
                break
        # Find random, vacant, inhibitory dendritic element and the respective neuron
        chosen_dendritic_element: int = random.randint(0, sums["dendritic inhibitory"] - 1)
        for neuron_index in range(len(free_d_ex)):
            chosen_dendritic_element -= free_d_ex[neuron_index]
            if chosen_dendritic_element < 1:
                # We got the neuron index (stored in dendritic_neuron_index)
                dendritic_neuron_index = neuron_index
                break
        # Adding connection to list
        assigned_inhibitory.append((axonal_neuron_index, dendritic_neuron_index))
        # Adjusting values
        free_a_ex[axonal_neuron_index] -= 1
        free_d_ex[dendritic_neuron_index] -= 1
        sums["axonal inhibitory"] -= 1
        sums["dendritic inhibitory"] -= 1

def check_assignment(assignments) -> list:
    """
    Takes a list of potential connections and returns a list of synapses to be established based on the euclidean distance.
    """
    actual_synapses: list = []
    for neuron_pair in assignments:
        outgoing, incoming = neuron_pair
        if random.uniform(0, 1) < calculate_kernel_value(outgoing, incoming):
            actual_synapses.append(neuron_pair)
    return actual_synapses