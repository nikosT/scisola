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

from multiprocessing import Process as multiProcess
import distutils.dir_util as copyutil
import shutil
import datetime
import os
import time

# scisola's libs
import stream
import isola
import settings
import origin
import database
import seedlink
import plot
import logger


##############################################################################
# DEFINE CLASS "Directory"                                                   #
##############################################################################

class Directory:

    def __init__(self):
        """
        All folders and files needed for process to run listed
        in Directory class
        """

        self.allstat = None
        self.allstreams = None
        self.beachball = None
        self.cmseed = None # folder
        self.corr = None
        self.correlation = None
        self.crustal = None
        self.dsr = None
        self.event = None # folder
        self.grdat = None
        self.inv1 = None
        self.inv2 = None
        self.inv3 = None
        self.inversion = None # folder
        self.inversions = None
        self.inpinv = None
        self.log = None
        self.map = None
        self.misfit = None
        self.mseed = None # folder
        self.origin = None # folder
        self.plot = None # folder
        self.rdata = None # folder
        self.result = None # folder
        self.station = None
        self.stream = None # folder
        self.streams = None # folder
        self.text = None


##############################################################################
# DEFINE CLASS "Process"                                                     #
##############################################################################

class Process:

    def __init__(self, parent=None, origin=None, settings=None,
                 db_scisola=None, station_list=[], delay= 0, timeout=3600,
                 save2DB=False):
        """
        Initializing Process Object (Constructor)
        """
        try:
            self.parent = parent
            self.origin = origin
            self.settings = settings
            self.db_scisola = db_scisola
            self.station_list = station_list
            self.delay = delay
            self.timeout = timeout
            self.save2DB = save2DB

            self.log = None
            self.proc = None
            self.seedlink = None
            self.retr_duration = None
            self.tl = None
            self.crustal_layers = 0
            self.f1 = None
            self.f2 = None
            self.f3 = None
            self.f4 = None
            self.depth_list = []
            self.mt_list = []

            self.dir = Directory()

        except:
            if self.parent:
                self.parent.master_log.exception()
            return -1


    def restart(self):
        """
        Restarting process
        """
        self.stop()
        self.start()


    def stop(self):
        """
        Terminating process
        """
        try:
            if self.proc:
                self.proc.terminate()
                self.proc = None

        except:
            if self.parent:
                self.parent.master_log.exception()
            return -1


    def start(self):
        """
        Starting process (automatic or revised)
        """
        try:
            if self.origin and self.settings and self.db_scisola:

                # if already running
                if self.proc:
                    self.stop()

                self.seedlink = seedlink.Seedlink()
                self.seedlink.name = self.settings.seedlink_path
                self.seedlink.host = self.settings.seedlink_host
                self.seedlink.port = self.settings.seedlink_port
                self.seedlink.sc3_path = self.settings.sc3_path

                # now
                self.origin.timestamp = datetime.datetime.utcnow()
                # if station_list is empty then the process is automatic
                # else is revised
                self.origin.automatic = not bool(self.station_list)

                # automatic or revised procedure
                if self.origin.automatic:
                    self.proc = multiProcess(target=self.automatic)

                else:
                    self.proc = multiProcess(target=self.revised)

                if self.parent:
                    if self.origin.automatic:
                        self.parent.master_log.info("Starting automatic " + \
                        "procedure for event_id: " + \
                        str(self.origin.event_id) + \
                        "...\n")
                        self.parent.master_log.origin(self.origin)

                    else:
                        self.parent.master_log.info("Starting revised " + \
                                                    "procedure for " + \
                                                    "origin_id: " + \
                                                    str(self.origin.id) + \
                                                    "...\n")

                self.proc.start()
                self.proc.join(timeout=self.timeout)
                self.stop()

                if self.parent:
                    if self.origin.automatic:
                        self.parent.master_log.info("Automatic procedure" + \
                                                " finished successfully...\n")
                    else:
                        self.parent.master_log.info("Revised procedure" + \
                                                " finished successfully...\n")

        except:
            if self.parent:
                self.parent.master_log.exception()
            return -1


    def automatic(self):
        """
        Automatic procedure after origin trigger
        """
        # sleep delay sec before starting
        time.sleep(self.delay)

        self.createWorkingDir()
        self.log.origin(self.origin)
        self.log.settings(self.settings)

        try:
            self.retrieveStations()
            self.filterCorrectType()
            self.filterBlacklisted()
            self.calculateDistAzm()
            self.selectByDist()
            self.filterUnavailable()
            self.retrieveMseed()
            self.filterClipped()
            self.filterGapped()
            self.rotateStreams()
            self.correctStreams()
            self.selectByAzm()
            self.selectByISOLA()
            self.createRawFiles()
            self.createStationFile()
            self.loadCrustalFile()
            self.createGrdatFile()
            self.createInpinvFile()
            self.createAllstatFile()
            self.calculateDepths()
            self.calculateInversion()
            self.createMTs()
            self.createInversionResults()
            self.plotInversionResults()
            self.saveOrigin()
            self.log.info('Automatic procedure successfully finished...\n')

        except:
            self.log.info('Error occurred in automatic procedure...\n')
            if self.parent:
                self.parent.master_log.exception()
            return -1


    def revised(self):
        """
        Revised procedure by user demand
        """
        # sleep delay sec before starting
        time.sleep(self.delay)

        self.copyProcessDir()

        try:
            self.retrieveVars()
            self.createInpinvFile()
            self.createAllstatFile()
            self.calculateRevisedInversion()
            self.createMTs()
            self.createInversionResults()
            self.plotInversionResults()
            self.saveOrigin()
            self.log.info('Revised procedure successfully finished...\n')

        except:
            self.log.info('Error occurred in revised procedure...\n')
            if self.parent:
                self.parent.master_log.exception()
            return -1


    def createWorkingDir(self):
        """
        Event folder is named to event datetime
        Origin folder is named to datetime of the process

        Check if event folder exists. If not, create it
        and then create origin folder inside it
        """

        # event directory according to datetime
        _tempdatetime = datetime.datetime.strptime(self.origin.datetime,
                                                   "%Y/%m/%d %H:%M:%S.%f")

        self.dir.event = os.path.join(self.settings.output_dir,
                         _tempdatetime.strftime("%Y%m%d_%H%M%S%f"))

        # origin directory according to timestamp (subfolder of event folder)
        self.dir.origin = os.path.join(self.dir.event,
                          self.origin.timestamp.strftime("%Y%m%d_%H%M%S%f"))

        # subfolders of origin folder
        self.dir.inversion = os.path.join(self.dir.origin, "inversion")
        self.dir.plot = os.path.join(self.dir.origin, "plot")
        self.dir.stream = os.path.join(self.dir.origin, "stream")

        # subfiles of inversion folder
        self.dir.station = os.path.join(self.dir.inversion, 'station.dat')
        self.dir.grdat = os.path.join(self.dir.inversion, 'grdat.hed')
        self.dir.crustal = os.path.join(self.dir.inversion, 'crustal.dat')
        self.dir.inpinv = os.path.join(self.dir.inversion, 'inpinv.dat')
        self.dir.allstat = os.path.join(self.dir.inversion, 'allstat.dat')

        # subfolder of inversion folder
        self.dir.result = os.path.join(self.dir.inversion, 'result')

        # subfolders of stream folder
        self.dir.mseed = os.path.join(self.dir.stream, 'mseed')
        self.dir.cmseed = os.path.join(self.dir.stream, 'corrected_mseed')
        self.dir.rdata = os.path.join(self.dir.stream, 'raw_data')

        # subfiles of result folder
        self.dir.inv1 = os.path.join(self.dir.result, 'inv1.dat')
        self.dir.inv2 = os.path.join(self.dir.result, 'inv2.dat')
        self.dir.inv3 = os.path.join(self.dir.result, 'inv3.dat')
        self.dir.corr = os.path.join(self.dir.result, 'corr01.dat')
        self.dir.dsr = os.path.join(self.dir.result, 'dsr.dat')

        # subfiles of plot folder
        self.dir.beachball = os.path.join(self.dir.plot, 'beachball.png')
        self.dir.inversions = os.path.join(self.dir.plot, 'inversions.png')
        self.dir.correlation = os.path.join(self.dir.plot, 'correlation.png')
        self.dir.misfit = os.path.join(self.dir.plot, 'misfit.png')
        self.dir.map = os.path.join(self.dir.plot, 'map.png')
        self.dir.allstreams = os.path.join(self.dir.plot, 'allstreams.png')
        self.dir.text = os.path.join(self.dir.plot, 'text')

        # subfolder of plot folder
        self.dir.streams = os.path.join(self.dir.plot, 'streams')

        # create folders
        if not os.path.exists(self.dir.event):
            os.makedirs(self.dir.event)
        os.makedirs(self.dir.origin)
        os.makedirs(self.dir.inversion)
        os.makedirs(self.dir.plot)
        os.makedirs(self.dir.stream)
        os.makedirs(self.dir.mseed)
        os.makedirs(self.dir.cmseed)
        os.makedirs(self.dir.rdata)
        os.makedirs(self.dir.result)
        os.makedirs(self.dir.streams)

        # set log directory for process
        self.dir.log = os.path.join(self.dir.origin, "log")
        self.log = logger.Logger(self.dir.log)

        self.log.info('Working directory is set to: ' + \
                      str(self.dir.origin) + '\n')

        # saving origin's working space to origin object
        self.origin.results_dir = self.dir.origin


    def retrieveStations(self):
        """
        Retrieving stations and streams info from scisola database
        """
        try:
            self.log.info('Retrieving stations info from ' + \
                          'scisola database...\n')

            self.station_list = self.db_scisola.loadStations(
                                                            self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred in stations info retrieval...\n')
            raise


    def filterCorrectType(self):
        """
        Filtering streams by certain type
        """
        try:
            # selecting stations' streams from the station list
            # based on specifications

            self.log.info('Filtering streams by accepted type...\n' + \
                          '(Accepted Types:\n' + \
                          ' Band Code: H, B\n' + \
                          ' Instrument Code: H, L ,N\n' + \
                          ' Orientation Code: N, E, Z)...\n')

            self.station_list = stream.selectStreamsByType(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred in stations filtering by type...\n')
            raise


    def filterBlacklisted(self):
        """
        Filtering blacklisted streams by (by user) -priority=0-
        """
        try:
            self.log.info('Removing blacklisted stations and streams ' + \
                          '(priority=0)...\n')

            self.station_list = stream.removeBlacklisted(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred in filtering blacklisted ' + \
                          'streams...\n')
            raise


    def calculateDistAzm(self):
        """
        Calculating the distance and the azimuth (from North) between
        qualified stations and epicenter and selects those who are
        at the specific distance range (from distance min to distance max)
        """
        try:
            self.log.info('Calculating distance and azimuth (from North) ' + \
                          'between epicenter and station...\n')

            self.station_list = stream.calculateDistAzm(self.station_list,
                                                        self.origin)

        except:
            self.log.info('Error occurred in distance and azimuth ' + \
                          'calculation...\n')
            raise


    def selectByDist(self):
        """
        Selecting station by distance,
        from distance min to distance max between station and epicenter
        """
        try:
            for _rule in self.settings.distance_selection:
                if self.origin.magnitude <= float(_rule[1]) and \
                self.origin.magnitude >= float(_rule[0]):
                    _distance_min = int(_rule[2])
                    _distance_max = int(_rule[3])
                    break

            self.log.info('Selecting stations within ' + \
                          str(_distance_min) + \
                          ' and ' +  str(_distance_max) + \
                          ' (km) -between epicenter and station-...\n')

            self.station_list = stream.selectByDist(self.station_list,
                                                    _distance_min,
                                                    _distance_max)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred stations\' selection ' + \
                          'by distance...\n')
            raise


    def filterUnavailable(self):
        """
        Removing streams with no data based on the ringbuffer
        of seedlink server of the seiscomp3 server and the specific date,
        time and retrieval duration of data that need to be retrieved
        """
        try:
            for _rule in self.settings.inversion_time:
                if self.origin.magnitude <= float(_rule[1]) and \
                    self.origin.magnitude >= float(_rule[0]):
                        _inver_time = float(_rule[2])
                        break

            self.tl = _inver_time
            self.retr_duration = int(self.tl) + 5 #sec

            self.log.info('Removing streams with no data for ' + \
                          'the specific timespan (according to datetime: ' +\
                           str(self.origin.datetime) + \
                          ' and retrieval duration: ' + \
                          str(self.retr_duration) + ' sec)...\n')

            self.station_list = stream.removeUnavailableStreams(
                                                         self.seedlink,
                                                         self.station_list,
                                                         self.origin.datetime,
                                                         self.retr_duration)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred in selecting streams ' + \
                          'by seedlink availability...\n')
            raise


    def retrieveMseed(self):
        """
        Retrieving the mseed records for the qualified streams and
        for the specific timespan via slinktool,
        and loading it to memory
        """
        try:
            self.log.info('Retrieving mseed records for selected streams ' + \
                          'via slinktool...\n')

            self.station_list = stream.retrieveMseed(self.seedlink,
                                                     self.station_list,
                                                     self.origin.datetime,
                                                     self.retr_duration,
                                                     self.dir.mseed)

            # load to memory
            self.log.info('Loading mseed files from hard disk to memory...\n')
            self.station_list = stream.loadMseed(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error in stream mseed retrieval...\n')
            raise


    def filterClipped(self):
        """
        Removing clipped streams based on
        configuration threshold
        """
        try:
            self.log.info('Removing clipped streams based on threshold (' + \
                          str(self.settings.clipping_threshold) + ')...\n')

            self.station_list = stream.removeClipped(
                                             self.station_list,
                                             self.settings.clipping_threshold)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error in filtering clipped streams...\n')
            raise


    def filterGapped(self):
        """
        Removing streams with gaps
        """
        try:
            self.log.info('Removing streams with gaps...\n')

            self.station_list = stream.removeGapped(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error in filtering streams with gaps...\n')
            raise


    def rotateStreams(self):
        """
        Rotating streams if need it
        and removes those who have wrong orientation
        """
        try:
            self.log.info('Rotating stream data where necessary and ' + \
                          'removing streams with wrong orientation...\n')

            self.station_list = stream.rotateStreams(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error in streams\' rotation...\n')
            raise


    def correctStreams(self):
        """
        Applying correction to streams
        """
        try:
            self.log.info('Applying corrections to streams...\n' + \
                          ' (time alignment based on origin, ' + \
                          'instrument effect removal)...\n')

            self.station_list = stream.correctStreams(self.station_list,
                                                      self.origin.datetime,
                                                      self.tl)

            # save corrected mseeds to hard disk
            self.log.info('Saving corrected mseed records to corrected ' + \
                          'mseed folder...\n')
            self.station_list = stream.saveMseed(self.station_list,
                                                 self.dir.cmseed)

            self.log.info('Removing streams that don\'t have exactly ' + \
                          '8192 samples...\n')
            self.station_list = stream.removeWrongSample(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error in streams\' correction...\n')
            raise


    def selectByAzm(self):
        """
        Selecting station by azimuth distribution
        """
        try:
            _sectors = {}

            self.log.info('Selecting streams by azimuth distribution...\n')

            self.station_list, _sectors = stream.selectByAzm(
                                       self.station_list,
                                       int(self.settings.stations_per_sector),
                                       int(self.settings.min_sectors))

            if _sectors:
                # printing stations to log file
                self.log.info('No. of selected Stations: ' + \
                              str(len(self.station_list)))
                self.log.stations(self.station_list)
                self.log.sectors(_sectors)

            else:
                _error_msg = str(self.station_list[0])
                self.log.info(_error_msg)
                raise

        except:
            self.log.info('Error occurred in stations\' selection ' + \
                          'by azimuth...\n')
            raise


    def selectByISOLA(self):
        """
        selecting exactly 3 streams pers station,
        and no more than 21 stations in station_list
        in order to work ISOLA
        and remove those that don't have exactly 8192 data points
        """
        try:
            self.log.info('Removing more than 21 stations ' + \
                          '(in order to work ISOLA)...\n' + \
                          'Selecting no more than 3 streams per station, ' + \
                          'one for each component N,E,Z...\n')

            self.station_list = stream.selectISOLAstreams(self.station_list)

            # printing stations to log file
            self.log.info('No. of selected Stations: ' + \
                          str(len(self.station_list)))
            self.log.stations(self.station_list)

        except:
            self.log.info('Error occurred in streams ISOLA preperation...\n')
            raise


    def createRawFiles(self):
        """
        Creating the raw files; one for each station
        """
        try:
            self.log.info('Creating raw data files...\n')

            isola.createRawFiles(self.station_list, self.dir.rdata)

        except:
            self.log.info('Error occurred in creating the raw files...\n')
            raise


    def createStationFile(self):
        """
        Creating the station file
        """
        try:
            self.log.info('Creating station.dat file...\n')

            isola.createStationFile(self.station_list, self.dir.station)

        except:
            self.log.info('Error occurred in creating the ' + \
                          'station.dat file...\n')
            raise


    def loadCrustalFile(self):
        """
        Copying crustal_file to working directory;
        changing name to crustal.dat (if necessary)
        and returning the number of crustal layers
        """
        try:
            self.log.info('Copying crustal file...\n')

            self.crustal_layers = isola.loadCrustalFile(
                                             self.settings.crustal_model_path,
                                             self.dir.crustal)

            self.log.info(str(self.crustal_layers) + \
                          '-layer crustal file from: ' + self.dir.crustal)

        except:
            self.log.info('Error occurred in loading the ' + \
                          'the crustal file...\n')
            raise


    def createGrdatFile(self):
        """
        Creating the grdat.hed file
        """
        try:
            self.log.info('Creating grdat.hed file...\n')

            _grdat_offset = 0.2 # Hz

            for _rule in self.settings.inversion_frequency:
                if self.origin.magnitude <= float(_rule[1]) and \
                    self.origin.magnitude >= float(_rule[0]):
                        self.f1 = float(_rule[2])
                        self.f2 = float(_rule[3])
                        self.f3 = float(_rule[4])
                        self.f4 = float(_rule[5])
                        break

            # calculating nfreq
            _nfreq = self.tl * (self.f4 + _grdat_offset)

            # calculating xl
            _max_dist = max(station.distance_by_origin for station in
                            self.station_list)

            # old rule: _xl = 20 * 1000 * _max_dist * 2
            # new rule in xl
	    if int(_max_dist) > 100:
                _xl = 20 * 1000 * _max_dist
            else:
	        _xl = 2000000
		
            isola.createGrdatFile(self.crustal_layers, _nfreq, self.tl,
                                  len(self.station_list), _xl,
                                  self.dir.grdat)

        except:
            self.log.info('Error occurred in creating the ' + \
                          'grdat.hed file...\n')
            raise


    def createInpinvFile(self):
        """
        Creating the inpinv.dat file
        """
        try:
            self.log.info('Creating inpinv.dat file...\n')

            isola.createInpinvFile(self.tl,
                                   self.settings.time_grid_start,
                                   self.settings.time_grid_step,
                                   self.settings.time_grid_end,
                                   self.f1, self.f2, self.f3, self.f4,
                                   self.dir.inpinv)

        except:
            self.log.info('Error occurred in creating the ' + \
                          'inpinv.dat file...\n')
            raise


    def createAllstatFile(self):
        """
        Creating the allstat.dat file
        """
        try:
            self.log.info('Creating allstat.dat file...\n')

            isola.createAllstatFile(self.origin.automatic,
                                    self.station_list,
                                    self.f1, self.f2, self.f3, self.f4,
                                    self.dir.allstat)

        except:
            self.log.info('Error occurred in creating the ' + \
                          'allstat.dat file...\n')
            raise


    def calculateDepths(self):
        """
        Returns a list of possible centroid depths based on initial depth
        """
        try:
            self.log.info('Calculating possible centroid depths...\n')

            self.depth_list = isola.calculateDepths(self.origin.depth,
                                                    self.settings.source_step,
                                                    self.settings.sources)

            self.log.info('The possible centroid depths (in km) are:\n' + \
                          str(self.depth_list))

        except:
            self.log.info('Error occurred in depth calculation...\n')
            raise


    def calculateInversion(self):
        """
        Calculating inversion for all possible centroid depths in parallel
        """
        try:
            _multi_proc_list = []

            self.log.info('Calculating inversions for all possible ' + \
                          'centroid depths...\n')

            for depth in self.depth_list:
                _p = multiProcess(target=self.invertDepth, args=(depth,))
                _p.start()
                _multi_proc_list.append(_p)

            # waiting for all inversions to finish
            for _p in _multi_proc_list:
                _p.join()

            # prints all logs to log file
            for depth in self.depth_list:

                _log_path = os.path.join(self.dir.inversion, str(depth),
                                         "green_log")
                _log_file = open(_log_path,"r")
                _log_path2 = os.path.join(self.dir.inversion, str(depth),
                                         "invert_log")
                _log_file2 = open(_log_path2,"r")

                # writing each separated log of multiprocessing
                # to main log file
                _log_file.seek(0)
                _msg = "Calculating Green's functions and elementary" +\
                        " seismograms for depth (in km): " + str(depth) + "\n"
                _msg += _log_file.read()
                _log_file.close()
                self.log.info(_msg)

                _log_file2.seek(0)
                _msg = "Calculating inversion for depth (in km): " +\
                        str(depth) + "\n"
                _msg += _log_file2.read()
                _log_file2.close()
                self.log.info(_msg)

        except:
            self.log.info('Error occurred in inversion calculation...\n')
            raise


    def invertDepth(self, depth):
        """
        Calculating inversion for specific centroid depth
        """

        _gr_xyz = "gr_xyz" # name of the executable
        _elemse = "elemse" # name of the executable
        _isola12c = "isola12c" # name of the executable
        _norm12c = "norm12c" # name of the executable

        # set folder and files
        _depth_folder = os.path.join(self.dir.inversion, str(depth))
        _station_file = os.path.join(_depth_folder, 'station.dat')
        _crustal_file = os.path.join(_depth_folder, 'crustal.dat')
        _grdat_file = os.path.join(_depth_folder, 'grdat.hed')
        _inpinv_file = os.path.join(_depth_folder, 'inpinv.dat')
        _allstat_file = os.path.join(_depth_folder, 'allstat.dat')
        _source_file = os.path.join(_depth_folder, 'source.dat')

        # create depth folder
        if not os.path.exists(_depth_folder):
            os.makedirs(_depth_folder)

        # copy raw files
        copyutil.copy_tree(self.dir.rdata, _depth_folder)

        # copy ISOLA files
        shutil.copyfile(self.dir.station, _station_file)
        shutil.copyfile(self.dir.crustal, _crustal_file)
        shutil.copyfile(self.dir.grdat, _grdat_file)
        shutil.copyfile(self.dir.inpinv, _inpinv_file)
        shutil.copyfile(self.dir.allstat, _allstat_file)

        # create src file
        _date = self.origin.datetime.split()[0]

        isola.createSource(_date, self.origin.magnitude,
                           depth, _source_file)

        # calculate Green's functions and elementary seismograms
        _gr_xyz_file = os.path.join(self.settings.isola_path, _gr_xyz)
        _elemse_file = os.path.join(self.settings.isola_path, _elemse)
        _isola12c_file = os.path.join(self.settings.isola_path, _isola12c)
        _norm12c_file = os.path.join(self.settings.isola_path, _norm12c)

        isola.calculateGreens(_gr_xyz_file, _elemse_file, _depth_folder)

        # rename "elemse.dat" to "elemse01.dat"
        # in order to run ISOLA properly
        shutil.move(os.path.join(_depth_folder, 'elemse.dat'),
            os.path.join(_depth_folder, 'elemse01.dat'))
        shutil.move(os.path.join(_depth_folder, 'gr.hea'),
            os.path.join(_depth_folder, 'gr.01.hea'))
        shutil.move(os.path.join(_depth_folder, 'gr.hes'),
            os.path.join(_depth_folder, 'gr.01.hes'))

        # calculate inversion
        isola.calculateInversion(_isola12c_file, _norm12c_file,
                                 _depth_folder)


    def createMTs(self):
        """
        Create a list with all possible mt results,
        one mt for each possible depth
        """
        try:
            self.log.info('Creating Moment Tensor objects ' + \
                          'for all possible centroid depths...\n')

            for depth in self.depth_list:

                _inv1_file = os.path.join(self.dir.inversion, str(depth),
                                          "inv1.dat")
                _inv3_file = os.path.join(self.dir.inversion, str(depth),
                                          "inv3.dat")

                # add moment tensor to list
                mt = origin.MomentTensor()
                mt = isola.load_MT(depth, self.tl, self.origin, _inv1_file,
                                  _inv3_file, mt, self.f1, self.f2, self.f3,
                                  self.f4)
                self.mt_list.append(mt)

            # prints all mts
            self.log.mts(self.mt_list)

        except:
            self.log.info('Error occurred in Moment Tensor collection...\n')
            raise


    def createInversionResults(self):
        """
        Creating the inversion results files
        """
        try:
            _kagan = "kagan"

            # finding best inversion centroid depth
            self.origin.mt = isola.getBestMT(self.mt_list)

            # create final corr file
            self.log.info('Creating final correlation file...\n')
            isola.createCorrFile(self.depth_list,
                                 self.dir.inversion,
                                 self.dir.corr)

            # calculating stVar and fmVar
            _kagan_path = os.path.join(self.settings.isola_path, _kagan)
            _results = plot.corr_file2data(self.dir.corr)
            _corr_list = _results[3]
            _bball_list = _results[4]
            _stVar, _fmVar = isola.calcuateStFmVar(_kagan_path,
                                                   _corr_list,
                                                   _bball_list,
                                                   self.origin.mt,
                                                   self.settings)
            self.origin.mt.stVar = _stVar
            self.origin.mt.fmVar = _fmVar

            # create final inv1 file
            self.log.info('Creating final inv1 file...\n')
            isola.createInv1File(self.mt_list,
                                 self.origin.mt,
                                 self.dir.inv1)

            # create final inv2 file
            self.log.info('Creating final inv2 file...\n')
            isola.createInv2File(self.origin.mt,
                                 self.dir.inv2)

            # create final inv3 file
            self.log.info('Creating final inv3 file...\n')
            isola.createInv3File(self.origin.mt,
                                 self.dir.inv3)

            self.log.info('Printing best Moment Tensor solution...\n')
            self.log.mts([self.origin.mt])

        except:
            self.log.info('Error occurred in inversion results creation...\n')
            raise


    def plotInversionResults(self):
        """
        Plotting inversion results to plot folder
        """
        try:
            _dsretc = "dsretc"
            self.log.info('Plotting inversion results...\n')

            self.log.info('Plotting stream waveforms...\n')
            plot.streams(self.station_list, self.dir.streams,
                         self.dir.allstreams)

            self.log.info('Plotting inversions...\n')
            _depth, _corr, _dc, _bballs =  plot.mt_list2data(self.mt_list)
            plot.correlation(_depth, _corr, _dc, _bballs, self.dir.inversions)

            self.log.info('Plotting misfits...\n')
            # find best mt depth folder
            _depth_folder = os.path.join(self.dir.inversion,
                                         str(self.origin.mt.cent_depth))
            plot.misfit(self.tl, self.station_list,
                        _depth_folder, self.dir.misfit)

            self.log.info('Plotting correlations...\n')
            _time_list, _depth_list, _dc_list, _corr_list, _bball_list = \
                                        plot.corr_file2data(self.dir.corr)
            plot.contour(_time_list, _depth_list, _dc_list, _corr_list,
                         _bball_list, self.dir.correlation)

            self.log.info('Plotting focal mechanism...\n')
            plot.beachBall(self.origin.mt.strike,
                           self.origin.mt.dip,
                           self.origin.mt.rake,
			   self.origin.mt.mrr,
			   self.origin.mt.mtt,
			   self.origin.mt.mpp,
			   self.origin.mt.mrt,
			   self.origin.mt.mrp,
			   self.origin.mt.mtp,
                           self.dir.beachball)

            self.log.info('Plotting map...\n')
            plot.maps(self.station_list, self.origin,
                      self.origin.mt.strike,
                      self.origin.mt.dip,
                      self.origin.mt.rake,
                      self.dir.map)

            self.log.info('Plotting text results...\n')

            _dsretc_path = os.path.join(self.settings.isola_path, _dsretc)
            plot.results2text(self.station_list, self.origin,
                              self.settings, self.dir.result,
                              _dsretc_path, self.f1, self.f2, self.f3,
                              self.f4, self.dir.text)

        except:
            self.log.info('Error occurred in plotting inversion results...\n')
            raise


    def saveOrigin(self):
        """
        Saving results to database
        """
        try:
            if self.save2DB:
                self.log.info('Saving results to scisola database...\n')
                self.db_scisola.saveOrigin(self.origin, self.station_list)

        except:
            self.log.info('Error occurred in saving results to ' + \
                          'scisola database...\n')
            raise


#*****************************************************************************
#*                         Start of revised functions                        *
#*****************************************************************************

    def copyProcessDir(self):
        """
        Copy all data from process folder (from the automatic procedure)
        """

        _original_results_dir = self.origin.results_dir

        self.createRevisedWorkingDir()

        # copy all contents
        copyutil.copy_tree(_original_results_dir, self.origin.results_dir)

        # delete initial plot streams
        shutil.rmtree(self.dir.streams)
        # re-create plot streams folder
        os.makedirs(self.dir.streams)

        self.log = logger.Logger(self.dir.log)
        self.log.info('Revised Working directory is set to: ' + \
                      str(self.dir.origin) + '\n')


    def createRevisedWorkingDir(self):
        """
        Event folder is named to event datetime
        Origin folder is named to datetime of the process

        Check if event folder exists. If not, create it
        and then create origin folder inside it
        """

        # event directory according to path
        self.dir.event = os.path.dirname(self.origin.results_dir)

        # origin directory according to timestamp (subfolder of event folder)
        self.dir.origin = os.path.join(self.dir.event,
                          self.origin.timestamp.strftime("%Y%m%d_%H%M%S%f"))

        self.dir.origin = self.dir.origin + "_rev"

        # subfolders of origin folder
        self.dir.inversion = os.path.join(self.dir.origin, "inversion")
        self.dir.plot = os.path.join(self.dir.origin, "plot")
        self.dir.stream = os.path.join(self.dir.origin, "stream")

        # subfiles of inversion folder
        self.dir.station = os.path.join(self.dir.inversion, 'station.dat')
        self.dir.grdat = os.path.join(self.dir.inversion, 'grdat.hed')
        self.dir.crustal = os.path.join(self.dir.inversion, 'crustal.dat')
        self.dir.inpinv = os.path.join(self.dir.inversion, 'inpinv.dat')
        self.dir.allstat = os.path.join(self.dir.inversion, 'allstat.dat')

        # subfolder of inversion folder
        self.dir.result = os.path.join(self.dir.inversion, 'result')

        # subfolders of stream folder
        self.dir.mseed = os.path.join(self.dir.stream, 'mseed')
        self.dir.cmseed = os.path.join(self.dir.stream, 'corrected_mseed')
        self.dir.rdata = os.path.join(self.dir.stream, 'raw_data')

        # subfiles of result folder
        self.dir.inv1 = os.path.join(self.dir.result, 'inv1.dat')
        self.dir.inv2 = os.path.join(self.dir.result, 'inv2.dat')
        self.dir.inv3 = os.path.join(self.dir.result, 'inv3.dat')
        self.dir.corr = os.path.join(self.dir.result, 'corr01.dat')
        self.dir.dsr = os.path.join(self.dir.result, 'dsr.dat')

        # subfiles of plot folder
        self.dir.beachball = os.path.join(self.dir.plot, 'beachball.png')
        self.dir.inversions = os.path.join(self.dir.plot, 'inversions.png')
        self.dir.correlation = os.path.join(self.dir.plot, 'correlation.png')
        self.dir.misfit = os.path.join(self.dir.plot, 'misfit.png')
        self.dir.map = os.path.join(self.dir.plot, 'map.png')
        self.dir.allstreams = os.path.join(self.dir.plot, 'allstreams.png')
        self.dir.text = os.path.join(self.dir.plot, 'text')

        # subfolder of plot folder
        self.dir.streams = os.path.join(self.dir.plot, 'streams')

        # set log directory for process
        self.dir.log = os.path.join(self.dir.origin, "log")

        # saving origin's working space to origin object
        self.origin.results_dir = self.dir.origin


    def retrieveVars(self):
        """
        Retrieving all important variables in order to run the revised
        procedure
        """
        try:
            self.log.info('Retrieving all important variables ' + \
                          'in order to run the revised procedure...\n')

            # get depth list
            _text = "The possible centroid depths (in km) are:"
            _f = open(self.dir.log, "r")
            _lines = _f.readlines()
            _f.close()
            for _i, _line in enumerate(_lines):
                if _text in _line:
                    self.depth_list = eval(_lines[_i+1][:-1])
                    break

            # tl
            _f = open(self.dir.grdat, "r")
            _lines = _f.readlines()
            _f.close()
            self.tl = float(_lines[3][3:-1])

            # time_grid_start, step, end
            _f = open(self.dir.inpinv, "r")
            _lines = _f.readlines()
            _f.close()
            _l = _lines[8][:-1].split()
            self.settings.time_grid_start = int(_l[0])
            self.settings.time_grid_step = int(_l[1])
            self.settings.time_grid_end = int(_l[2])

            # load stations info (coordinates)
            _station_list = []
            _station_list = self.db_scisola.loadStations(_station_list)

            for station in self.station_list:
                for _station in _station_list:
                    if _station.code == station.code:
                        station.latitude = _station.latitude
                        station.longitude = _station.longitude
                        break

            self.station_list = stream.calculateDistAzm(self.station_list,
                                                        self.origin)

        except:
            self.log.info('Error occurred in variables retrieval...\n')
            raise


    def calculateRevisedInversion(self):
        """
        Calculating inversion for all possible centroid depths in parallel
        """
        try:
            _multi_proc_list = []

            self.log.info('Calculating inversions for all possible ' + \
                          'centroid depths...\n')

            self.log.info('All possible centroid depths (in km) are:\n' + \
                          str(self.depth_list))

            for depth in self.depth_list:
                _p = multiProcess(target=self.invertRevisedDepth,
                                  args=(depth,))
                _p.start()
                _multi_proc_list.append(_p)

            # waiting for all inversions to finish
            for _p in _multi_proc_list:
                _p.join()

            # prints all logs to log file
            for depth in self.depth_list:

                _log_path2 = os.path.join(self.dir.inversion, str(depth),
                                         "invert_log")
                _log_file2 = open(_log_path2,"r")

                # writing each separated log of multiprocessing
                # to main log file
                _log_file2.seek(0)
                _msg = "Calculating inversion for depth (in km): " +\
                        str(depth) + "\n"
                _msg += _log_file2.read()
                _log_file2.close()
                self.log.info(_msg)

        except:
            self.log.info('Error occurred in revised inversion ' + \
                          'calculation...\n')
            raise


    def invertRevisedDepth(self, depth):
        """
        Calculating inversion for specific centroid depth
        """

        _isola12c = "isola12c" # name of the executable
        _norm12c = "norm12c" # name of the executable

        # set folder and files
        _depth_folder = os.path.join(self.dir.inversion, str(depth))

        _inpinv_file = os.path.join(_depth_folder, 'inpinv.dat')
        _allstat_file = os.path.join(_depth_folder, 'allstat.dat')
        shutil.copyfile(self.dir.inpinv, _inpinv_file)
        shutil.copyfile(self.dir.allstat, _allstat_file)

        _isola12c_file = os.path.join(self.settings.isola_path, _isola12c)
        _norm12c_file = os.path.join(self.settings.isola_path, _norm12c)

        # calculate inversion
        isola.calculateInversion(_isola12c_file, _norm12c_file,
                                 _depth_folder)


if __name__ == "__main__":


    orig = origin.Origin()
#    orig.datetime = "2014/06/25 09:21:41.00"
#    orig.magnitude = 3.9
#    orig.longitude = 21.747
#    orig.latitude = 38.3568
#    orig.depth = 7
    orig.datetime = str(sys.argv[1]) + " " + str(sys.argv[2])
    orig.magnitude = float(sys.argv[6])
    orig.longitude = float(sys.argv[4])
    orig.latitude = float(sys.argv[3])
    orig.depth = int(float(sys.argv[5]))
    orig.event_id = "dataset"

#    orig.datetime = "2014/02/26 01:42:50.00"
#    orig.magnitude = 4
#    orig.longitude = 21.6427
#    orig.latitude = 40.2275
#    orig.depth = 24.9

    db = database.Database()
    db.password = "11221122"

    sett = settings.Settings()

    sett = db.loadSettings(sett)
    print vars(orig)
    p = Process(origin=orig, settings=sett, db_scisola=db, save2DB=True, delay=0)
    p.start()

