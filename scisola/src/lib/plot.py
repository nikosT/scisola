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
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import obspy.imaging.beachball as beach
import matplotlib.tri as tri
import matplotlib.transforms as transforms
import matplotlib.colors as colors
import matplotlib.colorbar as colorbar
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.basemap import Basemap
from obspy.geodetics import kilometer2degrees
import numpy as np
import os
from PIL import Image
from obspy import read as obspy_read
import isola
import datetime



##############################################################################
# DEFINE FUNCTIONS "isola"                                                   #
##############################################################################

def streamReduction(stream):
    """
    Returns stream reduction or none if exist or not respectively
    """

    if stream:
        return stream[0].reduction
    else:
        return None


def corr_file2data(corr_file):
    """
    Reading corr file for plotting
    """

    time_list = []
    depth_list = []
    dc_list = []
    corr_list = []
    beachball_list = []

    # read file
    _f = open(corr_file, "r")
    lines = _f.readlines()
    _f.close()

    # writes from 3th line to the end, to best inv1 file
    lines = lines[2:]

    for line in lines:
        row = line.split()
        time_list.append(float(row[1]))
        depth_list.append(float(row[0]))
        dc_list.append(float(row[9]))
        corr_list.append(float(row[2]))
        beachball_list.append([int(row[3][:-1]), int(row[4][:-1]),
                               int(row[5][:-1])])

    return time_list, depth_list, dc_list, corr_list, beachball_list


def mt_list2data(mt_list):
    """
    input of inversion_list
    and return depth, correlation, dc and beachballs lists
    """
    depth_x = []
    correlation_y = []
    dc = []
    beachballs = []

    for mt in mt_list:
        depth_x.append(mt.cent_depth)
        correlation_y.append(mt.correlation)
        dc.append(mt.dc)
        beachballs.append([mt.strike, mt.dip, mt.rake])

    return depth_x, correlation_y, dc, beachballs


def calculateReduction(observed, synthetic, tl):
    """
    Calculates variance reduction of stations' streams
    """

    _dt = round((tl/8192.0),2)

    _obs = np.array(observed)
    _syn = np.array(synthetic)

    _ds = _obs - _syn
    _dsn = (np.linalg.norm(_ds)**2)*_dt
    _d = (np.linalg.norm(_obs)**2)*_dt

    vr = 1 - (_dsn/float(_d))

    return round(vr,2)


def mt2txt(station_list, origin, settings, f1, f2, f3, f4, text_file):
    """
    Printing results to ascii text
    """

    _datetime = datetime.datetime.strptime(origin.datetime,
                                           "%Y/%m/%d %H:%M:%S.%f")
    _date = _datetime.strftime("%Y%m%d")
    _time = _datetime.strftime("%H:%M:%S.%f")

    _stations_text = "\nStations\tN\tE\tZ\n"

    for station in station_list:

        # get all N, E, Z possible streams
        _N = [x for x in station.stream_list if x.code[2] == 'N']
        _E = [x for x in station.stream_list if x.code[2] == 'E']
        _Z = [x for x in station.stream_list if x.code[2] == 'Z']

        _stations_text += str(station.network) + "." + str(station.code) +\
                          "\t\t" + \
                          str(streamReduction(_N)) + \
                          "\t" + \
                          str(streamReduction(_E)) + \
                          "\t" + \
                          str(streamReduction(_Z)) + \
                          "\n"

    text = "=======================================================\n" + \
           "===================== Automatic =======================\n" + \
           "============== Moment Tensor Solution =================\n" + \
           "=======================================================\n" + \
           "\nOrigin Time: " + _date + " " + str(_time) + \
           "\nLatitude: " + str(origin.latitude) + "\tLongitude: " + \
           str(origin.longitude) + \
           "\nDepth (km): " + str(origin.depth) + \
           "\nMw: " + str(origin.mt.mw) + "\n\n" + \
           "======================================================\n" + \
           "Centroid Solution\n" + \
           "Centroid Time: " + str(origin.mt.cent_time) + \
           " (sec) relative to origin time\n" + \
           "Centroid Latitude: " + str(origin.mt.cent_latitude) + \
           "\tLongitude: " + str(origin.mt.cent_longitude) + "\n" + \
           "Centroid Depth (km): " + str(origin.mt.cent_depth) + "\n\n" + \
           "======================================================\n" + \
           "No of Stations: " + str(len(station_list)) + "\t" + \
           str(_stations_text) + "\n" + \
           "Freq band (Hz)\n" + \
           str(f2) + "-" + str(f3) + " tapered "+\
           str(f1) + "-" + str(f2) + " and " + \
           str(f3) + "-" + str(f4) + "\n" + \
           "Variance Reduction (%): " + str(origin.mt.var_reduction) + "\n" +\
           "\n======================================================\n" + \
           "Moment Tensor (Nm): \n" + \
           "Mrr\tMtt\tMpp\n" + \
           str(origin.mt.mrr) + "\t" + str(origin.mt.mtt) + "\t" + \
           str(origin.mt.mpp) + "\n" + \
           "Mrt\tMrp\tMtp\n" + \
           str(origin.mt.mrt) + "\t" + str(origin.mt.mrp) + "\t" + \
           str(origin.mt.mtp) + "\n\n" + \
           "VOL (%): " + str(origin.mt.vol) + \
           "\nDC (%): " + str(origin.mt.dc) + \
           "\nCLVD (%):" + str(origin.mt.clvd) + \
           "\n\nBest Double Couple: Mo= " + str(origin.mt.mo) + " Nm\n" + \
           "NP1:\tStrike\tDip\tRake\n" + \
           "\t" + str(origin.mt.strike) + "\t" + str(origin.mt.dip) + "\t" + \
           str(origin.mt.rake) + "\n" + \
           "NP2:\tStrike\tDip\tRake\n" + \
           "\t" + str(origin.mt.strike2) + "\t" + str(origin.mt.dip2) + \
           "\t" + str(origin.mt.rake2) + "\n\n" + \
           "minSV: " + str(origin.mt.minSV) + "\n" + \
           "maxSV: " + str(origin.mt.maxSV) + "\n" + \
           "CN: " + str(origin.mt.CN) + "\n" + \
           "stVar: " + str(origin.mt.stVar) + "\n" + \
           "fmVar: " + str(origin.mt.fmVar) + "\n"

    # writes to files
    isola.write2file(text, text_file)


def streams2one(plot_folder, total_file):

    _file_list = []
    _filenames = []

    # get filenames
    _filenames = os.listdir(plot_folder)
    _filenames = sorted(_filenames, key=str.lower)

    # get absolute path of filenames
    for _filename in _filenames:
        _file = os.path.join(plot_folder, _filename)
        _file_list.append(_file)

    # alphabetical order
    _file_list.sort()

    plots = map(Image.open, _file_list)

    w = plots[0].size[0] * 3
    h = plots[0].size[1] * (len(plots)/3)

    result = Image.new("RGBA", (w,h))

    E = plots[::3]
    N = plots[1::3]
    Z = plots[2::3]

    y=0
    for plot_N, plot_E, plot_Z in zip(N, E, Z):

        result.paste(plot_N, (0, y))
        result.paste(plot_E, (plots[0].size[0], y))
        result.paste(plot_Z, (2*plots[0].size[0], y))

        y += plots[0].size[1]

    result.save(total_file)


#*****************************************************************************
#*                         Start of main functions                           *
#*****************************************************************************

def correlation(depth_x, correlation_y, dc, beachballs, plot_file):
    """
    Illustrates an example for plotting beachballs and data points on line
    with specific color based on values with a labelled colorbar.
    """

    # sets figure's dimensions
    _fig_x = 30
    _fig_y = 20

    # creates figure
    fig, ax = plt.subplots(figsize=(_fig_x,_fig_y))

    # plots (depth_x, correlation_y) points on line
    ax.plot(depth_x, correlation_y, '--', linewidth=2, color = 'k')

    # creates a grid on the (main) plot
    ax.grid()

    # sets labels
    plt.xlabel('Depth (km)')
    plt.ylabel('Correlation')

    # sets font size
    plt.rcParams.update({'font.size': 28})

    # sets fixed y-axis range
    plt.ylim((0,1))

    # sets margins on the plot
    plt.margins(0.1)

    # sets color canvas for coloring beachball
    cm = plt.cm.jet

    # creates a colorbar at the right of main plot:
    divider = make_axes_locatable(ax)
    # makes room for colorbar
    cax = divider.append_axes("right", size="2%", pad=1)
    # set values to colorbar
    norm = colors.Normalize(vmin=0, vmax=100)
    # creates colorbar on specific axes, norm, canvas color and orientation
    cb1 = colorbar.ColorbarBase(cax, norm=norm, cmap=cm,
                                orientation='vertical')
    # sets colorbar label
    cb1.set_label('DC%')

    # plotting beachballs on specific x-axis and y-axis
    # with a color based on the data_dc values (normalized to 0-1)
    for i in xrange(len(depth_x)):

        # sets color value
        color = cm(dc[i]/100.0)

        # draws beachball
        b = beach.Beach([beachballs[i][0], beachballs[i][1],
                         beachballs[i][2]], xy=(depth_x[i], correlation_y[i]),
                         width=80, linewidth=1, facecolor=color)

        # holds the aspect but fixes positioning:
        b.set_transform(transforms.IdentityTransform())
        # brings the all patches to the origin (0, 0).
        for p in b._paths:
        	p.vertices -= [depth_x[i], correlation_y[i]]
        # uses the offset property of the collection to position the patches
        b.set_offsets((depth_x[i], correlation_y[i]))
        b._transOffset = ax.transData

	  # adds beachball to plot
        ax.add_collection(b)

    # saves plot to file
    plt.savefig(plot_file, dpi=fig.dpi)


def misfit(tl, station_list, depth_folder, plot_file):
    """
    Plotting the misfits of observed and synthetic timeseries
    of each enabled stream for each station
    """

    plot_list = []

    # for each station
    for station in station_list:
        # read file data
        _fil_file = os.path.join(depth_folder, str(station.code) + 'fil.dat')
        _syn_file = os.path.join(depth_folder, str(station.code) + 'syn.dat')

        _time_N, _obs_N = np.loadtxt(_fil_file,unpack=True, usecols=[0,1])
        _time_N, _syn_N = np.loadtxt(_syn_file,unpack=True, usecols=[0,1])
        _time_E, _obs_E = np.loadtxt(_fil_file,unpack=True, usecols=[0,2])
        _time_E, _syn_E = np.loadtxt(_syn_file,unpack=True, usecols=[0,2])
        _time_Z, _obs_Z = np.loadtxt(_fil_file,unpack=True, usecols=[0,3])
        _time_Z, _syn_Z = np.loadtxt(_syn_file,unpack=True, usecols=[0,3])

        # get all N, E, Z possible streams
        _N = [x for x in station.stream_list if x.code[2] == 'N']
        _E = [x for x in station.stream_list if x.code[2] == 'E']
        _Z = [x for x in station.stream_list if x.code[2] == 'Z']

        if _N:
            _N[0].reduction = calculateReduction(_obs_N, _syn_N, tl)

        if _E:
            _E[0].reduction = calculateReduction(_obs_E, _syn_E, tl)

        if _Z:
            _Z[0].reduction = calculateReduction(_obs_Z, _syn_Z, tl)

        plot_list.append([[_time_N, _obs_N, _syn_N, streamReduction(_N)],
                         [_time_E, _obs_E, _syn_E, streamReduction(_E)],
                         [_time_Z, _obs_Z, _syn_Z, streamReduction(_Z)]])

    # station_list and plot_list have same size

    plt.rcParams.update({'font.size': 15})

    # row and column sharing
    formatter = FormatStrFormatter('%.1e')

    f, axes = plt.subplots(len(plot_list), 3, sharex='col',
                           sharey='row', figsize=(30,20))

    if len(plot_list) == 1:
        axes = [axes]

    f.suptitle('Fit Results', fontsize=30)

    for sta_i, ax_station in enumerate(axes):
        # set Station's name to the N component of the first station
        ax_station[0].set_ylabel(str(station_list[sta_i].code))

        for i in xrange(3):
            _time = plot_list[sta_i][i][0]
            _obs = plot_list[sta_i][i][1]
            _syn = plot_list[sta_i][i][2]
            _red = plot_list[sta_i][i][3]

            if not _red == None:
                _obs_color = 'k'
                _syn_color = 'r'
            else:
                _obs_color = 'grey'
                _syn_color = '#5f5f5f'

            ax_station[i].yaxis.set_major_formatter(formatter)
            ax_station[i].plot(_time, _obs, color=_obs_color,
                               linewidth=3, label="observed")
            ax_station[i].plot(_time, _syn, color=_syn_color,
                               linewidth=3, label="synthetic")
            ax_station[i].locator_params(nbins=4)
            ax_station[i].grid()
            ax_station[i].autoscale(tight=True)

            ax_station[i].annotate(str(_red), xy=(0.99, 0.95),
                                   xycoords='axes fraction',
                                   fontsize=15, color='b',
                                   horizontalalignment='right',
                                   verticalalignment='top')

    # set N,E,Z titles to first station
    axes[0][0].set_title('N')
    axes[0][1].set_title('E')
    axes[0][2].set_title('Z')

    # set time title to last station
    axes[len(axes)-1][0].set_xlabel('Time (sec)')
    axes[len(axes)-1][1].set_xlabel('Time (sec)')
    axes[len(axes)-1][2].set_xlabel('Time (sec)')

    # set legend to right of the Z component of the first station
    # axes[0][2].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    pos = list(axes[0][2].get_position().bounds)

    plt.figtext(pos[0]+pos[2]-0.01, pos[1]+pos[3]+0.01,
              'black: observed\nred: synthetic\ngrey: unused\nblue: ' + \
              'variance reduction')

    # save plot to file
    plt.savefig(plot_file, dpi=f.dpi)


def contour(time_list, depth_list, dc_list, corr_list, beachball_list,
            plot_file):
    """
    Plotting contour
    """

    # sets figure's dimensions
    _fig_x = 60
    _fig_y = 40

    # creates figure
    fig, ax = plt.subplots(figsize=(_fig_x,_fig_y))

    # creates a grid on the (main) plot
    ax.grid()

    # sets labels
    plt.xlabel('Time (sec)')
    plt.ylabel('Centroid Depth (km)')

    # sets font size
    plt.rcParams.update({'font.size': 28})

    # sets margins on the plot
    plt.margins(0.05)

    tri.Triangulation(time_list, depth_list)
    levels=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 1.0]
    cont = plt.tricontour(time_list, depth_list, corr_list,
                          len(levels), levels=levels, linewidths=0.5,
                          colors='k')

    plt.tricontourf(time_list, depth_list, corr_list, len(levels),
                    levels=levels, cmap=plt.cm.cool)

    plt.clabel(cont)

    cm=plt.cm.copper_r #gia dc

    # plotting beachballs on specific x-axis and y-axis
    # with a color based on the data_dc values (normalized to 0-1)
    _max_corr = max(corr_list)
    _index = corr_list.index(_max_corr)

    for i in xrange(len(beachball_list)):
        if i == _index:
            # sets best beachball's color value to red
            _color = 'red'
            _width = 45 # bigger beachball for best match
        else:
            # sets beachball's color value
            _color = cm(dc_list[i]/100.0)
            _width = 35

	   # draws beachball
        b = beach.Beach([beachball_list[i][0], beachball_list[i][1],
                       beachball_list[i][2]], xy=(time_list[i],depth_list[i]),
                       width=_width, linewidth=1, facecolor=_color)

        # holds the aspect but fixes positioning:
        b.set_transform(transforms.IdentityTransform())

        # brings the all patches to the origin (0, 0).
        for p in b._paths:
            p.vertices -= [time_list[i], depth_list[i]]

        # uses the offset property of the collection to position the patches
        b.set_offsets((time_list[i], depth_list[i]))
        b._transOffset = ax.transData

	   # adds beachball to plot
        ax.add_collection(b)

    # creates a colorbar at the right of main plot
    divider = make_axes_locatable(ax)
    # makes room for colorbar
    cax = divider.append_axes("right", size="1%", pad=0.5)
    # set values to colorbar
    norm = colors.Normalize(vmin=0.0, vmax=1.0)
    # creates colorbar on specific axes, norm, canvas color and orientation
    colorbar.ColorbarBase(cax, cmap=plt.cm.cool, norm=norm,
                                orientation='vertical', label='Correlation')

    cax = divider.append_axes("right", size="1%", pad=1.5)
    # set values to colorbar
    norm = colors.Normalize(vmin=0, vmax=100)
    # creates colorbar on specific axes, norm, canvas color and orientation
    colorbar.ColorbarBase(cax, cmap=plt.cm.copper_r , norm=norm,
                                orientation='vertical', label='DC%')

    # save plot to file
    plt.savefig(plot_file, dpi=fig.dpi)


def beachBall(strike,dip,rake,mrr,mtt,mpp,mrt,mrp,mtp,plot_file):
    """
    Plotting the focal mechanism
    """

    # sets figure's dimensions
    _fig_x = 10
    _fig_y = 10
    fig = plt.figure(figsize=(_fig_x,_fig_y))

    # mt
    beach.Beachball([mrr,mtt,mpp,mrt,mrp,mtp], facecolor='r', fig=fig)
    # dc
    beach.Beachball([strike,dip,rake], nofill=True, fig=fig)

    fig.savefig(plot_file)


def streams(station_list, plot_folder, total_file):
    """
    Plotting every possible stream waveform after retrieval
    and before any correction
    """

    for _station in station_list:

        for _stream in _station.stream_list:

            _filename = str(_station.network) + "_" +  \
                           str(_station.code) + "_" + str(_stream.code) + \
                           ".png"
            _output_file = os.path.join(plot_folder, _filename)

            _fig_x = 21
            _fig_y = 7
            _fig = plt.figure(figsize=(_fig_x,_fig_y))
            _st = obspy_read(_stream.mseed_path)
            _st.plot(outfile=_output_file, fig=_fig)

        if not len(_station.stream_list) == 3:
            # plot blank figures in case of missing component
            # get all N, E, Z possible streams
            _N = [x for x in _station.stream_list if x.code[2] == 'N']
            _E = [x for x in _station.stream_list if x.code[2] == 'E']
            _Z = [x for x in _station.stream_list if x.code[2] == 'Z']

            _fig_x = 21
            _fig_y = 7
            _fig = plt.figure(figsize=(_fig_x,_fig_y))

            # first two digits of stream code
            _min_code = str(_station.stream_list[0].code[0:2])

            if not _N:
                _filename = str(_station.network) + "_" +  \
                            str(_station.code) + "_" + _min_code + "N" + \
                            ".png"
                _output_file = os.path.join(plot_folder, _filename)
                plt.savefig(_output_file)

            if not _E:
                _filename = str(_station.network) + "_" +  \
                            str(_station.code) + "_" + _min_code + "E" + \
                            ".png"
                _output_file = os.path.join(plot_folder, _filename)
                plt.savefig(_output_file)

            if not _Z:
                _filename = str(_station.network) + "_" +  \
                            str(_station.code) + "_" + _min_code + "Z" + \
                            ".png"
                _output_file = os.path.join(plot_folder, _filename)
                plt.savefig(_output_file)

    streams2one(plot_folder, total_file)


def maps(station_list, origin, strike, dip, rake, plot_file):
    """
    Plotting a map with epicenter and possible stations according to distance
    and a map with with the beachball
    """

    # sets figure's dimensions
    _fig_x = 10
    _fig_y = 10
    fig = plt.figure(figsize=(_fig_x,_fig_y))

    # calculating map space
    _max = max(_station.distance_by_origin for _station in station_list)
    _max = int(round(_max * 1000 *2))
    _size = _max + int(round(_max/7.0))
    _diff = kilometer2degrees(round(_size/(2*2.0*1000)))

    parallels = [round(origin.latitude,2), round((origin.latitude-_diff),2),
                 round((origin.latitude+_diff),2)]
    meridians = [round(origin.longitude,2), round((origin.longitude-_diff),2),
                 round((origin.longitude+_diff),2)]

    m = Basemap(projection='laea', lat_0 = origin.latitude,
                lon_0 = origin.longitude, lat_ts=origin.latitude,
                resolution = 'i', area_thresh = 0.1, width = _size,
                height = _size)
    m.drawparallels(parallels,labels=[1,0,0,0], color='grey', fontsize=10)
    m.drawmeridians(meridians,labels=[0,0,0,1], color='grey', fontsize=10)
    m.drawrivers(color='aqua')
    m.drawcoastlines(color='0.2')
    m.drawcountries(color='0.4')
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='coral',lake_color='aqua')
    x,y = m(origin.longitude, origin.latitude)

    # epicenter
    m.scatter(x, y, 1, color="#FFFF00", marker="*", zorder=3,
              linewidths=2, edgecolor="k")

    # beachball
    ax = plt.gca()
    b = beach.Beach([strike, dip, rake], xy=(x,y), width=35000, linewidth=1,
                    facecolor='r')
    b.set_zorder(10)
    ax.add_collection(b)

    # stations
    for station in station_list:
        x,y = m(station.longitude, station.latitude)
        m.scatter(x, y, 150, color="#33CC00", marker="^", zorder=3,
                  linewidths=1, edgecolor="k")
        plt.text(x+1800, y+3000, station.code, family="monospace",
                 fontsize=12)

    fig.savefig(plot_file)


def results2text(station_list, origin, settings, results_folder,
                 dsretc_path, f1, f2, f3, f4, text_file):
    """
    Printing results to ascii text with an ascii beachball
    """

    # writes text to temp file
    mt2txt(station_list, origin, settings, f1, f2, f3, f4, text_file)

    isola.createAsciiBeachball(origin.mt.strike,
                         origin.mt.dip,
                         origin.mt.rake,
                         dsretc_path,
                         results_folder)

    _temp_file = os.path.join(results_folder, "dsretc.lst")

    # append to file
    # read file
    _f = open(_temp_file, "r")
    lines = _f.readlines()
    _f.close()

    # read file
    _f = open(text_file, "a")

    for line in lines:
        _f.write(line)

    _str = "\n=======================================================\n" + \
           "=======================================================\n"

    _f.write(_str)
    _f.close()

