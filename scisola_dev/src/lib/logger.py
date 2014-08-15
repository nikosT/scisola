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
import logging


class Logger():

    def __init__(self, file_dir):
         self.file_dir = file_dir
         self.logger = logging.getLogger(self.file_dir)
         self.hdlr = logging.FileHandler(self.file_dir)
         self.form = \
              logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
         self.hdlr.setFormatter(self.form)
         self.logger.addHandler(self.hdlr)
         self.logger.setLevel(logging.DEBUG)


    def info(self, msg):
        """
        writes an info message to log file
        """
        self.logger.info(msg+"\n")


    def exception(self):
        self.logger.exception("Exception Raised")


    def error(self, msg):
        self.logger.error(msg)


    def stations(self, station_list):
       _message = "Printing available stations and their streams...\n\n" + \
                  "Network Station Latitude Longitude Distance_by_origin " + \
                  "Azimuth_by_origin Priority No._Streams Streams\n"

       for station in station_list:
           _str_streams = "[" + ", ".join([_stream.code for _stream \
           in station.stream_list]) + "]"
           _message += str(station.network) + " " + str(station.code) + " " +\
           str(station.latitude) + " " + str(station.longitude) + " " + \
           str(station.distance_by_origin) + " " + \
           str(station.azimuth_by_origin) + " " + str(station.priority) + " " +\
           str(len(station.stream_list)) + " " +  str(_str_streams) + "\n"

       self.info(_message)


    def origin(self, origin):
       _message = "Origin\'s parameters:\n" + \
                  "datetime: " + str(origin.datetime) + "\n" + \
                  "latitude: " + str(origin.latitude) + "\n" + \
                  "longitude: " + str(origin.longitude) + "\n" + \
                  "magnitude: " + str(origin.magnitude) + "\n" + \
                  "depth: " + str(origin.depth) + "\n" + \
                  "timestamp: " + str(origin.timestamp) + "\n" + \
                  "event_id: " + str(origin.event_id)

       self.info(_message)


    def settings(self, settings):

        _message = "Settings\'s parameters:\n"
        _set_d = vars(settings)

        for key in _set_d:
            _message += str(key) + ": " + str(_set_d[key]) + "\n"

        self.info(_message)


    def mts(self, mt_list):

        _message = ''

        for mt in mt_list:
            _mt_d = vars(mt)

            _message += "Moment Tensor solution for depth (in km): " +\
                        str(mt.cent_depth) + "\n"

            for key in _mt_d:
                _message += str(key) + ": " + str(_mt_d[key]) + "\n"

            _message += "\n"

        self.info(_message)


    def sectors(self, sectors):
       _message = "Sectors' distribution is: (in degrees)"

       _sectors = sectors.keys()
       _sectors.sort()

       for _sector in _sectors:
           _message += "\n" + '[' + str(_sector) + '-' + \
                       str(int(_sector + 45)) + '): '

           if sectors[_sector]:
               for station in sectors[_sector]:
                   _message += str(station.network) + "." + \
                   str(station.code) + " "
           else:
               _message += "None"

       self.info(_message)

