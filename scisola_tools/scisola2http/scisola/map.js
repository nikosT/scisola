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


google.load("jquery", "1.3.2");

//load on initialize
google.setOnLoadCallback(initialize);

//initialize map
var map;

//initialize markers
var markers = new Array();

//initialize markers' num
var i=0;

//initialize balloon
var infoWindow;

//catalog of earthquakes
var catalog_html="";



//functions
//initialize map and map's options
function initialize() {

//lat, lon for center google maps
var main_longitude="";
var main_latitude="";
var test="";


  //initialize variables
  markers=new Array();
  i=0;
  catalog_html="";

  //activate it
  document.getElementById("catalog").innerHTML = catalog_html;

  //read user input from search box
  var mw_min=document.getElementById('mw_min').value;
  var mw_max=document.getElementById('mw_max').value;
  var cd_min=document.getElementById('cd_min').value;
  var cd_max=document.getElementById('cd_max').value;
  var lat_min=document.getElementById('lat_min').value;
  var lat_max=document.getElementById('lat_max').value;
  var lon_min=document.getElementById('lon_min').value;
  var lon_max=document.getElementById('lon_max').value;

  //remove whitespaces and convert it to number; if empty string then NaN is returned
  mw_min=parseFloat($.trim(mw_min));
  mw_max=parseFloat($.trim(mw_max));
  cd_min=parseFloat($.trim(cd_min));
  cd_max=parseFloat($.trim(cd_max));
  lat_min=parseFloat($.trim(lat_min));
  lat_max=parseFloat($.trim(lat_max));
  lon_min=parseFloat($.trim(lon_min));
  lon_max=parseFloat($.trim(lon_max));

  $.ajax({
      type: "GET",
      url: "moment_tensors.xml",
      dataType: "xml",
      async: false, // <- this turns it into synchronous
      success: function(xml) {
        $(xml).find('moment_tensor').each(function(){
      	  main_latitude = $(this).find('cent_latitude').text();
          main_longitude = $(this).find('cent_longitude').text();
		  return false;
          });
        }
      });

  //set map's options
  var mapOptions = {
    center: new google.maps.LatLng(main_latitude.toString(), main_longitude.toString()),
    zoom: 6,
    mapTypeId: google.maps.MapTypeId.HYBRID
  };

  //create map
  map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

  //create balloon object
  infoWindow = new google.maps.InfoWindow();


      //#############################################################################
      //creating Markers area
      //#############################################################################

      //retrieve markers from xml file
      jQuery.get("moment_tensors.xml", {}, function(data) {
        jQuery(data).find("moment_tensor").each(function() {
          var marker = jQuery(this);
          var datetime = marker.find('origin_datetime').text();
          var cent_longitude = marker.find('cent_longitude').text(); 
          var cent_latitude = marker.find('cent_latitude').text(); 
          var cent_depth = marker.find('cent_depth').text();
          var cent_time = marker.find('cent_time').text();
          var mw = marker.find('mw').text();
          var mo = marker.find('mo').text();
          var red = marker.find('var_reduction').text();
          var strike1 = marker.find('strike').text(); 
          var dip1 = marker.find('dip').text(); 
          var rake1 = marker.find('rake').text(); 
          var strike2 = marker.find('strike_2').text(); 
          var dip2 = marker.find('dip_2').text(); 
          var rake2 = marker.find('rake_2').text(); 
          var dc = marker.find('dc').text(); 
          var clvd = marker.find('clvd').text();
          var type = marker.find('automatic').text();
          var id = marker.find('origin_id').text();
          var no_stations = marker.find('no_stations').text();
          var quality = marker.find('quality').text();

          //checks if current earthquake responds to users input search range about strike, dip and rake 
          if(
             ( isNaN(mw_min) || mw_min <= mw ) &&
             ( isNaN(mw_max) || mw_max >= mw ) &&
             ( isNaN(cd_min) || cd_min <= cent_depth ) &&
             ( isNaN(cd_max) || cd_max >= cent_depth ) &&
             ( isNaN(lat_min) || lat_min <= cent_latitude ) &&
             ( isNaN(lat_max) || lat_max >= cent_latitude ) &&
             ( isNaN(lon_min) || lon_min <= cent_longitude ) &&
             ( isNaN(lon_max) || lon_max >= cent_longitude )    
            ){

            //create marker
            markers[i]=createMarker(datetime, cent_longitude, cent_latitude, cent_depth, cent_time, mw, mo, red, strike1, dip1, rake1, strike2, dip2, rake2, dc, clvd, type, id, no_stations, quality);

            //append catalog right bar
            catalog_html+="&nbsp;<a href=\"javascript:void(0)\" style=\"text-decoration:none\" onclick=\"showBalloon(" + i + ");\">" + markers[i].getTitle() + "</a><br>"


            //activate it
            document.getElementById("catalog").innerHTML = catalog_html;

            //increase counter for next marker
            i++;

          } //end of if

        });
      });
                      
    }//endof initialize function

    //show balloon info when clicked on right catalog bar
    function showBalloon(i){

      google.maps.event.trigger(markers[i], 'click');

    }//endof showBalloon function


    //creating marker for map
    function createMarker(datetime, cent_longitude, cent_latitude, cent_depth, cent_time, mw, mo, red, strike1, dip1, rake1, strike2, dip2, rake2, dc, clvd, type, id, no_stations, quality) {

      //mouseover marker display
      var string = datetime.toString().split(".")[0] + ', Mw: ' + mw.toString()
  
      //set image to marker
      var icon = {
        url: "plots/beachball32_" + id.toString() + ".png", // url
        //scaledSize: new google.maps.Size(32, 32), // scaled size
        origin: new google.maps.Point(0,0), // origin
        anchor: new google.maps.Point(20,20) // anchor to center of image
      };

      //create marker
      var marker = new google.maps.Marker({
        position: new google.maps.LatLng(cent_latitude, cent_longitude),
        map: map,
        title: string,
        icon: icon
      });

      //set text to marker's balloon
      marker.balloon=createBalloon(datetime, cent_longitude, cent_latitude, cent_depth, cent_time, mw, mo, red, strike1, dip1, rake1, strike2, dip2, rake2, dc, clvd, type, id, no_stations, quality)

      //set balloon to marker and handler
      google.maps.event.addListener(marker, 'click', function () {
        infoWindow.setContent(this.balloon);
        infoWindow.open(map, this);
      });

    return marker

    }//endof createMarker function


    //creating balloon text for marker
    function createBalloon(datetime, cent_longitude, cent_latitude, cent_depth, cent_time, mw, mo, red, strike1, dip1, rake1, strike2, dip2, rake2, dc, clvd, type, id, no_stations, quality){

      var string = "<p style=\"font-size:12px\" line-height:2px;>" +
                   "<b>Origin Time:</b> " + datetime.toString() + " (GMT)<br>" +
                   "<b>Cent. Lat., Cent. Long.:</b> " + cent_latitude.toString() + " <sup>o</sup>N, " + cent_longitude.toString() + " <sup>o</sup>E" + "<br>" +
                   "<b>Cent. Depth:</b> " + cent_depth.toString() + " km&nbsp;&nbsp;&nbsp;&nbsp;" +
                   "<b>Cent. Time:</b> " + cent_time.toString() + " sec" + "<br>" +
                   "<b>Mo:</b> " + mo.toString() + " Nm&nbsp;&nbsp;&nbsp;&nbsp;" +
                   "<b>Mw:</b> " + mw.toString() + "<br>" +
                   "<b>VR:</b> " + red.toString() + " &nbsp;&nbsp;&nbsp;&nbsp;" +
				   "<b>No. Stations:</b> " + no_stations.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;" + "<b>Quality:</b> " + quality.toString() + "<br>" +
                   "<b>Strike1&nbsp;&nbsp;Dip1&nbsp;&nbsp;Rake1</b>" + "&nbsp;&nbsp;&nbsp;&nbsp;" + "<b>Strike2&nbsp;&nbsp;Dip2&nbsp;&nbsp;Rake2</b>" + "<br>" +
                   "&nbsp" + strike1.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dip1.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + rake1.toString() + "&nbsp&nbsp;&nbsp;&nbsp;&nbsp;" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + 
                   strike2.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dip2.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + rake2.toString() + "<br>" +
                   "<b>DC (%):</b> " + dc.toString() + "&nbsp;&nbsp;&nbsp;&nbsp;" +
                   "<b>CLVD (%):</b> " + clvd.toString() + "<br>" +
                   "<b>Type:</b> " + type.toString() + "<br>" +
                   "<img src=\"plots/beachball_" + id.toString() + ".png\" width=\"64\" height=\"64\">" + 
                   '<a href="mt.html?id=' + id.toString() + '">click here to view</a></p>'


      return string

    } //end of balloon function





