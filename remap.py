#!/usr/bin/env python2
from math import ceil, cos, degrees, pi, radians
from mapnik import *
from pango import ALIGN_CENTER, ALIGN_RIGHT
import cairo
import argparse

parser = argparse.ArgumentParser(description='Renders OSM data to PDF using a Mapnik stylesheet')
parser.add_argument('osmfile', help='The OSM data file(s)', nargs='+')
parser.add_argument('-x', '--style', default='styles/remap.xml', help='Mapnik XML style file')
parser.add_argument('-s', '--scale', type=float, help='Map scale denominator (i.e. render map as 1:x)')
parser.add_argument('-lon', '--longitude', type=float, help='Map center longitude (e.g. -3.1977)')
parser.add_argument('-lat', '--latitude', type=float, help='Map center latitude (e.g. 55.9486)')
parser.add_argument('--srs', default="+proj=ortho", help='Projection to be used (proj.4 string, default: +proj=ortho)')

parser.add_argument('-w', '--water', action='store_true', help='Render water and other natural bodies?')
parser.add_argument('-r', '--railways', action='store_true', help='Render railways?')
parser.add_argument('-n', '--names', action='store_true', help='Render names?')

parser.add_argument('-i', '--include-scale', action='store_true', help='Add scale and projection information to the map')
parser.add_argument('-u', '--url', action='store_true', help='Add remap url to the map')
parser.add_argument('-c', '--copyright', action='store_true', help='Add copyright information to the map')
parser.add_argument('-g', '--grid', action='store_true', help='Add red meridian/parallel lines to the map')

#parser.add_argument('-w', '--width', type=float, help='Output file width (in m)')
#parser.add_argument('-t', '--height', type=float, help='Output file height (in m)')
parser.add_argument('-f', '--format', default='a0', help='Cairo target page format (default a0)')
arrangement = parser.add_mutually_exclusive_group()
arrangement.add_argument('-l', '--landscape', action='store_true', help='When rendering to a target page format, use landscape orientation? (default)')
arrangement.add_argument('-p', '--portrait', action='store_true', help='When rendering to a target page format, use portrait orientation?')
parser.add_argument('-m', '--margin', type=float, default=0, help='Page margin in m (default 0)')
#parser.add_argument('-b', '--border', action='store_true', help='Fill margin area black')
parser.add_argument('-d', '--dpi', type=int, default=72, help='Target pdf resolution (default 72)')
parser.add_argument('-o', '--output', default='mymap.pdf', help='Output filename (default mymap.pdf)')
args = vars(parser.parse_args())

if len(args['osmfile']) > 1:
  print 'Passed more than one osm file, switching to twocities overlay-style.'
  print 'Map will be scaled dynamically so as to fit the *first* dataset.'
  args['style'] = 'styles/twocities.xml'

ds = Osm(file=args['osmfile'][0])

# resized later, initial size only matters for the resolution of the centering
m = Map(1000, 1000)
load_map(m, args['style'])

if args['scale'] == None:
  scale = m.find_style("scale")
  if (scale != None):
    print "Recommended scale for", args['style'], "is between", scale.rules[0].min_scale, "and", scale.rules[0].max_scale
    args['scale'] = scale.rules[0].min_scale

def addlayer(name):
#  if (m.find_style(name)):
  layer = Layer(name)
  layer.datasource = ds
  layer.styles.append(name)
  m.layers.append(layer)

#layer = Layer('l')
#layer.datasource = ds
#for style in ['highways-casing', 'highways-fill']:
#  layer.styles.append(style)
#m.layers.append(layer)

addlayer('tunnels-casing')
addlayer('tunnels-fill')
#if args['railways']:
#  addlayer('railway-tunnels')
if args['water']:
  addlayer('natural')
addlayer('highways-casing')
addlayer('highways-fill')
#if args['railways']:
#  addlayer('railway')
addlayer('bridges-casing')
addlayer('bridges-fill')
#if args['railways']:
#  addlayer('railway-bridges')
if args['names']:
  addlayer('bridges-names')
  addlayer('highways-names')
#  addlayer('tunnels-names')

m.zoom_all()
mapcenter = m.envelope().center()

print 'The center of the extent of the OSM map data is:'
print mapcenter

if args['longitude'] != None:
  mapcenter.x = args['longitude']
if args['latitude'] != None:
  mapcenter.y = args['latitude']

if (args['longitude'] != None) | (args['latitude'] != None):
  # m.pan(0, 0) sets center to northwestern-most point of the current envelope
  m.pan(int(m.width*(.5-(m.envelope().center().x-mapcenter.x)/m.envelope().width())), int(m.height*(.5+(m.envelope().center().y-mapcenter.y)/m.envelope().height())))
  print "Shifting map center based on command line arguments, target:"
  print mapcenter
  print "Map center is now at:"
  mapcenter = m.envelope().center()
  print mapcenter

digits = 4
m.srs = args['srs'] + ' +lon_0=' + str(round(mapcenter.x, 4)) + ' +lat_0=' + str(round(mapcenter.y, 4))
print "Aligning orthographic projection with map center:"
print m.srs

if args['format'] == "a0":
  fontsize = 10
else:
  fontsize = 6

if args['landscape']:
  args['format'] += "l"
else:
  # make a guess at whether the dataset is more high or wide
  ratio = pi*m.layers[0].envelope().width()*degrees(cos(radians(m.layers[0].envelope().height())))/180 / m.layers[0].envelope().height()
  print "Width-to-height ratio of the dataset is", ratio
  if ratio > 1:
    args['format'] += "l"

pagesize = printing.pagesizes[args['format']]
print pagesize

# 1 point == 1/72.0 inch
#pointspercm = 28.3464
# 1 pixel == 0.28 mm == 0.00028 m
pixelperm = 3571 # http://www.britishideas.com/2009/09/22/map-scales-and-printing-with-mapnik/

m.resize(int(pixelperm*printing.pagesizes[args['format']][0]), int(pixelperm*printing.pagesizes[args['format']][1]))
#print "Map size is now", m.width, "by", m.height
m.zoom(args['scale'] / m.scale_denominator())

print "Final scale = " , m.scale(), " 1 :", m.scale_denominator(), "printed on", args['format']

# write to PDF
surface = printing.PDFPrinter(pagesize=pagesize, margin=args['margin'], resolution=args['dpi'], centering=printing.centering.both, scale=lambda(s):round(s,-1))#printing.any_scale

surface.render_map(m, args['output'])


# add annotations

ctx = surface.get_context()
ctx.select_font_face("DejaVu Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
ctx.set_font_size(fontsize)

def addline(txt):
  extent = ctx.text_extents(txt)
  print(extent)
  ctx.show_text(txt)
  ctx.rel_move_to(-extent[4], 1.5*extent[3])

# respect margin
ctx.translate(args['margin']*pixelperm, args['margin']*pixelperm)
if args['include_scale']:
  scale = surface.render_scale(m, ctx)
  ctx.rel_move_to(0, scale[1])
  addline(m.srs)

if args['url']:
  addline("http://github.com/kevinstadler/remap")

if args['copyright']:
  addline("(c) OpenStreetMap contributors / The Residents Association")

if args['grid']: # red lat/lon grid
  surface.render_on_map_lat_lon_grid(m)

#surface.render_legend(m, attribution={"highway-fills": "foo"})
surface.finish()
#add_geospatial_pdf_header(, m, args['output'], wkt=)
