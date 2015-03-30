
import numpy as np

from PySide import QtGui, QtCore

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap.shapefile import Reader
import mpl_toolkits.basemap as basemap
import sys, os
import re
import urllib2

class Mapper(object):
    data_dir = os.path.join(os.path.dirname(basemap.__file__), "data/")
    min_lat = {'npstere':0., 'merc':-30., 'spstere':-90.}
    max_lat = {'npstere':90., 'merc':30., 'spstere':0.}

    def __init__(self, lambda_0, phi_0, proj='npstere'):
        self.proj = proj
        self.lambda_0 = lambda_0
        self.phi_0 = phi_0
        self.m = 6.6667e-7

    def getLambda0(self):
        return self.lambda_0

    def getPhi0(self):
        return self.phi_0

    def getLatBounds(self):
        return Mapper.min_lat[self.proj], Mapper.max_lat[self.proj]

    def __call__(self, lats, lons):
        return self._lltoxy_npstere(lats, lons, self.lambda_0, self.phi_0, self.m)

    # Functions to perform the map transformation to North Pole Stereographic
    # Equations from the SoM OBAN 2014 class
    def _get_sigma(self, phi_0, lats):
        sigma = (1. + np.sin(np.radians(phi_0)))/(1. + np.sin(np.radians(lats)))
        return sigma

    def _get_shifted_lon(self, lambda_0, lons):
        return lambda_0 - lons

    def _lltoxy_npstere(self, lats, lons, lambda_0, phi_0, m):
        rad_earth = 6.371e8
        sigma = self._get_sigma(phi_0, lats)
        lambdas = np.radians(self._get_shifted_lon(lambda_0 + 90, lons))
        x = m * sigma * rad_earth * np.cos(np.radians(lats)) * np.cos(lambdas)
        y = m * sigma * rad_earth * np.cos(np.radians(lats)) * np.sin(lambdas)

        return x, y

    def _loadShapefile(self, name):
        try:
            shf = Reader(os.path.join(Mapper.data_dir, name))
        except:
            raise IOError('error reading shapefile %s.shp' % name)
        fields = shf.fields
        try:
            shptype = shf.shapes()[0].shapeType
        except IndexError:
            return [], []
        bbox = shf.bbox.tolist()
        info = (shf.numRecords,shptype,bbox[0:2]+[0.,0.],bbox[2:]+[0.,0.])
        npoly = 0

        paths = []
        for shprec in shf.shapeRecords():
            shp = shprec.shape; rec = shprec.record
            npoly = npoly + 1
            if shptype != shp.shapeType:
                raise ValueError('readshapefile can only handle a single shape type per file')
            if shptype not in [1,3,5,8]:
                raise ValueError('readshapefile can only handle 2D shape types')
            verts = shp.points
            if shptype not in [1,8]: # not a Point or MultiPoint shape.
                parts = shp.parts.tolist()
                ringnum = 0
                for indx1,indx2 in zip(parts,parts[1:]+[len(verts)]):
                    ringnum = ringnum + 1
                    lons, lats = list(zip(*verts[indx1:indx2]))
                    if max(lons) > 721. or min(lons) < -721. or max(lats) > 91. or min(lats) < -91:
                        raise ValueError("shapefile must have lat/lon vertices")

                    path = QtGui.QPainterPath()
                    shp_x, shp_y = self(np.array(lats), np.array(lons))
                    path.moveTo(shp_x[0], shp_y[0])
                    for sx, sy in zip(shp_x, shp_y):
                        path.lineTo(sx, sy)

                    paths.append(path)
        return paths

    def _loadDat(self, name, res):
        bdatfile = open(os.path.join(Mapper.data_dir, name+'_' + res + '.dat'),'rb')
        bdatmetafile = open(os.path.join(Mapper.data_dir, name+'meta_' + res + '.dat'),'r')

        path = QtGui.QPainterPath()

        for line in bdatmetafile:
            lats, lons = [], []
            linesplit = line.split()
            area = float(linesplit[1])
            south = float(linesplit[3])
            north = float(linesplit[4])
            if area < 0:
                area = 1e30

            if north > 0 and area > 1500.:
                typ = int(linesplit[0])
                npts = int(linesplit[2])
                offsetbytes = int(linesplit[5])
                bytecount = int(linesplit[6])
                bdatfile.seek(offsetbytes,0)
                # read in binary string convert into an npts by 2
                # numpy array (first column is lons, second is lats).
                polystring = bdatfile.read(bytecount)
                # binary data is little endian.
                b = np.array(np.fromstring(polystring,dtype='<f4'),'f8')
                b.shape = (npts, 2)

                lb, ub = self.getLatBounds()
                idxs = np.where((b[:, 1] >= lb) & (b[:, 1] <= ub))[0]
                if len(idxs) < 2:
                    continue

                segs = (np.diff(idxs) == 1)
                try:
                    breaks = np.where(segs == 0)[0] + 1
                except IndexError:
                    breaks = []
                breaks = [ 0 ] + list(breaks) + [ -1 ]
 
                for idx in xrange(len(breaks) - 1):
                    if breaks[idx + 1] == -1:
                        seg_idxs = idxs[breaks[idx]:]
                    else:
                        seg_idxs = idxs[breaks[idx]:breaks[idx + 1]]

                    poly_xs, poly_ys = self(b[seg_idxs, 1], b[seg_idxs, 0])
                    if len(poly_xs) < 2 or len(poly_ys) < 2:
                        continue

                    path.moveTo(poly_xs[0], poly_ys[0])
                    for px, py in zip(poly_xs, poly_ys)[1:]:
                        path.lineTo(px, py)

        return path


    def loadBoundary(self, name):
        if name == 'coastlines':
            name = 'gshhs'
        if name == 'counties':
            bndy = self._loadShapefile('USCounties')
        else:
            res = 'h' if name == 'states' else 'i'
            bndy = self._loadDat(name, res)
        return bndy

class MapWidget(QtGui.QWidget):
    clicked = QtCore.Signal(dict)

    def __init__(self, data_source, init_time, **kwargs):
        super(MapWidget, self).__init__(**kwargs)
        self.scale = 0.60
        self.trans_x, self.trans_y = 0., 0.
        self.center_x, self.center_y = 0., 0.
        self.map_center_x, self.map_center_x = 0., 0.
        self.init_drag_x, self.init_drag_y = None, None
        self.dragging = False
        self.setMouseTracking(True)

        self.mapper = Mapper(-97.5, 60.)

        self.setDataSource(data_source, init_time, init=True)

        self.clicked_stn = None
        self.stn_readout = QtGui.QLabel(parent=self)
        self.stn_readout.setStyleSheet("QLabel { background-color:#000000; border-width: 0px; font-size: 16px; color: #FFFFFF; }")
        self.stn_readout.setText("")
        self.stn_readout.show()

        self.default_width, self.default_height = 800, 800
        self.setMinimumSize(self.width(), self.height())

#       self.setGeometry(300, 300, self.default_width, self.default_height)
        self.setWindowTitle('SHARPpy')
        self.stn_readout.setFixedWidth(self.width() - 20)

        self.map_center_x, self.map_center_y = self.width() / 2, -8 * self.height() / 10

        self.initMap()
        self.initUI()

    def initUI(self):
        self.center_x, self.center_y = self.width() / 2, self.height() / 2

        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.drawMap()

    def initMap(self):
        self._coast_path = self.mapper.loadBoundary('coastlines')
        self._country_path = self.mapper.loadBoundary('countries')
        self._state_path = self.mapper.loadBoundary('states')
        self._county_path = self.mapper.loadBoundary('counties')

        path = QtGui.QPainterPath()
        for lon in xrange(0, 360, 20):
            lats = np.linspace(0, 90, 2)
            lx, ly = self.mapper(lats, lon)

            path.moveTo(lx[0], ly[0])
            for x, y in zip(lx, ly)[1:]:
                path.lineTo(x, y)

        for lat in xrange(0, 90, 15):
            lons = np.arange(self.mapper.getLambda0(), self.mapper.getLambda0() + 360, 90)
            rx, ry = self.mapper(lat, lons)
            x_min, x_max = rx.min(), rx.max()
            y_min, y_max = ry.min(), ry.max()
            path.addEllipse(x_min, y_min, x_max - x_min, y_max - y_min)
        self._grid_path = path

    def setDataSource(self, data_source, data_time, init=False):
        self.cur_source = data_source
        self.setCurrentTime(data_time, init=init)

    def setCurrentTime(self, data_time, init=False):
        self.current_time = data_time
        self.clicked_stn = None
        self.clicked.emit(None)

        self.points = self.cur_source.getAvailableAtTime(self.current_time)
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

        if not init:
            self.drawMap()
            self.update()

    def drawMap(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)

        self.plotBitMap.fill(QtCore.Qt.black)

        map_center_x = self.map_center_x + self.trans_x
        map_center_y = self.map_center_y + self.trans_y

        qp.translate(map_center_x, map_center_y)
        qp.scale(1. / self.scale, 1. / self.scale)
        self.transform = qp.transform()

        qp.setPen(QtGui.QPen(QtGui.QColor('#333333'))) #, self.scale, QtCore.Qt.DashLine
        qp.drawPath(self._grid_path)

        # Modify the scale thresholds according to the ratio of the area of the plot to the default area
        default_area = self.default_width * self.default_height
        actual_area = self.width() * self.height()
        scaled_area = np.sqrt(default_area / float(actual_area))

        if self.scale < 0.10 * scaled_area:
            window_rect = QtCore.QRect(0, 0, self.width(), self.height())

            max_comp = 102
            full_scale = 0.05 * scaled_area
            zero_scale = 0.10 * scaled_area
            comp = max_comp * min(max((zero_scale - self.scale) / (zero_scale - full_scale), 0), 1)
            color = '#' + ("{0:02x}".format(int(round(comp)))) * 3

            qp.setPen(QtGui.QPen(QtGui.QColor(color)))
            for cp in self._county_path:
                if self.transform.mapRect(cp.boundingRect()).intersects(window_rect):
                    qp.drawPath(cp)

        qp.setPen(QtGui.QPen(QtGui.QColor('#999999')))
        qp.drawPath(self._state_path)

        qp.setPen(QtGui.QPen(QtCore.Qt.white))
        qp.drawPath(self._coast_path)
        qp.drawPath(self._country_path)

        self.drawStations(qp)
        qp.end()

    def drawStations(self, qp):
        stn_xs, stn_ys = self.mapper(self.stn_lats, self.stn_lons)
        lb_lat, ub_lat = self.mapper.getLatBounds()
        size = 3 * self.scale

        unselected_color = QtCore.Qt.red
        selected_color = QtCore.Qt.green

        window_rect = QtCore.QRect(0, 0, self.width(), self.height())
        for stn_x, stn_y, stn_lat, stn_id in zip(stn_xs, stn_ys, self.stn_lats, self.stn_ids):
            if self.clicked_stn == stn_id:
                color = selected_color
            else:
                color = unselected_color

            if lb_lat <= stn_lat and stn_lat <= ub_lat and window_rect.contains(*self.transform.map(stn_x, stn_y)):
                qp.setPen(QtGui.QPen(color))
                qp.setBrush(QtGui.QBrush(color))
                qp.drawEllipse(QtCore.QPointF(stn_x, stn_y), size, size)

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

        self.initUI()

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

    def mouseReleaseEvent(self, e):
        self.init_drag_x, self.init_drag_y = None, None
        self.map_center_x += self.trans_x
        self.map_center_y += self.trans_y
        self.trans_x, self.trans_y = 0, 0

        if not self.dragging:
            stn_xs, stn_ys = self.mapper(self.stn_lats, self.stn_lons)
            stn_xs, stn_ys = zip(*[ self.transform.map(sx, sy) for sx, sy in zip(stn_xs, stn_ys)  ])
            stn_xs = np.array(stn_xs)
            stn_ys = np.array(stn_ys)
            dists = np.hypot(stn_xs - e.x(), stn_ys - e.y())
            stn_idx = np.argmin(dists)
            if dists[stn_idx] <= 5:
                self.clicked_stn = self.stn_ids[stn_idx]
                self.clicked.emit(self.points[stn_idx])

                self.drawMap()
                self.update()

        self.dragging = False

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

    def _checkStations(self, e):
        stn_xs, stn_ys = self.mapper(self.stn_lats, self.stn_lons)
        stn_xs, stn_ys = zip(*[ self.transform.map(sx, sy) for sx, sy in zip(stn_xs, stn_ys) ])
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
                label_x = stn_x - fm.width(self.stn_names[stn_idx])
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

            self.stn_readout.setText(self.stn_names[stn_idx])
            self.stn_readout.move(label_x + sgn_x * label_offset, label_y + sgn_y * label_offset)
            self.stn_readout.setFixedWidth(fm.width(self.stn_names[stn_idx]))
            self.stn_readout.setAlignment(align)
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.stn_readout.setText("")
            self.stn_readout.setFixedWidth(0)
            self.stn_readout.move(self.width(), self.height())
            self.stn_readout.setAlignment(QtCore.Qt.AlignLeft)
            self.unsetCursor()
