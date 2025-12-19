#!/bin/sh
description='
A script to generate PyQt5 resources and/or documentation HTML/PDF for MoltenProt.
Run every time the GUI elements or the documentation ODT file is changed.

USAGE:
./make_resources.sh [option]

OPTIONS:
docs    make documentation in PDF and HTML format (requires libreoffice)
ui      make PyQt5 resource file for GUI (requires pyrcc5)
all     make both docs and resources
help    print this message
'
if [ "$1" = "" ] || [ "$1" = "help" ]; then
    echo "$description"
fi

if [ "$1" = "all" ] || [ "$1" = "docs" ]; then
    libreoffice --writer --convert-to html doc/index.odt --outdir doc
    libreoffice --writer --convert-to pdf doc/index.odt --outdir doc
fi

if [ "$1" = "all" ] || [ "$1" = "ui" ]; then
    pyrcc5 resources.qrc -o ui/resources.py
fi