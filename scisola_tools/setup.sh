#!/bin/bash

sudo apt-get install python-pip
sudo apt-get install python-dev
sudo apt-get install libpng-dev
sudo apt-get install libfreetype6-dev
sudo apt-get install gfortran gfortran-multilib libopenblas-dev liblapack-dev
sudo pip install numpy
sudo pip install matplotlib
sudo pip install obspy
sudo apt-get install python-mysqldb
sudo apt-get install python-psycopg2
sudo apt-get install python-qt4

wget http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz
tar -zxvf basemap-1.0.7.tar.gz
cd basemap-1.0.7

wget http://download.osgeo.org/geos/geos-3.5.0.tar.bz2
tar xvjf geos-3.5.0.tar.bz2
cd geos-3.5.0
./configure
make
sudo make install

cd ..
sudo python setup.py install
sudo pip install --upgrade six

sudo pip install -U obspy


