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

import src.main


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('scisola')

    db_scisola = None
    db_sc3 = None

    db_win = src.database.DBWindow()
    if db_win.exec_() == QtGui.QDialog.Accepted:
        db_scisola, db_sc3 = db_win.getDBvalues()

        main_win = src.main.MainWindow(db_scisola, db_sc3)
        main_win.main()
        sys.exit(app.exec_())

