
from PySide.QtCore import *
from PySide.QtGui import *

class PrefDialog(QDialog):
    def __init__(self, parent=None):
        super(PrefDialog, self).__init__(parent=parent)
        self.__initUI()

    def __initUI(self):
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.layout = QGridLayout()
        self.setLayout(main_layout)

        self.accept_button = QPushButton("Accept")
        self.accept_button.setDefault(True)
        self.accept_button.clicked.connect(self.applyChanges)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.rejectChanges)

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.layout)
        main_layout.addLayout(button_layout)

        temp_units_box, self.temp_units = self._createRadioSet("Temperature Units", ["Fahrenheit", "Celsius"], default="Fahrenheit")
        self.layout.addWidget(temp_units_box, 0, 0, 1, 1)

        wind_units_box, self.wind_units = self._createRadioSet("Wind Units", ["knots", "m/s"], default="knots")
        self.layout.addWidget(wind_units_box, 1, 0, 1, 1)

    def _createRadioSet(self, set_name, opt_names, default=None, orientation='horizontal'):
        radios = {}
        radio_box = QGroupBox(set_name)

        if orientation == 'horizontal':
            radio_layout = QHBoxLayout()
        elif orientation == 'vertical':
            radio_layout = QVBoxLayout()
        radio_box.setLayout(radio_layout)

        for oname in opt_names:
            radios[oname] = QRadioButton(oname)
            if oname == default:
                radios[oname].setChecked(True)

            radio_layout.addWidget(radios[oname])

        return radio_box, radios

    def applyChanges(self):
        # Change things here
        self.accept()

    def rejectChanges(self):
        self.reject()
