import sys
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider
from PyQt6.QtCore import Qt

class pyqtgui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RELeARN - Structural Plasiticity")
        self.resize(800, 600)

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
    gui = pyqtgui()
    gui.show()
    sys.exit(app.exec())