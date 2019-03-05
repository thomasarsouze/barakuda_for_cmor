#!/bin/bash

LIST_MOD="GCC/4.9.2 netCDF-Fortran/4.2-foss-2015a"


module add ${LIST_MOD}

##TA make clean
make

sleep 1

module rm ${LIST_MOD}

