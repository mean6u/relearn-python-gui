import objects
import calc

import unittest
import math
import numpy as np
from objects import Neuron, NeuronType, Network
import calc

class TestNeuronDynamics(unittest.TestCase):
    
    def setUp(self):
        """Wird vor jedem Test ausgeführt, um ein frisches Neuron zu erstellen."""
        self.neuron = Neuron(x=0.0, y=0.0, id=1, neuron_type=NeuronType.EXCITATORY)

    def test_resting_potential(self):
        """Testet, ob das Neuron ohne Input ruht und nicht spontan feuert."""
        spiked = self.neuron.step_electrical(I=0.0, dt=1.0)
        self.assertFalse(spiked)
        # Spannung sollte sich einpendeln/negativ bleiben
        self.assertTrue(self.neuron.v < 0.0)

    def test_spike_generation_and_calcium_influx(self):
        """Testet, ob ein starker Input zum Spike führt und Kalzium einströmt."""
        initial_calcium = self.neuron.calcium_level
        spiked = False
        
        # Simuliere 100ms mit starkem Input
        for _ in range(100):
            if self.neuron.step_electrical(I=15.0, dt=1.0):
                spiked = True
                break
            
        self.assertTrue(spiked, "Neuron sollte bei starkem Input feuern.")
        self.assertEqual(self.neuron.v, -65.0, "Spannung muss nach Spike auf -65.0 zurückgesetzt werden.")
        self.assertEqual(self.neuron.calcium_level, initial_calcium + self.neuron.beta, 
                         "Kalzium muss exakt um beta (0.001) steigen, wenn es feuert.")

    def test_calcium_decay(self):
        """Testet den exponentiellen Verfall von Kalzium."""
        self.neuron.calcium_level = 1.0 # Setze künstlich hohes Kalzium
        self.neuron.step_calcium(dt=1.0)
        
        self.assertTrue(self.neuron.calcium_level < 1.0, "Kalzium muss im Zeitverlauf abklingen.")
        self.assertTrue(self.neuron.calcium_level > 0.0, "Kalzium darf nicht sofort auf 0 fallen.")

    def test_growth_rate_math(self):
        """Testet die Gauß-Kurve für das Wachstum (Equ. 4)."""
        # Wenn Calcium 0 ist, muss das Wachstum negativ sein (Abbau)
        self.neuron.calcium_level = 0.0
        growth_zero_ca = self.neuron.calculate_growth_rate(eta=0.4)
        self.assertTrue(growth_zero_ca < 0.0, "Neuron ohne Aktivität muss Elemente abbauen.")
        
        # Wenn Calcium nahe am optimalen Bereich ist, muss Wachstum positiv sein
        self.neuron.calcium_level = 0.55 # Zwischen eta=0.4 und epsilon=0.7
        growth_opt_ca = self.neuron.calculate_growth_rate(eta=0.4)
        self.assertTrue(growth_opt_ca > 0.0, "Neuron in optimaler Aktivität muss wachsen.")

    def test_update_structural_elements_decay(self):
        """Testet den deterministischen Verfall von Vakanzen (Equ. 5 im Paper)."""
        # Wir geben dem Neuron 10 axonale Elemente
        self.neuron.A = 10.0 
        # Set-Point (0.7) -> Das Neuron ist perfekt ausbalanciert, es wächst und schrumpft nicht (Equ. 4 ist 0)
        self.neuron.calcium_level = 0.7 
        
        # Aufruf: 0 Elemente sind gebunden -> Das Neuron hat 10 freie Vakanzen (Equ. 8)
        # Bei tau_vac = 10.0 und 10 Vakanzen sollte pro Update exakt 1 Element verfallen
        # (vac_A / tau_vac = 10 / 10 = 1.0 -> math.floor(1.0) = 1)
        self.neuron.update_structural_elements(bound_A=0, bound_D_ex=0, bound_D_in=0, dt=100.0)
        
        self.assertEqual(self.neuron.A, 9.0, "Es sollte exakt 1 ungebundenes Element verfallen sein.")

    def test_update_structural_elements_growth(self):
        """Testet das kontinuierliche Wachstum der Variablen."""
        self.neuron.A = 5.0
        # Kalzium leicht unter dem Set-Point (z.B. 0.55), um Wachstum zu provozieren
        self.neuron.calcium_level = 0.55 
        
        # Aufruf: Alle 5 Elemente sind gebunden (0 Vakanzen -> kein spontaner Verfall)
        delta_A, _, _ = self.neuron.update_structural_elements(bound_A=5, bound_D_ex=0, bound_D_in=0, dt=100.0)
        
        # Die kontinuierliche Variable A muss nun größer sein als 5.0
        self.assertTrue(self.neuron.A > 5.0, "Die kontinuierliche Variable A muss durch das Wachstum steigen.")

    def test_update_structural_elements_deletion(self):
        """Testet, ob bei Inaktivität korrekte Abbau-Deltas (Löschaufträge) generiert werden."""
        self.neuron.A = 10.0
        # Kalzium auf 0.0 -> Extreme Inaktivität, das Neuron muss massiv schrumpfen
        self.neuron.calcium_level = 0.0 
        
        # Da das Wachstum sehr langsam ist (v=0.0001), simulieren wir so lange 100ms-Schritte,
        # bis das Neuron über die nächste ganze Zahl (9.0) abgerundet wird.
        delta_A = 0
        for _ in range(500): # Sicherheits-Limit, um Endlosschleifen zu vermeiden
            # Wir tun so, als ob alle 10 Elemente fest im Netzwerk verbaut sind
            delta_A, _, _ = self.neuron.update_structural_elements(bound_A=10, bound_D_ex=0, bound_D_in=0, dt=100.0)
            if delta_A < 0:
                break
                
        # Sobald self.A unter 10.0 fällt (z.B. 9.99), rundet math.floor auf 9 ab.
        # old_A war 10. Das Delta (9 - 10) muss also -1 sein.
        self.assertEqual(delta_A, -1, "Wenn das Neuron schrumpft, muss ein negatives Delta (-1) zurückgegeben werden.")
        self.assertTrue(self.neuron.A < 10.0, "Der absolute Zähler A muss geschrumpft sein.")
        
class TestNetworkTopology(unittest.TestCase):

    def setUp(self):
        """Erstellt ein kleines Netzwerk für schnelle Tests."""
        # Fixer Seed für reproduzierbare Tests
        np.random.seed(42)
        self.net = Network(num_neurons=100, excitatory_probability=0.8, exact_percentage=True)


    def test_distance_kernel(self):
        """Testet, ob die Wahrscheinlichkeitsmatrix logische Werte hat (Equ. 9)."""
        self.net.calculate_distance_kernel(sigma=150.0)
        
        # Diagonale muss 0 sein (kein Neuron verbindet sich mit sich selbst)
        for i in range(100):
            self.assertEqual(self.net.K[i, i], 0.0)
            
        # Generelle Wahrscheinlichkeiten müssen zwischen 0 und 1 liegen
        self.assertTrue(np.all((self.net.K >= 0.0) & (self.net.K <= 1.0)))

if __name__ == '__main__':
    unittest.main()