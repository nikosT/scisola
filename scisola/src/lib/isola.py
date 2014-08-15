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

import datetime
import codecs
import os
import shutil
import numpy as np
import subprocess
import decimal
import operator


##############################################################################
# DEFINE FUNCTIONS "isola"                                                   #
##############################################################################

def inv_file2list(inv_file):
    """
    read inv file to a 2x2 array (list)
    and return the list
    row = inv_file line
    column = splitted row
    """

    inv_txt = []

    # read file
    _f = open(inv_file, "r")
    lines = _f.readlines()
    _f.close()

    for line in lines:
        inv_txt.append(line.split())

    return inv_txt


def write2file(text, output_path):
    """
    Writes text to file
    """

    # writes text's content to output_path
    _f = codecs.open(output_path, "w", "utf-8")
    _f.write(text)
    _f.close()


def station2RawFile(station, output_path):
    """
    Creates raw file of data; contains 4 columns: time, N, E, Z data
    if there's less than 3 components data, it fills with ajacent data
    (dummy data) in order ISOLA to work
    """

    _text = ""

    # stream order in stream_list of each station is N, E, Z
    # cause of selectISOLAstreams() function

    # first two columns: time and N component
    _time = station.stream_list[0].data.times()
    _N = station.stream_list[0].data.data

    # if OK
    if len(station.stream_list) == 3:
        _E = station.stream_list[1].data.data
        _Z = station.stream_list[2].data.data

    # if 1 component only, fill other 2 with dummy data
    elif len(station.stream_list) == 1:
        _E = station.stream_list[0].data.data
        _Z = station.stream_list[0].data.data

    # if 2 components only, fill the other 1 with dummy data
    elif len(station.stream_list) == 2:
        if station.stream_list[0].code[2] == 'N':
            _E = station.stream_list[1].data.data
            _Z = station.stream_list[1].data.data
        else:
            _E = station.stream_list[0].data.data
            _Z = station.stream_list[1].data.data

    # after dummy filling when necessary, writes raw file
    for i in xrange(len(_time)):
        _time_str = str('%.6E' % decimal.Decimal(_time[i]))
        _N_str = str('%.6E' % decimal.Decimal(_N[i]))
        _E_str = str('%.6E' % decimal.Decimal(_E[i]))
        _Z_str = str('%.6E' % decimal.Decimal(_Z[i]))

        _text += _time_str + " " + _N_str + " " + _E_str + " " + _Z_str + "\n"

    # writes to files
    write2file(_text, output_path)


def readCorrFile(depth, corr_file):
    """
    Reading corr file from each depth
    """

    text = []

    # read file
    _f = open(corr_file, "r")
    lines = _f.readlines()
    _f.close()

    for line in lines[2:]:
        row = line.split()
        new_row = [str(depth)] + row[1:]
        text.append(new_row)

    return text


def calculateKagan(kagan_path, strike, dip, rake, strike2, dip2, rake2):
    """
    Calculating and returning Kagan angle
    """

    args = " " + str(strike) + " " + str(dip) + " " + str(rake) + \
           " " + str(strike2) + " " + str(dip2) + " " + str(rake2)


    # calculate inversion
    _proc = subprocess.Popen(kagan_path + args,
                             shell=True, universal_newlines=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _kagan_angle = float(_proc.communicate()[0])

    return round(_kagan_angle, 2)


#*****************************************************************************
#*                         Start of main functions                           *
#*****************************************************************************

def createRawFiles(station_list, output_folder):
    """
    Creates Raw files, one for each station,
    containing exactly 3 component data
    """

    for station in station_list:

        _file = str(station.code) + "raw.dat"
        _output_path = os.path.join(output_folder, _file)
        station2RawFile(station, _output_path)


def createStationFile(station_list, output_path):
    """
    Creates the station file, responsible for the calculation
    of Inversion
    """

    _text = " Station co-ordinates\n" + \
            " x(N>0,km),y(E>0,km),z(km),azim.,dist.,stat.\n"

    for station in station_list:

        # converting polar to cartesian
        _x = station.distance_by_origin * \
             np.cos(np.radians(station.azimuth_by_origin))
        _y = station.distance_by_origin * \
             np.sin(np.radians(station.azimuth_by_origin))

        _x = round(_x, 4)
        _y = round(_y, 4)
        _azm = round(station.azimuth_by_origin, 4)
        _dist = round(station.distance_by_origin, 4)

        # one line for each station
        _line = "   " + str(_x) + "   " + str(_y) + "    0.0000    " + \
                str(_azm) + "    " + str(_dist) + " " + \
                str(station.code) + " U\n"

        _text += _line

    # writes to file
    write2file(_text, output_path)


def loadCrustalFile(crustal_file, output_path):
    """
    Copying crustal_file to output path
    and returning the number of crustal layers
    """

    # copy crustal file to output path
    shutil.copyfile(crustal_file, output_path)

    _f = open(output_path)
    _lines=_f.readlines()
    _f.close()

    return int(_lines[2])


def createGrdatFile(nc, nfreq, tl, nr, xl, output_path):
    """
    Creates the grdat file, responsible for the calculation
    of Green's functions
    """

    # round up to int value
    nfreq = int(np.ceil(nfreq))

    # round up value
    xl = np.ceil(xl)

    # grdat file's content
    _text = "&input\n" + \
    "nc=" + str(nc) + "\n" + \
    "nfreq=" + str(nfreq) + "\n" + \
    "tl=" + str(tl) + "\n" + \
    "aw=0.1\n" + \
    "nr=" + str(nr) + "\n" + \
    "ns=1\n" + \
    "xl=" + str(xl) + "\n" + \
    "ikmax=100000\n" + \
    "uconv=0.1E-03\n" + \
    "fref=1.\n" + \
    "/end\n\n\n" + \
    "Edit only this:\n" + \
    " nc...number of layers from CRUSTAL.DAT\n" + \
    " nfreq... number of frequencies to be computed; then\n" + \
    "          maximum calculated frequency is nfreq * df,\n" + \
    "          where the frequency step is df=1./tl\n" + \
    " tl ... the time window length (in sec), it must be\n" + \
    "        tl=8192 * dt, where dt is the time step\n" + \
    "        of the XXXRAW.DAT input waveform files\n" + \
    " nr ... number of all stations in ALLSTAT.DAT\n" + \
    " xl ... this number should be larger than 20 * epimax,\n" + \
    "        where epimax is max.epic. distance (in meters !) \n"

    # writes to file
    write2file(_text, output_path)


def createInpinvFile(tl, start, step, end,
                     f1, f2, f3, f4, output_path):
    """
    Creates the grdat file, responsible for the calculation
    of Inversion
    """

    _nsources = 1 # 1 source per inversion subfolder

    # round to 2 decimals
    _dt = round((tl/8192.0),2)

    _text = "    mode of inversion: 1=full MT, 2=deviatoric MT " + \
    "(recommended), 3= DC MT, 4=known fixed DC MT\n" + \
    "2\n" + \
    "    time step of XXXRAW.DAT files (in sec)\n" + \
    str(_dt) + "\n" + \
    "    number of trial source positions (isourmax), max. 51\n" + \
    str(_nsources) + "\n" + \
    "    trial time shifts (max. 100 shifts): from (>-2500), " + \
    "step, to (<2500)\n" + \
    "    example: -10,5,50 means -10dt to 50dt, step = 5dt, " + \
    "i.e. 12 shifts\n" + \
    str(start) + " " + str(step) + " " + str(end) + "\n" + \
    "    number of subevents to be searched (isubmax), max. 20\n" + \
    "1\n" + \
    "    filter (f1,f2,f3,f4); flat band-pass between f2, f3\n" + \
    "    cosine tapered between f1, f2 and between f3, f4\n" + \
    str(f1) + " " + str(f2) + " " + str(f3) + " " + str(f4) + "\n" + \
    "    guess of data variance (important only for " + \
    "absolute value of the parameter variance)\n" + \
    "1.200000e-010\n"

    # writes to file
    write2file(_text, output_path)


def createAllstatFile(automatic, station_list, f1, f2, f3, f4,
                      output_path):
    """
    Creates the allstat file, including the selected stations
    for the calculation of Inversion
    """

    if automatic:
        _text = ""
        _freq = " " + str(f1) + " " + str(f2) + " " + str(f3) + " " + str(f4)

        for station in station_list:
            # stream order in stream_list of each station is N, E, Z
            # cause of selectISOLAstreams() function

            # get all N, E, Z possible streams
            _N = [x for x in station.stream_list if x.code[2] == 'N']
            _E = [x for x in station.stream_list if x.code[2] == 'E']
            _Z = [x for x in station.stream_list if x.code[2] == 'Z']

            # if any of the list exist then it's value is going to be 1,
            # unless 0
            _line = str(station.code) + " 1 " + \
                    str(int(bool(_N))) + " " + \
                    str(int(bool(_E))) + " " + \
                    str(int(bool(_Z))) + _freq + "\n"

            _text += _line

        # writes to file
        write2file(_text, output_path)

    else:
        _rows = []
        _text = ""

        _f = open(output_path, "r")
        _lines = _f.readlines()
        _f.close()

        for _line in _lines:
            _row = _line.split()

            _station = [x for x in station_list if x.code == _row[0]]
            if _station:
               _station = _station[0]
               # get all N, E, Z possible streams
               _N = [x for x in _station.stream_list if x.code[2] == 'N']
               _E = [x for x in _station.stream_list if x.code[2] == 'E']
               _Z = [x for x in _station.stream_list if x.code[2] == 'Z']
               _row[2] = int(bool(_N))
               _row[3] = int(bool(_E))
               _row[4] = int(bool(_Z))

            else:
               _row[2] = 0
               _row[3] = 0
               _row[4] = 0

            _row[5] = f1
            _row[6] = f2
            _row[7] = f3
            _row[8] = f4

            _rows.append(_row)

        for _row in _rows:
            _line = _row[0] + " 1 " + \
                str(_row[2]) + " " + \
                str(_row[3]) + " " + \
                str(_row[4]) + " " + \
                str(_row[5]) + " " + \
                str(_row[6]) + " " + \
                str(_row[7]) + " " + \
                str(_row[8]) + "\n"
            _text += _line

        # writes to file
        write2file(_text, output_path)


def calculateDepths(depth, step, nsources):
    """
    Calculates the possible centroid depths based on earthquake's depth,
    settings's step and number of sources
    depth must be int
    """

    # if even number then becomes odd by adding 1

    depth_list = []

    if nsources == 1:
        nsources = 2

    if not nsources%2 == 0:
        nsources -= 1

    # calculates from earthquake's depth to max
    _depth = depth
    for _i in range(0, (nsources/2) + 1):
        depth_list.append(int(_depth))
        _depth += step

    # calculates from earthquake's depth to min
    _depth = depth
    for _i in range(1, (nsources/2) + 1):
        _depth -= step
        if _depth <=0:
            break
        depth_list.append(int(_depth))

    # sorts depths in ascending order
    depth_list.sort()

    return depth_list


def createSource(date, magnitude, depth, output_path):
    """
    Creating the source file for the inversion procedure
    """

    _date = datetime.datetime.strptime(date, "%Y/%m/%d")
    _formed_date = _date.strftime("%Y%m%d")

    _text = " Source parameters\n x(N>0,km),y(E>0,km),z(km)," +\
                "magnitude,date\n    0.0000    0.0000    " + \
                str(int(depth)) + ".0000" + "    " + \
                str(magnitude) + "  \'" + str(_formed_date) + \
                "\'\n"

    # creates src file
    write2file(_text, output_path)


def calculateGreens(gr_xyz_path, elemse_path, depth_folder):
    """
    Calculating Green's functions and elementary seismograms
    for one depth
    """

    _log_path = os.path.join(depth_folder, "green_log")
    log = open(_log_path,"w")

    _command = gr_xyz_path + ";" + elemse_path + ";"

    # calculate inversion
    _proc = subprocess.Popen(_command, cwd=depth_folder,
                             shell=True, universal_newlines=True,
                             stdout=log, stderr=log)

    _proc.wait()


def calculateInversion(isola12c_path, norm12c_path, depth_folder):
    """
    Calculating inversion for one depth
    """

    _log_path = os.path.join(depth_folder, "invert_log")
    log = open(_log_path,"w")

    _command = isola12c_path + ";" + norm12c_path

    # calculate inversion
    _proc = subprocess.Popen(_command, cwd=depth_folder,
                             shell=True, universal_newlines=True,
                             stdout=log, stderr=log)

    _proc.wait()


def load_MT(depth, tl, origin, inv1_file, inv3_file, mt, f1, f2, f3, f4):
    """
    Create moment tensor objects for a certain depth
    """

    _inv1_txt = []
    _inv3_txt = []


    _inv1_txt = inv_file2list(inv1_file)
    _inv3_txt = inv_file2list(inv3_file)

    mt.cent_shift = int(_inv1_txt[3][1])
    mt.cent_time = float(round(tl/8192.0, 2) * mt.cent_shift)
    mt.cent_longitude = float(origin.longitude)
    mt.cent_latitude = float(origin.latitude)
    mt.cent_depth = int(depth)
    mt.correlation = float(_inv1_txt[3][2])
    mt.var_reduction = float(_inv1_txt[30][1])
    mt.mw = float(_inv1_txt[18][2])
    mt.mrr = float(_inv3_txt[0][2])
    mt.mtt = float(_inv3_txt[0][3])
    mt.mpp = float(_inv3_txt[0][4])
    mt.mrt = float(_inv3_txt[0][5])
    mt.mrp = float(_inv3_txt[0][6])
    mt.mtp = float(_inv3_txt[0][7])
    mt.vol = float(_inv1_txt[19][3])
    mt.dc = float(_inv1_txt[20][3])
    mt.clvd = float(_inv1_txt[21][3])
    mt.mo = float(_inv1_txt[17][2])
    mt.strike = int(_inv1_txt[22][1])
    mt.dip = int(_inv1_txt[22][2])
    mt.rake = int(_inv1_txt[22][3])
    mt.strike2 = int(_inv1_txt[23][1])
    mt.dip2 = int(_inv1_txt[23][2])
    mt.rake2 = int(_inv1_txt[23][3])
    mt.p_azm = float(_inv1_txt[24][4])
    mt.p_plunge = float(_inv1_txt[24][5])
    mt.t_azm = float(_inv1_txt[25][4])
    mt.t_plunge = float(_inv1_txt[25][5])
    mt.b_azm = float(_inv1_txt[26][4])
    mt.b_plunge = float(_inv1_txt[26][5])
    mt.minSV = float(_inv1_txt[9][0])
    mt.maxSV = float(_inv1_txt[9][1])
    mt.CN = float(_inv1_txt[9][2])
    mt.stVar = None
    mt.fmVar = None
    mt.frequency_1 = f1
    mt.frequency_2 = f2
    mt.frequency_3 = f3
    mt.frequency_4 = f4

    return mt


def getBestMT(mt_list):
    """
    Finds the best depth iversion result based on correlation value
    """

    # get the best inversion
    return max(mt_list, key=operator.attrgetter('correlation'))


def calcuateStFmVar(kagan_path, corr_list, bball_list, best_mt, settings):
    """
    Calculationg fmvar value and st value
    """
    _kagan_list = []
    _thresh_bballs = []

    _all_bballs = len(corr_list)
    _max_corr = max(corr_list)
    _thresh_corr = 0.9 * _max_corr

    for i, _corr in enumerate(corr_list):
        if _corr >= _thresh_corr:
            _thresh_bballs.append(bball_list[i])

    stvar = len(_thresh_bballs)/float(_all_bballs)

    for _bball in _thresh_bballs:
        _kagan_angle = calculateKagan(kagan_path,
                                      best_mt.strike,
                                      best_mt.dip,
                                      best_mt.rake,
                                      _bball[0],
                                      _bball[1],
                                      _bball[2])
        _kagan_list.append(_kagan_angle)

    fmvar = np.mean(_kagan_list)
    return [stvar, fmvar]


def createCorrFile(depth_list, invert_folder, output_path):
    """
    Creating final-best corr file
    """

    _text = " 2D correlation for event\n" + \
            "\tdepth\ttime\tcorrelation\tstrike\tdip\trake\tstrike2\t" + \
            "dip2\trake2\tDC%\tvolume\tmisfit\tmoment\n"
    lines= []

    for depth in depth_list:
        corr_file = os.path.join(invert_folder, str(depth), "corr01.dat")
        lines += readCorrFile(depth, corr_file)

    for line in lines:
        _text += "\t%s\n" % ("\t".join(line))

    write2file(_text, output_path)


def createInv1File(mt_list, best_mt, output_path):
    """
    Creating the final-best inv1 file
    """

    _text = " All trial positions and shifts\n" + \
           " (isour = source position -depth (km)-,ishift*dt=time shift)" +\
           "\n \tisour\tishift\tcorrelation\tmoment\t\tDC%\tstrike\tdip\t" +\
           "rake\tstrike2\tdip2\trake2\n"

    for mt in mt_list:

        _text += "\t" + str(mt.cent_depth) + "\t" + str(mt.cent_shift) + \
                 "\t" + str(mt.correlation) + "\t" + str(mt.mo) + \
                 "\t" + str(mt.dc) + "\t" + str(mt.strike) + \
                 "\t" + str(mt.dip) + "\t" + str(mt.rake) + \
                 "\t" + str(mt.strike2) + "\t" + str(mt.dip2) + \
                 "\t" + str(mt.rake2) + "\n"

    _text += "\n Selected source position\n depth (km), ishift:\t" + \
             str(best_mt.cent_depth) + ", " + str(best_mt.cent_shift) + \
             "\n\nSINGULAR values, incl. vardat (min., max, max/min)\n" + \
             "\t" + str(best_mt.minSV) + "\t" + str(best_mt.maxSV) + "\t" \
             + str(best_mt.CN) + "\n" + \
             "\nmoment (Nm):   " + str(best_mt.mo) + \
             "\n  moment magnitude:   " + str(best_mt.mw) + \
             "\n            VOL % :   " + str(best_mt.vol) + \
             "\n             DC % :   " + str(best_mt.dc) + \
             "\n      abs(CLVD) % :  " + str(best_mt.clvd) + \
             "\nstrike,dip,rake:\t" + str(best_mt.strike) + "\t\t" + \
             str(best_mt.dip) + "\t\t" + str(best_mt.rake) + \
             "\nstrike,dip,rake:\t" + str(best_mt.strike2) + "\t\t" + \
             str(best_mt.dip2) + "\t\t" + str(best_mt.rake2) + "\n" + \
             "P-axis azimuth and plunge:\t\t" + str(best_mt.p_azm) + "\t\t" +\
             str(best_mt.p_plunge) + "\n" + \
             "T-axis azimuth and plunge:\t\t" + str(best_mt.t_azm) + "\t\t" +\
             str(best_mt.t_plunge) + "\n" + \
             "B-axis azimuth and plunge:\t\t" + str(best_mt.b_azm) + "\t\t" +\
             str(best_mt.b_plunge) + "\n\n" + \
             "After subtraction of subevent\n" + \
             "variance reduction (from the used stations only):\n" + \
             "varred=   " + str(best_mt.var_reduction) + "\n" + \
             "=======================================\n"

    write2file(_text, output_path)


def createInv2File(mt, output_path):
    """
    Creating the final-best inv2 file
    """

    _text = "\t" + str(mt.cent_depth) + "\t" + str(mt.cent_time) + \
            "\t" + str(mt.mo) + "\t" + str(mt.strike) + \
            "\t" + str(mt.dip) + "\t" + str(mt.rake) + \
            "\t" + str(mt.strike2) + "\t" + str(mt.dip2) + \
            "\t" + str(mt.rake2) + "\t" + str(mt.p_azm) + \
            "\t" + str(mt.p_plunge) + "\t" + str(mt.t_azm) + \
            "\t" + str(mt.t_plunge) + "\t" + str(mt.b_azm) + \
            "\t" + str(mt.b_plunge) + "\t" + str(mt.dc) + \
            "\t" + str(mt.var_reduction) + "\n"

    write2file(_text, output_path)


def createInv3File(mt, output_path):
    """
    Creating the final-best inv3 file
    """

    _text = "\t" + str(mt.cent_depth) + "\t" + str(mt.mrr) + \
            "\t" + str(mt.mtt) + "\t" + str(mt.mpp) + \
            "\t" + str(mt.mrt) + "\t" + str(mt.mrp) + \
            "\t" + str(mt.mtp) + "\n"

    write2file(_text, output_path)


def createAsciiBeachball(strike, dip, rake, dsretc_path, results_folder):
    """
    Creating a beachball in ascii image (text file)
    """

    # temp file inside output_folder
    _f_path = os.path.join(results_folder, "dsr.dat")

    # write strike, dip and rake to temp file
    _text = str(dip) + " " + str(strike) + " " + str(rake) + "\n"
    write2file(_text, _f_path)


    _f = open(_f_path, "a")

    # run dsretc for creating ascii beachball to output_path
    # it will be created a file dsretc.lst in depth_folder
    _proc = subprocess.Popen(dsretc_path, cwd=results_folder,
                             shell=True, universal_newlines=True,
                             stdout=_f, stderr=_f)

    _proc.wait()


#
#if __name__ == "__main__":
#
#    date = "2014/02/17"
#    magnitude = 5.3
#    depth = 8.0
#    output = '/home/nikos/Desktop/source'
#
#    invert_folder = '/home/nikos/Desktop/output/20140217_090557456700/20140320_120131808811/isola/inversion'
#
#    depth_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
#
#   # createAsciiBeachball(1, 2, 3, dsretc_path, results_folder):
#
#
#    kagan = '/home/nikos/Programs/ISOLA/kagan_angle/kagan'
#
#    m = origin.Moment_Tensor()
#    m.strike=1
#    m.dip=2
#    m.rake=3
#
#    m2 = origin.Moment_Tensor()
#    m2.strike=14
#    m2.dip=22
#    m2.rake=3
#
# #   print calculateKagan(kagan, m, m2)
#
#   # print calculateSources(8,2,17)
#
# #   createInvFile('/home/nikos/Desktop/output/20140217_090557456700/20140325_024624416496/inversion/20/inv2.dat', 4,
#  #            '/home/nikos/Desktop/data')
#    #print readInvFile(4,'/home/nikos/Desktop/output/20140217_090557456700/20140325_024624416496/inversion/20/inv2.dat')
##    depth_x = []
##    correlation_y = []
##    dc = []
##    beachballs = []
##
##
##    for res in results:
##        depth_x.append(int(res[0]))
##        correlation_y.append(float(res[2]))
##        dc.append(float(res[4]))
##        beachballs.append([int(res[5]), int(res[6]), int(res[7])])

