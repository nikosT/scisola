#!/bin/bash

# invert
gfortran invert/isola15.for -o isola12c
gfortran invert/norm15.for -o norm12c
gfortran invert/dsretc.for -o dsretc
gfortran invert/kagan.for -o kagan

# green
gfortran green/gr_xyz.for -o gr_xyz
gfortran green/Elemse.for -o elemse


