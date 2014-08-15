#Copyright (C) 2014  Triantafyllis Nikolaos
#
#This file is part of Scisola.
#
#    Scisola is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Scisola is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Scisola.  If not, see <http://www.gnu.org/licenses/>.


#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True

from PyQt4 import QtCore, QtGui
import os
import shutil

import lib.gui.review

import lib.process
import lib.origin
import lib.database
import lib.stream
import lib.settings


class ReviewWindow(QtGui.QMainWindow, lib.gui.review.Ui_MainWindow):
    def __init__(self, id=0, parent=None):
        super(ReviewWindow, self).__init__(parent)
        # inherited from Ui_MainWindow
        self.setupUi(self)
        self.parent = parent
        self.id = id
        self.origin = None
        self.station_list = []
        self.review_list = []
        self.model = None
        self.thread = None


    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        self.parent.refreshOriginsT20()
        self.parent.setEnabled(True)
        self.parent.main()


    def main(self):
        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.showMaximized()
        self.setContents()
        self.setConnections()


    def setConnections(self):
        self.tableView.doubleClicked.connect(self.streamClicked)
        self.pushButton.clicked.connect(self.reviseClicked)
        self.pushButton_2.clicked.connect(self.deleteClicked)


    def setContents(self):
        self.origin = None
        self.station_list = []
        self.review_list = []
        self.origin, self.station_list = self.parent.db_scisola.loadOrigin(
                                                       self.id,
                                                       self.origin,
                                                       self.station_list)

        for _station in self.station_list:

            # get all N, E, Z possible streams
            _N = [x for x in _station.stream_list if x.code[2] == 'N']
            _E = [x for x in _station.stream_list if x.code[2] == 'E']
            _Z = [x for x in _station.stream_list if x.code[2] == 'Z']

            self.review_list.append([streamExist(_N),
                                     streamExist(_E),
                                     streamExist(_Z)])

        if self.origin and self.station_list:
            if not self.origin.automatic:
                _type = "revised"
            else:
                _type = "automatic"

            self.label_131.setText(str(self.origin.id))
            self.label_133.setText(str(self.origin.timestamp))
            self.label_2.setText(str(self.origin.datetime).split()[0])
            self.label_10.setText(str(self.origin.datetime).split()[1])
            self.label_76.setText(_type)
            self.label_129.setText(str(self.origin.event_id))
            self.label_14.setText(str(self.origin.mt.cent_time))
            self.label_13.setText(str(self.origin.mt.cent_latitude))
            self.label_4.setText(str(self.origin.mt.cent_longitude))
            self.label_6.setText(str(self.origin.mt.cent_depth))
            self.label_18.setText(str(self.origin.mt.correlation))
            self.label_23.setText(str(self.origin.mt.var_reduction))
            self.label_8.setText(str(self.origin.mt.mw))
            self.label_28.setText(str(self.origin.mt.mrr))
            self.label_30.setText(str(self.origin.mt.mtt))
            self.label_32.setText(str(self.origin.mt.mpp))
            self.label_34.setText(str(self.origin.mt.mrt))
            self.label_36.setText(str(self.origin.mt.mrp))
            self.label_38.setText(str(self.origin.mt.mtp))
            self.label_20.setText(str(self.origin.mt.vol))
            self.label_24.setText(str(self.origin.mt.dc))
            self.label_26.setText(str(self.origin.mt.clvd))
            self.label_16.setText(str(self.origin.mt.mo))
            self.label_42.setText(str(self.origin.mt.strike))
            self.label_47.setText(str(self.origin.mt.dip))
            self.label_48.setText(str(self.origin.mt.rake))
            self.label_44.setText(str(self.origin.mt.strike2))
            self.label_46.setText(str(self.origin.mt.dip2))
            self.label_49.setText(str(self.origin.mt.rake2))
            self.label_51.setText(str(self.origin.mt.p_azm))
            self.label_55.setText(str(self.origin.mt.p_plunge))
            self.label_58.setText(str(self.origin.mt.t_azm))
            self.label_57.setText(str(self.origin.mt.t_plunge))
            self.label_59.setText(str(self.origin.mt.b_azm))
            self.label_60.setText(str(self.origin.mt.b_plunge))
            self.label_67.setText(str(self.origin.mt.minSV))
            self.label_65.setText(str(self.origin.mt.maxSV))
            self.label_66.setText(str(self.origin.mt.CN))
            self.label_70.setText(str(self.origin.mt.stVar))
            self.label_62.setText(str(self.origin.mt.fmVar))
            self.doubleSpinBox_2.setValue(float(self.origin.mt.frequency_1))
            self.doubleSpinBox_3.setValue(float(self.origin.mt.frequency_2))
            self.doubleSpinBox_4.setValue(float(self.origin.mt.frequency_3))
            self.doubleSpinBox_5.setValue(float(self.origin.mt.frequency_4))

            _plot_dir = os.path.join(self.origin.results_dir, "plot")
            _beachball = os.path.join(_plot_dir, "beachball.png")
            _map = os.path.join(_plot_dir, "map.png")
            _misfit = os.path.join(_plot_dir, "misfit.png")
            _inversions = os.path.join(_plot_dir, "inversions.png")
            _correlation = os.path.join(_plot_dir, "correlation.png")
            _allstreams = os.path.join(_plot_dir, "allstreams.png")
            _text = os.path.join(_plot_dir, "text")
            _log = os.path.join(self.origin.results_dir, "log")

            pixmap = QtGui.QPixmap(_beachball)

            _scPixmap = pixmap.scaled(QtCore.QSize(160,160),
                                      QtCore.Qt.KeepAspectRatio,
                                      QtCore.Qt.SmoothTransformation)

            self.label_64.setPixmap(_scPixmap)

            pixmap6 = QtGui.QPixmap(_allstreams)
            graphicsScene(pixmap6, self.graphicsView_5, self)

            pixmap2 = QtGui.QPixmap(_map)
            graphicsScene(pixmap2, self.graphicsView_6, self)

            pixmap3 = QtGui.QPixmap(_misfit)
            graphicsScene(pixmap3, self.graphicsView_2, self)

            pixmap4 = QtGui.QPixmap(_inversions)
            graphicsScene(pixmap4, self.graphicsView_3, self)

            pixmap5 = QtGui.QPixmap(_correlation)
            graphicsScene(pixmap5, self.graphicsView_4, self)

            _f = open(_text, "r")
            _lines = _f.readlines()
            _f.close()

            _msg = ""
            for _line in _lines:
                _msg += "\t" + str(_line)

            self.textBrowser_2.setStyleSheet("font: 11pt \"Courier\";")
            self.textBrowser_2.setText(_msg)

            _f = open(_log, "r")
            _lines = _f.readlines()
            _f.close()

            _msg = ""
            for _line in _lines:
                _msg += "\t" + str(_line)
            self.textBrowser.setStyleSheet("font: 10pt \"Arial\";")

            self.textBrowser.setText(_msg)

            _headers = ['Network', 'Station', 'N', 'E', 'Z']

            self.model = StationsTableModel(self.station_list,
                                            self.review_list,
                                            _headers,
                                            self.tableView)
            self.tableView.setModel(self.model)

            self.tableView.horizontalHeader().setResizeMode(
                                              QtGui.QHeaderView.Stretch)


    def streamClicked(self):
        # ignore clicking on network code or station code
        if self.tableView.selectedIndexes()[0].column() > 1:
            _col = self.tableView.selectedIndexes()[0].column() - 2
            _row = self.tableView.selectedIndexes()[0].row()

            if self.review_list[_row][_col]:
                if self.review_list[_row][_col].enable:
                    self.review_list[_row][_col].enable = False
                else:
                    self.review_list[_row][_col].enable = True


    def reviseClicked(self):
        try:
            self.settings = lib.settings.Settings()
            self.settings = self.parent.db_scisola.loadSettings(self.settings)
            self.station_list = lib.stream.removeDisabled(self.station_list)
        except:
            self.parent.master_log.exception()
            self.close()

        try:
            self.label_73.setStyleSheet('QLabel { color: red }')
            self.label_73.setText("status: calculating inversion...")
            self.setEnabled(False)

            # starting revise process in thread
            self.thread = tThread(self)
            self.thread.finished.connect(self.thread.finish)
            self.thread.start()

        except:
            self.parent.master_log.exception()
            self.close()



    def deleteClicked(self):
        self.setEnabled(False)
        _msg = "Are you sure you want to delete the Origin?"
        _reply = QtGui.QMessageBox.question(self, 'Message', _msg,
                                            QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.No)

        if _reply == QtGui.QMessageBox.Yes:
            if self.checkBox.checkState() == QtCore.Qt.Checked:
                try:
                    self.parent.db_scisola.deleteOrigin(self.origin.id)
                    shutil.rmtree(self.origin.results_dir)
                except:
                    pass

                self.setEnabled(True)
                self.close()

            else:
                try:
                    shutil.rmtree(os.path.join(self.origin.results_dir,
                                               "inversion"))
                    shutil.rmtree(os.path.join(self.origin.results_dir,
                                               "stream"))
                    shutil.rmtree(os.path.join(self.origin.results_dir,
                                               "plot", "streams"))
                except:
                    pass

                self.setEnabled(True)
                self.close()

        self.setEnabled(True)


class tThread(QtCore.QThread):

    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self.pre_parent = self.parent.parent
        self.process = None


    def run(self):

        self.process = lib.process.Process(origin = self.parent.origin,
                                settings = self.parent.settings,
                                station_list = self.parent.station_list,
                                db_scisola = self.parent.parent.db_scisola,
                                save2DB = True,
                                timeout = self.parent.settings.process_timeout,
                                delay = 0,
                                parent = self.pre_parent)
        self.process.f1 = float(self.parent.doubleSpinBox_2.value())
        self.process.f2 = float(self.parent.doubleSpinBox_3.value())
        self.process.f3 = float(self.parent.doubleSpinBox_4.value())
        self.process.f4 = float(self.parent.doubleSpinBox_5.value())
        self.process.start()

    def finish(self):
        self.parent.close()


    def stop(self):
        # terminate process calculation
        self.process.stop()
        # terminate thread
        self.terminate()


class graphicsScene(QtGui.QGraphicsScene):

    def __init__ (self, pixmap, parent=None, topParent=None):
        self.__parent = parent
        self.__topParent = topParent
        self.__pixmap = pixmap
        self.__size = self.__topParent.size() * 0.7

        super(graphicsScene, self).__init__ (self.__parent)

        self.__parent.setScene(self)

        _scPixmap = self.__pixmap.scaled(QtCore.QSize(self.__size),
                                        QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.SmoothTransformation)

        self.addPixmap(_scPixmap)


    def wheelEvent (self, event):
        super(graphicsScene, self).wheelEvent(event)

        self.clear()

        # zoom in
        if event.delta() > 0 :
            self.__size = 1.1 * self.__size # + 10%

        # zoom out
        else:
            self.__size = 0.9 * self.__size # - 10%


        _scPixmap = self.__pixmap.scaled(QtCore.QSize(self.__size),
                                        QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.SmoothTransformation)

        self.addPixmap(_scPixmap)

        self.setSceneRect(QtCore.QRectF(0.0,
                                        0.0, self.__size.width(),
                                        self.__size.height()))


class StationsTableModel(QtCore.QAbstractTableModel):

    def __init__(self, station_list=[], review_list=[], headers=[],
                 parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__station_list = station_list
        self.__review_list = review_list
        self.__headers = headers


    def getValues(self):
        return self.__station_list


    def rowCount(self, parent):
        return len(self.__station_list)


    def columnCount(self, parent):
        return len(self.__headers)


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            self.dataChanged.emit(index, index)

            if index.column() == 0:
                _value = self.__station_list[index.row()].network

            elif index.column() == 1:
                _value = self.__station_list[index.row()].code

            else:
                _row = index.row()
                _col = index.column()-2
                if self.__review_list[_row][_col]:
                    if self.__review_list[_row][_col].enable:
                        _value = str(self.__review_list[_row][_col].reduction)
                    else:
                        _value = "-"
                else:
                    _value = "-"
            return _value

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignVCenter |
                   QtCore.Qt.AlignHCenter)


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.__headers[section]
            else: # if vertical
                return QtCore.QString("%1").arg(section+1)


def streamExist(stream):
    """
    Returns stream reduction or none if exist or not respectively
    """

    if stream:
        return stream[0]
    else:
        return None


#def review_list2station_list(review_list, station_list):
#    """
#    Converts review_list to station_list in order to run revision
#    with user's stream choices
#    """
#
#    for i, station in enumerate(review_list):
#        for _stream in station:
#            if _stream:
#                for x in station_list[i].stream_list:
#                    if x.code == _stream.code:
#                        x.enable = _stream.enable
#
#    return station_list

