import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QStyleFactory
from PyQt6.QtCore import QObject, QThread, Qt, QTimer, pyqtSignal, pyqtSlot, QMutex
from PyQt6.QtGui import QPalette, QColor, QIcon, QIntValidator, QPainterPath
from currentgraph import currentgraph
from objects import NeuronType, Neuron
import time

# global variable for dark mode
dark_mode = True

# Settings for dark mode
def get_dark_palette():
    dark_palette = QPalette()
        
    # background colors
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
        
    # text and input
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        
    # accent colors
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215)) # Ein schönes Blau
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
    # placeholder
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(100, 100, 100))
    dark_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(100, 100, 100))

    return dark_palette

def get_white_palette():
    return QApplication.style().standardPalette()

class guilauncher(QMainWindow):
    def __init__(self):
        super().__init__()

        global dark_mode

        # Initializing window
        self.setWindowTitle("RELeARN - Launcher")
        self.resize(300, 125)
        self.setMaximumSize(300, 125)

        fusion_style = QStyleFactory.create("Fusion")
        if fusion_style:
            QApplication.instance().setStyle(fusion_style)

        # Setting dark mode as default
        if dark_mode:
            QApplication.instance().setPalette(get_dark_palette())
        else:
            QApplication.instance().setPalette(get_white_palette())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.setWindowIcon(QIcon('launch.png'))

        #neuron_layout = QHBoxLayout()
        #neuron_layout.addWidget(QLabel("Number of Neurons:"))
        #self.input_neurons = QLineEdit()
        #self.input_neurons.setPlaceholderText("100")
        #neuron_layout.addWidget(self.input_neurons)
        #layout.addLayout(neuron_layout)
        
        # doesn't toggle, just activates bad dark mode
        self.dark_mode_btn = QPushButton("Toggle Dark Mode")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.setChecked(dark_mode)
        self.dark_mode_btn.setMaximumSize(300, 50)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_btn)

        # Adding input fields for neurons and synapses
        self.add_line(layout, "Number of Neurons:", "input_neurons", "10", True)
        self.add_line(layout, "Percentage of excitatory Neurons (%):", "input_exc", "80", True)

        #self.add_line(layout, "Growth Rate", "input_growth", "1", True)

        # Adding buttons
        self.start_button = QPushButton("Start Simulation")
        self.start_button.setStyleSheet("background-color: green; color: black; font: bold 14px;")
        self.start_button.setMaximumSize(300, 50)
        # start implementing the connection logic
        self.start_button.clicked.connect(self.start_sim)
        layout.addWidget(self.start_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #A82424; color: black; font: bold 14px;")
        self.exit_button.setMaximumSize(300, 50)
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
    
    def add_line(self, goal_layout, label_text: str, attribute_name: str, default_val: str, horizontal: bool):
        if horizontal:
            new_layout = QHBoxLayout()
        else:
            new_layout = QVBoxLayout()
        new_label = QLabel(label_text)
        new_font = new_label.font()
        new_font.setBold(True)
        #new_font.setPointSize(14)
        new_label.setFont(new_font)
        new_layout.addWidget(new_label)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(default_val)
        input_field.setValidator(QIntValidator())
        setattr(self, attribute_name, input_field)

        input_field.setMaximumSize(300, 50)
        new_layout.addWidget(input_field)
        goal_layout.addLayout(new_layout)

        return input_field
    
    
    def handle_input(self):
        user_input_neurons = int(self.input_neurons.text() or self.input_neurons.placeholderText())
        user_input_excitatory = int(self.input_exc.text() or self.input_exc.placeholderText())

        #user_input_growth = int(self.input_growth.text() or self.input_growth.placeholderText())
        return user_input_neurons, user_input_excitatory

    # start implementing the connection logic
    def start_sim(self):
        input = self.handle_input()
        #print(output[0], output[1])
        self.sim_gui = simulation(dark_mode, input[0], input[1])
        self.sim_gui.show()
        self.close()


    # not toggling yet, just applying dark mode, default values become invisible :/
    def toggle_dark_mode(self, checked: bool):
        global dark_mode
        dark_mode = checked

        if checked:
            cur_palette = get_dark_palette()
        else:
            cur_palette = get_white_palette()

        QApplication.instance().setPalette(cur_palette)

class SimulationWorker(QObject):

    def __init__(self, graph, mutex):
        super().__init__()
        self.graph = graph
        self.mutex = mutex
        self._is_running = False
        self._is_paused = False
        self.time_counter = 0
        self.counter = 0
        self.speed_controle = 100

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while self._is_running:
            if self._is_paused:
                QThread.msleep(100)
                continue
            
            self.mutex.lock()
            self.time_counter += 1
            self.graph.update_fast_processes()

            if self.time_counter % 100 == 0:
                self.graph.update_slow_processes()
            self.mutex.unlock()

            if self.speed_controle > 0:

                wait_seconds = (self.speed_controle / 100.0) / 1000.0 
                target_time = time.perf_counter() + wait_seconds
                
                while time.perf_counter() < target_time:
                    QThread.yieldCurrentThread()
            else:
                pass
                #QThread.yieldCurrentThread()


    @pyqtSlot()
    def stop(self):
        """Stops the simulation loop."""
        self._is_running = False

    @pyqtSlot()
    def pause(self):
        self._is_paused = True

    @pyqtSlot()
    def resume(self):
        self._is_paused = False


class simulation(QMainWindow):
    def __init__(self, is_dark_mode: bool, neuron_count: int, exc_count: int):
        super().__init__()

        self.mutex = QMutex()

        # Initialising currentgraph
        # TODO Seems to fail when entering 500 for the number of neurons (in the launcher)
        self.graph = currentgraph(neuron_count, exc_count/100, (100-exc_count)/100)
        self.neurons = self.graph.neurons



        # Test
        # TODO Remove
        """for neuron in self.neurons:
            neuron.A = 4
            neuron.D_ex = 6
            neuron.D_in = 6

            neuron.vac_A = 4
            neuron.vac_D_ex = 6
            neuron.vac_D_in = 6
        """
        for neuron in self.neurons:
            neuron.A = 0
            neuron.D_ex = 0
            neuron.D_in = 0

            neuron.vac_A = 0
            neuron.vac_D_ex = 0
            neuron.vac_D_in = 0


        # Configs
        
        pg.setConfigOptions(antialias=True)
        
        self.setWindowTitle("RELeARN - Structural Plasiticity Simulation")
        self.resize(800, 600)

        self.setWindowIcon(QIcon('plasticity.jpg'))


        # Central Widget
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)


        # Plot

        self.plot_widget = pg.GraphicsLayoutWidget()

        if is_dark_mode:
            self.plot_widget.setBackground("#000000")
        else:
            self.plot_widget.setBackground("#ffffff")
        
        layout.addWidget(self.plot_widget)

        self.view = self.plot_widget.addViewBox()
        self.view.setAspectLocked(True)

        self.view.scene().sigMouseClicked.connect(self.on_view_clicked)

        # Neuron Layer
        
        self.network_graph = pg.GraphItem()
        self.synapse_lines = pg.GraphItem()
        self.calcium_text_item = None
        self.synapse_count_texts = []
        self.selected_neuron_index = None  
        self.network_graph.scatter.sigClicked.connect(self.on_neuron_clicked)

        self.view.addItem(self.network_graph)
        self.view.addItem(self.synapse_lines)


        # Synaptic Elements Layer

        # Excitatory Dendritic Spines
        self.ex_spines = pg.ScatterPlotItem(size=2, symbol='s', brush=(231, 76, 60), pen=None, pxMode=False)

        # Inhibitory Dendritic Spines
        self.in_spines = pg.ScatterPlotItem(size=2, symbol='s', brush=(46, 0, 213), pen=None, pxMode=False)

        # Axonal Boutons
        self.axons = pg.ScatterPlotItem(size=2, symbol='t', brush=(255, 255, 0), pen=None, pxMode=False)

        self.view.addItem(self.ex_spines)
        self.view.addItem(self.in_spines)
        self.view.addItem(self.axons)


        # Initial Render

        self.spawn_neurons()


        # Legend

        ex_neuron_symbol = pg.ScatterPlotItem(symbol = 'o', brush = (231, 76, 60), pen=None)
        in_neuron_symbol = pg.ScatterPlotItem(symbol = 'o', brush = (46, 0, 213), pen=None)


        legend = pg.LegendItem((80,60), offset=(0,0))
        legend.setParentItem(self.view)
        legend.addItem(ex_neuron_symbol, 'Excitatory Neuron')
        legend.addItem(in_neuron_symbol, 'Inhibitory Neuron')
        legend.addItem(self.ex_spines, 'Excitatory Spine')
        legend.addItem(self.in_spines, 'Inhibitory Spine')
        legend.addItem(self.axons, 'Axons')



        self.GUI_FPS = 20  
        self.simulation_timer = QTimer()

        self.thread = QThread()
        self.worker = SimulationWorker(self.graph, self.mutex)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.simulation_timer.timeout.connect(self.fetch_and_update_gui)

        self.thread.start()
        self.simulation_timer.start(1000 // self.GUI_FPS)


        # Timer
        self.elapsed_ms = 0 
        self.time_overlay = QLabel("00:00.0", self.plot_widget)
        self.time_overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 120);
            color: #deff9a;
            font-family: 'Consolas', monospace;
            font-size: 20px;
            font-weight: bold;
            padding: 8px;
        """)
        # Timer Speedup
        
        timer_speed_layout = QHBoxLayout()

        self.timer_speed_txt = QLabel("Simulation Delay: 100")
        timer_speed_layout.addWidget(self.timer_speed_txt)

        self.timer_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.timer_speed_slider.setMinimum(0)
        self.timer_speed_slider.setMaximum(100)
        self.timer_speed_slider.setValue(100)
        self.timer_speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.timer_speed_slider.setTickInterval(50)
        self.timer_speed_slider.setFixedWidth(400)

        self.timer_speed_slider.valueChanged.connect(self.update_speed_control)

        timer_speed_layout.addWidget(self.timer_speed_slider)

        layout.addLayout(timer_speed_layout)


        # Timer Player

        timer_btn_layout = QHBoxLayout()

        self.timer_rewind_btn = QPushButton("⏮")
        self.timer_rewind_btn.clicked.connect(self.rewind_time)
        self.timer_rewind_btn.setStyleSheet("background-color: grey; color: white; font: bold 20px; border-color: red;")
        timer_btn_layout.addWidget(self.timer_rewind_btn)

        self.timer_pause_btn = QPushButton("⏸")
        self.timer_pause_btn.clicked.connect(self.toggle_simulation)
        self.timer_pause_btn.setStyleSheet("background-color: green; color: black; font: bold 20px;")
        timer_btn_layout.addWidget(self.timer_pause_btn)


        self.timer_forward_btn = QPushButton("⏭")
        self.timer_forward_btn.clicked.connect(self.forward_time)
        self.timer_forward_btn.setStyleSheet("background-color: grey; color: white; font: bold 20px;")
        timer_btn_layout.addWidget(self.timer_forward_btn)

        layout.addLayout(timer_btn_layout)



        # More Buttons
                
        button_layout = QHBoxLayout()
        
        self.return_button = QPushButton("Return to Launcher")
        self.return_button.setStyleSheet("background-color: yellow; color: black; font: bold 14px;")
        self.return_button.clicked.connect(self.return_to_launcher)
        button_layout.addWidget(self.return_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: red; color: black; font: bold 14px;")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)



        # Container for the collapsible controls
        self.controls_container = QWidget()
        controls_layout = QVBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0) # Remove margins for a compact view

        # Button to toggle controls
        self.toggle_controls_btn = QPushButton("▶ Expand Parameters")
        self.toggle_controls_btn.setCheckable(True)
        self.toggle_controls_btn.setChecked(True) # Startet eingeklappt
        self.toggle_controls_btn.setStyleSheet("background-color: #333333; color: white; padding: 5px; border-radius: 3px;")
        self.toggle_controls_btn.clicked.connect(self.toggle_controls)
        
        layout.addWidget(self.toggle_controls_btn)
        layout.addWidget(self.controls_container)

        self.I_ext_label = QLabel(f"External Input (I_ext_mean): {self.graph.network.I_ext_mean:.1f} mV/ms")
        self.I_ext_slider = QSlider(Qt.Orientation.Horizontal)
        self.I_ext_slider.setMinimum(0)   # Corresponds to 0.0 mV/ms
        self.I_ext_slider.setMaximum(150) # Corresponds to 15.0 mV/ms
        self.I_ext_slider.valueChanged.connect(self.update_I_ext_mean)
        controls_layout.addWidget(self.I_ext_label)
        controls_layout.addWidget(self.I_ext_slider)
        self.I_ext_slider.setValue(int(self.graph.network.I_ext_mean * 10))

        self.v_label = QLabel(f"Growth Rate (v): {self.graph.network.v:.4f}")
        self.v_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_slider.setMinimum(1)
        self.v_slider.setMaximum(500)
        self.v_slider.setValue(int(self.graph.network.v * 10000))
        self.v_slider.valueChanged.connect(self.update_v)
        controls_layout.addWidget(self.v_label)
        controls_layout.addWidget(self.v_slider)

        self.eps_label = QLabel(f"Stress Set-Point (epsilon): {self.graph.network.epsilon:.2f}")
        self.eps_slider = QSlider(Qt.Orientation.Horizontal)
        self.eps_slider.setMinimum(30)   
        self.eps_slider.setMaximum(150)  
        self.eps_slider.setValue(int(self.graph.network.epsilon * 100))
        self.eps_slider.valueChanged.connect(self.update_epsilon)
        controls_layout.addWidget(self.eps_label)
        controls_layout.addWidget(self.eps_slider)

        # Slider for Calcium Decay (Tau_Ca)
        self.tau_label = QLabel(f"Calcium Decay (tau_Ca): {self.graph.network.tau_ca:.0f} ms")
        self.tau_slider = QSlider(Qt.Orientation.Horizontal)
        self.tau_slider.setMinimum(100)   # Corresponds to 1000 ms
        self.tau_slider.setMaximum(15000) # Corresponds to 15000 ms
        self.tau_slider.valueChanged.connect(self.update_tau_ca)
        self.tau_slider.setValue(int(self.graph.network.tau_ca))
        controls_layout.addWidget(self.tau_label)
        controls_layout.addWidget(self.tau_slider)

        #Slider for Distance Kernel (Sigma)
        self.sigma_label = QLabel(f"Kernel Range (Sigma): {self.graph.network.sigma:.0f} µm")
        self.sigma_slider = QSlider(Qt.Orientation.Horizontal)
        self.sigma_slider.setMinimum(2)   # Corresponds to 100
        self.sigma_slider.setMaximum(50)  # Corresponds to 2500
        self.sigma_slider.setValue(int(self.graph.network.sigma / 50))
        self.sigma_slider.valueChanged.connect(self.update_sigma)
        controls_layout.addWidget(self.sigma_label)
        controls_layout.addWidget(self.sigma_slider)

        #Slider for eta_A (Axon)
        self.eta_a_label = QLabel(f"Max Ca for Axons (eta_A): {self.graph.network.eta_A:.2f}")
        self.eta_a_slider = QSlider(Qt.Orientation.Horizontal)
        self.eta_a_slider.setMinimum(10)  # Corresponds to 0.1
        self.eta_a_slider.setMaximum(80)   # Corresponds to 0.8
        self.eta_a_slider.setValue(int(self.graph.network.eta_A * 100))
        self.eta_a_slider.valueChanged.connect(self.update_eta_a)
        controls_layout.addWidget(self.eta_a_label)
        controls_layout.addWidget(self.eta_a_slider)

        #Slider for eta_D (Dendrite)
        self.eta_d_label = QLabel(f"Max Ca for Dendrites (eta_D): {self.graph.network.eta_D:.2f}")
        self.eta_d_slider = QSlider(Qt.Orientation.Horizontal)
        self.eta_d_slider.setMinimum(0)   # Corresponds to 0.0
        self.eta_d_slider.setMaximum(80)  # Corresponds to 0.8
        self.eta_d_slider.setValue(int(self.graph.network.eta_D * 100))
        self.eta_d_slider.valueChanged.connect(self.update_eta_d)
        controls_layout.addWidget(self.eta_d_label)
        controls_layout.addWidget(self.eta_d_slider)

        #Slider for k (Fire intensety)
        self.k_label = QLabel(f"Synapse Conductance (k): {self.graph.network.k:.2f}")
        self.k_slider = QSlider(Qt.Orientation.Horizontal)
        self.k_slider.setMinimum(0)    # Corresponds to 0.0
        self.k_slider.setMaximum(500)  # Corresponds to 5.0
        self.k_slider.setValue(int(self.graph.network.k * 100))
        self.k_slider.valueChanged.connect(self.update_k)
        controls_layout.addWidget(self.k_label)
        controls_layout.addWidget(self.k_slider)
        
        self.toggle_controls(True) 
        

    def toggle_controls(self, checked):
        if checked:
            self.controls_container.setVisible(False)
            self.toggle_controls_btn.setText("▶ Expand Parameters")
        else:
            self.controls_container.setVisible(True)
            self.toggle_controls_btn.setText("▼ Collapse Parameters")

    def update_I_ext_mean(self, value):
        val = value / 10.0
        self.graph.network.I_ext_mean = val
        self.I_ext_label.setText(f"External Input (I_ext_mean): {val:.1f} mV/ms")

    def update_v(self, value):
        val = value / 10000.0
        self.graph.network.v = val
        
        self.v_label.setText(f"Growth Rate (v): {val:.4f}")

    def update_epsilon(self, value):
        float_val = value / 100.0
        self.graph.network.epsilon = float_val
        self.eps_label.setText(f"Stress Set-Point (epsilon): {float_val:.2f}")

    def update_tau_ca(self, value):
        val = float(value)
        self.graph.network.tau_ca = val
        self.tau_label.setText(f"Calcium Decay (tau_Ca): {val:.0f} ms")

    def update_sigma(self, value):
        val = value * 50
        self.graph.network.sigma = val
        self.sigma_label.setText(f"Kernel Range (sigma): {val:.0f} µm")
        self.graph.network.kernel = self.graph.network.calculate_distance_kernel(sigma=val)

    def update_eta_a(self, value):
        val = value / 100.0
        self.graph.network.eta_A = val
        self.eta_a_label.setText(f"Max Ca for Axons (eta_A): {val:.2f}")

    def update_eta_d(self, value):
        val = value / 100.0
        self.graph.network.eta_D = val
        self.eta_d_label.setText(f"Max Ca for Dendrites (eta_D): {val:.2f}")

    def update_k(self, value):
        val = value / 100.0  # Scale the integer value from the slider to a float
        self.graph.network.k = val
        self.k_label.setText(f"Synapse Conductance (k): {val:.2f}")

    def update_speed_control(self, value):
        self.worker.speed_controle = value
        self.timer_speed_txt.setText(f"Simulation Delay: {value}")


    def update_gui_elements(self, adj, ax_x, ax_y, exc_x, exc_y, inh_x, inh_y, counter):
        self.mutex.lock()
        self.elapsed_ms = counter
        self.draw_synapses(adj)
        self.draw_synaptic_elements(ax_x, ax_y, exc_x, exc_y, inh_x, inh_y)
        self.display_time()

        if self.selected_neuron_index is not None and self.calcium_text_item:
            neuron = self.graph.network.get_neuron_by_index(self.selected_neuron_index)
            text = f"Ca: {neuron.calcium_level:.4f}"
            self.calcium_text_item.setText(text)
        self.mutex.unlock()

    def fetch_and_update_gui(self):
        self.mutex.lock()
        ax_x, ax_y, exc_x, exc_y, inh_x, inh_y = self.graph.update_synaptic_elements()
        active_synapses = self.graph.get_active_synapses()
        counter_val = self.worker.time_counter
        self.mutex.unlock()
    
        self.update_gui_elements(active_synapses, ax_x, ax_y, exc_x, exc_y, inh_x, inh_y, counter_val) 
        
    def display_time(self):
        total_seconds = self.elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        tenth_seconds = (self.elapsed_ms % 1000) // 100 # Berechnet die Zehntelsekunden
        self.time_overlay.setText(f"{minutes:02d}:{seconds:02d}.{tenth_seconds:01d}")


    def rewind_time(self):
        if self.elapsed_ms < 1000:
            self.elapsed_ms = 0
        else:
            self.elapsed_ms -= 1000
        self.display_time()

    def forward_time(self):
        self.elapsed_ms += 10000
        self.display_time()

    # Toggle Pause/Resume Button for Simulation

    def toggle_simulation(self):
        if self.simulation_timer.isActive():
            self.worker.pause()
            self.simulation_timer.stop()
            self.timer_pause_btn.setText("►")
        else:
            self.worker.resume()
            self.simulation_timer.start()
            self.timer_pause_btn.setText("⏸")

    def closeEvent(self, event):
        """Ensure the worker thread is properly shut down on window close."""
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()


    # Spawn Neurons (based on User Input)

    def spawn_neurons(self):

        # Positions of the Neurons
        
        pos = self.graph.neuron_positions
        

        # Types of the Neurons

        TYPE_CONFIG = {
            NeuronType.EXCITATORY: {"symbol": "o", "brush": (231, 76, 60)},
            NeuronType.INHIBITORY: {"symbol": "o", "brush": (46, 0, 213)},
        }


        # Plotting Data

        symbols = [TYPE_CONFIG[NeuronType(int(getattr(n.type, 'value', n.type)))]["symbol"] for n in self.neurons]
        colors  = [TYPE_CONFIG[NeuronType(int(getattr(n.type, 'value', n.type)))]["brush"] for n in self.neurons]


        # Plotting

        self.network_graph.setData(pos=pos, pen=pg.mkPen(color=(150, 150, 150), width=2), size=12, symbol=symbols, symbolBrush=colors, symbolPen=None, pxMode=False)

        empty_adj = np.empty((0, 2), dtype=int)
        self.synapse_lines.setData(pos=pos, adj=empty_adj, pen=pg.mkPen(color=(120,120,120,100), width=1.5), size=0, symbol='o')

        self.draw_synaptic_elements(*self.graph.update_synaptic_elements())
        
    

    def draw_synaptic_elements(self, ax_x, ax_y, exc_x, exc_y, inh_x, inh_y):
        self.axons.setData(x = ax_x, y = ax_y)
        self.ex_spines.setData(x = exc_x, y = exc_y)
        self.in_spines.setData(x = inh_x, y = inh_y)

    def draw_synapses(self, active_synapses):
        pos = self.graph.neuron_positions
        pen_color = (120, 120, 120, 100)

        for text_item in self.synapse_count_texts:
            self.view.removeItem(text_item)
        self.synapse_count_texts.clear()

        if len(active_synapses) == 0:
            active_synapses = np.empty((0, 2), dtype=int)
        else:
            for from_idx, to_idx in active_synapses:
                count = self.graph.network.get_amount_of_synapses(from_idx, to_idx)
                if count > 1:
                    mid_x = (pos[from_idx][0] + pos[to_idx][0]) / 2
                    mid_y = (pos[from_idx][1] + pos[to_idx][1]) / 2
                    text = pg.TextItem(str(count), color=pen_color[:-1], anchor=(0.5, 0.5))
                    text.setPos(mid_x, mid_y)
                    self.view.addItem(text)
                    self.synapse_count_texts.append(text)

        self.synapse_lines.setData(pos=pos, adj=active_synapses, pen=pg.mkPen(color=pen_color, width=1.5), size=0, symbol='o')


    # TODO Implement firing visualization
    def update_firing_neurons(self):
        return

    def return_to_launcher(self):
        self.launcher = guilauncher()
        self.launcher.show()
        # Properly close the current simulation window and its thread
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        self.close()
    
    def on_view_clicked(self, event):
        points = self.network_graph.scatter.pointsAt(event.pos())
        if len(points) == 0:
            if self.calcium_text_item:
                self.view.removeItem(self.calcium_text_item)
                self.calcium_text_item = None
                self.selected_neuron_index = None

    def on_neuron_clicked(self, scatter_item, points):
        if not points:
            self.view.removeItem(self.calcium_text_item)
            return

        point = points[0]
        self.selected_neuron_index = point.index()
        neuron = self.graph.network.get_neuron_by_index(self.selected_neuron_index)

        if not self.calcium_text_item:
            self.calcium_text_item = pg.TextItem("", color=(220, 220, 220), anchor=(0.5, -1.0))
            self.view.addItem(self.calcium_text_item)
        
        self.calcium_text_item.setPos(neuron.x, neuron.y)
        self.calcium_text_item.setText(f"Ca: {neuron.calcium_level:.4f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())