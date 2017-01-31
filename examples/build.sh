#!/bin/sh
# build all example pdfs

../scripts/download-area "City of Edinburgh"
../scripts/download-boundaries Wien
../scripts/download-boundaries Toronto
../scripts/download-ways Berlin
../scripts/download-boundaries Berlin
../scripts/download-area Bogalusa

cp ../{remap,overlay}.py .
source README.md
rm {remap,overlay}.py
