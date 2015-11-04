/*
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

Basic Template:
Design by Bryant Smith
http://www.bryantsmith.com
http://www.aszx.net
email: templates [-at-] bryantsmith [-dot-] com
*/


$(document).ready(function(){

  $("#map_link").click(function(){
    location.reload();
    });


  $("#list_link").click(function(){
    $("#main").html("<div id=\"main\" class=\"contentText\"><table id=\"mts\" style=\"width: 100%\" border=\"0\"><tbody><tr> \
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Datetime</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Latitude</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Longitude</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Depth (km)</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Mw</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Mo (Nm)</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">VR</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">No. Stations</span></td>\
                <td style=\"padding-right: 20px\"><span style=\"font-weight: bold;\">Quality</span></td>\
              </tr></tbody></table></div>");


	$.ajax({
      type: "GET",
      url: "moment_tensors.xml",
      dataType: "xml",
      async: false,
      success: function(xml) {
        $(xml).find('moment_tensor').each(function(){
          var originid = $(this).find('origin_id').text();
          var datetime = $(this).find('origin_datetime').text();
      	  var latitude = $(this).find('cent_latitude').text();
          var longitude = $(this).find('cent_longitude').text();
          var depth = $(this).find('cent_depth').text();
          var mw = $(this).find('mw').text();
          var mo = $(this).find('mo').text();
          var red = $(this).find('var_reduction').text();
          var no_stations = $(this).find('no_stations').text();
          var quality = $(this).find('quality').text();
          $('<tr></tr>').html('<td style="padding-right: 20px"><a href="mt.html?id=' + originid + '">'+datetime + '</a></td>' +
                              '<td style="padding-right: 20px">'+latitude + '</td>' +
                              '<td style="padding-right: 20px">'+longitude + '</td>' +
                              '<td style="padding-right: 20px">'+depth + '</td>' + 
                              '<td style="padding-right: 20px">'+mw + '</td>' +
                              '<td style="padding-right: 20px">'+mo + '</td>' +
                              '<td style="padding-right: 20px">'+red + '</td>' +
                              '<td style="padding-right: 20px">'+no_stations + '</td>' +
                              '<td style="padding-right: 20px">'+quality + '</td>').appendTo('#mts');
          });
        }
      });
    });


  $.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
  }
});

