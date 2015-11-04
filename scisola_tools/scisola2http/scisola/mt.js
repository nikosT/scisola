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
 
  var id=""

 $.ajax({
  type: "GET",
  url: "moment_tensors.xml",
  dataType: "xml",
  success: function(xml) {
   $(xml).find('moment_tensor').each(function(){
    var originid = $(this).find('origin_id').text();

    if ($.urlParam('id') == originid){

        // set text
        $("#origin_datetime2").text($(this).children('origin_datetime').text()+' (GMT)');
        $("#origin_datetime").text($(this).children('origin_datetime').text()+' (GMT)');
        $("#event_id").text($(this).children('event_id').text());
        $("#origin_id").text($(this).children('origin_id').text());
        $("#automatic").text($(this).children('automatic').text());
        $("#timestamp").text($(this).children('timestamp').text());
        $("#beachball").attr("src","beachball.png");
        $("#cent_latitude").text($(this).children('cent_latitude').text());
        $("#cent_longitude").text($(this).children('cent_longitude').text());
        $("#cent_depth").text($(this).children('cent_depth').text());
        $("#cent_time").text($(this).children('cent_time').text());
        $("#mw").text($(this).children('mw').text());
        $("#mo").text($(this).children('mo').text());
        $("#correlation").text($(this).children('correlation').text());
        $("#var_reduction").text($(this).children('var_reduction').text());
        $("#no_stations").text($(this).children('no_stations').text());
        $("#quality").text($(this).children('quality').text());
        $("#dc").text($(this).children('dc').text());
        $("#clvd").text($(this).children('clvd').text());
        $("#minSV").text($(this).children('minSV').text());
        $("#maxSV").text($(this).children('maxSV').text());
        $("#CN").text($(this).children('CN').text());
        $("#stVar").text($(this).children('stVar').text());
        $("#fmVar").text($(this).children('fmVar').text());
        $("#mrr").text($(this).children('mrr').text());
        $("#mtt").text($(this).children('mtt').text());
        $("#mpp").text($(this).children('mpp').text());
        $("#mrt").text($(this).children('mrt').text());
        $("#mrp").text($(this).children('mrp').text());
        $("#mtp").text($(this).children('mtp').text());
        $("#strike").text($(this).children('strike').text());
        $("#dip").text($(this).children('dip').text());
        $("#rake").text($(this).children('rake').text());
        $("#strike_2").text($(this).children('strike_2').text());
        $("#dip_2").text($(this).children('dip_2').text());
        $("#rake_2").text($(this).children('rake_2').text());
        $("#p_azm").text($(this).children('p_azm').text());
        $("#t_azm").text($(this).children('t_azm').text());
        $("#b_azm").text($(this).children('b_azm').text());
        $("#p_plunge").text($(this).children('p_plunge').text());
        $("#t_plunge").text($(this).children('t_plunge').text());
        $("#b_plunge").text($(this).children('b_plunge').text());
        $("#f1").text($(this).children('f1').text());
        $("#f2").text($(this).children('f2').text());
        $("#f3").text($(this).children('f3').text());
        $("#f4").text($(this).children('f4').text());


        id = $(this).children('origin_id').text();

        // load image beachball
        $('#beachball').html('<img id="beachball" src="plots/beachball_' + id + '.png" alt="double couple" height="200" width="200"/>');

        // load image map
        $('<tr></tr>').html('<div id="mapl"><a class="map" id="map" border-bottom:2px dashed #2A2A2A; href="plots/map_' + id + '.png" title="map"><img id="map2" src="plots/map_' + id + '.png" height="440" width="440"></a></div>').appendTo('#map');

        // set stations 
        var _N="-";
        var _E="-";
        var _Z="-";
        var _station="-";
        var _network="-";

        $(this).find('stream').each(function(){

	      if( $(this).children('station').text()!= _station && _station!="-" ){
            // put
            $('<tr></tr>').html('<td style="padding-right: 20px">' + _network + ' . ' + _station + '</td>' + 
                                '<td style="padding-right: 15px">' + _N + '</td>' + 
                                '<td style="padding-right: 15px">' + _E + '</td>' + 
                                '<td>' + _Z + '</td>').appendTo('#streams');
            // clear
            _N="-";
            _E="-";
            _Z="-";
          }

          // set
          if($(this).children('code').text().slice(-1)=="E") _E=$(this).children('stream_var_reduction').text();
          if($(this).children('code').text().slice(-1)=="N") _N=$(this).children('stream_var_reduction').text();
          if($(this).children('code').text().slice(-1)=="Z") _Z=$(this).children('stream_var_reduction').text();

          _station=$(this).children('station').text();
          _network=$(this).children('network').text();

        });

        if(!(_N=="-" && _E=="-" && _Z=="-")){
          // put
          $('<tr></tr>').html('<td style="padding-right: 20px">' + _network + ' . ' + _station + '</td>' + 
                              '<td style="padding-right: 20px">' + _N + '</td>' + 
                              '<td style="padding-right: 20px">' + _E + '</td>' + 
                              '<td>' + _Z + '</td>').appendTo('#streams');

        }

      return false;
      }
    
   });
  }
 });


  $("#results_plot").click(function(){
    location.reload();
    });

  $("#misfit_plot").click(function(){
    $("#main").html("<div id=\"main\" class=\"contentText\"><a class=\"misfit\" href=\"plots/misfit_" + id +".png\" title=\"misfit\"><img src=\"plots/misfit_" + id +".png\" height=\"400\" width=\"600\"></a></div>");
    });

  $("#inversions_plot").click(function(){
    $("#main").html("<div id=\"main\" class=\"contentText\"><a class=\"inversions\" href=\"plots/inversions_" + id +".png\" title=\"inversions\"><img src=\"plots/inversions_" + id +".png\" height=\"400\" width=\"600\"></a></div>");
    });

  $("#correlation_plot").click(function(){
    $("#main").html("<div id=\"main\" class=\"contentText\"><a class=\"correlation\" href=\"plots/correlation_" + id +".png\" title=\"correlation\"><img src=\"plots/correlation_" + id +".png\" height=\"400\" width=\"600\"></a></div>");
    });

  $("#streams_plot").click(function(){
    $("#main").html("<div id=\"main\" class=\"contentText\"><a class=\"streams\" href=\"plots/streams_" + id +".png\" title=\"streams\"><img src=\"plots/streams_" + id +".png\" height=\"400\" width=\"600\"></a></div>");
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
