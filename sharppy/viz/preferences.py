
from PySide.QtCore import *
from PySide.QtGui import *

from collections import OrderedDict

class ColorSwatch(QWidget):
    def __init__(self, color, parent=None):
        super(ColorSwatch, self).__init__(parent=parent)
        self._color = color

    def setColor(self, new_color):
        self._color = new_color

    def getColor(self):
        return self._color

    def getHexColor(self):
        red = "%02x" % self.getColor().red()
        green = "%02x" % self.getColor().green()
        blue = "%02x" % self.getColor().blue()
        return "#%s%s%s" % (red, green, blue)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self._color))
        qp.drawRect(0, 0, self.width(), self.height())
        qp.end()

    def mousePressEvent(self, e):
        color_choice = QColorDialog.getColor(self.getColor()) 
        if color_choice.isValid():
            self.setColor(color_choice)

class PrefDialog(QDialog):
    _color_names = OrderedDict([('temp_color', 'Temperature'), ('dewp_color', 'Dewpoint')])
    def __init__(self, config, parent=None):
        super(PrefDialog, self).__init__(parent=parent)
        self._config = config

        self.__initUI()

    def __initUI(self):
        self.setWindowTitle("SHARPpy Preferences")
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

        temp_units_box, self.temp_units = PrefDialog._createRadioSet("Temperature Units", ["Fahrenheit", "Celsius"], default=self._config.get('preferences', 'temp_units'))
        self.layout.addWidget(temp_units_box, 0, 0, 1, 1)

        wind_units_box, self.wind_units = PrefDialog._createRadioSet("Wind Units", ["knots", "m/s"], default=self._config.get('preferences', 'wind_units'))
        self.layout.addWidget(wind_units_box, 1, 0, 1, 1)

        colors_box = QGroupBox("Colors")
        colors_layout = QVBoxLayout()
        colors_layout.setContentsMargins(22, 4, 22, 4)
        colors_box.setLayout(colors_layout)

        self.colors = {}
        for cid, cname in PrefDialog._color_names.iteritems():
            cbox, self.colors[cid] = PrefDialog._createColorBox(cname, self._config.get('preferences', cid))
            colors_layout.addWidget(cbox)

        self.layout.addWidget(colors_box, 2, 0, 1, 1)

    @staticmethod
    def _createColorBox(name, default_color):
        swatch = ColorSwatch(QColor(default_color))
        swatch.setMaximumWidth(40)

        label = QLabel(name)

        colorbox = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        colorbox.setLayout(layout)

        layout.addWidget(swatch)
        layout.addWidget(label)
        return colorbox, swatch

    @staticmethod
    def _createRadioSet(set_name, opt_names, default=None, orientation='horizontal'):
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

    def _applyRadio(self, config_name, radio):
        for radio_name, rad in radio.iteritems():
            if rad.isChecked():
                self._config.set('preferences', config_name, radio_name)

    def applyChanges(self):
        self._applyRadio('temp_units', self.temp_units)
        self._applyRadio('wind_units', self.wind_units)

        for cid, cbox in self.colors.iteritems():
            self._config.set('preferences', cid, cbox.getHexColor())

        self.accept()

    def rejectChanges(self):
        self.reject()

    @staticmethod
    def initConfig(config):
        if not config.has_section('preferences'):
            config.add_section('preferences')
            config.set('preferences', 'temp_units', 'Fahrenheit')
            config.set('preferences', 'wind_units', 'knots')
            config.set('preferences', 'temp_color', '#ff0000')
            config.set('preferences', 'dewp_color', '#00ff00')
