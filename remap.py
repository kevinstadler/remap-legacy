#!/usr/bin/env python2
from argparse import ArgumentParser
from math import cos, degrees, pi, radians
from mapnik import *
import cairo
import os.path

parser = ArgumentParser(description='Renders OSM data to PDF using a Mapnik stylesheet')
parser.add_argument('osmfile', help='OSM data file to be rendered')
parser.add_argument('-x', '--style', default='styles/remap.xml', help='Mapnik XML style file')
parser.add_argument('-s', '--scale', type=float, help='Map scale denominator (i.e. render map as 1:x)')
parser.add_argument('-lon', '--longitude', type=float, help='Map center longitude (e.g. -3.1977)')
parser.add_argument('-lat', '--latitude', type=float, help='Map center latitude (e.g. 55.9486)')
parser.add_argument('--srs', default="+proj=ortho", help='Projection to be used (proj.4 string, default: +proj=ortho)')
parser.add_argument('--up', default='N', choices=['N', 'S', 'E', 'W'], help='"up" orientation of map (N, S, E or W). this will add an +axis option to the srs proj.4 string')

parser.add_argument('-w', '--water', action='store_true', help='render water and other natural bodies?')
parser.add_argument('-r', '--railways', action='store_true', help='Render railways?')
parser.add_argument('-n', '--names', action='store_true', help='Render names?')

parser.add_argument('-i', '--include-scale', action='store_true', help='Add scale and projection information to the map')
parser.add_argument('-c', '--copyright', action='store_true', help='add copyright information and url to the map')
# TODO choose pleasant font size between 6 and 10pt, depending on output file size
parser.add_argument('--fontsize', type=int, default=10, help='font size used for additional information')
parser.add_argument('-g', '--grid', action='store_true', help='add red meridian/parallel lines to the map (only correct with north-up)')

parser.add_argument('-f', '--format', default='a0', help='Cairo target page format (default a0)')
arrangement = parser.add_mutually_exclusive_group()
arrangement.add_argument('-l', '--landscape', action='store_true', help='When rendering to a target page format, use landscape orientation? (default)')
arrangement.add_argument('-p', '--portrait', action='store_true', help='When rendering to a target page format, use portrait orientation?')

parser.add_argument('--width', type=float, help='output file width in meters (overrides --format)')
parser.add_argument('--height', type=float, help='output file height in meters (overrides --format)')
parser.add_argument('-m', '--margin', type=float, default=0, help='page margin in meters (default 0)')
#parser.add_argument('-b', '--border', action='store_true', help='Fill margin area black')
parser.add_argument('-d', '--dpi', type=int, default=72, help='target pdf resolution (default 72)')
parser.add_argument('-o', '--output', default='remap.pdf', help='output filename (default remap.pdf)')
args = vars(parser.parse_args())

if os.path.exists('styles/' + args['style'] + '.xml'):
  args['style'] = 'styles/' + args['style'] + '.xml'

# resized later, initial size only matters for the resolution of the centering
m = Map(5000, 5000)
load_map(m, args['style'])

if args['scale'] == None:
  try:
    scale = m.find_style('scale')
    if (scale != None):
      print "Recommended scale for", args['style'], "is between", scale.rules[0].min_scale, "and", scale.rules[0].max_scale
      args['scale'] = scale.rules[0].min_scale
  except KeyError:
    print 'No scale specified, gonna make a guess.'

print 'loading', args['osmfile']
ds = Osm(file=args['osmfile'])

def addlayer(name):
  try:
    m.find_style(name)
    layer = Layer(name)
    layer.datasource = ds
    layer.styles.append(name)
    m.layers.append(layer)
  except KeyError:
    None

addlayer('tunnels-casing')
addlayer('tunnels-fill')
if args['railways']:
  addlayer('railway-tunnels')
if args['water']:
  addlayer('natural')

addlayer('highways-casing')
addlayer('highways-fill')
if args['railways']:
  addlayer('railway')

addlayer('bridges-casing')
addlayer('bridges-fill')
if args['railways']:
  addlayer('railway-bridges')

if args['names']:
  addlayer('bridges-names')
  addlayer('highways-names')
  addlayer('tunnels-names')
  if args['water']:
    addlayer('natural-names')
  if args['railways']:
    addlayer('railway-names')

m.zoom_all()

if args['longitude'] == None:
  args['longitude'] = m.layers[0].envelope().center().x
if args['latitude'] == None:
  args['latitude'] = m.layers[0].envelope().center().y

print 'map center is at', args['longitude'], '/', args['latitude']

# default: +axis=enu (east, north, up), south up: +axis=wsu (west, south, up)
up = {'N': 'enu', 'E': 'seu', 'S': 'wsu', 'W': 'nwu'}
if args['up'] != 'N':
  args['srs'] += ' +axis=' + up[args['up']]

displaydigits = 4
m.srs = args['srs'] + ' +lon_0=' + str(round(args['longitude'], displaydigits)) + ' +lat_0=' + str(round(args['latitude'], displaydigits))


if args['landscape']:
  args['format'] += "l"
elif args['portrait'] == None:
  # make a guess at whether the dataset is more high or wide
  ratio = pi*m.layers[0].envelope().width()*degrees(cos(radians(m.layers[0].envelope().height())))/180 / m.layers[0].envelope().height()
  print "Width-to-height ratio of the dataset is", ratio
  if ratio > 1:
    args['format'] += "l"

# if only one set, make square
args['width'] = args['width'] or args['height']
args['height'] = args['height'] or args['width']
# --width/--height override --format
if args['width']:
  pagesize = (args['width'], args['height'])
else:
  pagesize = printing.pagesizes[args['format']]

# 1 point == 1/72.0 inch
#pointspercm = 28.3464
# 1 pixel == 0.28 mm == 0.00028 m
pixelperm = 3571 # http://www.britishideas.com/2009/09/22/map-scales-and-printing-with-mapnik/

m.resize(int(pixelperm*pagesize[0]), int(pixelperm*pagesize[1]))

# TODO:
#if args['scale'] == None:
#print 'No scale specified, dynamic scale that fits the full extent of all data on the target page format is 1:' + str(m.scale_denominator())

m.zoom(args['scale'] / m.scale_denominator())

# write to PDF
surface = printing.PDFPrinter(pagesize=pagesize, margin=args['margin'], resolution=args['dpi'], centering=printing.centering.both, scale=lambda(s):round(s,-1))#printing.any_scale

print 'writing map at scale 1:' + str(m.scale_denominator())
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
ctx.set_font_size(args['fontsize'])

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
print 'successfully wrote to', args['output']
