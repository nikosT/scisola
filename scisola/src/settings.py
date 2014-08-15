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

import lib.gui.settings
import lib.settings
import stations
import lib.database


class MainWindow(QtGui.QMainWindow, lib.gui.settings.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # inherited from Ui_MainWindow
        self.setupUi(self)
        self.setConnections()
        self.parent = parent


    def main(self):
        # access to parent's variables (main window's variables)
        self.parent.settings = self.parent.db_scisola.loadSettings(
                                                         self.parent.settings)
        if self.parent.settings:
            self.settings2GUI(self.parent.settings)

        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.showMaximized()


    def closeEvent(self, event):
        self.parent.main()


    def setConnections(self):
        # right arrow -add- (distance selection)
        self.toolButton.clicked.connect(self.toolButtonClicked)
        # left arrow -remove- (distance selection)
        self.toolButton_2.clicked.connect(self.toolButton_2Clicked)
        # right arrow -add- (inversion time)
        self.toolButton_3.clicked.connect(self.toolButton_3Clicked)
        # right arrow -remove- (inversion time)
        self.toolButton_4.clicked.connect(self.toolButton_4Clicked)
        # right arrow -add- (inversion frequency)
        self.toolButton_5.clicked.connect(self.toolButton_5Clicked)
        # right arrow -remove- (inversion frequency)
        self.toolButton_6.clicked.connect(self.toolButton_6Clicked)
        # edit stations button
        self.pushButton_17.clicked.connect(self.editStationsButtonClicked)
        # apply settings
        self.pushButton.clicked.connect(self.applyButtonClicked)
        # browse button
        self.pushButton_14.clicked.connect(self.browseFileOnClicked_14)
        self.pushButton_2.clicked.connect(self.browseFileOnClicked_2)
        self.pushButton_20.clicked.connect(self.browseFileOnClicked_20)
        self.pushButton_18.clicked.connect(self.browseFileOnClicked_18)
        self.pushButton_16.clicked.connect(self.browseFileOnClicked_16)
        self.pushButton_19.clicked.connect(self.browseFileOnClicked_19)
        self.pushButton_9.clicked.connect(self.browseFileOnClicked_9)
        # update button
        self.pushButton_13.clicked.connect(self.updateButtonClicked)


    # browse functions
    def browseFileOnClicked_14(self):
        _text = QtGui.QFileDialog.getOpenFileName()
        if _text:
            self.lineEdit_19.setText(_text)


    def browseFileOnClicked_2(self):
        _text = QtGui.QFileDialog.getExistingDirectory()
        if _text:
            self.lineEdit_2.setText(_text)


    def browseFileOnClicked_20(self):
        _text = QtGui.QFileDialog.getOpenFileName()
        if _text:
            self.lineEdit_24.setText(_text)


    def browseFileOnClicked_18(self):
        _text = QtGui.QFileDialog.getOpenFileName()
        if _text:
            self.lineEdit_21.setText(_text)


    def browseFileOnClicked_16(self):
        _text = QtGui.QFileDialog.getOpenFileName()
        if _text:
            self.lineEdit_20.setText(_text)


    def browseFileOnClicked_19(self):
        _text = QtGui.QFileDialog.getOpenFileName()
        if _text:
            self.lineEdit_22.setText(_text)


    def browseFileOnClicked_9(self):
        _text = QtGui.QFileDialog.getExistingDirectory()
        if _text:
            self.lineEdit_3.setText(_text)


    def toolButtonClicked(self):
        _mag_min = self.doubleSpinBox.text()
        _mag_max = self.doubleSpinBox_2.text()
        _dist_min = self.spinBox_6.text()
        _dist_max = self.spinBox_8.text()
        _value = _mag_min + " <= magnitude <= " + _mag_max + " and " + \
                 _dist_min + " <= distance <= " + _dist_max
        self.listWidget.addItem(_value)


    def toolButton_2Clicked(self):
        self.listWidget.takeItem(self.listWidget.currentRow())


    def toolButton_3Clicked(self):
        _mag_min = self.doubleSpinBox_3.text()
        _mag_max = self.doubleSpinBox_5.text()
        _tl = self.comboBox_2.currentText()
        _value = _mag_min + " <= magnitude <= " + _mag_max + " and tl = " + \
                 _tl
        self.listWidget_2.addItem(_value)


    def toolButton_4Clicked(self):
        self.listWidget_2.takeItem(self.listWidget_2.currentRow())


    def toolButton_5Clicked(self):
        _mag_min = self.doubleSpinBox_9.text()
        _mag_max = self.doubleSpinBox_12.text()
        _f1 = self.doubleSpinBox_13.text()
        _f2 = self.doubleSpinBox_14.text()
        _f3 = self.doubleSpinBox_18.text()
        _f4 = self.doubleSpinBox_19.text()
        _value = _mag_min + " <= magnitude <= " + _mag_max + " and " + \
                 "frequencies = [" + _f1 + ", " + _f2 + ", " + _f3 + ", " + \
                 _f4 + "]"
        self.listWidget_3.addItem(_value)


    def toolButton_6Clicked(self):
        self.listWidget_3.takeItem(self.listWidget_3.currentRow())


    def editStationsButtonClicked(self):
        sta_win = stations.StationsWindow(self)
        sta_win.main()
        self.hide()


    def GUI2Settings(self):
        settings = lib.settings.Settings()
        settings.center_latitude = float(self.lineEdit_15.text())
        settings.center_longitude = float(self.lineEdit_14.text())
        settings.distance_range = int(self.spinBox_5.value())
        settings.magnitude_threshold = float(self.doubleSpinBox_4.value())
        settings.min_sectors = int(self.comboBox.currentText())
        settings.stations_per_sector = int(self.spinBox_7.value())
        settings.sources = int(self.spinBox_13.value())
        settings.source_step = int(self.spinBox_14.value())
        settings.clipping_threshold = float(self.doubleSpinBox_8.value())
        settings.time_grid_start = int(self.lineEdit_17.text())
        settings.time_grid_step = int(self.spinBox_15.value())
        settings.time_grid_end = int(self.lineEdit_18.text())
        settings.watch_interval = int(self.spinBox_2.value())
        settings.process_delay = int(self.spinBox_3.value())
        settings.process_timeout = int(self.spinBox_4.value())
        settings.crustal_model_path = str(self.lineEdit_19.text())
        settings.output_dir = str(self.lineEdit_2.text())
        settings.isola_path = str(self.lineEdit_3.text())
        settings.sc3_path = str(self.lineEdit_24.text())
        settings.sc3_scevtls = str(self.lineEdit_21.text())
        settings.sc3_scxmldump = str(self.lineEdit_20.text())
        settings.seedlink_path = str(self.lineEdit_22.text())
        settings.seedlink_host = str(self.lineEdit_23.text())
        settings.seedlink_port = int(self.spinBox_9.value())

         # distance selection list
        for i in xrange(self.listWidget.count()):
            _row = str(self.listWidget.item(i).text()).split(' ')
            settings.distance_selection.append([float(_row[0]),
                                                float(_row[4]),
                                                int(_row[6]),
                                                int(_row[10])
                                                ])

         # inversion time list
        for i in xrange(self.listWidget_2.count()):
            _row = str(self.listWidget_2.item(i).text()).split(' ')
            settings.inversion_time.append([float(_row[0]),
                                            float(_row[4]),
                                            float(_row[8])
                                            ])

         # inversion frequency list
        for i in xrange(self.listWidget_3.count()):
            _row = str(self.listWidget_3.item(i).text()).split(' ')
            settings.inversion_frequency.append([float(_row[0]),
                                                 float(_row[4]),
                                                 float(str(_row[8])[1:-1]),
                                                 float(str(_row[9])[:-1]),
                                                 float(str(_row[10])[:-1]),
                                                 float(str(_row[11])[:-1])
                                                 ])

        return settings


    def settings2GUI(self, settings):
        self.lineEdit_15.setText(str(settings.center_latitude))
        self.lineEdit_14.setText(str(settings.center_longitude))
        self.spinBox_5.setValue(int(settings.distance_range))
        self.doubleSpinBox_4.setValue(float(settings.magnitude_threshold))
        _index = self.comboBox.findText(str(settings.min_sectors))
        self.comboBox.setCurrentIndex(_index)
        self.spinBox_7.setValue(int(settings.stations_per_sector))
        self.spinBox_13.setValue(int(settings.sources))
        self.spinBox_14.setValue(int(settings.source_step))
        self.doubleSpinBox_8.setValue(float(settings.clipping_threshold))
        self.lineEdit_17.setText(str(settings.time_grid_start))
        self.spinBox_15.setValue(int(settings.time_grid_step))
        self.lineEdit_18.setText(str(settings.time_grid_end))
        self.spinBox_2.setValue(int(settings.watch_interval))
        self.spinBox_3.setValue(int(settings.process_delay))
        self.spinBox_4.setValue(int(settings.process_timeout))
        self.lineEdit_19.setText(str(settings.crustal_model_path))
        self.lineEdit_2.setText(str(settings.output_dir))
        self.lineEdit_3.setText(str(settings.isola_path))
        self.lineEdit_24.setText(str(settings.sc3_path))
        self.lineEdit_21.setText(str(settings.sc3_scevtls))
        self.lineEdit_20.setText(str(settings.sc3_scxmldump))
        self.lineEdit_22.setText(str(settings.seedlink_path))
        self.lineEdit_23.setText(str(settings.seedlink_host))
        self.spinBox_9.setValue(int(settings.seedlink_port))
        self.label_4.setText(str(settings.timestamp))
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.listWidget_3.clear()

        for _entry in settings.distance_selection:
            _value = str(_entry[0]) + " <= magnitude <= " + str(_entry[1]) + \
                     " and " + str(_entry[2]) + " <= distance <= " + \
                     str(_entry[3])

            self.listWidget.addItem(_value)

        for _entry in settings.inversion_time:
            _value = str(_entry[0]) + " <= magnitude <= " + str(_entry[1]) + \
                     " and tl = " + str(_entry[2])

            self.listWidget_2.addItem(_value)

        for _entry in settings.inversion_frequency:
            _value = str(_entry[0]) + " <= magnitude <= " + str(_entry[1]) + \
                     " and frequencies = [" + str(_entry[2]) + ", " + \
                     str(_entry[3]) + ", " + str(_entry[4]) + ", " + \
                     str(_entry[5]) + "]"

            self.listWidget_3.addItem(_value)

        self.label_4.setText(str(settings.timestamp))


    # apply button
    def applyButtonClicked(self):
        self.__settings = self.GUI2Settings()
        self.setEnabled(False)
        _message = self.parent.db_scisola.saveSettings(self.__settings)

        if not _message:
            QtGui.QMessageBox.information(self, 'Saving to scisola',
                                          'Settings successfully applied.')
            self.parent.master_log.info("Settings successfully applied.")
            # apply new settings to system
            self.parent.settings = self.__settings
            # apply new settings to watcher
            if self.parent.watcher:
                self.parent.watcher.setConf(self.parent.settings)
                self.parent.watcher.restart()

        else:
            QtGui.QMessageBox.critical(self, 'Saving to scisola',
                                       "Could not save settings.\nError:\n" +\
                                       str(_message[:2]))
        self.setEnabled(True)


    # update button
    def updateButtonClicked(self):
        if self.checkBox.checkState() == QtCore.Qt.Checked:
            _reset = True
        else:
            _reset = False

        self.setEnabled(False)
        _message = self.parent.db_scisola.importFromSc3(self.parent.db_sc3,
                                                        reset=_reset)

        if not _message:
            QtGui.QMessageBox.information(self, 'Saving to scisola',
                                          'Stations successfully updated.')
            self.parent.master_log.info("Stations successfully updated.")
        else:
            QtGui.QMessageBox.critical(self, 'Saving to scisola',
                                   "Could not update stations.\nError:\n" +\
                                   str(_message[:2]))
        self.setEnabled(True)

