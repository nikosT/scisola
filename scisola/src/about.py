##Copyright (C) 2014  Triantafyllis Nikolaos
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

# scisola's import
import lib.gui.about

class AboutWindow(QtGui.QDialog, lib.gui.about.Ui_Dialog):
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__(parent)
        # inherited from Ui_Dialog
        self.setupUi(self)
        self.parent = parent
        try:
            self.main()
        except:
            self.parent.master_log.info("Error in about.py\n" + \
                                                  str(sys.exc_info()))


    def main(self):
        # center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())

