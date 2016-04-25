### JDFeditor v 1.1
GUI application for editing database files,
specifically designed for the new JDF file format.
(J)son(D)atabase(F)ormat

Copyright (C) 2016 Damian Chrzanowski
License : GNU Public License v3
Check out my website at: http://damianch.eu.pn/

### Overview:
The purpose is to be a cross-platform, quick and simple database manager.
Main goal is to provide developers with a tool
to produce small to medium size databases efficiently.
If you need a database at its simplest form, without any
extra hassle of knowing how to access the produced library.
Then JDFeditor is the right tool for you.

JDFeditor is bundled with an easy-to-use Python library: jdf_lib.
jdf_lib will quickly load the content of your database into a variable.
All you need to know is the filename!


### Usage:

#### Windows:

So far only from source code (easy enough):
Make sure that you have python 2.7 installed.  [Python 2.7](https://www.python.org/download/releases/2.7/)

GTK3 library for windows is also necessary. Download the pygi-slimgtk.zip package from
the [files section](https://sourceforge.net/projects/jdfeditor/files/) of the JDFeditor's Source Forge page.
Inside of it there are 4 folders: py2.7-32, py2.7-64, py3.4-32 and py3.4-64.
These folders are the libraries for Python 2.7 and 3+ 32/64 bit.
Unpack the relevant (usually its either Python 2.7 or 3.4, 32 bit) into your &python&/lib/site-packages folder.
&python& is the location of your python installation.
Once python 2.7 is installed, just double click the downloaded jdf_editor.py file to launch the program.


#### Linux:

Download the package, unzip wherever you would like it. Run JDFeditor.sh or jdf_editor.py,
both files are made executable.

* From a terminal run   ./JDFeditor.sh
* From a file manager (Nautilus/Thunar etc.) just doubleclick JDFeditor.sh

A good idea is to make a folder called 'bin' inside of your home folder.
Anything inside of it can be launched without providing a full path.
So that if you make a shortcut (launcher) on your desktop,
you only need to type the command JDFeditor.sh, not a full path.


#### Mac OS X:

So far I found out that these 2 packages need to be installed from the terminal:

* brew install gtk+3
* brew install pygobject3

 Then just launch jdf_editor.py


#### TODO:

* object type cells
* undo / redo
* help section
* export/import sqlite
* export/import xml
* export/import csv


#### Known Issues:
* On linux, columns do not resize if there is a horizontal bar on the bottom of the window, this is a bug filed some time ago to Gnome....
* Searching rows by typing them in the database view posts errors, harmless but annoying.(fix in 1.2)
* Focus is lost when right clicking on a cell with a float or integer value


#### Change Log:

* version 1.2
    * fixed an incorrect shebang information
* version 1.1
    * added export html option, under the file menu section
* version 1.0
    * final release version



#### JDFlibrary uses the following libraries:

* JSON
* GTK+ 3
* pynsist 1.6  (coming soon, Windows only)
* Typodermic sofachrome font (logo)

Refer to the LICENSE file for details on licenses for the above mentioned.


#### JDFeditor License

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

