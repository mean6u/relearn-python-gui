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
    
    # -100.0 als absoluter Tiefpunkt, 35.0 als Obergrenze (knapp über Spike-Schwelle).
    neuron.v = max(-100.0, min(neuron.v, 35.0))

    has_spiked = False

    if neuron.v >= 30.0:
        neuron.v = -65.0
        neuron.u += 2.0
        neuron.calcium_level += neuron.beta
        has_spiked = True

    return has_spiked
    
def step_calcium(neuron, tau_ca: float = 10000.0, dt: float = 1.0):
    """Eq. 3"""
    dCa_dt = -(neuron.calcium_level / tau_ca)
    neuron.calcium_level += dCa_dt*dt

def calculate_growth_rate(neuron, eta: float, epsilon: float = 0.7, v: float = 0.0001) -> float:
    """The growth rate of synaptic elements is given by the Gaussian function in Eq. 4, where $eta_z$ is the optimal calcium level for growth and $epsilon_z$ determines the width of the Gaussian curve."""
    xi_z = (eta + epsilon)/2
    zeta_z = (eta - epsilon) / (2 * np.sqrt(-np.log(0.5)))

    dz_dt = v*(2.0*np.exp(-((neuron.calcium_level - xi_z)/zeta_z)**2) - 1.0)
    return dz_dt




def update_structural_elements(neuron, bound_A: int, bound_D_ex: int, bound_D_in: int, v: float, epsilon: float, eta_A: float = 0.4, eta_D: float = 0.1, dt: float = 100.0):
    """
    This method models the slow processes.
    """

    #The value of $\eta_z$ depends on the type of synaptic element 
    #Because $\eta_D = 0.1$ and $\eta_A = 0.4$ lead to network recovery, we compare the results
    #obtained with these values with the experimental data.
  
    neuron.A = max(0.0, neuron.A + calculate_growth_rate(neuron, eta=eta_A, epsilon=epsilon,v=v) * dt)
    neuron.D_ex = max(0.0, neuron.D_ex + calculate_growth_rate(neuron, eta=eta_D, epsilon=epsilon, v=v) * dt)
    neuron.D_in = max(0.0, neuron.D_in + calculate_growth_rate(neuron, eta=eta_D, epsilon=epsilon, v=v) * dt)
    
   # neuron.A += max(0.0, calculate_growth_rate(neuron, eta=0.4) * dt)
    #neuron.D_ex += max(0, calculate_growth_rate(neuron, eta=0.1) * dt)
    #neuron.D_in += max(0.0, calculate_growth_rate(neuron, eta=0.1) * dt)

    #In the numerical integration, $A_j$, $D_i^{ex}$ and $D_i^{in}$ are treated as continuous variables, 
    #but when synaptic elements are deleted or used for synapse formation, the values of $A_j$, $D_i^{ex}$ and $D_i^{in}$ 
    #are rounded off to their smallest integer values.""""

    new_A = int(neuron.A)
    new_D_ex = int(neuron.D_ex)
    new_D_in = int(neuron.D_in)

    #Equ. 8: 
    #Vakanzen dürfen nicht negativ werden
    neuron.vac_A = max(0, new_A - bound_A)
    neuron.vac_D_ex = max(0, new_D_ex - bound_D_ex)
    neuron.vac_D_in =  max(0, new_D_in - bound_D_in)

    #Equ. 5: Deterministischer Zerfall ungenutzter Vakanzen
    tau_vac = 10.0

    # Axonal update
    if neuron.vac_A > 0:
        neuron.decay_acc_A += neuron.vac_A / tau_vac
        decayed = int(neuron.decay_acc_A)
        #if abrage eigentlich nicht nötig aber trozdem vorhanden aus performanze gründen
        if decayed > 0:
            #decay_acc_A (und auch decay_acc_D_ex, decay_acc_D_in) muss um den Anteil der Elemente reduziert werden, die in diesem schritt verfallen,
            #da sonst im nächsten Schritt wieder die gleiche Anzahl an Elementen verfallen würde, 
            #obwohl sie schon verfallen sind. 
            neuron.decay_acc_A -= decayed 
            neuron.A -= decayed
            neuron.vac_A -= decayed

    

    # Dendritic excitatory update
    if neuron.vac_D_ex > 0:
        neuron.decay_acc_D_ex += neuron.vac_D_ex / tau_vac
        decayed = int(neuron.decay_acc_D_ex)
        if decayed > 0:
            neuron.decay_acc_D_ex -= decayed
            neuron.D_ex -= decayed
            neuron.vac_D_ex -= decayed

    # Dendritic inhibitory update
    if neuron.vac_D_in > 0:
        neuron.decay_acc_D_in += neuron.vac_D_in / tau_vac
        decayed = int(neuron.decay_acc_D_in)
        if decayed > 0:
            neuron.decay_acc_D_in -= decayed
            neuron.D_in -= decayed
            neuron.vac_D_in -= decayed

    
    #For example, if neuron j had previously 100 axonal elements bound in 100 outgoing
    #synapses [...] and $A_j$ decreased to e.g. 95.32 due to Eq. 4, $A_j$ is rounded off to 95 and 
    #consequently neuron j has to delete $\Delta A_j$ outgoing synapses at the next update in connectivity.

    # Deltas berechnen. Wie viele gebundenen Synapsen müssen abgebaut werden
    # Das passiert, wenn die neue Gesamtanzahl unter die bereits gebundenen fällt.
    delta_A = max(0, bound_A - new_A)
    delta_D_ex = max(0, bound_D_ex - new_D_ex)
    delta_D_in = max(0, bound_D_in - new_D_in)
    
    return delta_A, delta_D_ex, delta_D_in

# TODO change all occurrences of sigma to 5.0 * 150 * 10^-6? Because it's micrometers
def calculate_kernel_value(neuron_out, neuron_in, sigma: float = 5.0 * 150.0):
    dist_sq = (neuron_out.x - neuron_in.x)**2 + (neuron_out.y - neuron_in.y)**2
    return math.exp(-dist_sq / sigma**2)


def calculate_distance_kernel(network, sigma: float = 5.0 * 150.0) -> np.ndarray[np.ndarray]:
    num_neurons = network.num_neurons
    value_matrix = np.zeros((num_neurons, num_neurons))
    for n_out in range(num_neurons):
        for n_in in range(num_neurons):
            if n_out == n_in:
                continue
            # dist_sq = (network.neurons[i].x - network.neurons[j].x)**2 + (network.neurons[i].y - network.neurons[j].y)**2
            # network.K[i, j] = math.exp(-dist_sq / sigma**2)
            value_matrix[n_out, n_in] = calculate_kernel_value(network.neurons[n_out], network.neurons[n_in], sigma)
    return value_matrix

def electrical_activity_step(network):
    """Fast process: Wird alle 1 ms aufgerufen."""
    #TODO soll über GUI veränderbar sein
    tau_m = 5.0

    network.I_syn *= np.exp(-1.0 / tau_m) # Exponentieller Spannungsabfall von allen Neuronen

    #Kappt extrem winzige Kommazahlen auf exakt 0.0 
    network.I_syn[np.abs(network.I_syn) < 1e-6] = 0.0
    # Es üs halt ein Giotto :/

    spiked_index = []
    for i, neuron in enumerate(network.neurons):
        #Hintergruund aktivität wird nach paiper so berechnet
        I_ext = np.random.normal(network.I_ext_mean, 1.0)
        I_total = I_ext + network.I_syn[i]

        #feuer frei!!!
        if step_electrical(neuron, I_total):
            spiked_index.append(i)
                     
        step_calcium(neuron, network.tau_ca)
        
    for i in spiked_index:
        neuron = network.get_neuron_by_index(i)
        voltage_change = 1.0 if neuron.is_excitatory() else -1.0
        outgoing_synapses_array = network.get_outgoing_synapses(i)
        network.I_syn += outgoing_synapses_array * voltage_change
        """
        #addiere auf auf alle rausgehenden neuronen die entsprechende spannung
        #TODO müssen wir die spannung noch gewichten???
        neuron = network.get_neuron_by_index(i)

        network.I_syn[network.get_outgoing_synapses(i)] += 1.0 if neuron.is_excitatory() else -1.0
        """

def execute_deletions(network, deletion_requests):

    for neuron_index, dA, dD_ex, dD_in in deletion_requests:
        neuron = network.get_neuron_by_index(neuron_index)

        #Axonale Löschungen (Das Neuron verliert ausgehende Stecker)
        if dA > 0:
            out_synapses = network.get_outgoing_synapse_list(neuron_index)
            bound_A = len(out_synapses)
            total_A = int(neuron.A) + dA  # Ursprüngliche Gesamtmenge vor dem Schrumpfen

            for _ in range(dA):
                if total_A <= 0: break
                probably_bound = bound_A / total_A  
                if random.random() < probably_bound and bound_A > 0:
                    target_index = random.choice(out_synapses)
                    network.update_synapses(neuron_index, target_index, -1)
                    neuron.vac_A -= 1
                    out_synapses.remove(target_index)
                    bound_A -= 1
                total_A -= 1      
                

        #Exzitatorische Dendriten-Löschungen (Das Neuron verliert eingehende Verbindungen von exzitatorischen Quellen)
        if dD_ex > 0:
            excitatory_sources = network.get_incoming_excitatory_source_list(neuron_index)
            bound_D_ex = len(excitatory_sources)
            total_D_ex = int(neuron.D_ex) + dD_ex

            for _ in range(dD_ex):
                if total_D_ex <= 0: break
                prob_bound = bound_D_ex / total_D_ex
                if random.random() < prob_bound and bound_D_ex > 0:
                    source_index = random.choice(excitatory_sources)
                    network.update_synapses(source_index, neuron_index, -1)
                    neuron.vac_D_ex -= 1
                    excitatory_sources.remove(source_index)
                    bound_D_ex -= 1
                total_D_ex -= 1

        #Inhibitorische Dendriten-Löschungen (Das Neuron verliert eingehende Verbindungen von inhibitorischen Quellen)
        if dD_in > 0:
            inhibitory_sources = network.get_incoming_inhibitory_source_list(neuron_index)
            bound_D_in = len(inhibitory_sources)
            total_D_in = int(neuron.D_in) + dD_in

            for _ in range(dD_in):
                if total_D_in <= 0: break
                prob_bound = bound_D_in / total_D_in
                if random.random() < prob_bound and bound_D_in > 0:
                    source_index = random.choice(inhibitory_sources)
                    network.update_synapses(source_index, neuron_index, -1)
                    neuron.vac_D_in -= 1
                    inhibitory_sources.remove(source_index)
                    bound_D_in -= 1
                total_D_in -= 1
             

def structural_plasticity_step(network):
    # TODO Does not seem to work (few synaptic elements are created)
    """Slow process: Wird alle 100 ms aufgerufen."""
    # Deletion of synaptic elements?

    deletion_requests = []

    for neuron_index, neuron in enumerate(network.neurons):
        #Herausfinden, wie viele Elemente aktuell gebunden sind
        
        bound_A = np.sum(network.get_outgoing_synapses(neuron_index)) # Ausgehende Synapsen (Spalte i)
        bound_D_ex, bound_D_in = network.get_bound_dendrites(neuron_index)

        # Das Neuron aktualisieren
        delta_A, delta_D_ex, delta_D_in = update_structural_elements(neuron, bound_A, bound_D_ex, bound_D_in, network.v, network.epsilon, network.eta_A, network.eta_D)
        if delta_A > 0 or delta_D_ex > 0 or delta_D_in > 0:
            deletion_requests.append((neuron_index, delta_A, delta_D_ex, delta_D_in))
    

    execute_deletions(network, deletion_requests)
    create_random_connection(network)
    

    # Creation of new synapses (via assign_vacant_elements and check_assignment)
    #create_random_connection(network)

    

# Proposes synaptic connections among the neurons based on free synaptic elements of the respective neurons
def assign_vacant_elements(network) -> list:
    """
    # Takes a network and returns a list of tuples. A tuple for a synapse from neuron a to neuron b is (a, b).
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
    """
    # Takes a list of potential connections and returns a list of synapses to be established based on the euclidean distance.
"""
    actual_synapses: list = []
    for neuron_pair in assignments:
        outgoing, incoming = neuron_pair
        if random.uniform(0, 1) < network.kernel[outgoing, incoming]:
            actual_synapses.append(neuron_pair)
    return np.array(actual_synapses)


def create_random_connection(network):
    potential_synapses = assign_vacant_elements(network)
    assigments = check_assignment(network, potential_synapses)
    if len(assigments) == 0:
        return
    new_from, new_to = assigments.T
    network.update_synapses(new_from, new_to, 1)
