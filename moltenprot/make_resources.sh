#!/bin/bash
description='
A script to generate PyQt5 resources and/or documentation HTML/PDF for MoltenProt.
Run every time the GUI elements or the documentation ODT file is changed.

USAGE:
./make_resources.sh [option]

OPTIONS:
docs    make documentation in PDF and HTML format (requires libreoffice)
ui      make PySide6 resource file for GUI (requires PySide6)
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
    # using cross-platform compression for resources as recommended here https://forum.qt.io/topic/163835
    pyside6-rcc resources.qrc --compress-algo zlib -o ui/resources_rc.py
    # convert UI files to python files
    for i in ui/*.ui; do pyside6-uic --from-imports "$i" -o "${i//.ui/.py}" ; done
fi
