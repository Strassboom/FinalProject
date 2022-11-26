#!/bin/bash
#If there is a flash drive plugged in
if [[ $(ls /media/$USER | wc -l) > 0 ]]; then
    #If there is not an instance of the program running
    #$1 = path to executable folder
    if [ ! -f $1/dist/$2/holdFile ]; then
        touch $1/dist/$2/holdFile
        gnome-terminal -- bash -c "$1/dist/$2/$2 $1/dist/$2 $3;"
    fi
fi