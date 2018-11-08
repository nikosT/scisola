#!/bin/bash

cur_year=`date -u +%Y`
previous_month=`date --date='-1 month' +%m`

path='my_path' # path to results folder as set in scisola settings

find $path/${cur_year}${previous_month}* -name "inversion" -type d -exec rm -r {} +
find $path/${cur_year}${previous_month}* -name "stream" -type d -exec rm -r {} +
find $path/${cur_year}${previous_month}* -name "streams" -type d -exec rm -r {} +

