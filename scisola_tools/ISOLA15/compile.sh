#!/bin/bash

# invert
gfortran invert/isola15.for -O2 -o isola12c
gfortran invert/norm15.for -O2 -o norm12c
gfortran invert/dsretc.for -O2 -o dsretc
gfortran invert/kagan.for -O2 -o kagan

# green
gfortran green/gr_xyz.for -O2 -o gr_xyz
gfortran green/Elemse.for -O2 -o elemse


