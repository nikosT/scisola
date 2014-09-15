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

import subprocess
import datetime as date

##############################################################################
# DEFINE CLASS "Seedlink"                                                    #
##############################################################################

class Seedlink:

    def __init__(self, sc3_path=None, name="slinktool", host="localhost",
                 port=18000):
        self.name = name
        self.host = host
        self.port = port
        self.sc3_path = sc3_path


    def online(self):
        """
        Checks if seedlink server is online
        Returns True if online, false if offline
        """
        if self.sc3_path:
            _proc = subprocess.Popen([self.sc3_path, "exec", self.name,
                                      self.host+":"+str(self.port), "-P"],
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
            _msg = _proc.stderr.readline()

            # if server is offline
            if "Could not" in _msg:
                return False
            else:
                return True


    def getSeedlinkStreams(self, datetime, duration):
        """
        Selects only available streams of seedlink server
        for the specific datetime and duration
        """
        _offset = 2 #secs

        _seedlink_streams = [] # streams returned from seedlink server
        timespan_streams = [] # streams returned from seedlink server
                              # that are on a specific timespan

        _proc = subprocess.Popen([self.sc3_path, "exec", self.name,
                          self.host+":"+str(self.port), "-v", "-Q"],
                          stderr=subprocess.PIPE, stdout=subprocess.PIPE)
      #  while _proc.poll() is None:
     #       _msg = _proc.stderr.readline()

            # if an error occured, kill process
     #       if "error:" in _msg:
     #           _proc.kill()
     #           return []

        # output contains available streams
        _output = _proc.communicate()[0]

        # formats output list to seedlink_streams
        # seedlink_streams contains streams available from seedlink server
        _output = _output.split('\n')
        for _line in _output:
            _temp_line = [_x for _x in _line.split(' ') if _x]
            if len(_temp_line) == 10:
                del _temp_line[2]
            _seedlink_streams.append(_temp_line)
        _seedlink_streams.pop()

        # from all available streams of seedlink server,
        # selects those stream that are in the specific timespan
        _start = date.datetime.strptime(datetime, "%Y/%m/%d %H:%M:%S.%f")

        # setting an initial offset
        _start = _start - date.timedelta(seconds=_offset)

        _end = _start + date.timedelta(seconds=duration)

        for stream in _seedlink_streams:
            _stream_start = date.datetime.strptime(stream[4] + " " + \
                            stream[5], "%Y/%m/%d %H:%M:%S.%f")
            _stream_end = date.datetime.strptime(stream[7] + " " + \
                          stream[8], "%Y/%m/%d %H:%M:%S.%f")

            # rule: stream_start < start < start + duration < stream_end
            if _stream_start < _start and _end < _stream_end:
                timespan_streams.append(stream)

        return timespan_streams


    def getMseed(self, datetime, duration, network_code, station_code,
                 stream_code, output_path):
        """
        Creates mseed record for specific time and stream
        of the seedlink server
        """
        try:
            _start = date.datetime.strptime(datetime,
                                                "%Y/%m/%d %H:%M:%S.%f")
            _end = _start + date.timedelta(seconds=duration+1)

            _str_time = str(_start.strftime("%Y,%m,%d,%H,%M,%S")) + ":" + \
                        str(_end.strftime("%Y,%m,%d,%H,%M,%S"))

            _str_stream = str(network_code) + "_" + str(station_code) + ":" +\
                          str(stream_code) + ".D"

            _proc = subprocess.Popen([self.sc3_path, "exec", self.name,
                               self.host+":"+str(self.port), "-v",
                               "-nd", "1", "-tw", _str_time, "-S",
                               _str_stream, "-o", output_path],
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE)

            while _proc.poll() is None:
                _msg = _proc.stderr.readline()

                # if an error occured, kill process
                if "error:" in _msg:
                    _proc.kill()
                    return False

            return True

        except:
            return False


#if __name__ == "__main__":
#
#    sl = Seedlink()
#
#    sl.host = "83.212.117.71"
#    sl.sc3_path = "/home/nikos/Programs/seiscomp3_exp/bin/seiscomp"
#
#    if sl.online():
#        print "nai"
#
#    date = "2014/03/03"
#    time = "13:57:38.0000"
#    duration = 400
#
#    print getSeedlinkStreams(sl,date,time,duration)
#
#    sys.exit(0)
#    print getMseed(sl, date, time, duration, "MN", "TIR", "HHE", "/home/nikos/Desktop/file.mseed")

#time = "2013,11,28,00,00,00:2013,11,28,00,02,00"
#stream = "\'HP_DID:HHZ.D\'"
#output = "/home/nikos/Desktop/data.mseed"

#print getMseed(sl, time, stream, output)


