
from PySide.QtCore import *
from PySide.QtGui import *

from collections import OrderedDict

class ColorSwatch(QWidget):
    """
    A color swatch widget for displaying and selecting colors.
    """
    def __init__(self, color, parent=None):
        """
        Construct a ColorSwatch class
        color:  A QColor specifying the starting color for the swatch.
        """
        super(ColorSwatch, self).__init__(parent=parent)
        self._color = color

    def setColor(self, new_color):
        """
        Set the color of the swatch.
        new_color:  A QColor containing the new color.
        """
        self._color = new_color

    def getColor(self):
        """
        Returns the current color as a QColor
        """
        return self._color

    def getHexColor(self):
        """
        Returns the current color as a hex string.
        """
        red = "%02x" % self.getColor().red()
        green = "%02x" % self.getColor().green()
        blue = "%02x" % self.getColor().blue()
        return "#%s%s%s" % (red, green, blue)

    def paintEvent(self, e):
        """
        Paint event handler
        """
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self._color))
        qp.drawRect(0, 0, self.width(), self.height())
        qp.end()

    def mousePressEvent(self, e):
        """
        Mouse press event handler (opens a dialog to select a new color for the swatch).
        """
        color_choice = QColorDialog.getColor(self.getColor()) 
        if color_choice.isValid():
            self.setColor(color_choice)

    def enterEvent(self, e):
        """
        Enter event handler (sets the cursor to a pointing hand).
        """
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, e):
        """
        Leave event handler (sets the cursor to whatever it was before).
        """
        self.unsetCursor()

class PrefDialog(QDialog):
    """
    The preferences dialog box for SHARPpy.
    """

    _color_names = OrderedDict([('temp_color', 'Temperature'), ('dewp_color', 'Dewpoint')])
    def __init__(self, config, parent=None):
        """
        Construct the preferences dialog box.
        config: A Config object containing the user's configuration.
        """
        super(PrefDialog, self).__init__(parent=parent)
        self._config = config

        self.__initUI()

    def __initUI(self):
        """
        Set up the user interface [private method].
        """
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

        temp_units_box, self.temp_units = PrefDialog._createRadioSet("Surface Temperature Units", ["Fahrenheit", "Celsius"], default=self._config['preferences', 'temp_units'])
        self.layout.addWidget(temp_units_box, 0, 0, 1, 1)

        wind_units_box, self.wind_units = PrefDialog._createRadioSet("Wind Units", ["knots", "m/s"], default=self._config['preferences', 'wind_units'])
        self.layout.addWidget(wind_units_box, 1, 0, 1, 1)

        calc_vector_box, self.calc_vector = PrefDialog._createRadioSet("Storm Motion Vector Used in Calculations", ["Left Mover", "Right Mover"], default=self._config['preferences', 'calc_vector'])
        self.layout.addWidget(calc_vector_box, 2, 0, 1, 1)

        colors_box = QGroupBox("Colors")
        colors_layout = QVBoxLayout()
        colors_layout.setContentsMargins(22, 4, 22, 4)
        colors_box.setLayout(colors_layout)

        self.colors = {}
        for cid, cname in PrefDialog._color_names.iteritems():
            cbox, self.colors[cid] = PrefDialog._createColorBox(cname, self._config['preferences', cid])
            colors_layout.addWidget(cbox)

        self.layout.addWidget(colors_box, 3, 0, 1, 1)

    @staticmethod
    def _createColorBox(name, default_color):
        """
        Create a color swatch and label [private static method]
        name:   The label on the color swatch.
        default_color:  The starting color for the swatch as a hex string.

        Returns a QWidget and a ColorSwatch object.
        """
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
        """
        Create a set of radio buttons [private static method]
        set_name:    Name of the group of buttons
        opt_names:   A list of names for the radio buttons.
        default:     The name of the button to be selected initially.
        orientation: The direction to arrange the radio buttons. Accepted values are 'horizontal'
                        and 'vertical'. Default is 'horizontal'.
        Returns a QGroupBox and a dictionary with names as keys of QRadioButton's as values.
        """
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
        """
        Apply the radio button selection to the configuration [private method].
        config_name:    Field in the configuration file to set.
        radio:          Dictionary with names of the radio buttons as keys and QRadioButtons as values.
        """
        for radio_name, rad in radio.iteritems():
            if rad.isChecked():
                self._config['preferences', config_name] = radio_name

    def applyChanges(self):
        """
        Apply the state of the preferences box to the configuration and close the box.
        """
        self._applyRadio('temp_units', self.temp_units)
        self._applyRadio('wind_units', self.wind_units)
        self._applyRadio('calc_vector', self.calc_vector)

        for cid, cbox in self.colors.iteritems():
            self._config['preferences', cid] = cbox.getHexColor()

        self.accept()

    def rejectChanges(self):
        """
        Close the box without applying the changes to the configuration.
        """
        self.reject()

    @staticmethod
    def initConfig(config):
        """
        Initialize the configuration with the user preferences [static method].
        config: A Config object containing the configuration.
        """
        pref_config = {
            ('preferences', 'temp_units'):'Fahrenheit',
            ('preferences', 'wind_units'):'knots',

            ('preferences', 'calc_vector'):'Right Mover',

            ('preferences', 'temp_color'):'#ff0000',
            ('preferences', 'dewp_color'):'#00ff00',
        }

        config.initialize(pref_config)
