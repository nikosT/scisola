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

import lib.gui.stations
import lib.stream


class StationsWindow(QtGui.QMainWindow, lib.gui.stations.Ui_MainWindow):
    def __init__(self, parent=None):
        super(StationsWindow, self).__init__(parent)
        # inherited from Ui_MainWindow
        self.setupUi(self)
        self.setConnections()
        self.parent = parent
        self.pre_parent = parent.parent
        self.station_list = []
        self.station_list2D = []
        self.model = None


    def main(self):
        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.showMaximized()

        self.setStationsTable()


    def closeEvent(self, event):
        self.parent.main()


    def setConnections(self):
        # apply button
        self.pushButton.clicked.connect(self.buttonClicked)


    def setStationsTable(self):
        try:
            self.station_list = self.pre_parent.db_scisola.loadStations(
                                                            self.station_list)
        except:
            self.parent.label_5.setStyleSheet('QLabel { color: red }')
            self.parent.label_5.setText("status: database error\nError: " +\
                                        str(sys.exc_info()))
            self.close()
            self.parent.showMaximized()

        headers = ['network', 'station', 'stream', 'latitude', 'longitude',
                   'station_priority', 'stream_priority', 'azimuth', 'dip',
                   'sensor_gain', 'datalogger_gain', 'normalization_factor',
                   'number_of_zeros', 'zeros_content', 'number_of_poles',
                   'poles_content']

        self.model = StationsTableModel(self.station_list, headers,
                                        self.tableView)
        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()


    # apply button
    def buttonClicked(self):
        self.setEnabled(False)
        self.station_list2D = self.model.getValues()

        _message = self.pre_parent.db_scisola.updateStations(
                                                          self.station_list2D)

        if not _message:
            QtGui.QMessageBox.information(self, 'Saving to scisola',
                                   'Scisola database successfully updated.')
            self.pre_parent.master_log.info("Scisola database " + \
                                            "successfully updated.")
        else:
            QtGui.QMessageBox.critical(self, 'Saving to scisola',
                               "Scisola database could not be updated.\n" + \
                               "Error:\n" + \
                               str(_message[:2]))

        self.setEnabled(True)


class StationsTableModel(QtCore.QAbstractTableModel):

    def __init__(self, station_list=[], headers=[], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__station_list = station_list
        self.__station_list2D = self.station_list2table2D(self.__station_list)
        self.__headers = headers


    def getValues(self):
        return self.__station_list2D


    def rowCount(self, parent):
        return len(self.__station_list2D)


    def columnCount(self, parent):
        return len(self.__headers)


    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.__station_list2D[index.row()][index.column()]
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignVCenter |
                   QtCore.Qt.AlignHCenter)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if index.column() == 5:
                _network = self.__station_list2D[index.row()][0]
                _station = self.__station_list2D[index.row()][1]

                for _row in self.__station_list2D:
                    if _row[0] == _network and _row[1] == _station:
                        _row[5] = value.toPyObject()
            elif not (index.column() == 0 or index.column() == 1
                      or index.column() == 2):
                self.__station_list2D[index.row()][index.column()] = \
                          str(value.toPyObject())
            self.dataChanged.emit(index, index)
            return True


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.__headers[section]
            else: # if vertical
                return QtCore.QString("%1").arg(section+1)


    def station_list2table2D(self, station_list):
        station_list2D = []

        for station in station_list:
            for i in range(len(station.stream_list)):
                _row = []
                _row.append(str(station.network))
                _row.append(str(station.code))
                _row.append(str(station.stream_list[i].code))
                _row.append(str(station.latitude))
                _row.append(str(station.longitude))
                _row.append(str(station.priority))
                _row.append(str(station.stream_list[i].priority))
                _row.append(str(station.stream_list[i].azimuth))
                _row.append(str(station.stream_list[i].dip))
                _row.append(str(station.stream_list[i].gain_sensor))
                _row.append(str(station.stream_list[i].gain_datalogger))
                _row.append(str(station.stream_list[i].norm_factor))
                _row.append(str(station.stream_list[i].nzeros))
                _row.append(str(station.stream_list[i].zeros_content))
                _row.append(str(station.stream_list[i].npoles))
                _row.append(str(station.stream_list[i].poles_content))

                station_list2D.append(_row)

        return station_list2D

