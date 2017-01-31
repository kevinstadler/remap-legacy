#!/bin/bash

# overlay.py can also be used for general simple world projections
if [ ! -f world.osm ]; do
  wget http://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip
  unzip TM_WORLD_BORDERS-0.3.zip
  ogr2osm TM_WORLD_BORDERS-0.3.shp

  # we have to manually add the +-180 degree meridians to render the outline
  STR="<node id=\"0\" lat=\"90\" lon=\"-179\" visible=\"true\"/><node id=\"181\" lat=\"90\" lon=\"178\" visible=\"true\"/>"
  for (( lat=1; lat<=180; lat++ )); do
    STR="${STR}<node id=\"$lat\" lat=\"$((90-lat))\" lon=\"-179\" visible=\"true\"/><way id=\"$lat\" visible=\"true\"><nd ref=\"$((lat-1))\"/><nd ref=\"$lat\"/></way><node id=\"$((lat+181))\" lat=\"$((90-lat))\" lon=\"178\" visible=\"true\"/><way id=\"$((lat+181))\" visible=\"true\"><nd ref=\"$((lat+180))\"/><nd ref=\"$((lat+181))\"/></way>"
  done

  head -n 2 TM_WORLD_BORDERS-0.3.osm > world.osm
  echo $STR >> world.osm
  tail -n +3 TM_WORLD_BORDERS-0.3.osm >> world.osm
fi

./overlay.py world.osm --render-all --srs "+proj=moll" --up S --scale 30500000 -f a0l -col black --stroke-width 1.0 -o Mollweide.pdf
