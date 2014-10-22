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

# imports
import sys
sys.dont_write_bytecode = True

import time
from multiprocessing import Process as multi_Process
import datetime
import obspy.core.utcdatetime as obspy_utc
import subprocess
import obspy.core.util.geodetics as obspy_geo

# scisola's imports
import process
import database
import settings
import origin


##############################################################################
# DEFINE CLASS "Watcher"                                                     #
##############################################################################

class Watcher:

    def __init__(self, parent=None, db_scisola=None, db_sc3=None,
                 settings=None):
        self.parent = parent
        self.process = None
        self.db_scisola = db_scisola
        self.db_sc3 = db_sc3
        self.settings = settings
        self.sc3_path = self.settings.sc3_path
        self.scevtls = self.settings.sc3_scevtls
        self.scxmldump = self.settings.sc3_scxmldump
        self.interval = self.settings.watch_interval


    def setConf(self, settings):
        """
        Setting watcher
        """
        self.settings = settings
        self.sc3_path = self.settings.sc3_path
        self.scevtls = self.settings.sc3_scevtls
        self.scxmldump = self.settings.sc3_scxmldump
        self.interval = self.settings.watch_interval


    def start(self):
        if self.db_sc3 and self.settings:
            # command to run in seiscomp3
            self.command = self.sc3_path + " exec " + self.scevtls + \
                           " -q -d " + str(self.db_sc3.type).lower() + \
                           "://" + \
                           str(self.db_sc3.user) + ":" + \
                           str(self.db_sc3.password) + "@" + \
                           str(self.db_sc3.host) + "/" + \
                           str(self.db_sc3.database)

            if self.process:
                self.stop()

            self.process = multi_Process(target=self.listen)
            self.process.start()


    def stop(self):
        if self.db_sc3 and self.settings:
            if self.process:
                self.process.terminate()
                self.process = None


    def restart(self):
        self.stop()
        self.start()


    def listen(self):
        try:
            while True:
                self.processing()
                time.sleep(self.interval)

        except:
            if self.parent:
                self.parent.master_log.exception()
            pass


    def processing(self):
        _event_id = None
        _event_id = self.getEvent()

        if _event_id:
            if not self.db_scisola.EventExist(_event_id):
                print _event_id
                orig = origin.Origin()
                orig = self.getOriginInfo(_event_id, orig)
		# if event's info exist
		if orig.datetime and orig.magnitude and orig.depth:

                    # two threshold requirements in order to run a new event
                    if orig.magnitude >= self.settings.magnitude_threshold and \
                    inrange(self.settings.center_latitude,
                    self.settings.center_longitude,
                    orig.latitude,
                    orig.longitude,
                    self.settings.distance_range):

                        _p = process.Process(origin=orig,
                                    settings=self.settings,
                                    station_list=[],
                                    db_scisola=self.db_scisola,
                                    save2DB=True,
                                    timeout = self.settings.process_timeout,
                                    delay = self.settings.process_delay,
                                    parent = self.parent)

                        _p.start()


    def getEvent(self):

        _command = ""
        _event_id = ""
	_offset = 120 #sec

        _end = datetime.datetime.utcnow() - datetime.timedelta(seconds=_offset)

        _begin = obspy_utc.UTCDateTime(
                      _end - datetime.timedelta(seconds=self.interval-1))

     #  _begin = datetime.datetime(2007,09,01,00,00,00) #needs remove!!
        _end_date = _end.strftime("%Y-%m-%d %H:%M:%S.%f")
        _begin_date = _begin.strftime("%Y-%m-%d %H:%M:%S.%f")

        _command = self.command + " --begin \"" + _begin_date + "\"" + \
                                  " --end \"" + _end_date + "\""

        _proc = subprocess.Popen(_command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True,
                                 universal_newlines=True)

        _event_id = _proc.communicate()[0].split("\n")
        _event_id = _event_id[:-1] # remove last (none)
        if _event_id:
            return str(_event_id[0])
        else:
            return None


    def getOriginInfo(self, _event_id, orig):

        _latitude = None
        _longitude = None
        _depth = None
        _magnitude = None
        _datetime = None

        _command = self.sc3_path + " exec " + self.scxmldump + \
                   " -q -d " + str(self.db_sc3.type).lower() + "://" + \
                   str(self.db_sc3.user) + ":" + \
                   str(self.db_sc3.password) + "@" + \
                   str(self.db_sc3.host) + "/" + \
                   str(self.db_sc3.database) + \
                   " -fpa -E " + str(_event_id)

        _proc = subprocess.Popen(_command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True,
                                 universal_newlines=True)

        _lines = _proc.communicate()[0].split("\n")

	for _i, _value in enumerate(_lines):
	    if "<latitude>" in _value:
                _latitude = round(float(
                  _lines[_i+1].replace('<value>','').replace('</value>','')),4)
	    elif "<longitude>" in _value:
                _longitude = round(float(
                  _lines[_i+1].replace('<value>','').replace('</value>','')),4)
	    elif "<depth>" in _value:
		_depth = int(round(float(
	          _lines[_i+1].replace('<value>','').replace('</value>','')),4))
	    elif "<magnitude>" in _value:
                _magnitude = round(float(
		  _lines[_i+1].replace('<value>','').replace('</value>','')),2)
	    elif "<time>" in _value:
		_datetime = str(
		  _lines[_i+1].strip().replace('<value>','').replace('</value>',''))

    #    _latitude = round(float(
    #                _lines[9].replace('<value>','').replace('</value>','')),4)
    #    _longitude = round(float(
    #               _lines[13].replace('<value>','').replace('</value>','')),4)
    #    _depth = int(
    #                _lines[17].replace('<value>','').replace('</value>',''))
    #    _magnitude = round(float(
    #               _lines[41].replace('<value>','').replace('</value>','')),2)
    #    _datetime = str(
    #           _lines[5].strip().replace('<value>','').replace('</value>',''))
        _dtime = datetime.datetime.strptime(
                         _datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        _datetime = _dtime.strftime("%Y/%m/%d %H:%M:%S.%f")

        orig.timestamp = datetime.datetime.utcnow()
        orig.datetime = _datetime
        orig.magnitude = _magnitude
        orig.latitude = _latitude
        orig.longitude = _longitude
        orig.depth = _depth
        orig.event_id = str(_event_id)

        return orig


def inrange(center_lat, center_lon, event_lat, event_lon, dist_range):
    """
    Checks if event location is inside the range (in km) from the
    center location defined by the user
    """

    dist = obspy_geo.gps2DistAzimuth(center_lat, center_lon,
                                     event_lat, event_lon)

    dist = float(dist[0]/1000.0)

    if dist <= dist_range:
        return True
    else:
        return False


if __name__ == "__main__":

    _db = database.Database()
    _db.password = "11221122"


    _db3 = database.Database()
    _db3.database = "seiscomp3"
    _db3.host = "localhost"
    _db3.user = "sysop"
    _db3.password = "sysop"

    _sett = settings.Settings()

    _result = _db.loadSettings(_sett)

    _sett = _result[1]

    w = Watcher(_db, _db3, _sett)

    w.start()

    time.sleep(3)
    w.stop()

