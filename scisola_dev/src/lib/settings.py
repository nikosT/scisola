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


##############################################################################
# DEFINE CLASS "Settings"                                                    #
##############################################################################

class Settings:
    """
    The configuration parameters in order to work scisola
    """

    def __init__(self):
        # unique id for configuration
        self.id = None
        # time when settings applied
        self.timestamp = None
        # location threshold
        self.center_latitude = None
        self.center_longitude = None
        # distance range in km
        self.distance_range = None
        # magnitude threshold
        self.magnitude_threshold = None
        # minimum number of sectors in order to run process
        self.min_sectors = None
        # max number of selected stations per sector
        self.stations_per_sector = None
        # max number of possible centroid sources
        self.sources = None
        # step per next centroid source in km
        self.source_step = None
        # stations above clipping threshold are removed from process
        self.clipping_threshold = None
        # time grid search
        self.time_grid_start = None
        self.time_grid_step = None
        self.time_grid_end = None
        # every interval to watch for new events in sec
        self.watch_interval = None
        # delay in sec before process start
        # (it might need for seedlink ring buffers to save data)
        self.process_delay = None
        # fatal timeout in sec
        # (in case of a problematic loop in process)
        self.process_timeout = None
        # crustal model file
        self.crustal_model_path = None
        # results folder (all processes save result files here)
        self.output_dir = None
        # path to ISOLA program
        # (gr_xyz, elemse, isola12c, norm12c, dsretc, kagan)
        self.isola_path = None
        # path to SeisComP3 program
        self.sc3_path = None
        self.sc3_scevtls = None
        self.sc3_scxmldump = None
        # path to seedlink
        self.seedlink_path = None
        self.seedlink_host = None
        self.seedlink_port = None
        # list with all possible distance selections
        self.distance_selection = []
        # list with all possible inversion time
        self.inversion_time = []
        # list with all possible inversion frequency
        self.inversion_frequency = []

