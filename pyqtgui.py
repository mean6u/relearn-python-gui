import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QStyleFactory
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QIcon, QIntValidator, QPainterPath
from currentgraph import currentgraph
from objects import NeuronType, Neuron

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
        self.start_button.setGeometry
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



class simulation(QMainWindow):
    def __init__(self, is_dark_mode: bool, neuron_count: int, exc_count: int):
        super().__init__()


        # Initialising currentgraph
        
        self.graph = currentgraph(neuron_count, exc_count/100, (100-exc_count)/100)
        self.neurons = self.graph.neurons


        # Speed for Timer

        self.speed_factor = 1


        # Test
        # TODO Remove
        for neuron in self.neurons:
            neuron.A = 4
            neuron.D_ex = 6
            neuron.D_in = 6
        


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


        # Neuron Layer
        
        self.network_graph = pg.GraphItem()

        self.view.addItem(self.network_graph)


        # Synaptic Elements Layer

        # Excitatory Dendritic Spines
        self.ex_spines = pg.ScatterPlotItem(size=6, symbol='s', brush=(231, 76, 60), pen=None)

        # Inhibitory Dendritic Spines
        self.in_spines = pg.ScatterPlotItem(size=6, symbol='s', brush=(46, 0, 213), pen=None)

        # Axonal Boutons
        self.axons = pg.ScatterPlotItem(size=6, symbol='t', brush=(255, 255, 0), pen=None)

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


        # Timer

        self.elapsed_ms = 0 # keep track of elapsed time, linked with timer
        self.time_overlay = QLabel("00:00.0", self.plot_widget)
        self.time_overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 120);
            color: #deff9a;
            font-family: 'Consolas', monospace;
            font-size: 20px;
            font-weight: bold;
            padding: 8px;
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_time_stamp)
        self.timer.start(100)


        # Timer Speedup
        
        timer_speed_layout = QHBoxLayout()

        self.timer_speed_txt = QLabel("Simulation Speed")
        timer_speed_layout.addWidget(self.timer_speed_txt)

        self.timer_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.timer_speed_slider.setMinimum(1)
        self.timer_speed_slider.setMaximum(4)
        self.timer_speed_slider.setValue(1)
        self.timer_speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.timer_speed_slider.setTickInterval(1)
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

        # Timer for slow and fast process

        self.timer_slow = QTimer()
        self.timer_slow.timeout.connect(self.slow_process)
        self.timer_slow.start(1000)

        self.timer_fast = QTimer()
        self.timer_fast.timeout.connect(self.fast_process)
        self.timer_fast.start(10)



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


    def simulate_time_stamp(self):
        self.elapsed_ms += 100 * self.speed_factor
        self.display_time()


    def slow_process(self):
        self.graph.update_slow_processes(self.speed_factor)
        self.draw_synaptic_elements(*self.graph.update_synaptic_elements())

        




    def fast_process(self):
        self.graph.update_fast_processes(self.speed_factor)


    def display_time(self):
        total_seconds = self.elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        tenth_seconds = (self.elapsed_ms % 1000) // 100
        # self.time_overlay.setText("Ös üs halt :/")
        self.time_overlay.setText(f"{minutes:.2f}:{seconds:.2f}.{tenth_seconds:.1f}")


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
        if self.timer.isActive():
            self.timer.stop()
            self.timer_pause_btn.setText("►")
        else:
            self.timer.start()
            self.timer_pause_btn.setText("⏸")


    # Spawn Neurons (based on User Input)

    def spawn_neurons(self):

        # Positions of the Neurons
        
        pos = np.array([[n.x, n.y] for n in self.neurons])
        

        # Types of the Neurons

        TYPE_CONFIG = {
            NeuronType.EXCITATORY: {"symbol": "o", "brush": (231, 76, 60)},
            NeuronType.INHIBITORY: {"symbol": "o", "brush": (46, 0, 213)},
        }


        # Plotting Data

        symbols = [TYPE_CONFIG[NeuronType(int(getattr(n.type, 'value', n.type)))]["symbol"] for n in self.neurons]
        colors  = [TYPE_CONFIG[NeuronType(int(getattr(n.type, 'value', n.type)))]["brush"] for n in self.neurons]


        # Plotting

        self.network_graph.setData(pos=pos, pen=pg.mkPen(color=(150, 150, 150), width=2), size=25, symbol=symbols, symbolBrush=colors, symbolPen=None)

        self.draw_synaptic_elements(*self.graph.update_synaptic_elements())
        
    

    def draw_synaptic_elements(self, ax_x, ax_y, exc_x, exc_y, inh_x, inh_y):
        self.axons.setData(x = ax_x, y = ax_y)
        self.ex_spines.setData(x = exc_x, y = exc_y)
        self.in_spines.setData(x = inh_x, y = inh_y)



    # TODO Implement firing visualization
    def update_firing_neurons(self):
        return

    def return_to_launcher(self):
        self.launcher = guilauncher()
        self.launcher.show()
        self.close()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())