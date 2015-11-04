#!/bin/bash
#Copyright (C) 2015  Triantafyllis Nikolaos
#
#This file is part of Scisola tools.
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

http_port=$1

init_dir=$PWD

_script="$(readlink -f ${BASH_SOURCE[0]})" # full path to this script
dirname=`dirname "$_script"` # folder of this script

html_folder="$dirname/scisola" # full path to scisola folder (html folder)

cd $html_folder
python -m SimpleHTTPServer $http_port> /dev/null 2>&1
cd $init_dir




