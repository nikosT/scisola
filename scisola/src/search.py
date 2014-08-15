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

import lib.gui.search
import main


class SearchWindow(QtGui.QDialog, lib.gui.search.Ui_Dialog):
    def __init__(self, parent=None):
        super(SearchWindow, self).__init__(parent)
        # inherited from Ui_Dialog
        self.setupUi(self)
        self.parent = parent
        try:
            self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTimeUtc())
            self.dateTimeEdit_2.setDateTime(QtCore.QDateTime.currentDateTimeUtc())

            self.setFunctionality()
            self.main()
        except:
            self.parent.master_log.info("Error in search.py\n" + \
                                                  str(sys.exc_info()))


    def main(self):

        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())


    def setFunctionality(self):
        self.pushButton.clicked.connect(self.pushButtonClicked)


    def pushButtonClicked(self):
        try:
            _headers = ['datetime', 'latitude', 'longitude',
                       'depth', 'mw', 'mo', 'type', 'id']

            _start_date = self.dateTimeEdit.date().toString("yyyy/MM/dd")
            _start_time = self.dateTimeEdit.time().toString("hh:mm:ss.zzz")

            _end_date = self.dateTimeEdit_2.date().toString("yyyy/MM/dd")
            _end_time = self.dateTimeEdit_2.time().toString("hh:mm:ss.zzz")

            _start_datetime = _start_date + " " + _start_time
            _end_datetime = _end_date + " " + _end_time


            _origins = self.parent.db_scisola.loadOrigins(_start_datetime,
                                                          _end_datetime)

            _model = main.OriginsTableModel(_origins, _headers,
                                            self.parent.tableView)
            self.parent.tableView.setModel(_model)
            self.parent.tableView.horizontalHeader().setResizeMode(
                                                  QtGui.QHeaderView.Stretch)

            self.accept()
        except:
            self.parent.master_log.info("Error in search.py\n" + \
                                                  str(sys.exc_info()))

