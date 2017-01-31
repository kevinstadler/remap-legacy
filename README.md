> **this repository is no longer maintained**

Unless you are for some reason limited to mapnik v2.3 and/or rendering directly from `.osm` files, this repository is mainly for reference. The successor project (based on mapnik v3 and postGIS) can be found [here](https://github.com/kevinstadler/remap)

---

# re:map

[mapnik](http://mapnik.org/) styles and python scripts developed for and by [The Residents Association](http://theresidentsassociation.tumblr.com)

## what's here

* *mapnik XML styles* in the `styles` folder
* `remap.py`: a python script that allows easy and flexible rendering of .osm files
* `overlay.py`: a python script for overlaying several .osm files translated on top of each other

see also the [examples](examples) directory

## remap.py

```
EXAMPLES
```

## overlay.py

`overlay.py` takes several .osm files as arguments, and some of its options (`-lat`, `-lon`, `-up`, `-col`) can take as many arguments as there are .osm files. to stop the options from eating up all following arguments it is wise to specify the .osm files first (see also the help below)

```
EXAMPLES
```

neatly packaged metropolitan data sets are available at https://mapzen.com/data/metro-extracts/

notes on projection: `overlay.py` puts the separate osm files in separate mapnik layers, each with its own `srs` argument using `+proj=ob_tran` to rotate the center of the underlying latlong coordinates to the origin of the grid at (0,0). The `--srs` argument to the python script sets the projection of the output map, which should logically be centered on (0,0), the default being an orthographic projection.

as `ob_tran` assumes a spherical earth and the osm files are presumably in WGS84 this means that there might be some distortion. when overlaying a polar region over an equatorial one, the size of the polar one will be rendered around 1% smaller than it actually is on the ellipsoid sphere.

## dependencies

`mapnik` and `mapnik-python` (at least version 2.3) from the [PPA](https://launchpad.net/~mapnik/+archive/ubuntu/nightly-2.3/+packages). depending on what files you want to render you'll also need `mapnik-input-plugin-osm` and/or `mapnik-input-plugin-ogr`

## todos

i'd like to be able to do arbitrary rotations of the maps - at the moment there is only a simple `--up` option, with `remap.py` supporting rotation by multiples of 90 (`N, S, E, W`), and `overlay.py` only supporting north and south-up (`N, S`).

for `remap.py` it is possible to achieve arbitrary rotations by providing an appropriate [two-point equidistant projection](https://en.wikipedia.org/wiki/Two-point_equidistant_projection) as its `--srs` argument, see https://gist.github.com/eyeNsky/9853026

for `overlay.py` it should be possible to perform rotations around the centers using proj's `+towgs84` parameter - since the map data is centered on (0,0), a simple rotation around the x axis (i.e. `'+towgs84=0,0,0,3600*phi,0,0,0`) should suffice. it appears that the 7 parameter [Helmert transformation](https://en.wikipedia.org/wiki/Helmert_transformation) is not meant for rotations that exceed a few arcseconds. as we're only rotating around one axis it should theoretically be possible to compensate for the inaccuracy of the transformation by setting the 7th 'scale' argument to `cos(phi)` and adjusting the x-rotation argument accordingly. at least in my version of proj the scale argument doesn't seem to be doing anything though. maybe it would be possible to perform rotation around the map center via `ob_tran` also?

## license

some sort of free/CC license to be confirmed, (c) [The Residents Association](http://theresidentsassociation.tumblr.com) 2016

## remap.py options

```
usage: remap.py [-h] [-x STYLE] [-s SCALE] [-lon LONGITUDE] [-lat LATITUDE]
                [--srs SRS] [--up {N,S,E,W}] [-w] [-r] [-n] [-i] [-c] [-g]
                [-f FORMAT] [-l | -p] [-m MARGIN] [-d DPI] [-o OUTPUT]
                osmfile

render OSM data to PDF using a mapnik stylesheet

positional arguments:
  osmfile               OSM data file to be rendered

optional arguments:
  -h, --help            show this help message and exit
  -x STYLE, --style STYLE
                        Mapnik XML style file
  -s SCALE, --scale SCALE
                        Map scale denominator (i.e. render map as 1:x)
  -lon LONGITUDE, --longitude LONGITUDE
                        Map center longitude (e.g. -3.1977)
  -lat LATITUDE, --latitude LATITUDE
                        Map center latitude (e.g. 55.9486)
  --srs SRS             Projection to be used (proj.4 string, default:
                        +proj=ortho)
  --up {N,S,E,W}        "up" orientation of map (N, S, E or W). this will add
                        an +axis option to the srs proj.4 string
  -w, --water           Render water and other natural bodies?
  -r, --railways        Render railways?
  -n, --names           Render names?
  -i, --include-scale   Add scale and projection information to the map
  -c, --copyright       add copyright information and url to the map
  -g, --grid            add red meridian/parallel lines to the map (only
                        correct with north-up)
  -f FORMAT, --format FORMAT
                        Cairo target page format (default a0)
  -l, --landscape       When rendering to a target page format, use landscape
                        orientation? (default)
  -p, --portrait        When rendering to a target page format, use portrait
                        orientation?
  -m MARGIN, --margin MARGIN
                        page margin in meters (default 0)
  -d DPI, --dpi DPI     target pdf resolution (default 72)
  -o OUTPUT, --output OUTPUT
                        output filename (default remap.pdf)
```

## overlay.py options

```
usage: overlay.py [-h] [-s SCALE] [--srs SRS]
                  [-lon [LONGITUDE [LONGITUDE ...]]]
                  [-lat [LATITUDE [LATITUDE ...]]] [-u [{N,S} [{N,S} ...]]]
                  [-bg BACKGROUND_COLOR] [-col [COLOR [COLOR ...]]]
                  [--filter [FILTER [FILTER ...]]]
                  [--stroke-width [STROKE_WIDTH [STROKE_WIDTH ...]]] [-r] [-i]
                  [-c] [-n] [-g] [-f FORMAT] [-m MARGIN] [-d DPI] [-o OUTPUT]
                  osmfile [osmfile ...]

Overlay several .osm files on top of each other. By default all layers are
translated so that the center of their extents coincide with the center of the
target map (which is the origin). Different centers (and map orientations) can
be specified per input file with the -lon -lat and --up options. When using
those options, it is often safer to pass the osmfile arguments first, to stop
the options from eating up all following arguments.

positional arguments:
  osmfile               The OSM data file(s)

optional arguments:
  -h, --help            show this help message and exit
  -s SCALE, --scale SCALE
                        map scale denominator (i.e. render map as 1:x)
  --srs SRS             projection to be used (proj.4 string, default:
                        +proj=ortho)
  -lon [LONGITUDE [LONGITUDE ...]], --longitude [LONGITUDE [LONGITUDE ...]]
                        map center longitude, one per osm file (e.g. -3.1977
                        -.2326)
  -lat [LATITUDE [LATITUDE ...]], --latitude [LATITUDE [LATITUDE ...]]
                        map center latitude, one per osm file (e.g. 55.9486
                        51.5465)
  -u [{N,S} [{N,S} ...]], --up [{N,S} [{N,S} ...]]
                        "up" orientation of map (currently only supports north
                        and south). Can specify either one (for entire map) or
                        one per osm file for individual rotations.
  -bg BACKGROUND_COLOR, --background-color BACKGROUND_COLOR
                        background color (default white)
  -col [COLOR [COLOR ...]], --color [COLOR [COLOR ...]]
                        stroke color, provide one for each osm file
  --filter [FILTER [FILTER ...]], --draw [FILTER [FILTER ...]]
                        mapnik filter(s) specifying what entities to render
                        (default: a single filter "[highway] != null")
  --stroke-width [STROKE_WIDTH [STROKE_WIDTH ...]]
                        stroke width(s) to draw entities with in pt, one per
                        specified filter (default 0.5)
  -r, --railways        render railways
  -i, --include-scale   add scale and projection information to the map
  -c, --copyright       add copyright information and url to the map
  -n, --names           add osm file names and center point information
  -g, --grid            add red meridian/parallel lines to the map (latitude
                        and longitude labels are bogus/relative to map center)
  -f FORMAT, --format FORMAT
                        Cairo target page format (default a4l)
  -m MARGIN, --margin MARGIN
                        page margin in meters (default 0)
  -d DPI, --dpi DPI     target pdf resolution (default 72)
  -o OUTPUT, --output OUTPUT
                        output filename (default overlay.pdf)
```
