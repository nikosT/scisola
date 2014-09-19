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
import time

# scisola's imports
import lib.gui.main
import database
import settings
import search
import about
import review
import lib.logger
import lib.settings
import lib.watcher


class MainWindow(QtGui.QMainWindow, lib.gui.main.Ui_MainWindow):
    def __init__(self, db_scisola, db_sc3, parent=None):
        super(MainWindow, self).__init__(parent)
        # inherited from Ui_MainWindow
        self.setupUi(self)
        self.setConnections()

        self.startFlag = True

        # create tray icon
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setIcon(QtGui.QIcon(":/logo/beachball.png"))
        self.trayIcon.activated.connect(self.on_trayIcon_activated)

        ####### Main Variables ##########################
        self.master_log_path = "scisola_log"
        self.master_log = lib.logger.Logger(self.master_log_path)
        self.db_scisola = db_scisola
        self.db_sc3 = db_sc3
        self.settings = lib.settings.Settings()
        self.watcher = None

        self.settings = self.db_scisola.loadSettings(self.settings)
        if self.settings:
            self.watcher = lib.watcher.Watcher(parent = self,
                                               db_scisola = self.db_scisola,
                                               db_sc3 = self.db_sc3,
                                               settings = self.settings)

        ####### EOF Main Variables ######################

    # when tray icon is deactivated
    @QtCore.pyqtSlot(QtGui.QSystemTrayIcon.ActivationReason)
    def on_trayIcon_activated(self, event):
        if event == QtGui.QSystemTrayIcon.Trigger:
            self.show()
            self.setWindowState(QtCore.Qt.WindowNoState)
            self.trayIcon.hide()


    # when tray icon is activated
#    def changeEvent(self, event):
#        if event.type() == QtCore.QEvent.WindowStateChange:
#            if self.windowState() & QtCore.Qt.WindowMinimized:
#                event.ignore()
#                self.hide()
#                self.trayIcon.show()
#                time.sleep(0.01)
#                self.trayIcon.showMessage('Running',
#                                          'Running in the background...')


    def closeEvent(self, event):
        self.setEnabled(False)
        _msg = "Are you sure you want to exit scisola?"
        _reply = QtGui.QMessageBox.question(self, 'Message', _msg,
                                            QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.No)

        if _reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

        self.setEnabled(True)


    def setConnections(self):
        # settings window
        self.actionConfigure.triggered.connect(self.configureClicked)
        self.actionStart.triggered.connect(self.startClicked)
        self.actionRefresh.triggered.connect(self.refreshClicked)
        self.actionSearch.triggered.connect(self.searchClicked)
        self.actionAbout.triggered.connect(self.aboutClicked)
        self.tableView.doubleClicked.connect(self.originClicked)
        self.tabWidget.currentChanged.connect(self.setLog)


    def main(self):
        # enable window
        self.setEnabled(True)
        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        # brings latest 20 origins
        self.refreshOriginsT20()
        self.setLog()

        self.showMaximized()


    def setLog(self):
        """
        Sets the main log to print to screen
        """

        _f = open(self.master_log_path, "r")
        _lines = _f.readlines()
        _f.close()

        _msg = ""
        # latest log messages first
        for _line in reversed(_lines):
            _msg += "\t" + str(_line)

        self.textBrowser.setStyleSheet("font: 10pt \"Arial\";")
        self.textBrowser.setText(_msg)


    def originClicked(self):
        # get origin's id (by double click)
        _orig_id = int(self.tableView.selectedIndexes()[7].data().toString())
        self.setEnabled(False)
        conf_win = review.ReviewWindow(_orig_id, self)
        conf_win.main()
        self.hide()


    def searchClicked(self):
        sh_win = search.SearchWindow(self)
        sh_win.exec_()


    def aboutClicked(self):
        ab_win = about.AboutWindow(self)
        ab_win.exec_()


    def refreshClicked(self):
        self.refreshOriginsT20()


    def configureClicked(self):
        conf_win = settings.MainWindow(self)
        conf_win.main()
        self.hide()


    def startClicked(self):
        try:
            if self.watcher:
                if self.startFlag:
                    _icon = QtGui.QIcon()
                    _icon.addPixmap(QtGui.QPixmap(":/icons/stop.png"),
                                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.actionStart.setIcon(_icon)
                    self.actionStart.setText("stop")
                    self.startFlag = False
                    self.master_log.info("Starting watcher...")

                    self.watcher.start()

                else:
                    self.setEnabled(False)
                    _msg = "Are you sure you want to stop the Event listener?"
                    _reply = QtGui.QMessageBox.question(self, 'Message', _msg,
                                                        QtGui.QMessageBox.Yes,
                                                        QtGui.QMessageBox.No)

                    if _reply == QtGui.QMessageBox.Yes:
                        _icon = QtGui.QIcon()
                        _icon.addPixmap(QtGui.QPixmap(":/icons/play.png"),
                                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        self.actionStart.setIcon(_icon)
                        self.actionStart.setText("start")
                        self.startFlag = True
                        self.watcher.stop()
                        self.master_log.info("Stoping watcher...")
                    self.setEnabled(True)
        except:
            self.setEnabled(True)
            self.master_log.exception()


    def refreshOriginsT20(self):
        _headers = ['datetime', 'latitude', 'longitude',
                   'depth', 'mw', 'mo', 'type', 'id']

        _originsT20 = self.db_scisola.loadOriginsT20()

        _model = OriginsTableModel(_originsT20, _headers,
                                          self.tableView)
        self.tableView.setModel(_model)

        self.tableView.horizontalHeader().setResizeMode(
                                              QtGui.QHeaderView.Stretch)


class OriginsTableModel(QtCore.QAbstractTableModel):

    def __init__(self, origins=[], headers=[], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__origins = origins
        self.__headers = headers


    def getValues(self):
        return self.__origins


    def rowCount(self, parent):
        return len(self.__origins)


    def columnCount(self, parent):
        return len(self.__headers)


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.__origins[index.row()][index.column()+1]

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignVCenter |
                   QtCore.Qt.AlignHCenter)


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.__headers[section]
            else: # if vertical
                return QtCore.QString("%1").arg(section+1)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('scisola')

    db_scisola = None
    db_sc3 = None

    db_win = database.DBWindow()
    if db_win.exec_() == QtGui.QDialog.Accepted:
        db_scisola, db_sc3 = db_win.getDBvalues()

        main_win = MainWindow(db_scisola, db_sc3)
        main_win.main()
        sys.exit(app.exec_())

