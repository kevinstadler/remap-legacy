# re:map

[Mapnik](https://github.com/mapnik/) styles and scripts developed for and by [The Residents Association](http://theresidentsassociation.tumblr.com)

## what's here

* **Mapnik XML styles** in the `styles` folder
* **remap.py**: a python script that allows easy and flexible rendering of .osm files

## usage

    # make a nice big A0 map
    ./remap.py -cirw -lon -3.1977 -lat 55.9486 Edinburgh.osm

    # make a wee pocket map (don't plot water/other natural bodies)
    ./remap.py -cir --scale 6000 -f a4 -lon -3.1947 -lat 55.9486 Edinburgh.osm

    # include names
    ./remap.py -inrw --scale 10700 -f a5 --landscape -lon -89.8722 -lat 30.7745 Bogalusa.osm
    ./remap.py -inrw --scale 2200 -f a5 --landscape -lon -3.1935 -lat 55.9486 Edinburgh.osm


## dependencies

mapnik and mapnik-python (at least version 2.3) from the [PPA](https://launchpad.net/~mapnik/+archive/ubuntu/nightly-2.3/+packages)

## license

some sort of free/CC license to be confirmed, (c) [The Residents Association](http://theresidentsassociation.tumblr.com) 2016
