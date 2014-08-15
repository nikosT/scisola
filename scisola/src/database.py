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

from PyQt4 import QtGui

import lib.gui.database

import lib.database

class DBWindow(QtGui.QDialog, lib.gui.database.Ui_Dialog):
    def __init__(self, parent=None):
        super(DBWindow, self).__init__(parent)
        # inherited from Ui_Dialog
        self.setupUi(self)

        self.db_scisola = None
        self.db_sc3 = None

        self.setFunctionality()
        self.main()


    def main(self):

        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())


    def setFunctionality(self):

        self.comboBox.currentIndexChanged.connect(self.comboBoxChanged)
        self.comboBox_2.currentIndexChanged.connect(self.comboBoxChanged_2)
        self.pushButton.clicked.connect(self.pushButtonClicked)


    def comboBoxChanged(self):

        # if PostgreSQL
        if self.comboBox.currentIndex() == 1:
            self.lineEdit.setText("postgres")
            self.lineEdit_2.setText("postgres")
            self.lineEdit_4.setText("5432")

        # if MySQL or empty
        else:
            self.lineEdit.setText("root")
            self.lineEdit_2.setText("root")
            self.lineEdit_4.setText("3306")

    def comboBoxChanged_2(self):

        # if PostgreSQL
        if self.comboBox_2.currentIndex() == 1:
            self.lineEdit_6.setText("postgres")
            self.lineEdit_7.setText("postgres")
            self.lineEdit_9.setText("5432")

        # if MySQL or empty
        else:
            self.lineEdit_6.setText("root")
            self.lineEdit_7.setText("root")
            self.lineEdit_9.setText("3306")


    def pushButtonClicked(self):

        _db_scisola = lib.database.Database()
        _db_scisola.type = str(self.comboBox.currentText())
        _db_scisola.user = str(self.lineEdit.text())
        _db_scisola.password = str(self.lineEdit_2.text())
        _db_scisola.host = str(self.lineEdit_3.text())
        _db_scisola.port = int(self.lineEdit_4.text())
        _db_scisola.database = str(self.lineEdit_5.text())

        _db_sc3 = lib.database.Database()
        _db_sc3.type = str(self.comboBox_2.currentText())
        _db_sc3.user = str(self.lineEdit_6.text())
        _db_sc3.password = str(self.lineEdit_7.text())
        _db_sc3.host = str(self.lineEdit_8.text())
        _db_sc3.port = int(self.lineEdit_9.text())
        _db_sc3.database = str(self.lineEdit_10.text())

        self.db_scisola = _db_scisola
        self.db_sc3 = _db_sc3

        # if database doesn't exist
        if not (self.db_scisola.checkDB() and self.db_sc3.checkDB()):
            self.label_9.setStyleSheet('QLabel { color: red }')
            self.label_9.setText("status: database error")

        else:
            self.accept()

    def getDBvalues(self):
        return [self.db_scisola, self.db_sc3]

