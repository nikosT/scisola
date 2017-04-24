#!/bin/bash

flags='-O2 -m32 -std=legacy -fbacktrace -ffpe-trap=zero,overflow,underflow -fbounds-check -Wall -Wextra -Wconversion -Wunused-parameter'

flags2="-m32 -O2 -ggdb -fbacktrace"

# green
gfortran  green/gr_xyz.for $flags -o gr_xyz
gfortran  green/elemse.for $flags -o elemse

# invert
gfortran invert/isola15.for $flags2 -ffpe-summary='none' -o isola12c
gfortran invert/norm15.for $flags2  -ffpe-summary='none' -o norm12c
gfortran invert/dsretc.for $flags -o dsretc
gfortran invert/kagan.for $flags -o kagan

