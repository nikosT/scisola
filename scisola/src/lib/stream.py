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

from obspy import read as obspy_read
import obspy.core.stream as obspy_stream
import obspy.core.utcdatetime as obspy_utc
import obspy.geodetics as obspy_geo
import operator
import datetime as date
import os
import numpy as np
# scisola's libs
import database


##############################################################################
# DEFINE CLASS "Station"                                                     #
##############################################################################

class Station:

  def __init__(self):
    self.code = ""
    self.network = ""
    self.description = ""
    self.latitude = None
    self.longitude = None
    self.elevation = None
    self.distance_by_origin = None #not mysql variables
    self.azimuth_by_origin = None
    self.priority = 5
    self.stream_list = []


##############################################################################
# DEFINE CLASS "Stream"                                                      #
##############################################################################

class Stream:

  def __init__(self):
    self.station = None #Station Object
    self.code = ""
    self.azimuth = None
    self.dip = None
    self.gain_sensor = None
    self.gain_datalogger = None
    self.norm_factor = None
    self.nzeros = None
    self.zeros_content = []
    self.npoles = None
    self.poles_content = []
    self.priority = 5 # from 0 to 10 e.g. 0 -> blacklisted
    self.mseed_path = None
    self.data = None
    self.enable = True
    self.reduction = None


##############################################################################
# DEFINE FUNCTIONS "stream"                                                  #
##############################################################################

def removeDisabled(station_list):
    """
    remove Disabled streams for review purpose
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            if not stream.enable:
                _stream_list.remove(stream)

            # make new stream list as station's stream list
        station.stream_list=list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def blob2list(text):
    """
    Converts mysql blob type to python list
    """

    content = []

    text = text.replace('(','')
    text = text.replace(',','+')
    text = text.replace(')','j')
    text = text.replace('+-','-')
    _text_list = text.split(' ')

    for x in _text_list:
        if x:
            content.append(complex(x))

    return content


def list2blob(content_list):
    """
    Converts python list to mysql blob type
    """

    text = ""

    for elem in content_list:

        if str(elem) == '0j':
            content = '(0,0)'
        else:
            content = str(elem).replace('+',',')
            content = content.replace('j)',')')

        text += content + " "

    text = text[:-1]

    return text


def removeEmptyStations(station_list):
    """
    Remove stations with empty stream list
    """

    new_station_list = []

    if station_list:
        for station in station_list:
            if not len(station.stream_list) == 0:
                new_station_list.append(station)

    return new_station_list


def flip(stream):
    """
    Flipping Data
    """

    stream.data.data *= -1

    return stream


def rotate2NE(data_N, data_E, angle):
    """
    Rotates data components of stream in North-East components
    at counter-clockwise angle
    """

    new_data_N = data_N * np.cos(angle * 2 * np.pi / 360) + data_E * \
                 np.sin(angle * 2 * np.pi / 360)
    new_data_E = -data_N * np.sin(angle * 2 * np.pi / 360) + data_E * \
                 np.cos(angle * 2 * np.pi / 360)

    data_N = [round(_x,4) for _x in new_data_N]
    data_E = [round(_x,4) for _x in new_data_E]

    return data_N, data_E


def convertAcc2Vel(stream):
    """
    Converts Acceleration data to Velocity data
    by inserting one zero at stream's zeros
    """

    stream.zeros_content.append(complex('0+0j'))
    stream.nzeros += 1

    return stream


def downsample(stream, tl):
    """
    Downsampling at known frequency at 8192 elements
    """

    _sampling_rate = 8192.0/tl

    stream.data.resample(_sampling_rate)
    stream.data.data = stream.data.data[:8192]

    return stream


def limitStation_list(station_list):
    """
    In case of more than 21 stations, leftover station are being removed
    """

    # station_list is already sorted by priority
    while len(station_list) > 21:
        station_list.pop()

    return station_list


#*****************************************************************************
#*                         Start of main functions                           *
#*****************************************************************************

def selectStreamsByType(station_list):
    """
    Filter a list of objects of class streams, where
    accepted streams are:
    Band Code: H, B
    Instrument Code: H, L ,N
    Orientation Code: N, E, Z
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        # remove from stream list unaccepted streams (by type)
        for stream in station.stream_list:
            if not ((stream.code[0]=='H' or stream.code[0]=='B') and
            (stream.code[1]=='H' or stream.code[1]=='L' or \
            stream.code[1]=='N') and \
            (stream.code[2]=='N' or stream.code[2]=='E' or \
            stream.code[2]=='Z')):
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    return removeEmptyStations(station_list)


def removeBlacklisted(station_list):
    """
    Removes streams with priority 0 (blacklisted)
    """

    # removes blacklisted stations

    # temp copy of station list
    _station_list = list(station_list)

    for station in station_list:
        if station.priority == 0:
            _station_list.remove(station)

    # make new station list
    station_list = list(_station_list)

    # removes blacklisted streams

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            if stream.priority == 0:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def calculateDistAzm(station_list, origin):
    """
    Calculates the distance and the azimuth between stream and origin
    stream_list = list of objects of class stream
    origin = object of class origin
    """

    for station in station_list:
        _result = obspy_geo.base.gps2dist_azimuth(origin.latitude,
                                            origin.longitude,
                                            station.latitude,
                                            station.longitude)

        if _result:
            station.distance_by_origin = float(_result[0]/1000.0)
            station.azimuth_by_origin = _result[1]

    # removes stations with no streams
    return station_list


def selectByDist(station_list, distance_min, distance_max):
    """
    Creates a list of objects of class station within distance_min and
    distance_max from station_list and returns it
    """

    new_station_list = []

    for station in station_list:
        if (station.distance_by_origin >= distance_min and
        station.distance_by_origin <= distance_max):
            new_station_list.append(station)

    # removes stations with no streams
    return new_station_list


def removeUnavailableStreams(sl, station_list, datetime, duration):
    """
    Selects only available streams in specific timespan for each station
    """

    _sl_streams = sl.getSeedlinkStreams(datetime, duration)

    # for each station remove unavailable streams
    for station in station_list:
        # returns a list of available streams' code for this station
        _stream_code_list = [_row[2] for _row in _sl_streams
                            if _row[0] == station.network and
                            _row[1] == station.code]

        # check if streams in station are available
        # and removes the unvailable ones

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            if stream.code not in _stream_code_list:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    return removeEmptyStations(station_list)


def retrieveMseed(sl, station_list, datetime, duration, output_folder):
    """
    Retrieves all possible stream mseed records for each station
    """

    for station in station_list:
        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            _output_file = str(station.network) + "_" +  \
                           str(station.code) + "_" + str(stream.code) + \
                           ".mseed"

            _output_path = os.path.join(output_folder, _output_file)

            _success = sl.getMseed(datetime, duration,
                                   station.network, station.code,
                                   stream.code, _output_path)

            # if success
            if _success:
                stream.mseed_path = _output_path
            else:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def loadMseed(station_list):
    """
    Load mseed to memory
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:
                _st = obspy_read(stream.mseed_path, format="MSEED")
                stream.data = _st[0]
            except:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    return removeEmptyStations(station_list)


def removeClipped(station_list, threshold):
    """
    Remove clipped data
    """

    _max_value = threshold * (2**23)

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:

                # get max value (pos or neg)
                _max = stream.data.data.max()
                _min = stream.data.data.min()
                if abs(_min) > abs(_max):
                  _max = _min

                if _max_value <= _max:
                    _stream_list.remove(stream)
            except:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    return removeEmptyStations(station_list)


def removeGapped(station_list):
    """
    Remove data with gaps
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:
                _st = obspy_stream.Stream()
                _st.append(stream.data)
                _gaps = _st.get_gaps()
                if _gaps:
                    _stream_list.remove(stream)
            except:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    return removeEmptyStations(station_list)


def rotateStreams(station_list):
    """
    Rotates streams and removes invalid position of N-E components
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:
                # if Z component stream
                if stream.code[2] == 'Z':
                    if stream.dip == 90:
                        stream = flip(stream)
                    elif not stream.dip == -90:
                        _stream_list.remove(stream)

                # if E component stream
                # just check if it's one horizontal component
                # and azimuth angle is at the right position
                elif stream.code[2] == 'E':
                    # finding N component stream
                    # stream_N points to N component stream
                    _code_N = str(stream.code[0:2]) + "N"
                    _list_N = [_x for _x in station.stream_list \
                               if _x.code == _code_N]

                    if len(_list_N) == 0 and (not stream.azimuth == 90):
                        _stream_list.remove(stream)

                # if N component stream
                elif stream.code[2] == 'N':
                    # finding E component stream
                    # stream_E points to E component stream
                    _code_E = str(stream.code[0:2]) + "E"
                    _list_E = [_x for _x in station.stream_list \
                               if _x.code == _code_E]

                    if len(_list_E) == 0 and (not stream.azimuth == 0):
                        _stream_list.remove(stream)

                    elif len(_list_E) == 1:
                        stream_E = _list_E[0]

                        # finds possible valid position of E component
                        # according to N component
                        _angle_R = stream.azimuth + 90
                        _angle_L = stream.azimuth - 90
                        if _angle_R >= 360:
                            _angle_R = _angle_R - 360
                        if _angle_L < 0:
                            _angle_L = _angle_L + 360

                        if stream_E.azimuth == _angle_L:
                            stream = flip(stream_E)

                        elif not stream_E.azimuth == _angle_R:
                            _stream_list.remove(stream)

                        # rotates data
                        if not stream.azimuth == 0:
                            print "rotating N,E streams: " + station.code
                            stream.data, stream_E.data = rotate2NE(
                                                            stream.data, \
                                                            stream_E.data, \
                                                            -stream.azimuth)
            except:
                if stream in _stream_list:
                    _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def correctStreams(station_list, datetime, tl):
    """
    Correcting Streams
    """

    # cut before origin time (in seconds)
    _offset = 0 # sec
    _pre_filt = (0.001, 0.01, 10, 11) #filter for correction

    _datetime = date.datetime.strptime(datetime, "%Y/%m/%d %H:%M:%S.%f")

    for station in station_list:
        _paz_sts = None

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:
                # if accelerometer
                if stream.code[1] == 'N':
                    stream = convertAcc2Vel(stream)

                _paz_sts = {'poles': stream.poles_content,
                            'zeros': stream.zeros_content,
                            'gain': stream.norm_factor,
                            'sensitivity': stream.gain_sensor * \
                                           stream.gain_datalogger
                            }

                _start_time = obspy_utc.UTCDateTime(_datetime - \
                                        date.timedelta(seconds=_offset))

                # cutting time (data alignment)
                stream.data = stream.data.slice(_start_time)
                # correct data
                stream.data.detrend('demean')
                stream.data.detrend('linear')
                stream.data.taper(type='hann', max_percentage=0.05)
                stream.data.filter(type='lowpass', freq=10.0, corners=5)
                stream.data.detrend('demean')
                stream.data.detrend('linear')
                stream.data.taper(type='hann', max_percentage=0.05)
                stream.data.filter(type='highpass', freq=0.01, corners=3)
                stream.data.detrend('demean')
                stream.data.detrend('linear')
                stream.data.taper(type='hann', max_percentage=0.05)
                stream.data.simulate(paz_remove=_paz_sts,
                                     pre_filt=_pre_filt)
                stream.data.detrend('demean')
                stream.data.detrend('linear')
                stream.data.taper(type='hann', max_percentage=0.05)

                # downsampling to 8192 elements
                downsample(stream, tl)

            except:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def saveMseed(station_list, output_folder):
    """
    Load mseed to memory
    """

    for station in station_list:
        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            try:
                _output_file = str(station.network) + "_" +  \
                               str(station.code) + "_" + \
                               str(stream.code) + ".mseed"
                output_path = os.path.join(output_folder, _output_file)

                # write to file
                stream.data.write(output_path, format="MSEED")
            except:
                _stream_list.remove(stream)

        # make new stream list as station's stream list
        station.stream_list = list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def removeWrongSample(station_list):
    """
    Data need to be exactly 8192 samples
    """

    for station in station_list:

        # temp copy of station's stream list
        _stream_list = list(station.stream_list)

        for stream in station.stream_list:
            if not len(stream.data.data) == 8192:
                _stream_list.remove(stream)

            # make new stream list as station's stream list
        station.stream_list=list(_stream_list)

    # removes stations with no streams
    return removeEmptyStations(station_list)


def selectByAzm(station_list, station_per_sector, station_min):
    """
    Creates a list of objects of class streams where:
    * there are streamPerSector streams for each sector
    (priority to nearest streams to origin's location),
    * checks if sectors are more or equal of sectorMin,
    and returns it
    """

    _sector = {0:[], 45:[], 90:[], 135:[], 180:[], 225:[], 270:[], 315:[]}
    _sector_counter = 0
    new_station_list = []

    # sort stations by priority and then by distance from origin

    _temp_station_list = sorted(station_list, key=operator.attrgetter('distance_by_origin'))
    station_list = sorted(_temp_station_list, key=operator.attrgetter('priority'), reverse=True)

    #  for each stream object setting sector number based on azimuth and
    #  append stream to a temporary sector list

    for station in station_list:

        if ((station.azimuth_by_origin >= 0.0 and \
            station.azimuth_by_origin < 45.0) or \
            station.azimuth_by_origin == 360.0):
            _sector[0].append(station)
        elif station.azimuth_by_origin >= 45.0 and \
            station.azimuth_by_origin < 90.0:
            _sector[45].append(station)
        elif station.azimuth_by_origin >= 90.0 and \
            station.azimuth_by_origin < 135.0:
            _sector[90].append(station)
        elif station.azimuth_by_origin >= 135.0 and \
            station.azimuth_by_origin < 180.0:
            _sector[135].append(station)
        elif station.azimuth_by_origin >= 180.0 and \
            station.azimuth_by_origin < 225.0:
            _sector[180].append(station)
        elif station.azimuth_by_origin >= 225.0 and \
            station.azimuth_by_origin < 270.0:
            _sector[225].append(station)
        elif station.azimuth_by_origin >= 270.0 and \
            station.azimuth_by_origin < 315.0:
            _sector[270].append(station)
        elif station.azimuth_by_origin >= 315.0 and \
            station.azimuth_by_origin < 360.0:
            _sector[315].append(station)

    #  Gets the first streamPerSector stations of each sector,
    #  checks if sectors are more or equal of sectorMin and
    #  creates a list which contains only the selected stations

    for _key, _sector_list in _sector.iteritems():
        if _sector[_key]:
            _sector[_key] = _sector_list[:station_per_sector]
            _sector_counter += 1
            new_station_list += _sector[_key]

    if _sector_counter >= station_min:
        return removeEmptyStations(new_station_list), _sector
    else:
        return ['Station coverage is less than applied one...\n'], {}


def selectISOLAstreams(station_list):
    """
    Selects three streams per station for each component N,E,Z mandatory
    """

    # sort stations by priority and then by distance from origin
    _temp_station_list = sorted(station_list, key=operator.attrgetter('distance_by_origin'))
    station_list = sorted(_temp_station_list, key=operator.attrgetter('priority'), reverse=True)

    # stations can't be more than 21 in order to run ISOLA
    station_list = limitStation_list(station_list)

    for station in station_list:

        # get all N, E, Z possible streams
        _list_N = [x for x in station.stream_list if x.code[2] == 'N']
        _list_E = [x for x in station.stream_list if x.code[2] == 'E']
        _list_Z = [x for x in station.stream_list if x.code[2] == 'Z']

        # sort streams by priority
        _list_N.sort(key=operator.attrgetter("priority"), reverse=True)
        _list_E.sort(key=operator.attrgetter("priority"), reverse=True)
        _list_Z.sort(key=operator.attrgetter("priority"), reverse=True)

        # stream_list contains at the most one stream per component (N,E,Z)
        station.stream_list = _list_N[0:1] + _list_E[0:1] + _list_Z[0:1]

    return station_list


def insertStations2scisola(db, list2D):

    try:
        for _row in list2D:
            _row[13] = list2blob(eval(_row[13]))
            _row[15] = list2blob(eval(_row[15]))

        database.insertStations2scisola(db, list2D)

        for _row in list2D:
            _row[13] = str(blob2list(_row[13]))
            _row[15] = str(blob2list(_row[15]))

        return True

    except:
        return False

#
#def loadMseedByFolder(station_list, mseed_folder):
#    """
#    Load mseed to memory
#    """
#    #copy mseed folder to results folder
#
#    for station in station_list:
#
#        # temp copy of station's stream list
#        _stream_list = list(station.stream_list)
#
#        for stream in station.stream_list:
#            try:
#                _output_file = str(station.network) + "_" +  \
#                               str(station.code) + "_" + str(stream.code) + \
#                               ".mseed"
#                _output_path = os.path.join(mseed_folder, _output_file)
#
#                _st = obspy_read(stream.mseed_path, format="MSEED")
#                stream.data = _st[0]
#            except:
#                _stream_list.remove(stream)
#
#        # make new stream list as station's stream list
#        station.stream_list = list(_stream_list)
#
#    return removeEmptyStations(station_list)

