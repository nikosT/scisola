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


############################### VARS ####################################################

_script="$(readlink -f ${BASH_SOURCE[0]})" # full path to this script
dirname=`dirname "$_script"` # folder of this script

http_script="$dirname/httpserver.sh" # full path to httpserver.sh
settings_path="$dirname/settings"
id_path="$dirname/id"

. /lib/lsb/init-functions # load linux functions

############################### FUNCTIONS ###############################################

# SETUP
#makes settings
#makes id =0 file
#and 50mts

function setup {

  echo -e "Setting up scisola2html script...\n"
  echo "Press ENTER to use [default] value"

  printf 'scisola MySQL host [localhost] :  '
  read -r host
  : ${host:="localhost"}

  printf 'scisola MySQL port [3306] :  '
  read -r port
  : ${port:="3306"}

  printf 'scisola MySQL user [root] :  '
  read -r user
  : ${user:="root"}

  printf 'scisola MySQL database [scisola] :  '
  read -r database
  : ${database:="scisola"}

  printf 'scisola MySQL password [root] :  '
  read -s password
  : ${password:="root"}
  echo

  printf "update every (minutes) [5] :  "
  read -r interval
  : ${interval:="5"}

  printf "use python SimpleHTTPServer [n] :  "
  read -r http
  : ${http:="n"}

  if [ "$http" == "y" ]; then
    printf "SimpleHTTPServer port[8000] :  "
    read -r http_port
  : ${http_port:="8000"}
  fi

  {
    echo "# MySQL Settings"
    echo "host=\"$host\""
    echo "port=\"$port\""
    echo "user=\"$user\""
    echo "database=\"$database\""
    echo "password=\"$password\""
    echo -e "\n# More Settings"
    echo "path=\"$PWD\""
    echo "interval=\"$interval\" # update every interval minutes using cron service"
    echo "http=\"$http\" # use python SimpleHTTPServer"
    echo "http_port=\"$http_port\" # SimpleHTTPServer port"
  } > $settings_path || { echo "cannot create settings file"; exit -1; }

  # secure settings (e.g. MySQL password)
  chmod 600 $settings_path &
  chown root:root $settings_path || { echo "cannot change settings file permissions"; exit -1; }

  # creates id file 
  echo "0" > $id_path

  # creates 50 latest MTs
  ./mapmts.sh

} # end-of function


# START
#add to cron
#start http

function start {

  # check if settings file exist
  if [ ! -f "$settings_path" ]; then
    echo "No settings file found. Run setup first."
    return
  else
    source $settings_path # import settings
  fi

  # add to cron
  crontab -u $SUDO_USER -l | { cat; echo "*/$interval * * * * $_script >/dev/null 2>&1"; } | crontab -u $SUDO_USER -

  # if SimpleHTTPServer is chosen and http_port has value
  if [ "$http" == "y" ] && ! [ -z "$http_port" ]; then
    status_of_proc "$http_script" "httpserver.sh" > /dev/null || {
    start-stop-daemon --start --quiet --exec $http_script -- $http_port
    } &
  fi

  # creates 50 latest MTs if the id file suggests update
  ./mapmts.sh
}


# STOP
#remove from cron
#stop http

function stop {

  # check if settings file exist
  if [ ! -f "$settings_path" ]; then
    echo "No settings file found. Run setup first."
    return
  else
    source $settings_path # import settings
  fi

  # remove from cron
  crontab -u $SUDO_USER -l | grep -v "$_script" | crontab -u $SUDO_USER -

  # if SimpleHTTPServer is chosen and http_port has value
  if [ "$http" == "y" ] && ! [ -z "$http_port" ]; then

    start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --name "httpserver.sh"
    # Wait for children to finish too if this is a daemon that forks
    # and if the daemon is only ever run from this initscript.
    # If the above conditions are not satisfied then add some other code
    # that waits for the process to drop all resources that could be
    # needed by services started subsequently.  A last resort is to
    # sleep for some time.
    start-stop-daemon --stop --quiet --oknodo --retry=0/30/KILL/5 --exec "$http_script"
    pkill -f "python -m SimpleHTTPServer $http_port"
  fi

}


############################### MAIN ####################################################

if [[ $EUID -ne 0 ]]; then
   echo "Script must be run as root" 
   exit 1
fi


case "$1" in
  setup)
    setup
  ;;

  start)
    start
  ;;

  stop)
    stop
  ;;

  status)
    status_of_proc "$http_script" "httpserver.sh"
  ;;

  restart)
    stop
	stap
  ;;

  *)
    echo -e " |-------------------------------------------|"
    echo  " |              `basename ${BASH_SOURCE[0]}`              |"
    echo -e " |-------------------------------------------|"
    echo -e " |--- real-time MT solutions monitoring   ---|\n |--- through website (plugin to scisola) ---|"
    echo -e " |-------------------------------------------|"

    echo -e "\n`basename ${BASH_SOURCE[0]}` {start | stop | restart | status}"
    echo -e "\nOptions"
    echo "
    setup   : creates the settings file, id file and 
              updates the 50 latest MT solutions

    start   : continuously updates the 50 latest MT 
              solutions (adds to cron), starts the 
              HTTP Server (if enabled)

    stop    : stops updates of the 50 latest MT 
              solutions (removes from cron), stops 
              the HTTP Server (if enabled)

    restart : stops and starts

    status  : informs if HTTP Server is started/stopped"

    echo -e "\ne.g.: ${BASH_SOURCE[0]} start # starting service\n"
  ;;
esac


