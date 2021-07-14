
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from collections import OrderedDict
import numpy as np

import os
import sys

def resource_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "rc")
    return os.path.join(os.path.dirname(__file__), "..", "..", "rc")

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


class ColorPreview(QWidget):

    _color_imgs = {
        'standard': 'sample_std.png',
        'inverted': 'sample_inv.png',
        'protanopia': 'sample_pro.png',
    }

    def __init__(self, styles, default='standard', **kwargs):
        super(ColorPreview, self).__init__(**kwargs)
        self._img_path =  resource_path() #os.path.join(os.path.dirname(__file__), "..", "..", "rc")
        self._styles = [ s.lower() for s in styles ]
        self.changeImage(self._styles.index(default))

        self._base_x, self._base_y = 118, 80
        self._aspect = float(self._base_x) / self._base_y

        self.setMinimumSize(self._base_x, self._base_y)
        self.show()

    @Slot(str)
    def changeImage(self, img_index):
        self._current = self._styles[img_index]
        self._img = QPixmap(os.path.join(self._img_path, ColorPreview._color_imgs[self._current]))
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(QColor("#000000")))
        qp.drawPixmap(0, 0, self.width(), self.height(), self._img, 0, 0, self._img.width(), self._img.height())
        qp.end()


class PrefDialog(QDialog):
    """
    The preferences dialog box for SHARPpy.
    """

    _styles = {
        'standard': {
            'bg_color': '#000000',
            'fg_color': '#ffffff',

            'temp_color': '#ff0000',
            'dewp_color': '#00ff00',
            'wetb_color': '#00ffff',
            'skew_dgz_color':'#f5d800',
            'skew_itherm_color':'#555555',
            'skew_itherm_hgz_color':'#0000ff',
            'skew_adiab_color':'#333333',
            'skew_mixr_color':'#006600',
            'skew_hgt_color':'#ff0000',
            'skew_lcl_mkr_color':'#00ff00',
            'skew_lfc_mkr_color':'#ffff00',
            'skew_el_mkr_color':'#ff00ff',

            'hodo_itach_color':'#555555',
            'hodo_crit_color':'#00ffff',

            'eff_inflow_color':'#04dbd8',

            '0_3_color': '#ff0000',
            '3_6_color': '#00ff00',
            '6_9_color': '#ffff00',
            '9_12_color': '#00ffff',
            '12_15_color': '#00ffff',

            'pwat_m3_color':'#ff7f00',
            'pwat_m2_color':'#ee9a00',
            'pwat_m1_color':'#ffdab9',
            'pwat_p1_color':'#98fb98',
            'pwat_p2_color':'#66cd00',
            'pwat_p3_color':'#00ff00',

            'alert_l1_color':'#775000',
            'alert_l2_color':'#996600',
            'alert_l3_color':'#ffffff',
            'alert_l4_color':'#ffff00',
            'alert_l5_color':'#ff0000',
            'alert_l6_color':'#e700df',
            'alert_lscp_color':'#00ffff',

            'stp_box_color':'#00ff00',
            'stp_line_color':'#0080ff',

            'pcl_sel_color':'#00ffff',
            'pcl_cin_hi_color':'#993333',
            'pcl_cin_md_color':'#996600',
            'pcl_cin_lo_color':'#00ff00',

            'spd_itach_color':'#9d5736',

            'srw_clsc_color':'#b1019a',
            'srw_trace_color':'#ff0000',
            'srw_0_2_color':'#8b0000',
            'srw_4_6_color':'#6495ed',
            'srw_9_11_color':'#9400d3',

            'winter_dgz_color':'#ffff00',

            'watch_pdstor_color':'#ff00ff',
            'watch_tor_color':'#ff0000',
            'watch_svr_color':'#ffff00',
            'watch_mrglsvr_color':'#0099cc',
            'watch_flood_color':'#5ffb17',
            'watch_blizzard_color':'#3366ff',
            'watch_fire_color':'#ff9900',
            'watch_heat_color':'#c85a17',
            'watch_none_color':'#ffcc33',
        },
        'inverted': {
            'bg_color': '#ffffff',
            'fg_color': '#000000',

            'temp_color': '#dd0000',
            'dewp_color': '#00dd00',
            'wetb_color': '#00cccc',
            'skew_dgz_color':'#f5d800',
            'skew_itherm_color':'#bbbbbb',
            'skew_itherm_hgz_color':'#6666ff',
            'skew_adiab_color':'#dddddd',
            'skew_mixr_color':'#adebad',
            'skew_hgt_color':'#dd0000',
            'skew_lcl_mkr_color':'#00bb00',
            'skew_lfc_mkr_color':'#bbbb00',
            'skew_el_mkr_color':'#bb00bb',

            'hodo_itach_color':'#bbbbbb',
            'hodo_crit_color':'#00cccc',

            'eff_inflow_color': '#00cccc',

            '0_3_color': '#dd0000',
            '3_6_color': '#00dd00',
            '6_9_color': '#dddd00',
            '9_12_color': '#00dddd',
            '12_15_color': '#00dddd',

            'pwat_m3_color':'#ff9900',
            'pwat_m2_color':'#cc7a00',
            'pwat_m1_color':'#804d00',
            'pwat_p1_color':'#006600',
            'pwat_p2_color':'#00b300',
            'pwat_p3_color':'#00ff00',

            'alert_l1_color':'#dfbb9f',
            'alert_l2_color':'#cc9666',
            'alert_l3_color':'#666666',
            'alert_l4_color':'#999900',
            'alert_l5_color':'#cc0000',
            'alert_l6_color':'#e700df',
            'alert_lscp_color':'#00cccc',

            'stp_box_color':'#00aa00',
            'stp_line_color':'#66b3ff',

            'pcl_sel_color':'#00cccc',
            'pcl_cin_hi_color':'#dfbb9f',
            'pcl_cin_md_color':'#cc9666',
            'pcl_cin_lo_color':'#00cc00',

            'spd_itach_color':'#ebd2c6',

            'srw_clsc_color':'#fe81ed',
            'srw_trace_color':'#dd0000',
            'srw_0_2_color':'#8b0000',
            'srw_4_6_color':'#6495ed',
            'srw_9_11_color':'#9400d3',

            'winter_dgz_color':'#999900',

            'watch_pdstor_color':'#dd00dd',
            'watch_tor_color':'#dd0000',
            'watch_svr_color':'#aaaa00',
            'watch_mrglsvr_color':'#0099cc',
            'watch_flood_color':'#5ffb17',
            'watch_blizzard_color':'#3366ff',
            'watch_fire_color':'#ff9900',
            'watch_heat_color':'#c85a17',
            'watch_none_color':'#cc9900',
        },
        'protanopia': {
            'bg_color': '#000000',
            'fg_color': '#ffffff',

            'temp_color': '#ff0000',
            'dewp_color': '#00ffff',
            'wetb_color': '#6666ff',
            'skew_dgz_color':'#f5d800',
            'skew_itherm_color':'#555555',
            'skew_itherm_hgz_color':'#0000ff',
            'skew_adiab_color':'#333333',
            'skew_mixr_color':'#006600',
            'skew_hgt_color':'#ff0000',
            'skew_lcl_mkr_color':'#00ff00',
            'skew_lfc_mkr_color':'#ffff00',

            'hodo_itach_color':'#555555',
            'hodo_crit_color':'#00ffff',

            'eff_inflow_color': '#00ffff',

            '0_3_color': '#ff0000',
            '3_6_color': '#0000ff',
            '6_9_color': '#ff9900',
            '9_12_color': '#00ffff',
            '12_15_color': '#00ffff',

            'pwat_m3_color':'#ff7f00',
            'pwat_m2_color':'#ee9a00',
            'pwat_m1_color':'#ffdab9',
            'pwat_p1_color':'#98fb98',
            'pwat_p2_color':'#66cd00',
            'pwat_p3_color':'#00ff00',

            'alert_l1_color':'#775000',
            'alert_l2_color':'#996600',
            'alert_l3_color':'#00ff99',
            'alert_l4_color':'#ffffff',
            'alert_l5_color':'#00ffff',
            'alert_l6_color':'#ff00ff',
            'alert_lscp_color':'#ffff00',

            'stp_box_color':'#00ff00',
            'stp_line_color':'#0080ff',

            'pcl_sel_color':'#00ffff',
            'pcl_cin_hi_color':'#993333',
            'pcl_cin_md_color':'#996600',
            'pcl_cin_lo_color':'#00ff00',

            'spd_itach_color':'#9d5736',

            'srw_clsc_color':'#b1019a',
            'srw_trace_color':'#ff0000',
            'srw_0_2_color':'#8b0000',
            'srw_4_6_color':'#6495ed',
            'srw_9_11_color':'#9400d3',

            'winter_dgz_color':'#ffff00',

            'watch_pdstor_color':'#ff00ff',
            'watch_tor_color':'#ff0000',
            'watch_svr_color':'#ffff00',
            'watch_mrglsvr_color':'#0099cc',
            'watch_flood_color':'#5ffb17',
            'watch_blizzard_color':'#3366ff',
            'watch_fire_color':'#ff9900',
            'watch_heat_color':'#c85a17',
            'watch_none_color':'#ffcc33',
        }
    }

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

        tab_widget = QTabWidget()

        color_widget = self._createColorWidget()
        tab_widget.addTab(color_widget, "Colors")

        map_widget = self._createMapWidget()
#       tab_widget.addTab(map_widget, "Map")

        misc_widget = self._createMiscWidget()
        readout_widget = self._createReadoutWidget()
        tab_widget.addTab(misc_widget, "Units")
        tab_widget.addTab(readout_widget, "Readout")

        self.layout.addWidget(tab_widget, 0, 0, 1, 1)

    def _createReadoutWidget(self):
        layout = QVBoxLayout()
        box = QWidget()
        label = QLabel("Top Right Readout Variable:")
        box.setLayout(layout)
        layout.addWidget(label)
        self.combo1 = QComboBox()
        layout.addWidget(self.combo1)
        self.combo2 = QComboBox()
        layout.addWidget(QLabel("Bottom Right Readout Variable:"))
        layout.addWidget(self.combo2)
        self.variables = {"Temperature (C)": 'tmpc', 'Dewpoint (C)': 'dwpc',\
                          "Equiv. Potential Temp. (K)": 'thetae',\
                          "Wetbulb Temperature (C)": 'wetbulb',\
                          "Potential Temperature (K)": 'theta',\
                          "Water Vapor Mixing Ratio (g/kg)": 'wvmr',\
                          "Vertical Velocity (mb/hr)": 'omeg'}
        for k in self.variables.keys():
            self.combo1.addItem(k)
            self.combo2.addItem(k)

        idx1 = np.where(np.asarray(list(self.variables.values())) == self._config['preferences', 'readout_tr'])[0][0]
        idx2 = np.where(np.asarray(list(self.variables.values())) == self._config['preferences', 'readout_br'])[0][0]
        self.combo1.setCurrentIndex(idx1)
        self.combo2.setCurrentIndex(idx2)

        return box

    def _createColorWidget(self):
        colors_box = QWidget()
        colors_layout = QVBoxLayout()
        colors_box.setLayout(colors_layout)

        color_styles = ['Standard', 'Inverted', 'Protanopia']
        self._color_style = self._config['preferences', 'color_style']

        def updateStyle(style_idx):
            self._color_style = color_styles[style_idx].lower()

        colors_list = QComboBox()
        colors_list.addItems(color_styles)
        colors_list.setCurrentIndex(color_styles.index(self._color_style.title()))
        colors_layout.addWidget(colors_list)

        colors_prvw = ColorPreview(color_styles, default=self._color_style, parent=self)
        colors_layout.addWidget(colors_prvw)
        colors_list.activated.connect(colors_prvw.changeImage)
        colors_list.activated.connect(updateStyle)
        return colors_box

    def _createMapWidget(self):
        return QWidget()

    def _createMiscWidget(self):
        misc_box = QWidget()
        layout = QVBoxLayout()
        misc_box.setLayout(layout)

        temp_units_box, self.temp_units = PrefDialog._createRadioSet("Surface Temperature Units", ["Fahrenheit", "Celsius"], default=self._config['preferences', 'temp_units'])
        layout.addWidget(temp_units_box)

        wind_units_box, self.wind_units = PrefDialog._createRadioSet("Wind Units", ["knots", "m/s"], default=self._config['preferences', 'wind_units'])
        layout.addWidget(wind_units_box)

        pw_units_box, self.pw_units = PrefDialog._createRadioSet("Precipitable Water Vapor Units", ["in", "cm"], default=self._config['preferences', 'pw_units'])
        layout.addWidget(pw_units_box)

        return misc_box

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
        swatch.setMinimumWidth(40)

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
        for radio_name, rad in radio.items():
            if rad.isChecked():
                self._config['preferences', config_name] = radio_name

    def applyChanges(self):
        """
        Apply the state of the preferences box to the configuration and close the box.
        """
        self._applyRadio('temp_units', self.temp_units)
        self._applyRadio('wind_units', self.wind_units)
        self._applyRadio('pw_units', self.pw_units)

        self._config['preferences', 'color_style'] = self._color_style
        for item, color in PrefDialog._styles[self._color_style].items():
            self._config['preferences', item] = color

        self._config['preferences', 'readout_tr'] = self.variables[self.combo1.currentText()]
        self._config['preferences', 'readout_br'] = self.variables[self.combo2.currentText()]

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
            ('preferences', 'pw_units'):'in',
            ('preferences', 'color_style'):'standard',
            ('preferences', 'readout_br'): 'dwpc',
            ('preferences', 'readout_tr'): 'tmpc'
        }

        color_config = dict((('preferences', k), v) for k, v in PrefDialog._styles['standard'].items())
        pref_config.update(color_config)

        config.initialize(pref_config)

        color_style = config['preferences', 'color_style']
        for item, color in PrefDialog._styles[color_style].items():
            config['preferences', item] = color
