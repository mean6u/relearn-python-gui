import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QStyleFactory
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class guilauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RELeARN - Launcher")
        self.resize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)



        #neuron_layout = QHBoxLayout()
        #neuron_layout.addWidget(QLabel("Number of Neurons:"))
        #self.input_neurons = QLineEdit()
        #self.input_neurons.setPlaceholderText("100")
        #neuron_layout.addWidget(self.input_neurons)
        #layout.addLayout(neuron_layout)
        
        # doesn't toggle, just activates bad dark mode
        self.dark_mode = QPushButton("Toggle Dark Mode")
        self.dark_mode.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode)

        self.add_line(layout, "Number of Neurons:", "input_neurons", "100", True)

        self.add_line(layout, "Number of Synapses per Neuron:", "input_synapses", "10", True)

        self.start_button = QPushButton("Start Simulation")
        
        # start implementing the connection logic
        self.start_button.clicked.connect(self.start_sim())
    
    def add_line(self, goal_layout, label_text: str, attribute_name: str, default_val: str, horizontal: bool):
        if horizontal:
            new_layout = QHBoxLayout()
        else:
            new_layout = QVBoxLayout()
        new_layout.addWidget(QLabel(label_text))
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(default_val)
        setattr(self, attribute_name, input_field)
        
        new_layout.addWidget(input_field)
        goal_layout.addLayout(new_layout)
    
    # start implementing the connection logic
    def start_sim(self):
        pass

    # not toggling yet, just applying dark mode, default values become invisible :/
    def toggle_dark_mode(app: QApplication):
        # fusion style
        fusion_style = QStyleFactory.create("Fusion")
        if fusion_style:
            app.setStyle(fusion_style)
        
        # new color palette
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
        
        app.setPalette(dark_palette)



class pyqtgui(QMainWindow):
    def __init__(self, neuron_count, synapse_count):
        super().__init__()
        self.setWindowTitle("RELeARN - Structural Plasiticity Simulation")
        self.resize(800, 600)

        self.Neurons = neuron_count
        self.Synapses = synapse_count

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # test plot
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # test plot
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

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

    # test purpose
    def change_zoom(self):
        cur_value = self.slider.value()
        print(f"Slider steht auf: {cur_value}")

    def do_something(self):
        new_activity = np.random.normal(size=100)
        self.plot_line.setData(new_activity)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #apply_dark_mode(app)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())