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
# DEFINE CLASS "Origin"                                                      #
##############################################################################

class Origin:

    def __init__(self):
        self.id = None
        self.timestamp = None
        self.datetime = None
        self.description = None
        self.magnitude = None
        self.latitude = None
        self.longitude = None
        self.depth = None
        self.automatic = True # automatic or revised (True/False)
        self.results_dir = None # folder with scisola origin's data
        self.event_id = None
        self.mt = None # Moment_Tensor object


##############################################################################
# DEFINE CLASS "Moment_Tensor"                                               #
##############################################################################

class MomentTensor:

    def __init__(self):
        self.cent_shift = None
        self.cent_time = None
        self.cent_latitude = None
        self.cent_longitude = None
        self.cent_depth = None
        self.correlation = None
        self.var_reduction = None
        self.mw = None
        self.mrr = None
        self.mtt = None
        self.mpp = None
        self.mrt = None
        self.mrp = None
        self.mtp = None
        self.vol = None
        self.dc = None
        self.clvd = None
        self.mo = None
        self.strike = None
        self.dip = None
        self.rake = None
        self.strike2 = None
        self.dip2 = None
        self.rake2 = None
        self.p_azm = None
        self.p_plunge = None
        self.t_azm = None
        self.t_plunge = None
        self.b_azm = None
        self.b_plunge = None
        self.minSV = None
        self.maxSV = None
        self.CN = None
        self.stVar = None
        self.fmVar = None
        self.frequency_1 = None
        self.frequency_2 = None
        self.frequency_3 = None
        self.frequency_4 = None

