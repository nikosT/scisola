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
import MySQLdb as mysql
import psycopg2 as psql
import datetime as date

# scisola's imports
import stream
import origin


##############################################################################
# DEFINE CLASS "Database"                                                    #
##############################################################################

class Database:

    """
    The class used for database connections
    """
    def __init__(self, type="MySQL"):
        """
        Constructor of database class
        """
        self.type = type
        self.host = "localhost"
        self.database = "scisola"
        self.setDefault()


    def setDefault(self):
        """
        Setting default values
        """
        if self.type == "MySQL":
            self.user = "root"
            self.password = "root"
            self.port = 3306
        else:
            self.user = "postgres"
            self.password = "postgres"
            self.port = 5432


    def read(self, queries):
        """
        read from database
        queries = [query1, query2, ...]
        return type: list -results-
        results = [result1, result2, ...]
        """
        results=[]

        if self.type == "MySQL":
            _db = mysql.connect(user=self.user, passwd=self.password,
                        host=self.host, port=self.port, db=self.database)
        else:
            _db = psql.connect(user=self.user, password=self.password,
                       host=self.host, port=self.port, database=self.database)

        _cur = _db.cursor()
        for query in queries:
            _cur.execute(query)
            _result = _cur.fetchall()

            # append result to to results list that will be returned
            results.append(_result)

        _cur.close()
        _db.close()

        return results


    def write(self, queries):
        """
        write to databases
        queries = [query1, query2, ...]
        return type: [action, results]
        action = 0 for success and -1 for error
        on success results = [result1, result2, ...]
        on error results = [error code, error message]
        """

        try:
            if self.type == "MySQL":
                _db = mysql.connect(user=self.user, passwd=self.password,
                            host=self.host, port=self.port, db=self.database)
            else:
                _db = psql.connect(user=self.user, password=self.password,
                           host=self.host, port=self.port,
                           database=self.database)

            _db.autocommit(False)
            _cur = _db.cursor()
            for query in queries:
                _cur.execute(query)

            _db.commit()

            _cur.close()
            _db.close()

        except (mysql.Error, psql.Error):
            if _db:
                _db.rollback()
            raise


    def checkDB(self):
        """
        Checks if database is accessible.
        Returns True/False.
        """

        try:
            self.read(["show tables"])
            return True
        except:
            return False


    def saveSettings(self, settings):
        """
        Saves setting to scisola database.
        Returns True/False and ()/error.
        """

        try:
            queries = []

            _query = "DELETE FROM `Settings` WHERE id = 1;"
            queries.append(_query)

            _query = "INSERT IGNORE INTO `Settings` (`id`, " + \
            "`timestamp`, `center_latitude`, `center_longitude`, " + \
            "`distance_range`, `magnitude_threshold`, `min_sectors`, " + \
            "`stations_per_sector`, `sources`, `source_step`, " + \
            "`clipping_threshold`, `time_grid_start`, " + \
            "`time_grid_step`, `time_grid_end`, `watch_interval`, " + \
            "`process_delay`, `process_timeout`, " + \
            "`crustal_model_path`, `output_dir`, `isola_path`, " + \
            "`sc3_path`, `sc3_scevtls`, `sc3_scxmldump`, " + \
            "`seedlink_path`, `seedlink_host`, `seedlink_port`) " + \
            "VALUES (1, utc_timestamp(), " + \
            str(settings.center_latitude) + ", " + \
            str(settings.center_longitude) + ", " + \
            str(settings.distance_range) + ", " + \
            str(settings.magnitude_threshold) + ", " + \
            str(settings.min_sectors) + ", " + \
            str(settings.stations_per_sector) + ", " + \
            str(settings.sources) + ", " + \
            str(settings.source_step) + ", " + \
            str(settings.clipping_threshold) + ", " + \
            str(settings.time_grid_start) + ", " + \
            str(settings.time_grid_step) + ", " + \
            str(settings.time_grid_end) + ", " + \
            str(settings.watch_interval) + ", " + \
            str(settings.process_delay) + ", " + \
            str(settings.process_timeout) + ", " + \
            "\"" + str(settings.crustal_model_path) + "\", " + \
            "\"" + str(settings.output_dir) + "\", " + \
            "\"" + str(settings.isola_path) + "\", " + \
            "\"" + str(settings.sc3_path) + "\", " + \
            "\"" + str(settings.sc3_scevtls) + "\", " + \
            "\"" + str(settings.sc3_scxmldump) + "\", " + \
            "\"" + str(settings.seedlink_path) + "\", " + \
            "\"" + str(settings.seedlink_host) + "\", " + \
            str(settings.seedlink_port) + ");"
            queries.append(_query)

            for _entry in settings.distance_selection:
                _query = "INSERT IGNORE INTO Distance_selection " + \
                "(min_magnitude, max_magnitude, min_distance, " + \
                "max_distance, Settings_id)" + \
                "VALUES (" + \
                str(_entry[0]) + ", " + \
                str(_entry[1]) + ", " + \
                str(_entry[2]) + ", " + \
                str(_entry[3]) + ", 1);"
                queries.append(_query)

            for _entry in settings.inversion_time:
                _query = "INSERT IGNORE INTO Inversion_time " + \
                "(min_magnitude, max_magnitude, tl, Settings_id)" + \
                "VALUES (" + \
                str(_entry[0]) + ", " + \
                str(_entry[1]) + ", " + \
                str(_entry[2]) + ", 1);"
                queries.append(_query)

            for _entry in settings.inversion_frequency:
                _query = "INSERT IGNORE INTO Inversion_frequency " + \
                "(min_magnitude, max_magnitude, frequency_1, " + \
                "frequency_2, frequency_3, frequency_4, " + \
                "Settings_id)" + \
                "VALUES (" + \
                str(_entry[0]) + ", " + \
                str(_entry[1]) + ", " + \
                str(_entry[2]) + ", " + \
                str(_entry[3]) + ", " + \
                str(_entry[4]) + ", " + \
                str(_entry[5]) + ", 1);"
                queries.append(_query)

            self.write(queries)
            return None

        except:
            return sys.exc_info()


    def loadSettings(self, settings):
        """
        Loads settings from scisola database.
        Returns True/False and settings/error.
        """
        try:
            queries = []

            _query = "SELECT `id`, `timestamp`, `center_latitude`, " + \
            "`center_longitude`, `distance_range`, " + \
            "`magnitude_threshold`, `min_sectors`, " + \
            "`stations_per_sector`, `sources`, `source_step`, " + \
            "`clipping_threshold`, `time_grid_start`, " + \
            "`time_grid_step`, `time_grid_end`, `watch_interval`, " + \
            "`process_delay`, `process_timeout`, " + \
            "`crustal_model_path`, `output_dir`, `isola_path`, " + \
            "`sc3_path`, `sc3_scevtls`, `sc3_scxmldump`, " + \
            "`seedlink_path`, `seedlink_host`, `seedlink_port` " + \
            "FROM `Settings` WHERE id = 1;"
            queries.append(_query)

            _query = "SELECT `min_magnitude`, `max_magnitude`, " + \
            "`min_distance`, `max_distance`, `Settings_id` " + \
            "FROM `Distance_selection`;"
            queries.append(_query)

            _query = "SELECT `min_magnitude`, `max_magnitude`, `tl`, " + \
            "`Settings_id` FROM `Inversion_time`;"
            queries.append(_query)

            _query = "SELECT `min_magnitude`, `max_magnitude`, " + \
            "`frequency_1`, `frequency_2`, `frequency_3`, " + \
            "`frequency_4`, `Settings_id` FROM `Inversion_frequency`;"
            queries.append(_query)

            _dsettings, _ddistance, _dtime, _dfrequency = self.read(queries)

            _dsettings = _dsettings[0]

            settings.id = int(_dsettings[0])
            settings.timestamp = str(_dsettings[1])
            settings.center_latitude = float(_dsettings[2])
            settings.center_longitude = float(_dsettings[3])
            settings.distance_range = int(_dsettings[4])
            settings.magnitude_threshold = float(_dsettings[5])
            settings.min_sectors = int(_dsettings[6])
            settings.stations_per_sector = int(_dsettings[7])
            settings.sources = int(_dsettings[8])
            settings.source_step = int(_dsettings[9])
            settings.clipping_threshold = float(_dsettings[10])
            settings.time_grid_start = int(_dsettings[11])
            settings.time_grid_step = int(_dsettings[12])
            settings.time_grid_end = int(_dsettings[13])
            settings.watch_interval = int(_dsettings[14])
            settings.process_delay = int(_dsettings[15])
            settings.process_timeout = int(_dsettings[16])
            settings.crustal_model_path = str(_dsettings[17])
            settings.output_dir = str(_dsettings[18])
            settings.isola_path = str(_dsettings[19])
            settings.sc3_path = str(_dsettings[20])
            settings.sc3_scevtls = str(_dsettings[21])
            settings.sc3_scxmldump = str(_dsettings[22])
            settings.seedlink_path = str(_dsettings[23])
            settings.seedlink_host = str(_dsettings[24])
            settings.seedlink_port = int(_dsettings[25])

            settings.distance_selection = []
            for _row in _ddistance:
                if _row:
                    settings.distance_selection.append([_row[0], _row[1],
                                                      int(_row[2]), int(_row[3])])

            settings.inversion_time = []
            for _row in _dtime:
                if _row:
                    settings.inversion_time.append([_row[0], _row[1],
                                                    _row[2]])

            settings.inversion_frequency = []
            for _row in _dfrequency:
                if _row:
                    settings.inversion_frequency.append([_row[0], _row[1],
                                                         _row[2], _row[3],
                                                         _row[4], _row[5]])

            return settings
        except:
            return None


    def loadStations(self, station_list):
        """
        Fetches Streams (and Stations) from the scisola database
        and saves them in station_list (list containing stations objects).
        Returns list -station_list-.
        """
        queries = []

        _query = "SELECT Station.code, Station.network, " + \
        "Station.description, Station.latitude, " + \
        "Station.longitude, Station.elevation, " + \
        "Station.priority FROM Station;"
        queries.append(_query)

        _query = "SELECT Station.network, Station.code, Stream.code, " + \
        "Station.description, Station.latitude, Station.longitude, " + \
        "Station.elevation, Stream.azimuth, Stream.dip, " + \
        "Stream.gain_sensor, Stream.gain_datalogger, " + \
        "Stream.norm_factor, Stream.nzeros, Stream.zeros_content, " + \
        "Stream.npoles, Stream.poles_content, Stream.priority " + \
        "FROM Station INNER JOIN Stream ON Station.id=Stream.station_id;"
        queries.append(_query)

        _station_rows, _stream_rows = self.read(queries)

        for _row in _station_rows:
            station = stream.Station()
            station.code = _row[0]
            station.network = _row[1]
            station.description = _row[2]
            station.latitude = _row[3]
            station.longitude = _row[4]
            station.elevation = _row[5]
            station.priority= int(_row[6])
            station_list.append(station)

        _stream_list = []
        for _row in _stream_rows:
            strm = stream.Stream()
            strm.station = stream.Station()
            strm.station.code = _row[1]
            strm.station.network = _row[0]
            strm.station.description = _row[3]
            strm.station.latitude = _row[4]
            strm.station.longitude = _row[5]
            strm.station.elevation = _row[6]
            strm.code = _row[2]
            strm.azimuth = _row[7]
            strm.dip = _row[8]
            strm.gain_sensor = _row[9]
            strm.gain_datalogger = _row[10]
            strm.norm_factor = _row[11]
            strm.nzeros = _row[12]
            strm.zeros_content = stream.blob2list(_row[13])
            strm.npoles = _row[14]
            strm.poles_content = stream.blob2list(_row[15])
            strm.priority = int(_row[16])
            _stream_list.append(strm)

        for station in station_list:
            station.stream_list = [_stream for _stream in _stream_list
                                 if _stream.station.network == station.network
                                 and _stream.station.code == station.code]

        return stream.removeEmptyStations(station_list)


    def importFromSc3(self, db_sc3, reset=False):
        """
        Imports stations and streams from SeisComP3 database
        to scisola database. If reset True, deletes all previous rows
        from stations and streams tables before inserts new ones
        otherwise appends new stations and streams without losing old ones
        and their settings.
        Returns True/False and ()/error.
        """

        try:
            queries = []

            # IF SEISCOMP3 MYSQL DATABASE
            if db_sc3.type == "MySQL":
                # fetching sc3 info
                # query for fetching stations from SeisComP3
                _query = "SELECT Station._oid, Station.code, " + \
                "Network.code, Station.description, Station.latitude, " + \
                "Station.longitude, Station.elevation from Network " + \
                "INNER JOIN Station on Network._oid=Station._parent_oid;"
                queries.append(_query)

                # query for fetching streams from SeisComP3
                _query = "SELECT Stream._oid, Station._oid, Stream.code, " + \
                "Stream.azimuth, Stream.dip, ResponsePAZ.gain, " + \
                "Datalogger.gain, ResponsePAZ.normalizationFactor, " + \
                "ResponsePAZ.numberOfZeros, ResponsePAZ.zeros_content, " + \
                "ResponsePAZ.numberOfPoles, ResponsePAZ.poles_content " + \
                "FROM Stream " + \
                "INNER JOIN PublicObject ON " + \
                "PublicObject.publicID=Stream.sensor " + \
                "INNER JOIN Sensor ON Sensor._oid=PublicObject._oid " + \
                "INNER JOIN PublicObject PublicObject2 ON " + \
                "PublicObject2.publicID=Sensor.response " + \
                "INNER JOIN ResponsePAZ ON " + \
                "ResponsePAZ._oid=PublicObject2._oid " + \
                "INNER JOIN PublicObject PublicObject3 ON " + \
                "PublicObject3.publicID=Stream.datalogger " + \
                "INNER JOIN Datalogger ON " + \
                "Datalogger._oid=PublicObject3._oid " + \
                "INNER JOIN SensorLocation ON " + \
                "SensorLocation._oid=Stream._parent_oid " + \
                "INNER JOIN Station ON " + \
                "Station._oid=SensorLocation._parent_oid;"
                queries.append(_query)

            # IF SEISCOMP3 POSTGRES DATABASE
            else:
                # fetching sc3 info
                # query for fetching stations from SeisComP3
                _query = "SELECT Station._oid, Station.m_code, " + \
                "Network.m_code, Station.m_description, " + \
                "Station.m_latitude, " + \
                "Station.m_longitude, Station.m_elevation from Network " + \
                "INNER JOIN Station on Network._oid=Station._parent_oid;"
                queries.append(_query)

                # query for fetching streams from SeisComP3
                _query = "SELECT Stream._oid, Station._oid, " + \
                "Stream.m_code, " + \
                "Stream.m_azimuth, Stream.m_dip, ResponsePAZ.m_gain, " + \
                "Datalogger.m_gain, ResponsePAZ.m_normalizationFactor, " + \
                "ResponsePAZ.m_numberOfZeros, " + \
                "encode(ResponsePAZ.m_zeros_content,'escape'), " + \
                "ResponsePAZ.m_numberOfPoles, " + \
                "encode(ResponsePAZ.m_poles_content,'escape') " + \
                "FROM Stream " + \
                "INNER JOIN PublicObject ON " + \
                "PublicObject.m_publicID=Stream.m_sensor " + \
                "INNER JOIN Sensor ON Sensor._oid=PublicObject._oid " + \
                "INNER JOIN PublicObject PublicObject2 ON " + \
                "PublicObject2.m_publicID=Sensor.m_response " + \
                "INNER JOIN ResponsePAZ ON " + \
                "ResponsePAZ._oid=PublicObject2._oid " + \
                "INNER JOIN PublicObject PublicObject3 ON " + \
                "PublicObject3.m_publicID=Stream.m_datalogger " + \
                "INNER JOIN Datalogger ON " + \
                "Datalogger._oid=PublicObject3._oid " + \
                "INNER JOIN SensorLocation ON " + \
                "SensorLocation._oid=Stream._parent_oid " + \
                "INNER JOIN Station ON " + \
                "Station._oid=SensorLocation._parent_oid;"
                queries.append(_query)

            _sc3_stations, _sc3_streams = db_sc3.read(queries)

            # importing sc3 info to scisola
            queries= []

            # if True, deletes all rows from stations and streams tables
            if reset:
                _query = "DELETE FROM `Station`;"
                queries.append(_query)

            # query for inserting stations from SeisComP3
            _query = "INSERT IGNORE INTO Station VALUES "
            for _row in _sc3_stations:
                _query += str(_row)[:-1].replace("L","",1) + ", 5),"

            _query = _query[:-1] + ";"
            queries.append(_query)

            # query for inserting streams from SeisComP3
            _query = "INSERT IGNORE INTO Stream VALUES "
            for _row in _sc3_streams:
                if _row[2][1] == "H":
                    _priority = 7
                elif _row[2][1] == "L":
                    _priority = 6
                else:
                    _priority = 5

                _query += str(_row)[:-1].replace("L","",2) + ", " + \
                str(_priority) + "),"

            _query = _query[:-1] + ";"
            queries.append(_query)

            self.write(queries)
            return None

        except:
            return sys.exc_info()


    def updateStations(self, station_list2D):
        """
        Updates stations and streams info
        (based on edit database option in settings window)
        """

        try:
            queries = []

            for _row in station_list2D:
                _network = str(_row[0])
                _station = str(_row[1])
                _stream = str(_row[2])
                _latitude = str(_row[3])
                _longitude = str(_row[4])
                _sta_priority = str(_row[5])
                _stm_priority = str(_row[6])
                _azimuth = str(_row[7])
                _dip = str(_row[8])
                _gain_sensor = str(_row[9])
                _gain_datalogger = str(_row[10])
                _norm_factor = str(_row[11])
                _nzeros = str(_row[12])
                _zeros_content = stream.list2blob(eval(_row[13]))
                _npoles = str(_row[14])
                _poles_content = stream.list2blob(eval(_row[15]))

                _query = "UPDATE Station INNER JOIN Stream ON " + \
                          "Station.id = Stream.station_id " + \
                          "SET Station.latitude=" + _latitude + ", " + \
                          "Station.longitude=" + _longitude + ", " + \
                          "Station.priority=" + _sta_priority + ", " + \
                          "Stream.priority=" + _stm_priority + ", " + \
                          "Stream.azimuth=" + _azimuth + ", " + \
                          "Stream.dip=" + _dip + ", " + \
                          "Stream.gain_sensor=" + _gain_sensor + ", " + \
                          "Stream.gain_datalogger=" + _gain_datalogger + \
                          ", " + \
                          "Stream.norm_factor=" + _norm_factor + ", " + \
                          "Stream.nzeros=" + _nzeros + ", " + \
                          "Stream.zeros_content=\"" + _zeros_content + \
                          "\", " + \
                          "Stream.npoles=" + _npoles + ", " + \
                          "Stream.poles_content=\"" + _poles_content + \
                          "\" " + \
                          "WHERE Station.network=\"" + _network + "\"" + \
                          " AND Station.code=\"" + _station + "\"" + \
                          " AND Stream.code=\"" + _stream + "\""

                queries.append(_query)

            if queries:
                self.write(queries)

            return None

        except:
            return sys.exc_info()


    def loadOriginsT20(self):
        """
        Fetches Origins (and MTs) from the scisola database
        and saves them in list.
        Returns True/False and origins' data/error.
        """

        queries = []

        _query = "SELECT `Origin`.`timestamp`, " + \
        "`Origin`.`datetime`, " + \
        "`Moment_Tensor`.`cent_latitude`, " + \
        "`Moment_Tensor`.`cent_longitude`, " + \
        "`Moment_Tensor`.`cent_depth`, " + \
        "`Moment_Tensor`.`mw`, " + \
        "`Moment_Tensor`.`mo`, " + \
        "(CASE WHEN `Origin`.`automatic` <> 0 THEN 'automatic' " + \
        "ELSE 'revised' END), `Origin`.`id` FROM `Origin` " + \
        "INNER JOIN `Moment_Tensor` ON " + \
        "`Origin`.`id` = `Moment_Tensor`.`Origin_id` " + \
        "ORDER BY `Origin`.`timestamp` DESC LIMIT 20;"
        queries.append(_query)

        _originsT20 = self.read(queries)[0]

        return _originsT20


    def loadOrigins(self, start_datetime, end_datetime):
        """
        Fetches Origins (and MTs) from the scisola database
        and saves them in list.
        Returns True/False and origins' data/error.
        """

        queries = []

        _query = "SELECT `Origin`.`timestamp`, " + \
        "`Origin`.`datetime`, " + \
        "`Moment_Tensor`.`cent_latitude`, " + \
        "`Moment_Tensor`.`cent_longitude`, " + \
        "`Moment_Tensor`.`cent_depth`, " + \
        "`Moment_Tensor`.`mw`, " + \
        "`Moment_Tensor`.`mo`, " + \
        "(CASE WHEN `Origin`.`automatic` <> 0 THEN 'automatic' " + \
        "ELSE 'revised' END), `Origin`.`id` FROM `Origin` " + \
        "INNER JOIN `Moment_Tensor` ON " + \
        "`Origin`.`id` = `Moment_Tensor`.`Origin_id` " + \
        "WHERE `Origin`.`datetime` between '" + \
        str(start_datetime) + "' AND '"+ str(end_datetime) + \
        "' ORDER BY `Origin`.`timestamp` DESC;"
        queries.append(_query)

        _origins = self.read(queries)[0]

        return _origins


    def loadOrigin(self, origin_id, orig, station_list):
        """
        Fetches Origin (and MT) from the scisola database
        and return it in origin object.
        Returns True/False and origin object/error.
        """

        _query = "SELECT `Origin`.`id`, `Origin`.`timestamp`, " + \
        "`Origin`.`datetime`, " + \
        "`Origin`.`magnitude`, `Origin`.`latitude`, " + \
        "`Origin`.`longitude`, `Origin`.`depth`, " + \
        "`Origin`.`automatic`, `Origin`.`results_dir`, " + \
        "`Event`.`id`, " + \
        "`Moment_Tensor`.`cent_shift`, " + \
        "`Moment_Tensor`.`cent_time`, `Moment_Tensor`." + \
        "`cent_latitude`, `Moment_Tensor`.`cent_longitude`, " + \
        "`Moment_Tensor`.`cent_depth`, `Moment_Tensor`." + \
        "`correlation`, `Moment_Tensor`.`var_reduction`, " + \
        "`Moment_Tensor`.`mw`, `Moment_Tensor`.`mrr`, " + \
        "`Moment_Tensor`.`mtt`, `Moment_Tensor`.`mpp`, " + \
        "`Moment_Tensor`.`mrt`, `Moment_Tensor`.`mrp`, " + \
        "`Moment_Tensor`.`mtp`, `Moment_Tensor`.`vol`, " + \
        "`Moment_Tensor`.`dc`, `Moment_Tensor`.`clvd`, " + \
        "`Moment_Tensor`.`mo`, `Moment_Tensor`.`strike`, " + \
        "`Moment_Tensor`.`dip`, `Moment_Tensor`.`rake`, " + \
        "`Moment_Tensor`.`strike_2`, `Moment_Tensor`.`dip_2`, " + \
        "`Moment_Tensor`.`rake_2`, `Moment_Tensor`.`p_azm`, " + \
        "`Moment_Tensor`.`p_plunge`, `Moment_Tensor`.`t_azm`, " + \
        "`Moment_Tensor`.`t_plunge`, `Moment_Tensor`.`b_azm`, " + \
        "`Moment_Tensor`.`b_plunge`, `Moment_Tensor`.`minSV`, " + \
        "`Moment_Tensor`.`maxSV`, `Moment_Tensor`.`CN`, " + \
        "`Moment_Tensor`.`stVar`, `Moment_Tensor`.`fmVar`, " + \
        "`Moment_Tensor`.`frequency_1`, `Moment_Tensor`." + \
        "`frequency_2`, `Moment_Tensor`.`frequency_3`, " + \
        "`Moment_Tensor`.`frequency_4` FROM `Origin` INNER JOIN " + \
        "`Event` ON `Origin`.`id` = `Event`.`Origin_id` INNER JOIN " + \
        "`Moment_Tensor` ON " + \
        "`Origin`.`id` = `Moment_Tensor`.`Origin_id` " + \
        "WHERE `Origin`.`id` = " + str(origin_id) + ";"

        _row = self.read([_query])[0][0]

        # converts string to datetime object
        _orig_tp = date.datetime.strptime(_row[1], "%Y/%m/%d %H:%M:%S.%f")

        orig = origin.Origin()
        orig.id = int(_row[0])
        orig.timestamp = _orig_tp
        orig.datetime = _row[2]
        orig.magnitude = float(_row[3])
        orig.latitude = float(_row[4])
        orig.longitude = float(_row[5])
        orig.depth = float(_row[6])
        orig.automatic = bool(_row[7])
        orig.results_dir = _row[8]
        orig.event_id = _row[9]

        orig.mt = origin.MomentTensor()

        orig.mt.cent_shift = int(_row[10])
        orig.mt.cent_time = float(_row[11])
        orig.mt.cent_latitude = float(_row[12])
        orig.mt.cent_longitude = float(_row[13])
        orig.mt.cent_depth = float(_row[14])
        orig.mt.correlation = float(_row[15])
        orig.mt.var_reduction = float(_row[16])
        orig.mt.mw = float(_row[17])
        orig.mt.mrr = float(_row[18])
        orig.mt.mtt = float(_row[19])
        orig.mt.mpp = float(_row[20])
        orig.mt.mrt = float(_row[21])
        orig.mt.mrp = float(_row[22])
        orig.mt.mtp = float(_row[23])
        orig.mt.vol = float(_row[24])
        orig.mt.dc = float(_row[25])
        orig.mt.clvd = float(_row[26])
        orig.mt.mo = float(_row[27])
        orig.mt.strike = float(_row[28])
        orig.mt.dip = float(_row[29])
        orig.mt.rake = float(_row[30])
        orig.mt.strike2 = float(_row[31])
        orig.mt.dip2 = float(_row[32])
        orig.mt.rake2 = float(_row[33])
        orig.mt.p_azm = float(_row[34])
        orig.mt.p_plunge = float(_row[35])
        orig.mt.t_azm = float(_row[36])
        orig.mt.t_plunge = float(_row[37])
        orig.mt.b_azm = float(_row[38])
        orig.mt.b_plunge = float(_row[39])
        orig.mt.minSV = float(_row[40])
        orig.mt.maxSV = float(_row[41])
        orig.mt.CN = float(_row[42])
        orig.mt.stVar = float(_row[43])
        orig.mt.fmVar = float(_row[44])
        orig.mt.frequency_1 = float(_row[45])
        orig.mt.frequency_2 = float(_row[46])
        orig.mt.frequency_3 = float(_row[47])
        orig.mt.frequency_4 = float(_row[48])

        _query = "SELECT DISTINCT `streamNetworkCode`, " + \
        "`streamStationCode` FROM `Stream_Contribution` " + \
        "WHERE `Origin_id` = " + str(orig.id) + ";"

        _rows = self.read([_query])[0]

        # get stations
        for _row in _rows:
            _station = stream.Station()
            _station.network = _row[0]
            _station.code = _row[1]

            _query = "SELECT `streamCode`, `var_reduction`, " + \
            "`mseed_path` FROM `Stream_Contribution` " + \
            "WHERE `Origin_id` = " + str(orig.id) + \
            " AND streamStationCode = '" + str(_station.code) + \
            "' ORDER BY `streamCode`;"

            _stream_rows = self.read([_query])[0]

            # get station's streams
            for _stream_row in _stream_rows:
                _stream = stream.Stream()
                _stream.code = _stream_row[0]
                _stream.reduction = float(_stream_row[1])
                _stream.mseed_path = _stream_row[2]
                _station.stream_list.append(_stream)

            station_list.append(_station)

        return orig, station_list


    def saveOrigin(self, origin, station_list):
        """
        Saves setting to scisola database.
        Returns True/False and ()/error.
        """

        queries = []

        # converts datetime to string
        _orig_tp = origin.timestamp.strftime("%Y/%m/%d %H:%M:%S.%f")

        # insert to Origin
        _query = "INSERT INTO `Origin` (`timestamp`, " + \
        "`datetime`, `magnitude`, `latitude`, " + \
        "`longitude`, `depth`, `automatic`, `results_dir`) " + \
        "VALUES (" + \
        "'" + _orig_tp + "', " + \
        "'" + str(origin.datetime) + "', " + \
        "'" + str(origin.magnitude) + "', " + \
        "'" + str(origin.latitude) + "', " + \
        "'" + str(origin.longitude) + "', " + \
        "'" + str(origin.depth) + "', " + \
        str(origin.automatic) + ", " + \
        "'" + str(origin.results_dir) + "');"
        queries.append(_query)

        # insert to Moment_Tensor
        _query = "INSERT INTO `Moment_Tensor` (`cent_shift`, " + \
        "`cent_time`, `cent_latitude`, `cent_longitude`, " + \
        "`cent_depth`, `correlation`, `var_reduction`, `mw`, `mrr`, " + \
        "`mtt`, `mpp`, `mrt`, `mrp`, `mtp`, `vol`, `dc`, `clvd`, " + \
        "`mo`, `strike`, `dip`, `rake`, `strike_2`, `dip_2`, " + \
        "`rake_2`, `p_azm`, `p_plunge`, `t_azm`, `t_plunge`, " + \
        "`b_azm`, `b_plunge`, `minSV`, `maxSV`, `CN`, `stVar`, " + \
        "`fmVar`, `frequency_1`, `frequency_2`, `frequency_3`, " + \
        "`frequency_4`, `Origin_id`) " + \
        "VALUES (" + \
        "'" + str(origin.mt.cent_shift) + "', " + \
        "'" + str(origin.mt.cent_time) + "', " + \
        "'" + str(origin.mt.cent_latitude) + "', " + \
        "'" + str(origin.mt.cent_longitude) + "', " + \
        "'" + str(origin.mt.cent_depth) + "', " + \
        "'" + str(origin.mt.correlation) + "', " + \
        "'" + str(origin.mt.var_reduction) + "', " + \
        "'" + str(origin.mt.mw) + "', " + \
        "'" + str(origin.mt.mrr) + "', " + \
        "'" + str(origin.mt.mtt) + "', " + \
        "'" + str(origin.mt.mpp) + "', " + \
        "'" + str(origin.mt.mrt) + "', " + \
        "'" + str(origin.mt.mrp) + "', " + \
        "'" + str(origin.mt.mtp) + "', " + \
        "'" + str(origin.mt.vol) + "', " + \
        "'" + str(origin.mt.dc) + "', " + \
        "'" + str(origin.mt.clvd) + "', " + \
        "'" + str(origin.mt.mo) + "', " + \
        "'" + str(origin.mt.strike) + "', " + \
        "'" + str(origin.mt.dip) + "', " + \
        "'" + str(origin.mt.rake) + "', " + \
        "'" + str(origin.mt.strike2) + "', " + \
        "'" + str(origin.mt.dip2) + "', " + \
        "'" + str(origin.mt.rake2) + "', " + \
        "'" + str(origin.mt.p_azm) + "', " + \
        "'" + str(origin.mt.p_plunge) + "', " + \
        "'" + str(origin.mt.t_azm) + "', " + \
        "'" + str(origin.mt.t_plunge) + "', " + \
        "'" + str(origin.mt.b_azm) + "', " + \
        "'" + str(origin.mt.b_plunge) + "', " + \
        "'" + str(origin.mt.minSV) + "', " + \
        "'" + str(origin.mt.maxSV) + "', " + \
        "'" + str(origin.mt.CN) + "', " + \
        "'" + str(origin.mt.stVar) + "', " + \
        "'" + str(origin.mt.fmVar) + "', " + \
        "'" + str(origin.mt.frequency_1) + "', " + \
        "'" + str(origin.mt.frequency_2) + "', " + \
        "'" + str(origin.mt.frequency_3) + "', " + \
        "'" + str(origin.mt.frequency_4) + "', " + \
        "LAST_INSERT_ID());"
        queries.append(_query)

        # insert to Stream_Contribution
        for station in station_list:
            for stream in station.stream_list:
                if stream.enable:
                    _query = "INSERT INTO `Stream_Contribution` " + \
                    "(`streamNetworkCode`, `streamStationCode`, " + \
                    "`streamCode`, `var_reduction`, `mseed_path`, " + \
                    "`Origin_id`) VALUES (" + \
                    "'" + str(station.network) + "' ," + \
                    "'" + str(station.code) + "' ," + \
                    "'" + str(stream.code) + "' ," + \
                    "'" + str(stream.reduction) + "' ," + \
                    "'" + str(stream.mseed_path) + "' ," + \
                    "LAST_INSERT_ID());"
                    queries.append(_query)

        # insert to Event
        _query = "INSERT INTO `Event` " + \
        "(`id`, `Origin_id`) " + \
        "VALUES (" + \
        "'" + str(origin.event_id) + "' ," + \
        "LAST_INSERT_ID());"
        queries.append(_query)

        self.write(queries)


    def deleteOrigin(self, origin_id):
        """
        Fetches streams info that contributed to mt calculation
        from the scisola database, and saves them in list.
        Returns True/False and streams' data list/error.
        """

        try:

            queries = []

            _query = "DELETE FROM `Origin` " + \
            "WHERE `Origin`.`id` = " + str(origin_id) + ";"

            queries.append(_query)

            self.write(queries)
            return True, ()

        except:
            return False, sys.exc_info()


    def EventExist(self, event_id):

        _query = "SELECT COUNT(`id`) FROM `Event` WHERE `Event`.`id` " + \
        "LIKE BINARY '" + str(event_id) + "';"

     #   "LIKE '" + str(event_id) + "' COLLATE utf8_bin;"

        _count = self.read([_query])[0]

        return bool(int(_count[0][0]))


if __name__ == "__main__":

    db = Database()
    db.password = "11221122"


    db3 = Database(type = "postgres")

    db3.database = "seiscomp3"

    #print db.checkDB()

    print db.importFromSc3(db3, False)


