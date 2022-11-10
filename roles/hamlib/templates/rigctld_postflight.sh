#! /bin/bash

echo 'Cleaning up...';
rigctl -m {{ hamlib_rigid }} -c {{ hamlib_civ }} -r {{ hamlib_device }} -s {{ hamlib_baud }} T 0 #ensure we stop TX if it got stuck
