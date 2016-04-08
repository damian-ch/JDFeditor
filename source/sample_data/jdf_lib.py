#!/usr/bin/env python
# coding=utf-8
# -----------------------------------------------------------------------------
# Name:        jdf_lib.py
# Purpose:     Quick read/write jdf library
# Author:      Damian Chrzanowski
# Created:     24/03/16
# Modified:    07/04/16
# Copyright:   pjdamian.chrzanowski@gmail.com
# License:     GNU Public License v3
# Version:     1.0
# Revision:    N/A
# -----------------------------------------------------------------------------
# jdf_lib, Is a library that can open and save JDF file format.
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
import json

JDF_VERSION = '1'
VERSION = '1.0'


def save_database(file_name, field_names, field_types, data_base):
    """Save database to a file.

    (str, list, list, list) -> None

    :param file_name: file name or path to the file that will be saved
    :param field_names: a list of databases' column names
    :param field_types: a list of databases' column types
    :param data_base: a list containing the actual database contents

    This function saves the database into a file using the JDF format.
    """
    f_handle = open(file_name, 'w')
    data_base.insert(0, field_types)
    data_base.insert(0, field_names)
    f_handle.write('JDF' + JDF_VERSION + '\n')
    json.dump(data_base, f_handle)
    f_handle.close()


def load_database(file_name):
    field_names = list()
    field_types = list()
    data_base = list()
    line_counter = 0
    try:
        f_handle = open(file_name, 'r')
        for each in f_handle:
            if line_counter == 0:
                if each.strip() == 'JDF1':
                    line_counter += 1
                    continue
                else:
                    raise Exception
            elif line_counter == 1:
                load_dump = json.loads(each)
                break
    except Exception:
        return -1
    for each in load_dump:
        data_base.append(each)
    field_names = data_base.pop(0)
    field_types = data_base.pop(0)
    return field_names, field_types, data_base

if __name__ == '__main__':
    stuff = load_database('Untitled.jdf')
    if stuff == -1:
        print 'load error'
    else:
        print(type(stuff), type(stuff[0]))
        print stuff
    raw_input('press enter')
