#!/usr/bin/env python2
# coding=utf-8
# -----------------------------------------------------------------------------
# Name:        export_html.py
# Purpose:     JDF database editor's html creator
# Author:      Damian Chrzanowski
# Created:     14/04/16
# Modified:    14/04/16
# Copyright:   pjdamian.chrzanowski@gmail.com
# License:     GNU Public License v3
# Version:     1.0
# Revision:    N/A
# -----------------------------------------------------------------------------
# export_html, html document creator for the JDFeditor
# Copyright (C) 2016 Damian Chrzanowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------
import os

if os.name == 'nt':  # different os'es use different file path separators.
    SEPARATOR = '\\'  # for windows
else:
    SEPARATOR = '/'  # for linux and os x


def build_html(file_name, path, header_names, header_types, database, prog_version):
    """Build a html file.

    (str, list, list, list, str) -> None

    :param file_name: input file name
    :param path: path to the html file
    :param header_names: a list of the header name
    :param header_types: a list of the types of headers
    :param database: content of the database, list type
    :param prog_version: name of the program and its version

    Build a html file that contains a table with the all the records of the database.
    """
    # out_str is the output string for the html file
    out_str = """<!DOCTYPE html>
<html>
<head>
<style>
body {text-align: center; background: #111; color: #FFF;}
.header {font-size: 13px; color: white; position: fixed; top: 10px; right: 20px;}
table {
    border-collapse: collapse;
    border-spacing: 0;
    border: 1px solid white;
    box-shadow: 1px 1px 5px white;
    align: center;
    margin-left: auto;
    margin-right: auto;
}
tr{
    border-top: 1px solid white;
    border-bottom: 1px solid white;
}
th{
    border-left: 1px dotted white;
    border-right: 1px dotted white;
}
td {
    padding: 6px;
    border-left: 1px dotted white;
    border-right: 1px dotted white;
}
</style>
</head>
<body>
<p class="header">Created with %s</p>
<br><h1>Database: <span style="color:#28ADB5">%s</span></h1>""" % (prog_version, file_name)
    out_str += '<table>'  # add a table
    # add the first row with header names
    out_str += '<tr>'
    out_str += '<th style="color: #1CFF00;">#</th>'  # make the number counter column
    for idx, val in enumerate(header_names):
        out_str += '<th>' + str(val) + ' - ' + header_types[idx] + '</th>'
    # close header names row
    out_str += '</tr>'
    # add the remaining rows (actual data)
    row_color = '#FFFFFF'
    for idx, row in enumerate(database):
        if idx % 2 == 0:
            row_color = '#111111'
        else:
            row_color = '#222222'
        out_str += '<tr style="background: %s">' % row_color  # add a row
        out_str += '<td style="color: #1CFF00;">' + str(idx) + '</td>'   # number the row after the index
        for each_column in row:
            out_str += '<td>' + str(each_column) + '</td>'   # add the data to each of the column

    out_str += '</table></body></html>'

    out_file = open(path, 'w')  # open file for saving, wiping its content if it already exists
    out_file.write(out_str)  # save the html source to the file
    out_file.close()  # close the file


if __name__ == '__main__':
    prog = 'JDFeditor v1.0'
    filename = 'hello.jdf'
    path_to_file = '/home/grimscythe/something.html'
    head_names = ['Name', 'E-Mail']
    head_types = ['str', 'str']
    sample_data = [["John Smith", "j.smith@email.com"],
                   ["John Smith", "j.smith@email.com"],
                   ["John Smith", "j.smith@email.com"]]
    build_html(filename, path_to_file, head_names, head_types, sample_data, prog)
