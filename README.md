# JDFeditor
GUI application for editing database files,
specifically designed for the new JDF file format.
(J)son(D)atabase(F)ormat


JDFeditor Version 1.0
----------------------------------------------------------------------------
Copyright (C) 2016 Damian Chrzanowski
pjdamian.chrzanowski@gmail.com
License : GNU Public License v3
Check out my website at: http://damianch.eu.pn/


OVERVIEW:
The purpose is to be a cross-platform, quick and simple database manager,
main goal is to provide developers with a tool
to produce small to medium size databases efficiently.
If you need a database at its simplest form, without any
extra hassle of knowing how to access the produced library.
Then JDFeditor is the right tool for you.

JDFeditor is bundled with an easy-to-use library: jdf_lib.
jdf_lib will quickly load the content of your database into a variable.
All you need to know is the filename!
Check out the MANUAL.txt for more information.


HOW TO RUN:

-------------------- Linux -------------------------------

Download the package, unzip wherever you would like it. Run JDFeditor.sh or jdf_editor.py,
both files are made executable.
  -From a terminal run   ./JDFeditor.sh   or  python jdf_editor.py
  -From a file manager (Nautilus/Thunar etc.) just doubleclick JDFeditor.sh   or   jdf_editor.py

A good idea is to make a folder called 'bin' inside of your home folder.
Anything inside of it can be launched without providing a full path.
So that if you make a shortcut (launcher) on your desktop,
you only need to type the command JDFeditor.sh, not a full path.


-------------------- Windows ----------------------------

So far only from source code (easy enough):
Make sure that you have python 2.7 installed.  https://www.python.org/download/releases/2.7/

GTK3 library for windows is also necessary. Download the pygi-slimgtk.7z package from
the files section of the JDFeditor's Source Forge page or from:
https://sourceforge.net/projects/pygobjectwin32/files/pygi-slimgtk-3.18.2_py27_py34_win32_win64.7z/download
Inside of it there are 4 folders: py2.7-32, py2.7-64, py3.4-32 and py3.4-64.
These folders are the libraries for Python 2.7 and 3+ 32/64 bit.
Unpack the relevant (usually its either Python 2.7 or 3.4, 32 bit) into your &python&/lib/site-packages folder.
&python& is the location of your python installation.
Once python 2.7 is installed, just double click the downloaded jdf_editor.py file to launch the program.


 -------------------- Mac OS X ----------------------------


 I unfortunately do not have the option to test functionality on a Mac OS X system yet.
 So far I found out that these 2 packages need to be installed from the terminal:
  brew install gtk+3
  brew install pygobject3

 Then just launch jdf_editor.py from your terminalby typing in:
 python jdf_editor.py




TODO:
    - undo / redo
    - help section
    - export/import sqlite
    - export/import xml
    - export/import csv
    - export html


KNOWN ISSUES:
    - On linux, columns do not resize if there is a horizontal bar on the bottom of the window,
      this is a bug filed some time ago....

    - searching rows by typing them in the database posts errors, harmless but annoying.(fix in 1.01)

    - in a cell containing integer or float numbers focus is lost upon a right click, text cell are ok.


CHANGE LOG:

- version 1.0
    - final release version



JDFlibrary uses:

JSON library
GTK+ 3 library
pynsist 1.6  (coming for Windows)
Typodermic sofachrome font (logo)

Refer to the LICENSE file for details on licenses for the above mentioned.


========================================
JDFeditor License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see:
http://www.gnu.org/licenses/
========================================
