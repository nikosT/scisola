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

settings_path="$dirname/settings"
id_path="$dirname/id"
plots_path="$dirname/scisola/plots" 
xml_path="$dirname/scisola/moment_tensors.xml"
id="0"

source $settings_path # import settings

############################### FUNCTIONS ###############################################

function check {

  q_check="SELECT Origin.id FROM Origin ORDER BY Origin.datetime DESC LIMIT 1;"
  _id=`mysql --silent -h $host -P $port -u $user --password=$password -D $database<<<$q_check`

  id=$_id

  cat $id_path > /dev/null 2>&1 || echo "0" > $id_path

  id_file=`cat $id_path`

  # id <= id_file
  if [ "$id" -le "$id_file" ]; then
    exit
  fi
}


############################### MAIN ####################################################

# check if it's necessary to run
check

{
# init files and folders
rm -rf $plots_path &&
rm -rf $xml_path &&
rm -rf $id_path

# mysql db credentials
q_mt="SELECT Event.id, Origin.id, Origin.datetime, Origin.timestamp, (CASE WHEN Origin.automatic <> 0 THEN 'automatic' ELSE 'revised' END), Origin.results_dir, Moment_Tensor.cent_time, Moment_Tensor.cent_latitude, Moment_Tensor.cent_longitude, Moment_Tensor.cent_depth, Moment_Tensor.mw, Moment_Tensor.mo,
Moment_Tensor.correlation, Moment_Tensor.var_reduction, Moment_Tensor.vol, Moment_Tensor.dc, Moment_Tensor.clvd, Moment_Tensor.minSV, Moment_Tensor.maxSV, Moment_Tensor.CN, Moment_Tensor.stVar, Moment_Tensor.fmVar, Moment_Tensor.mrr, Moment_Tensor.mtt, Moment_Tensor.mpp, Moment_Tensor.mrt, Moment_Tensor.mrp, Moment_Tensor.mtp, Moment_Tensor.strike, Moment_Tensor.dip, Moment_Tensor.rake, Moment_Tensor.strike_2, Moment_Tensor.dip_2, Moment_Tensor.rake_2, Moment_Tensor.p_azm, Moment_Tensor.p_plunge, Moment_Tensor.t_azm, Moment_Tensor.t_plunge, Moment_Tensor.b_azm, Moment_Tensor.b_plunge, Moment_Tensor.frequency_1, Moment_Tensor.frequency_2, Moment_Tensor.frequency_3, Moment_Tensor.frequency_4 FROM Event INNER JOIN Origin ON Event.Origin_id = Origin.id INNER JOIN Moment_Tensor ON Origin.id = Moment_Tensor.Origin_id ORDER BY Origin.datetime DESC LIMIT 50;"

# remakes plots folder from scratch
rm -rf $plots_path && mkdir $plots_path
touch "$plots_path/index.html"

echo "<moment_tensors>" > $xml_path

while read line
do

  array=($line)

  echo "  <moment_tensor>
    <event_id>${array[0]}</event_id>
    <origin_id>${array[1]}</origin_id>
    <origin_datetime>${array[2]} `date -d ${array[3]} '+%H:%M:%S.%2N'`</origin_datetime>
    <timestamp>${array[4]} `date -d ${array[5]} '+%H:%M:%S.%2N'`</timestamp>
    <automatic>${array[6]}</automatic>
    <results_dir>${array[7]}</results_dir>
    <cent_time>`printf "%0.2f" ${array[8]}`</cent_time>
    <cent_latitude>`printf "%0.4f" ${array[9]}`</cent_latitude>
    <cent_longitude>`printf "%0.4f" ${array[10]}`</cent_longitude>
    <cent_depth>${array[11]}</cent_depth>
    <mw>`printf "%0.1f" ${array[12]}`</mw>
    <mo>`printf "%0.2e\n" ${array[13]}`</mo>
    <correlation>`printf "%0.2f" ${array[14]}`</correlation> 
    <var_reduction>`printf "%0.2f" ${array[15]}`</var_reduction>
    <dc>`printf "%1.0f" ${array[17]}`</dc>
    <clvd>`printf "%1.0f" ${array[18]}`</clvd>
    <minSV>`printf "%0.2e\n" ${array[19]}`</minSV>
    <maxSV>`printf "%0.2e\n" ${array[20]}`</maxSV>
    <CN>`printf "%1.0f" ${array[21]}`</CN>
    <stVar>`printf "%0.2f" ${array[22]}`</stVar>
    <fmVar>`printf "%1.0f" ${array[23]}`</fmVar>
    <mrr>`printf "%0.2e\n" ${array[24]}`</mrr>
    <mtt>`printf "%0.2e\n" ${array[25]}`</mtt>
    <mpp>`printf "%0.2e\n" ${array[26]}`</mpp>
    <mrt>`printf "%0.2e\n" ${array[27]}`</mrt>
    <mrp>`printf "%0.2e\n" ${array[28]}`</mrp>
    <mtp>`printf "%0.2e\n" ${array[29]}`</mtp>
    <strike>${array[30]}</strike>
    <dip>${array[31]}</dip>
    <rake>${array[32]}</rake>
    <strike_2>${array[33]}</strike_2>
    <dip_2>${array[34]}</dip_2>
    <rake_2>${array[35]}</rake_2>
    <p_azm>${array[36]}</p_azm>
    <p_plunge>${array[37]}</p_plunge>
    <t_azm>${array[38]}</t_azm>
    <t_plunge>${array[39]}</t_plunge>
    <b_azm>${array[40]}</b_azm>
    <b_plunge>${array[41]}</b_plunge>
    <f1>${array[42]}</f1>
    <f2>${array[43]}</f2>
    <f3>${array[44]}</f3>
    <f4>${array[45]}</f4>
    <streams>" >> $xml_path

  q_streams="SELECT Stream_Contribution.streamNetworkCode, Stream_Contribution.streamStationCode, Stream_Contribution.streamCode, Stream_Contribution.var_reduction from Stream_Contribution INNER JOIN Origin ON Stream_Contribution.Origin_id = Origin.id WHERE Origin.id = ${array[1]} ORDER BY Stream_Contribution.streamStationCode;"

  station_num=0
  last_station=""
  quality=""
  CLVD=0
  VR=0

  while read line2
  do

    array2=($line2)

    echo "      <stream>
        <network>${array2[0]}</network>
        <station>${array2[1]}</station>
        <code>${array2[2]}</code>
        <stream_var_reduction>`printf "%0.2f" ${array2[3]}`</stream_var_reduction>
      </stream>" >> $xml_path


    if [ "${array2[1]}" != "$last_station" ] ||  [ "$last_station" = "" ];
    then
      station_num=$(( $station_num+1 ))
      last_station=${array2[1]}
    fi


  done < <(mysql --silent -h $host -P $port -u $user --password=$password -D $database<<<$q_streams)


  # estimating quality
  VR=`echo "100 * ${array[15]}" | bc -l`
  VR=`printf "%1.0f" $VR`

  # if VR>=60% and station>4
  if [ $VR -ge 60 ] && [ $station_num -gt 4 ];
  then
    quality="A"

  # if 40%<=VR<60% and station>=4
  elif [ $VR -lt 60 ] && [ $VR -ge 40 ] && [ $station_num -ge 4 ];
  then
    quality="B"

  # if VR>=70% and station=2
  elif [ $VR -ge 70 ] && [ $station_num -eq 2 ];
  then
    quality="B"

  # if VR>=70% and station=3
  elif [ $VR -ge 70 ] && [ $station_num -eq 3 ];
  then
    quality="B"

  # if 15%<=VR<40% and station>4
  elif [ $VR -ge 15 ] && [ $VR -lt 40 ] && [ $station_num -gt 4 ];
  then
    quality="C"

  # if 20%<=VR<40% and station=4
  elif [ $VR -ge 20 ] && [ $VR -lt 40 ] && [ $station_num -eq 4 ];
  then
    quality="C"

  # if 20%<=VR<70% and station=3
  elif [ $VR -ge 20 ] && [ $VR -lt 70 ] && [ $station_num -eq 3 ];
  then
    quality="C"

  # if 30%<=VR<70% and station=2
  elif [ $VR -ge 30 ] && [ $VR -lt 70 ] && [ $station_num -eq 2 ];
  then
    quality="C"

  # otherwise
  else
    quality="D"
  fi


  CLVD=`printf "%1.0f" ${array[18]}`

  # if CLVD<=20%
  if [ $CLVD -le 20 ];
  then
    quality+="1"

  # if 20%<CLVD<=50%
  elif [ $CLVD -gt 20 ] && [ $CLVD -le 50 ];
  then
    quality+="2"

  # if 50%<CLVD<=80%
  elif [ $CLVD -gt 50 ] && [ $CLVD -le 80 ];
  then
    quality+="3"

  # if CLVD>80%
  elif [ $CLVD -gt 80 ];
  then
    quality+="4"
  fi

  echo "    </streams>" >> $xml_path
  echo "  <no_stations>$station_num</no_stations>" >> $xml_path
  echo "  <quality>$quality</quality>" >> $xml_path
  echo "</moment_tensor>" >> $xml_path
  

  # creates beachballs for maps
  code="import matplotlib as mpl;mpl.use('Agg');import matplotlib.pyplot as plt;from obspy.imaging.beachball import Beachball;import Image;Beachball([${array[30]}, ${array[31]}, ${array[32]}], linewidth=1, facecolor='r', bgcolor='w', width=100, outfile='$plots_path/beachball32_${array[1]}.png');Image.open('$plots_path/beachball32_${array[1]}.png').resize((40,40), Image.ANTIALIAS).save('$plots_path/beachball32_${array[1]}.png')"

  python -c "$code"

  #$mopad_path plot ${array[30]},${array[31]},${array[32]} -f "$plots_/beachball32_${array[1]}.png" -s 1 &&
  #convert -resize 32x32 "$plots/beachball32_${array[1]}.png" "$plots/beachball32_${array[1]}.png"

  # link solution plots to html review
  ln -s "${array[7]}/plot/beachball.png" "$plots_path/beachball_${array[1]}.png"
  ln -s "${array[7]}/plot/map.png" "$plots_path/map_${array[1]}.png"
  ln -s "${array[7]}/plot/misfit.png" "$plots_path/misfit_${array[1]}.png"
  ln -s "${array[7]}/plot/inversions.png" "$plots_path/inversions_${array[1]}.png"
  ln -s "${array[7]}/plot/correlation.png" "$plots_path/correlation_${array[1]}.png"
  ln -s "${array[7]}/plot/allstreams.png" "$plots_path/streams_${array[1]}.png"

done < <(mysql --silent -h $host -P $port -u $user --password=$password -D $database<<<$q_mt)

echo "</moment_tensors>" >> $xml_path

if ! [[ $EUID -ne 0 ]]; then
  chown -R $SUDO_USER:$SUDO_USER $plots_path
  chown $SUDO_USER:$SUDO_USER $xml_path
fi


# save id to file after update
} && echo $id > $id_path


