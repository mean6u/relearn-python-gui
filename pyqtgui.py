import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QStyleFactory
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QIcon, QIntValidator
from currentgraph import currentgraph
from objects import NeuronType 

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
        # Initializing window
        self.setWindowTitle("RELeARN - Launcher")
        self.resize(300, 125)
        self.setMaximumSize(300, 125)

        fusion_style = QStyleFactory.create("Fusion")
        if fusion_style:
            QApplication.instance().setStyle(fusion_style)

        # Setting dark mode as default
        QApplication.instance().setPalette(get_dark_palette())

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
        self.dark_mode_btn.setMaximumSize(300, 50)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_btn)
        self.dark_mode_btn.setChecked(True)

        # Adding input fields for neurons and synapses
        self.add_line(layout, "Number of Neurons:", "input_neurons", "10", True)

        #self.add_line(layout, "Growth Rate", "input_growth", "1", True)

        # Adding buttons
        self.start_button = QPushButton("Start Simulation")
        self.start_button.setMaximumSize(300, 50)
        self.start_button.setGeometry
        # start implementing the connection logic
        self.start_button.clicked.connect(self.start_sim)
        layout.addWidget(self.start_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #A82424; color: black;")
        self.exit_button.setMaximumSize(300, 50)
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
    
    def add_line(self, goal_layout, label_text: str, attribute_name: str, default_val: str, horizontal: bool):
        if horizontal:
            new_layout = QHBoxLayout()
        else:
            new_layout = QVBoxLayout()
        new_layout.addWidget(QLabel(label_text))
        
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
        #user_input_growth = int(self.input_growth.text() or self.input_growth.placeholderText())
        return user_input_neurons

    # start implementing the connection logic
    def start_sim(self):
        input = self.handle_input()
        #print(output[0], output[1])
        self.sim_gui = simulation(dark_mode, input)
        self.sim_gui.show()
        self.close()


    # not toggling yet, just applying dark mode, default values become invisible :/
    def toggle_dark_mode(self, checked: bool):
        global dark_mode
        app = QApplication.instance()

        if checked:
            cur_palette = get_dark_palette()
            dark_mode = True
        else:
            cur_palette = get_white_palette()
            dark_mode = False

        app.setPalette(cur_palette)



class simulation(QMainWindow):
    def __init__(self, is_dark_mode: bool, neuron_count: int):
        super().__init__()
        self.graph = currentgraph(neuron_count)
        # slightly reduces performance but prettier
        pg.setConfigOptions(antialias=True)
        
        self.setWindowTitle("RELeARN - Structural Plasiticity Simulation")
        self.resize(800, 600)

        self.setWindowIcon(QIcon('plasticity.jpg'))

        self.neurons = self.graph.neurons

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # earlier used simpler PlotWidget
        #self.plot_widget = pg.PlotWidget()

        self.plot_widget = pg.GraphicsLayoutWidget()
        if is_dark_mode:
            self.plot_widget.setBackground("#000000")
        else:
            self.plot_widget.setBackground("#ffffff")
        
        #self.plot_widget.showAxis("left", False) # used with PlotWidget
        #self.plot_widget.showAxis("bottom", False) # used with PlotWidget
        
        layout.addWidget(self.plot_widget)

        self.view = self.plot_widget.addViewBox()
        self.view.setAspectLocked(True)

        self.network_graph = pg.GraphItem()
        self.view.addItem(self.network_graph)

        button_layout = QHBoxLayout()
        self.new_neurons()
        self.random_button = QPushButton("Randomize")
        self.random_button.setStyleSheet("background-color: #00ff00; color: black;")
        self.random_button.clicked.connect(self.new_neurons)
        button_layout.addWidget(self.random_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #A82424; color: black;")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)

    # spawn new neurons and connect them using the euclidean distance
    def new_neurons(self):
        pos = [[n.x, n.y] for n in self.neurons]
        
        TYPE_CONFIG = {
            1: {"symbol": "o", "brush": (46, 204, 113)},
            0: {"symbol": "s", "brush": (231, 76, 60)}
        }

        symbols = [TYPE_CONFIG[n.type]["symbol"] for n in self.neurons]
        colors  = [TYPE_CONFIG[n.type]["brush"] for n in self.neurons]

        #dx = pos[:, 0, np.newaxis] - pos[:, 0]
        #dy = pos[:, 1, np.newaxis] - pos[:, 1]
        #distances = np.sqrt(dx**2 + dy**2)
        #radius = 5
        #i, j = np.where((distances < radius) & (distances > 0))
        #transition_edges = np.stack((i,j))
        self.network_graph.setData(pos=pos, adj=None, pen=pg.mkPen(color=(150, 150, 150), width=2), size=14, symbol=symbols, symbolBrush=colors, symbolPen=None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())