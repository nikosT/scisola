##Copyright (C) 2017 Triantafyllis Nikolaos
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

# This script imports the stations and streams from SeisComP3 directly to scisola.
# It can be run as a daily routine in cron:
# * # update inventory every day
# * @daily /usr/bin/python /home/user/update_db.py

#!/usr/bin/env python

import imp
import sys
sys.dont_write_bytecode = True
import MySQLdb as mysql
import psycopg2 as psql
import datetime as date

# fix your scisola path here
sys.path.append('/home/user/scisola-master/scisola/src/lib')
import database
import stream

db = database.Database()
db.user="user"
db.password="password"
db.database="scisola"
db.host="host"

db_sc3=database.Database()
db_sc3.host="host" # local or remote host
db_sc3.database="seiscomp3"
db_sc3.user="sysop"
db_sc3.password="sysop"

db.importFromSc3(db_sc3, reset=True)

