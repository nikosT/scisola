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

# append the folder of scisola to python path
sys.path.append("scisola-master/scisola")

# import the process module
import  src.lib.process as process


# creates an Origin object
# fill with the desired values
# the attributes of the Origin object can be found at (scisola/src/lib/origin.py)
orig = origin.Origin()
orig.datetime = "2014/11/08 09:21:41.00"
orig.magnitude = round(3.9,2) # must be no more than 2 decimals
orig.longitude = 21.747
orig.latitude = 38.3568
orig.depth = int(7) # must be integer
orig.event_id = "test" # the id provided by seiscomp3 or anything you want


# creates a Database object
# fill with the desired values
# the attributes of the Database object can be found at (scisola/src/lib/database.py)
db = database.Database()
db.password = "11221122"

# creates a Settings object
sett = settings.Settings()
# retrieves configuration from database
sett = db.loadSettings(sett)

# by-passing database values by filling desired variables
# the attributes of the Settings object can be found at (scisola/src/lib/settings.py)
# e.g.
# setting different crustal model than the one provided by the database
sett.crustal_model_path = '/home/user/mycrustal.dat'
# setting different results folder than the one provided by the database
sett.output_dir = '/home/user/myoutput'

# creates a Process Object for calculating
# fill with the desired values
# the attributes of the Process object can be found at (scisola/src/lib/process.py)
# if for example provide a station_list, it calculates a revise procedure, if however station_list is empty, it calculates an automatic procedure. By default, is empty
# if for example save2DB is False, it won't store the results to scisola database
# check (scisola/src/lib/process.py) for more info and options
p = Process(origin=orig, settings=sett, db_scisola=db, save2DB=True, delay=0)
# starting MT calculation
p.start()


# run from terminal: python example.py

