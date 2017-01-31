# remap.py examples

### for automatic download of data and building of examples, see [build.sh](build.sh)

## make a nice big A0 map
./remap.py -cirw -lon -3.1977 -lat 55.9486 "City of Edinburgh-area.osm"

## make a wee pocket map (don't plot water/other natural bodies)
./remap.py -cir --scale 6000 -f a4 -lon -3.1947 -lat 55.9486 "City of Edinburgh-area.osm"

## include names
./remap.py -inrw --scale 10700 -f a5 --landscape -lon -89.8722 -lat 30.7745 -o "Bogalusa-grid.pdf" Bogalusa.osm
./remap.py -inrw --scale 2200 -f a5 --landscape -lon -3.1927 -lat 55.9486 -l "Old Town.pdf" "City of Edinburgh-area.osm"

./remap.py -inrw --scale 11500 -f a3 --portrait -lon 13.4393 -lat 52.483 --margin 0.003 -o NeuKoelln.pdf Berlin-ways.osm

./remap.py -inrw --scale 15000 -f a3 -lon 16.38587 -lat 48.29547 Wien-area.osm

# overlay.py examples

## default setting draws street grids on top of each other
./overlay.py -i --scale 8000 Edinburgh.osm London.osm -lat 55.9385 51.5465 -lon -3.1916 -.2326 -col "#6c6" "#c88" -o Willesdenburgh.pdf

## draw a 10cm square north-up and south-up Edinburgh on top of each other, with the rotation/flipping centered on the castle
./overlay.py Edinburgh.osm Edinburgh.osm -lon -3.1947 -lat 55.9486 --up N S --width 0.1

## compare boundaries only (less messy than overlapping streets)
./overlay.py -cin Wien-boundaries.osm Berlin-boundaries.osm --draw "[admin_level] = '4'" "[admin_level] = '9'" --stroke-width 3 1 -lon 16.41 13.42 -lat 48.21 52.51 -s 185000 -m 0.005 -o ViennainBerlin.pdf

./overlay.py -cin Wien-boundaries.osm Leipzig-boundaries.osm --draw "[admin_level] = '4' or [admin_level] = '6'" "[admin_level] = '9' or [boundary] = 'postal_code'" --stroke-width 3 1 -lon 16.41 12.39 -lat 48.21 51.34 -s 120000 -o ViennainLeipzig.pdf

# artistic all-roads grid
./overlay.py --format a4 ednbrsmall.osm Gaithersburg39.175-77.1527.osm -lon -3.1977 -77.15281 -lat 55.9486 39.1747 -col '#633' '#356' --stroke-width 0.2 -s 25000 --draw "[highway] != null and [name] != null" -o ScottishNames.pdf

#./overlay.py scripts/Wien-boundaries.osm Toronto-boundaries.osm -lon 16.32 -79.4 -lat 48.15 43.63 --draw "[boundary] != null" --scale 250000 -i

# http://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative
# county borders are admin_level 4, municipal 6, boroughs 8, districts 9
if you're more interested in outlines, make sure to filter your data sets not just by simple bounding box. for example, use the overpass API like so:
