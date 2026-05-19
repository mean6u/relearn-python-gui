import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QStyleFactory
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QIcon, QIntValidator

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
        self.dark_mode = QPushButton("Toggle Dark Mode")
        self.dark_mode.setCheckable(True)
        self.dark_mode.setMaximumSize(300, 50)
        self.dark_mode.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode)

        # Adding input fields for neurons and synapses
        self.add_line(layout, "Number of Neurons:", "input_neurons", "100", True)
        # TODO add input fields for dendritic and axonal elements
        self.add_line(layout, "Number of Synapses per Neuron:", "input_synapses", "10", True)

        self.add_line(layout, "Growth Rate", "input_growth", "1", True)

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
        user_input_synapses = int(self.input_synapses.text() or self.input_synapses.placeholderText())
        user_input_growth = int(self.input_growth.text() or self.input_growth.placeholderText())
        return user_input_neurons, user_input_synapses, user_input_growth

    # start implementing the connection logic
    def start_sim(self):
        inputs = self.handle_input()
        #print(output[0], output[1])
        self.sim_gui = simulation(dark_mode, inputs[0], inputs[1], inputs[2])
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
    def __init__(self, is_dark_mode: bool, neuron_count, synapse_count, growth_rate):
        super().__init__()
        
        # slightly reduces performance but prettier
        pg.setConfigOptions(antialias=True)
        
        self.setWindowTitle("RELeARN - Structural Plasiticity Simulation")
        self.resize(800, 600)

        self.setWindowIcon(QIcon('plasticity.jpg'))

        self.Neurons = neuron_count
        self.Synapses = synapse_count
        self.Growth = growth_rate

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # ealier used simpler PlotWidget
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
        self.new_neurons_and_eucl_con()
        self.random_button = QPushButton("Randomize")
        self.random_button.setStyleSheet("background-color: #00ff00; color: black;")
        self.random_button.clicked.connect(self.new_neurons_and_eucl_con)
        button_layout.addWidget(self.random_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #A82424; color: black;")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)

        # TODO replace with graph
        # TODO start of section
        # test plot
        """
        time = np.linspace(0, 10, 100)
        activity = np.sin(time)
        self.plot_line = self.plot_widget.plot(time, activity, pen=pg.mkPen('g', width=2))

        # test slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 200)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.change_zoom)
        layout.addWidget(self.slider)

        # test button
        self.button = QPushButton("Random Signal")
        layout.addWidget(self.button)
        # connecting test signal "Random Signal" to slot (function)
        self.button.clicked.connect(self.do_something)
        # TODO end of section
        """

    # spawn new neurons and connect them using the euclidean distance
    def new_neurons_and_eucl_con(self):
        pos = np.random.randint(-10, 10, size=(10, 2))
        dx = pos[:, 0, np.newaxis] - pos[:, 0]
        dy = pos[:, 1, np.newaxis] - pos[:, 1]
        distances = np.sqrt(dx**2 + dy**2)
        radius = 5
        i, j = np.where((distances < radius) & (distances > 0))
        transition_edges = np.stack((i,j))
        self.network_graph.setData(pos=pos, adj=transition_edges, pen=pg.mkPen(color=(150, 150, 150), width=2), symbolBrush='g', size=1, symbol='o', pxMode=False)

    # test purpose
    def change_zoom(self):
        cur_value = self.slider.value()
        print(f"Slider steht auf: {cur_value}")

    def do_something(self):
        new_activity = np.random.normal(size=100)
        self.plot_line.setData(new_activity)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())