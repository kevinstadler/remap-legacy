#!/usr/bin/env python2
from math import cos, degrees, pi, radians
from mapnik import *
from pango import ALIGN_CENTER, ALIGN_RIGHT
import cairo
import argparse

parser = argparse.ArgumentParser(description='Renders OSM data to PDF using a Mapnik stylesheet')
parser.add_argument('osmfile', help='OSM data file to be rendered')
parser.add_argument('-x', '--style', default='styles/remap.xml', help='Mapnik XML style file')
parser.add_argument('-s', '--scale', type=float, help='Map scale denominator (i.e. render map as 1:x)')
parser.add_argument('-lon', '--longitude', type=float, help='Map center longitude (e.g. -3.1977)')
parser.add_argument('-lat', '--latitude', type=float, help='Map center latitude (e.g. 55.9486)')
parser.add_argument('--srs', default="+proj=ortho", help='Projection to be used (proj.4 string, default: +proj=ortho)')
parser.add_argument('--up', default='N', choices=['N', 'S', 'E', 'W'], help='"up" orientation of map (N, S, E or W). this will add an +axis option to the srs proj.4 string')

parser.add_argument('-w', '--water', action='store_true', help='Render water and other natural bodies?')
parser.add_argument('-r', '--railways', action='store_true', help='Render railways?')
parser.add_argument('-n', '--names', action='store_true', help='Render names?')

parser.add_argument('-i', '--include-scale', action='store_true', help='Add scale and projection information to the map')
parser.add_argument('-c', '--copyright', action='store_true', help='add copyright information and url to the map')
parser.add_argument('-g', '--grid', action='store_true', help='add red meridian/parallel lines to the map (only correct with north-up)')

#parser.add_argument('-w', '--width', type=float, help='Output file width (in m)')
#parser.add_argument('-t', '--height', type=float, help='Output file height (in m)')
parser.add_argument('-f', '--format', default='a0', help='Cairo target page format (default a0)')
arrangement = parser.add_mutually_exclusive_group()
arrangement.add_argument('-l', '--landscape', action='store_true', help='When rendering to a target page format, use landscape orientation? (default)')
arrangement.add_argument('-p', '--portrait', action='store_true', help='When rendering to a target page format, use portrait orientation?')
parser.add_argument('-m', '--margin', type=float, default=0, help='page margin in meters (default 0)')
#parser.add_argument('-b', '--border', action='store_true', help='Fill margin area black')
parser.add_argument('-d', '--dpi', type=int, default=72, help='target pdf resolution (default 72)')
parser.add_argument('-o', '--output', default='remap.pdf', help='output filename (default remap.pdf)')
args = vars(parser.parse_args())

# resized later, initial size only matters for the resolution of the centering
m = Map(1000, 1000)
load_map(m, args['style'])

if args['scale'] == None:
  try:
    scale = m.find_style('scale')
    if (scale != None):
      print "Recommended scale for", args['style'], "is between", scale.rules[0].min_scale, "and", scale.rules[0].max_scale
      args['scale'] = scale.rules[0].min_scale
  except KeyError:
    print 'No scale specified, gonna make a guess.'

ds = Osm(file=args['osmfile'])

def addlayer(name):
  layer = Layer(name)
  layer.datasource = ds
  layer.styles.append(name)
  m.layers.append(layer)

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

print "Map center is at:"
mapcenter = m.envelope().center()
print mapcenter

# default: +axis=enu (east, north, up), south up: +axis=wsu (west, south, up)
up = {'N': 'enu', 'E': 'seu', 'S': 'wsu', 'W': 'nwu'}
if args['up'] != 'N':
  args['srs'] += ' +axis=' + up[args['up']]

digits = 4
m.srs = args['srs'] + ' +lon_0=' + str(round(mapcenter.x, digits)) + ' +lat_0=' + str(round(mapcenter.y, digits))

print
print "Aligning projection with map center:"
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

# 1 point == 1/72.0 inch
#pointspercm = 28.3464
# 1 pixel == 0.28 mm == 0.00028 m
pixelperm = 3571 # http://www.britishideas.com/2009/09/22/map-scales-and-printing-with-mapnik/

m.resize(int(pixelperm*printing.pagesizes[args['format']][0]), int(pixelperm*printing.pagesizes[args['format']][1]))
#print "Map size is now", m.width, "by", m.height

# TODO:
#if args['scale'] == None:
#print 'No scale specified, dynamic scale that fits the full extent of all data on the target page format is 1:' + str(m.scale_denominator())

m.zoom(args['scale'] / m.scale_denominator())

print "Final scale = " , m.scale(), " 1 :", m.scale_denominator(), "printed on", args['format']

# write to PDF
surface = printing.PDFPrinter(pagesize=pagesize, margin=args['margin'], resolution=args['dpi'], centering=printing.centering.both, scale=lambda(s):round(s,-1))#printing.any_scale

surface.render_map(m, args['output'])


# add annotations

if args['grid']: # red lat/lon grid
  surface.render_on_map_lat_lon_grid(m)

ctx = surface.get_context()
# could also find fontset from style file
#fonts = m.find_fontset('fonts')
#if (fonts != None):
#  print m.find_fontset('book-fonts').names[0]
ctx.select_font_face("DejaVu Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
ctx.set_font_size(fontsize)

def addline(txt):
  extent = ctx.text_extents(txt)
  ctx.show_text(txt)
  ctx.rel_move_to(-extent[4], 1.5*extent[3])

# respect margin
ctx.translate(args['margin']*pixelperm, args['margin']*pixelperm)
if args['include_scale']:
  scale = surface.render_scale(m, ctx)
  ctx.rel_move_to(0, scale[1])
  addline(m.srs)

if args['copyright']:
  addline("(c) OpenStreetMap contributors / The Residents Association")
  addline("http://github.com/kevinstadler/remap")

#surface.render_legend(m, attribution={"highway-fills": "foo"})
surface.finish()
#add_geospatial_pdf_header(, m, args['output'], wkt=)
