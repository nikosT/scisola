#!/bin/bash

# add alter.sh to daily cron job

# set your own paths
# update scisola db from sc3 db
/usr/bin/python /home/sysop/scisola/scisola_tools/updatedb_daily/update_db.py

# set your own credentials
user='root'
password='pass'
# set the stations file
# which can be generated through mysql code
stationfile='/home/sysop/scisola/scisola_tools/updatedb_daily/stations.txt'

while read line; do

  IFS=',' read -r -a array <<< "$line"
  network=${array[0]}
  code=${array[1]}
  priority=${array[4]}

  #echo "Updating $network.$code priority --> $priority"
  # alter priority
  mysql -u $user -p$password scisola -e "UPDATE Station SET priority='$priority' WHERE network='$network' and code='$code'";


