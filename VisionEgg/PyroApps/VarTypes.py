# The Vision Egg: VarTypes
#
# Copyright (C) 2004 Imran S. Ali, Lachlan Dowd
#
# Author: Imran S. Ali, Lachlan Dowd
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

# Add your supported supported demo script "variable types" here:

def getID(var_type):
    if var_type == "float":
	return 1
    elif var_type == "int" or var_type == "integer":
	return 2
    elif var_type == "string" or var_type == "str":
        return 3
    else:
	return -1

def getType(ID):
    if ID == 1:
	return "float"
    elif ID == 2:
	return "integer"
    elif ID == 3:
	return "string"
    else:
	return "undefined type"

