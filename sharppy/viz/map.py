
import numpy as np
import sharppy
from PySide import QtGui, QtCore
from datetime import datetime
import sys, os
import re

class Mapper(object):
    data_dir = os.path.join(os.path.dirname(sharppy.__file__), 'databases', 'shapefiles')
    min_lat = {'npstere':0., 'merc':-35., 'spstere':-90.}
    max_lat = {'npstere':90., 'merc':35., 'spstere':0.}

    def __init__(self, lambda_0, phi_0, proj='npstere'):
        self.proj = proj
        self.lambda_0 = lambda_0
        self.phi_0 = phi_0
        if proj == 'spstere':
            self.phi_0 = -np.abs(self.phi_0)

        self.m = 6.6667e-7
        self.rad_earth = 6.371e8
        self._bnds = {}

    def getLambda0(self):
        return self.lambda_0

    def setLambda0(self, lambda_0):
        self.lambda_0 = lambda_0

    def getPhi0(self):
        return self.phi_0

    def setProjection(self, proj):
        if proj not in ['npstere', 'spstere', 'merc']:
            raise ValueError("Projection must be one of 'npstere', 'spstere', or 'merc'; got '%s'." % proj)
        self.proj = proj

        if proj == 'spstere':
            self.phi_0 = -np.abs(self.phi_0)
        elif proj == 'npstere':
            self.phi_0 = np.abs(self.phi_0)

    def getProjection(self):
        return self.proj

    def getCoordPaths(self):
        path = QtGui.QPainterPath()
        lb_lat, ub_lat = Mapper.min_lat[self.proj], Mapper.max_lat[self.proj]

        if self.proj == 'npstere':
            for lon in range(0, 360, 20):
                lats = np.linspace(lb_lat, ub_lat, 2)
                lx, ly = self(lats, lon)

                path.moveTo(lx[0], ly[0])
                for x, y in zip(lx[1:], ly[1:]):
                    path.lineTo(x, y)

            for lat in range(int(lb_lat), int(ub_lat), 15):
                lons = np.arange(self.getLambda0(), self.getLambda0() + 360, 90)
                rx, ry = self(lat, lons)
                x_min, x_max = rx.min(), rx.max()
                y_min, y_max = ry.min(), ry.max()
                path.addEllipse(x_min, y_min, x_max - x_min, y_max - y_min)

        elif self.proj == 'merc':
            for lon in range(-180, 180 + 20, 20):
                lats = np.linspace(lb_lat, ub_lat, 2)
                lx, ly = self(lats, lon)

                path.moveTo(lx[0], ly[0])
                for x, y in zip(lx[1:], ly[1:]):
                    path.lineTo(x, y)

            lat_spc = 10
            rnd_lat_lb = np.ceil(lb_lat / lat_spc) * lat_spc
            rnd_lat_ub = np.floor(ub_lat / lat_spc) * lat_spc
            lat_lines = list(range(int(rnd_lat_lb), int(rnd_lat_ub + lat_spc), lat_spc))
            if rnd_lat_lb != lb_lat:
                lat_lines = [int(lb_lat)] + lat_lines 
            if rnd_lat_ub != ub_lat:
                lat_lines = lat_lines + [int(ub_lat)]

            for lat in lat_lines:
                lons = np.linspace(-180, 180, 2)
                lx, ly = self(lat, lons)

                path.moveTo(lx[0], ly[0])
                for x, y in zip(lx[1:], ly[1:]):
                    path.lineTo(x, y)

        elif self.proj == 'spstere':
            for lon in range(0, 360, 20):
                lats = np.linspace(lb_lat, ub_lat, 2)
                lx, ly = self(lats, lon)

                path.moveTo(lx[0], ly[0])
                for x, y in zip(lx[1:], ly[1:]):
                    path.lineTo(x, y)

            for lat in range(int(ub_lat), int(lb_lat), -15):
                lons = np.arange(self.getLambda0(), self.getLambda0() + 360, 90)
                rx, ry = self(lat, lons)
                x_min, x_max = rx.min(), rx.max()
                y_min, y_max = ry.min(), ry.max()
                path.addEllipse(x_min, y_min, x_max - x_min, y_max - y_min)

        return path

    def getLatBounds(self):
        return Mapper.min_lat[self.proj], Mapper.max_lat[self.proj]

    def __call__(self, coord1, coord2, inverse=False):
        if inverse:
            if self.proj in ['npstere', 'spstere']:
                return self._xytoll_stere(coord1, coord2, self.lambda_0, self.phi_0, self.m, self.rad_earth)
            elif self.proj in ['merc']:
                return self._xytoll_merc(coord1, coord2, self.lambda_0, self.m, self.rad_earth)
        else:
            if self.proj in ['npstere', 'spstere']:
                return self._lltoxy_stere(coord1, coord2, self.lambda_0, self.phi_0, self.m, self.rad_earth)
            elif self.proj in ['merc']:
                return self._lltoxy_merc(coord1, coord2, self.lambda_0, self.m, self.rad_earth)

    # Functions to perform the map transformation to North Pole Stereographic
    # Equations from the SoM OBAN 2014 class
    # Functions adapted for either hemisphere and inverse transformations added by Tim Supinie, April 2015
    def _get_sigma(self, phi_0, lats, south_hemis=False):
        sign = -1 if south_hemis else 1
        sigma = (1. + np.sin(np.radians(sign * phi_0))) / (1. + np.sin(np.radians(sign * lats)))
        return sigma

    def _get_shifted_lon(self, lambda_0, lons, south_hemis=False):
        sign = -1 if south_hemis else 1
        return sign * (lambda_0 - lons)

    def _lltoxy_stere(self, lats, lons, lambda_0, phi_0, m, rad_earth):
        sigma = self._get_sigma(phi_0, lats, south_hemis=(phi_0 < 0))
        lambdas = np.radians(self._get_shifted_lon(lambda_0 + 90, lons, south_hemis=(phi_0 < 0)))
        x = m * sigma * rad_earth * np.cos(np.radians(lats)) * np.cos(lambdas)
        y = m * sigma * rad_earth * np.cos(np.radians(lats)) * np.sin(lambdas)
        return x, y

    def _xytoll_stere(self, xs, ys, lambda_0, phi_0, m, rad_earth):
        sign = -1 if (phi_0 < 0) else 1

        lon = (lambda_0 + 90 - sign * np.degrees(np.arctan2(ys, xs)))
        lat = sign * np.degrees(2 * np.arctan(rad_earth * m * (1 + sign * np.sin(np.radians(phi_0))) / np.hypot(xs, ys)) - np.pi / 2)

        if lon < -180: lon += 360
        elif lon > 180: lon -= 360
        return lat, lon

    # Function to perform map transformation to and from Mercator projection
    def _lltoxy_merc(self, lats, lons, lambda_0, m, rad_earth):
        x = m * rad_earth * (np.radians(lons) - np.radians(lambda_0))
        y = -m * rad_earth * np.log(np.tan(np.pi / 4 + np.radians(lats) / 2))

        if type(x) in [ np.ndarray ] or type(y) in [ np.ndarray ]:
            if type(x) not in [ np.ndarray ]:
                x = x * np.ones(y.shape)
            if type(y) not in [ np.ndarray ]:
                y = y * np.ones(x.shape)
        return x, y

    def _xytoll_merc(self, xs, ys, lambda_0, m, rad_earth):
        lon = np.degrees(np.radians(lambda_0) + xs / (m * rad_earth))
        lat = -np.degrees(2 * np.arctan(np.exp(ys / (m * rad_earth))) - np.pi / 2)
        return lat, lon

    def _loadDat(self, name, res):
        """
        Code shamelessly lifted from Basemap's data file parser by Jeff Whitaker.
        http://matplotlib.org/basemap/
        """
        def segmentPath(b, lb_lat, ub_lat):
            paths = []
            if b[:, 1].max() <= lb_lat or b[:, 1].min() >= ub_lat:
                return paths

            idxs = np.where((b[:, 1] >= lb_lat) & (b[:, 1] <= ub_lat))[0]
            if len(idxs) < 2:
                return paths

            segs = (np.diff(idxs) == 1)
            try:
                breaks = np.where(segs == 0)[0] + 1
            except IndexError:
                breaks = []
            breaks = [ 0 ] + list(breaks) + [ -1 ]
 
            for idx in range(len(breaks) - 1):
                if breaks[idx + 1] == -1:
                    seg_idxs = idxs[breaks[idx]:]
                else:
                    seg_idxs = idxs[breaks[idx]:breaks[idx + 1]]

                if len(seg_idxs) >= 2:
                    paths.append(b[seg_idxs, ::-1])

            return paths

        bdatfile = open(os.path.join(Mapper.data_dir, name + '_' + res + '.dat'), 'rb')
        bdatmetafile = open(os.path.join(Mapper.data_dir, name + 'meta_' + res + '.dat'), 'r')

        projs = ['npstere', 'merc', 'spstere']
        paths = dict( (p, []) for p in projs )

#       old_proj = self.proj
        for line in bdatmetafile:
            lats, lons = [], []
            linesplit = line.split()
            area = float(linesplit[1])
            south = float(linesplit[3])
            north = float(linesplit[4])
            if area < 0:
                area = 1e30

            if area > 1500.:
                typ = int(linesplit[0])
                npts = int(linesplit[2])
                offsetbytes = int(linesplit[5])
                bytecount = int(linesplit[6])
                bdatfile.seek(offsetbytes,0)
                # read in binary string convert into an npts by 2
                # numpy array (first column is lons, second is lats).
                polystring = bdatfile.read(bytecount)
                # binary data is little endian.
                #b = np.array(np.fromstring(polystring,dtype='<f4'),'f8')
                b = np.array(np.frombuffer(polystring,dtype='<f4'),'f8')
                b.shape = (npts, 2)

                if np.any(b[:, 0] > 180):
                    b[:, 0] -= 360

                for proj in projs:
                    lb_lat, ub_lat = Mapper.min_lat[proj], Mapper.max_lat[proj]
                    path = segmentPath(b, lb_lat, ub_lat)
                    paths[proj].extend(path)

        return paths


    def getBoundary(self, name):
        if name == 'coastlines':
            name = 'gshhs'

        if name == 'states':
            res = 'h'
        elif name == 'uscounties':
            res = 'f'
        else:
            res = 'i'

        if name not in self._bnds:
            self._bnds[name] = self._loadDat(name, res)

        paths = []
        for bnd in self._bnds[name][self.proj]:
            path = QtGui.QPainterPath()

            path_lats, path_lons = list(zip(*bnd))
            path_x, path_y = self(np.array(path_lats), np.array(path_lons))

            path.moveTo(path_x[0], path_y[0])
            for px, py in zip(path_x[1:], path_y[1:]):
                path.lineTo(px, py)

            paths.append(path)
        return paths

class MapWidget(QtGui.QWidget):
    clicked = QtCore.Signal(dict)

    def __init__(self, data_source, init_time, async_object, **kwargs):
        config = kwargs.get('cfg', None)
        del kwargs['cfg']

        super(MapWidget, self).__init__(**kwargs)

        self.trans_x, self.trans_y = 0., 0.
        self.center_x, self.center_y = 0., 0.
        self.init_drag_x, self.init_drag_y = None, None
        self.dragging = False
        self.map_rot = 0.0
        self.setMouseTracking(True)

        self.has_internet = True

        self.init_scale = 0.6
        if config is None or not ('map', 'proj') in config:
            self.scale = self.init_scale
            self.map_center_x, self.map_center_y = 0., 0.
            std_lon = -97.5
            proj = 'npstere'
            init_from_config = False
        else:
            proj = config['map', 'proj']
            std_lon = float(config['map', 'std_lon'])
            self.scale = float(config['map', 'scale'])
            self.map_center_x = float(config['map', 'center_x'])
            self.map_center_y = float(config['map', 'center_y'])
            init_from_config = True

        self.mapper = Mapper(std_lon, 60., proj=proj)

        self.stn_lats = np.array([])
        self.stn_lons = np.array([])
        self.stn_ids = []
        self.stn_names = []

        self.default_width, self.default_height = self.width(), self.height()
        self.setMinimumSize(self.width(), self.height())

        self.clicked_stn = None
        self.stn_readout = QtGui.QLabel(parent=self)
        self.stn_readout.setStyleSheet("QLabel { background-color:#000000; border-width: 0px; font-size: 16px; color: #FFFFFF; }")
        self.stn_readout.setText("")
        self.stn_readout.show()
        self.stn_readout.move(self.width(), self.height())

        self.load_readout = QtGui.QLabel(parent=self)
        self.load_readout.setStyleSheet("QLabel { background-color:#000000; border-width: 0px; font-size: 18px; color: #FFFFFF; }")
        self.load_readout.setText("Loading ...")
        self.load_readout.setFixedWidth(100)
        self.load_readout.show()
        self.load_readout.move(self.width(), self.height())

        self.latlon_readout = QtGui.QLabel(parent=self)
        self.latlon_readout.setStyleSheet("QLabel { background-color:#000000; border-width: 0px; font-size: 18px; color: #FFFFFF; }")
        self.latlon_readout.setText("")
        self.latlon_readout.setFixedWidth(150)
        self.latlon_readout.show()
        self.latlon_readout.move(10, 10)

        self.no_internet = QtGui.QLabel(parent=self)
        self.no_internet.setStyleSheet("QLabel { background-color:#000000; border-width: 0px; font-size: 32px; color: #FFFFFF; }")
        self.no_internet.setText("No Internet Connection")
        self.no_internet.show()
        txt_width = self.no_internet.fontMetrics().width(self.no_internet.text())

        self._async = async_object
        self.no_internet.setFixedWidth(txt_width)
        self.no_internet.move(self.width(), self.height())

        self.setDataSource(data_source, init_time, init=True)
        self.setWindowTitle('SHARPpy')

        if not init_from_config:
            self.resetViewport()
            self.saveProjection(config)

        self.pt_x, self.pt_y = None, None

        self.initMap()
        self.initUI()

    def initUI(self):
        self.center_x, self.center_y = self.width() / 2, self.height() / 2

        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.backgroundBitMap = self.plotBitMap.copy()
        self.drawMap()

    def initMap(self):
        self._coast_path = self.mapper.getBoundary('coastlines')
        self._country_path = self.mapper.getBoundary('countries')
        self._state_path = self.mapper.getBoundary('states')
        self._county_path = self.mapper.getBoundary('uscounties')

        self._grid_path = self.mapper.getCoordPaths()

    def setDataSource(self, data_source, data_time, init=False):
        self.cur_source = data_source
        self.setCurrentTime(data_time, init=init)

    def setCurrentTime(self, data_time, init=False):
                
        self.clicked_stn = None
        self.clicked.emit(None)

        self._showLoading()

        def update(points):
            self.points = points[0]

            self.stn_lats = np.array([ p['lat'] for p in self.points ])
            self.stn_lons = np.array([ p['lon'] for p in self.points ])
            self.stn_ids = [ p['srcid'] for p in self.points ]
            self.stn_names = []
            for p in self.points:
                if p['icao'] != "":
                    id_str = " (%s)" % p['icao']
                else:
                    id_str = ""
                if p['state'] != "":
                    pol_str = ", %s" % p['state']
                elif p['country'] != "":
                    pol_str = ", %s" % p['country']
                else:
                    pol_str = ""

                nm = p['name']
                if id_str == "" and pol_str == "":
                    nm = nm.upper()
                name = "%s%s%s" % (nm, pol_str, id_str)
                self.stn_names.append(name)

            self._hideLoading()

            if not init:
                self.drawMap()
                self.update()
       
        self.current_time = data_time
        getPoints = lambda: self.cur_source.getAvailableAtTime(self.current_time)

        if init:
            points = getPoints()
            update([ points ])
        else:
            self._async.post(getPoints, update)

    def setProjection(self, proj):
        old_proj = self.mapper.getProjection()
        self.mapper.setProjection(proj)
        self.resetViewport()
        self._showLoading()

        def update(args):
            self.resetViewport()
            self.drawMap()
            self._hideLoading()
            self.update()
            return

        self._async.post(self.initMap, update)

    def resetViewport(self, ctr_lat=None, ctr_lon=None):
        self.map_center_x = self.width() / 2
        if ctr_lat is not None and ctr_lon is not None:
            center_x, center_y = self.mapper(ctr_lat, ctr_lon)
            self.map_center_y = -center_y + self.height() / 2
            self.map_center_y = self.center_y - (self.center_y - self.map_center_y) / self.scale
        else:
            self.scale = self.init_scale
            self.map_rot = 0.
            proj = self.mapper.getProjection()
            if proj == 'npstere':
                self.map_center_y = -13 * self.height() / 10 + self.height() / 2 
            elif proj == 'merc':
                self.map_center_y = self.height() / 2
            elif proj == 'spstere':
                self.map_center_y = 13 * self.height() / 10 + self.height() / 2

    def drawMap(self):
        def mercRotate(qp, center_x, center_y, angle):
            center_lat, center_lon = self.mapper(center_x - self.width() / 2, center_y - self.height() / 2, inverse=True)
            center_lon -= angle
            new_center_x, new_center_y = self.mapper(center_lat, center_lon)
            new_center_x += self.width() / 2
            new_center_y += self.height() / 2
            qp.translate((new_center_x - center_x) / self.scale, (new_center_y - center_y) / self.scale)
            return new_center_x, new_center_y

        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)

        self.plotBitMap.fill(QtCore.Qt.black)

        map_center_x = self.map_center_x + self.trans_x
        map_center_y = self.map_center_y + self.trans_y

        qp.translate(map_center_x, map_center_y)
        proj = self.mapper.getProjection()

        if proj == 'npstere':
            qp.rotate(self.map_rot)
        elif proj == 'merc':
            new_center_x, new_center_y = mercRotate(qp, map_center_x, map_center_y, self.map_rot)
        elif proj == 'spstere':
            qp.rotate(-self.map_rot)

        qp.scale(1. / self.scale, 1. / self.scale)

        self.drawPolitical(qp)
        self.backgroundBitMap = self.plotBitMap.copy()
        self.drawStations(qp)

        qp.end()

    def drawPolitical(self, qp):
        self.transform = qp.transform()
        window_rect = QtCore.QRect(0, 0, self.width(), self.height())

        qp.setPen(QtGui.QPen(QtGui.QColor('#333333'))) #, self.scale, QtCore.Qt.DashLine
        qp.drawPath(self._grid_path)

        # Modify the scale thresholds according to the ratio of the area of the plot to the default area
        default_area = self.default_width * self.default_height
        actual_area = self.width() * self.height()
        scaled_area = np.sqrt(default_area / float(actual_area))

        if self.scale < 0.15 * scaled_area:

            max_comp = 102
            full_scale = 0.10 * scaled_area
            zero_scale = 0.15 * scaled_area
            comp = max_comp * min(max((zero_scale - self.scale) / (zero_scale - full_scale), 0), 1)
            color = '#' + ("{0:02x}".format(int(round(comp)))) * 3

            qp.setPen(QtGui.QPen(QtGui.QColor(color)))
            for cp in self._county_path:
                if self.transform.mapRect(cp.boundingRect()).intersects(window_rect):
                    qp.drawPath(cp)

        qp.setPen(QtGui.QPen(QtGui.QColor('#999999')))
        for sp in self._state_path:
            if self.transform.mapRect(sp.boundingRect()).intersects(window_rect):
                qp.drawPath(sp)

        qp.setPen(QtGui.QPen(QtCore.Qt.white))
        for cp in self._coast_path:
            if self.transform.mapRect(cp.boundingRect()).intersects(window_rect):
                qp.drawPath(cp)

        for cp in self._country_path:
            if self.transform.mapRect(cp.boundingRect()).intersects(window_rect):
                qp.drawPath(cp)

    def drawStations(self, qp):
        stn_xs, stn_ys = self.mapper(self.stn_lats, self.stn_lons + self.map_rot)
        lb_lat, ub_lat = self.mapper.getLatBounds()
        size = 3 * self.scale

        unselected_color = QtCore.Qt.red
        selected_color = QtCore.Qt.green

        window_rect = QtCore.QRect(0, 0, self.width(), self.height())
        clicked_x, clicked_y, clicked_lat, clicked_id = None, None, None, None
        color = unselected_color
        for stn_x, stn_y, stn_lat, stn_id in zip(stn_xs, stn_ys, self.stn_lats, self.stn_ids):
            if self.clicked_stn == stn_id:
                clicked_x = stn_x
                clicked_y = stn_y
                clicked_lat = stn_lat
                clicked_id = stn_id
            else:
               if lb_lat <= stn_lat and stn_lat <= ub_lat and window_rect.contains(*self.transform.map(stn_x, stn_y)):
                    qp.setPen(QtGui.QPen(color))
                    qp.setBrush(QtGui.QBrush(color))
                    qp.drawEllipse(QtCore.QPointF(stn_x, stn_y), size, size)
        
        color = selected_color
        if clicked_lat is not None and lb_lat <= clicked_lat and clicked_lat <= ub_lat and window_rect.contains(*self.transform.map(clicked_x, clicked_y)):
            qp.setPen(QtGui.QPen(color))
            qp.setBrush(QtGui.QBrush(color))
            qp.drawEllipse(QtCore.QPointF(clicked_x, clicked_y), size, size)

        if self.cur_source.getName() == "Local WRF-ARW" and self.pt_x != None:
            qp.drawEllipse(QtCore.QPointF(self.pt_x, self.pt_y), size, size)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()

    def resizeEvent(self, e):
        old_size = e.oldSize()
        new_size = e.size()

        if old_size.width() == -1 and old_size.height() == -1:
            old_size = self.size()

        self.map_center_x += (new_size.width() - old_size.width()) / 2.
        self.map_center_y += (new_size.height() - old_size.height()) / 2.
        self._hideLoading()
        self.hasInternet(self.has_internet)

        self.initUI()

    def keyPressEvent(self, e):
        if e.key() == 61:
            delta = -100
        elif e.key() == 45:
            delta = 100
        scale_fac = 10 ** (delta / 1000.)

        scaled_size = float(min(self.default_width, self.default_height)) / min(self.width(), self.height())
        if self.scale * scale_fac > 2.5 * scaled_size:
            scale_fac = 2.5 * scaled_size / self.scale

        self.scale *= scale_fac
        self.map_center_x = self.center_x - (self.center_x - self.map_center_x) / scale_fac
        self.map_center_y = self.center_y - (self.center_y - self.map_center_y) / scale_fac

        self.drawMap()
        self.update()

    def mousePressEvent(self, e):
        self.init_drag_x, self.init_drag_y = e.x(), e.y()

    def mouseMoveEvent(self, e):
        if self.init_drag_x is not None and self.init_drag_y is not None:
            self.dragging = True
            self.trans_x = e.x() - self.init_drag_x
            self.trans_y = e.y() - self.init_drag_y
            self.drawMap()
            self.update()
        self._checkStations(e)

        trans_inv, is_invertible = self.transform.inverted()
        mouse_x, mouse_y = trans_inv.map(e.x(), e.y())
        lat, lon = self.mapper(mouse_x, mouse_y, inverse=True)
        lon -= self.map_rot

        if lon > 180: 
            lon -= 360.
        elif lon <= -180: 
            lon += 360.

        self.latlon_readout.setText("%.3f; %.3f" % (lat, lon))

    def mouseReleaseEvent(self, e):
        self.init_drag_x, self.init_drag_y = None, None
        self.map_center_x += self.trans_x
        self.map_center_y += self.trans_y
        self.trans_x, self.trans_y = 0, 0

        if not self.dragging and len(self.stn_lats) > 0:
            lb_lat, ub_lat = self.mapper.getLatBounds()
            idxs = np.array([ idx for idx, slat in enumerate(self.stn_lats) if lb_lat <= slat <= ub_lat ])

            stn_xs, stn_ys = self.mapper(self.stn_lats[idxs], self.stn_lons[idxs] + self.map_rot)
            stn_xs, stn_ys = list(zip(*[ self.transform.map(sx, sy) for sx, sy in zip(stn_xs, stn_ys)  ]))
            stn_xs = np.array(stn_xs)
            stn_ys = np.array(stn_ys)
            dists = np.hypot(stn_xs - e.x(), stn_ys - e.y())
            stn_idx = np.argmin(dists)
            if dists[stn_idx] <= 5:
                self.clicked_stn = self.stn_ids[idxs[stn_idx]]
                self.clicked.emit(self.points[idxs[stn_idx]])

                self.drawMap()
                self.update()
        if not self.dragging and self.cur_source.getName() == "Local WRF-ARW":
            trans_inv, is_invertible = self.transform.inverted()
            self.pt_x, self.pt_y = trans_inv.map(e.x(), e.y())
            lat, lon = self.mapper(self.pt_x, self.pt_y, inverse=True)
            lon -= self.map_rot
            self.clicked.emit((lon, lat))
            self.drawMap()
            self.update()

        self.dragging = False

    def mouseDoubleClickEvent(self, e):
        trans_inv, is_invertible = self.transform.inverted()
        mouse_x, mouse_y = trans_inv.map(e.x(), e.y())
        lat, lon = self.mapper(mouse_x, mouse_y, inverse=True)
        lon -= self.map_rot

        self.map_rot += (lon - self.mapper.getLambda0())

#       if self.map_rot > 180:
#           self.map_rot -= 360
#       if self.map_rot <= -180:
#           self.map_rot += 360

        self.mapper.setLambda0(lon)
        self._showLoading()

        def update(args):
            self.resetViewport(ctr_lat=lat, ctr_lon=lon)
            self.drawMap()
            self._hideLoading()
            self.update()
            return

        update(None)
#       self._async.post(self.initMap, update)

    def wheelEvent(self, e):
        max_speed = 75
        delta = max(min(-e.delta(), max_speed), -max_speed)
        scale_fac = 10 ** (delta / 1000.)

        scaled_size = float(min(self.default_width, self.default_height)) / min(self.width(), self.height())
        if self.scale * scale_fac > 2.5 * scaled_size:
            scale_fac = 2.5 * scaled_size / self.scale

        self.scale *= scale_fac
        self.map_center_x = self.center_x - (self.center_x - self.map_center_x) / scale_fac
        self.map_center_y = self.center_y - (self.center_y - self.map_center_y) / scale_fac

        self.drawMap()
        self._checkStations(e)
        self.update()

    def saveProjection(self, config):
        map_center_x = self.map_center_x + (self.default_width  - self.width() ) / 2.
        map_center_y = self.map_center_y + (self.default_height - self.height()) / 2.

        config['map', 'proj']     = self.mapper.getProjection()
        config['map', 'std_lon']  = self.mapper.getLambda0()
        config['map', 'scale']    = self.scale
        config['map', 'center_x'] = map_center_x
        config['map', 'center_y'] = map_center_y

    def getBackground(self):
        return self.backgroundBitMap

    def hasInternet(self, has_connection):
        self.has_internet = has_connection

        if has_connection:
            self.no_internet.move(self.width(), self.height())
        else:
            met = self.no_internet.fontMetrics()
            txt_width = met.width(self.no_internet.text())
            txt_height = met.height()
            self.no_internet.move((self.width() - txt_width) / 2, (self.height() - txt_height) / 2)

    def _showLoading(self):
        self.load_readout.move(10, self.height() - 25)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

    def _hideLoading(self):
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.load_readout.move(self.width(), self.height())

    def _checkStations(self, e):
#       if len(self.stn_lats) == 0:
#           return

        lb_lat, ub_lat = self.mapper.getLatBounds()
        idxs = np.array([ idx for idx, slat in enumerate(self.stn_lats) if lb_lat <= slat <= ub_lat ])
        if len(idxs) == 0:
            return

        stn_xs, stn_ys = self.mapper(self.stn_lats[idxs], self.stn_lons[idxs] + self.map_rot)
        stn_xs, stn_ys = list(zip(*[ self.transform.map(sx, sy) for sx, sy in zip(stn_xs, stn_ys) ]))
        stn_xs = np.array(stn_xs)
        stn_ys = np.array(stn_ys)
        dists = np.hypot(stn_xs - e.x(), stn_ys - e.y())
        stn_idx = np.argmin(dists)
        if dists[stn_idx] <= 5:
            stn_x, stn_y = stn_xs[stn_idx], stn_ys[stn_idx]
            fm = QtGui.QFontMetrics(QtGui.QFont(self.font().rawName(), 16))

            label_offset = 5
            align = 0
            if stn_x > self.width() / 2:
                sgn_x = -1
                label_x = stn_x - fm.width(self.stn_names[idxs[stn_idx]])
                align |= QtCore.Qt.AlignRight
            else:
                sgn_x = 1
                label_x = stn_x
                align |= QtCore.Qt.AlignLeft

            if stn_y > self.height() / 2:
                sgn_y = -1
                label_y = stn_y - fm.height()
                align |= QtCore.Qt.AlignBottom
            else:
                sgn_y = 1
                label_y = stn_y
                align |= QtCore.Qt.AlignTop

            self.stn_readout.setText(self.stn_names[idxs[stn_idx]])
            self.stn_readout.move(label_x + sgn_x * label_offset, label_y + sgn_y * label_offset)
            self.stn_readout.setFixedWidth(fm.width(self.stn_names[idxs[stn_idx]]))
            self.stn_readout.setAlignment(align)
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.stn_readout.setText("")
            self.stn_readout.setFixedWidth(0)
            self.stn_readout.move(self.width(), self.height())
            self.stn_readout.setAlignment(QtCore.Qt.AlignLeft)
            self.unsetCursor()
