## Automatically adapted for numpy.oldnumeric Jun 18, 2007 by alter_code1.py

# The Vision Egg: AST_ext
#
# Copyright (C) 2004 Imran S. Ali, Lachlan Dowd
#
# Authors: Imran S. Ali, Lachlan Dowd
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

# This "AST extensions" module works for Python 2.2.1
# Because the structure of code trees changes with different Python versions, this module may not work with some
# previous Python releases, or future releases.

import pprint
import parser
import symbol
import token
import tokenize
import sys

# Hopefully, the node ID numbers in the name sequence is all that
# needs to be changed in order to get this module working with
# different Python release versions.

name_sequence = [292, 293, 294, 295, 297, 298, 299, 300, 301, 302,
303, 304, 305]

# Method for generating an AST sub tree (in list form) suitable for a
def gen_assign_val_subtree(assign_val, assign_val_type):
    name_sequence.reverse()
    sublist = []
    if assign_val_type == 2:
        sublist = [2, '%(assign_val)d' % vars()]
    elif assign_val_type == 1:
        sublist = [2, '%(assign_val)f' % vars()]
    elif assign_val_type == 3:
        sublist = [3, '"%(assign_val)s"' % vars()]
    for val in name_sequence[0:len(name_sequence) - 1]:
        sublist = [val, sublist]
    name_sequence.reverse()
    return sublist


class AST_Visitor:
    def __init__(self, modifying_AST):
        # Flags:

        # Checking assignment name (ie. "x = ..." where we are
        # checking if 'x' == 'assign_name'):
        self.checking_assign_name = 0

        # Setting assignment value (we are changing a found occurrence
        # of "assign_name = x" to "assign_name = assign_val"):
        self.setting_assign_val = 0

        # Index of where the AST visitor is currently at in the
        # 'name_sequence' defined earlier:
        self.name_seq_index = 0

        # AST visitor expects a subtree associated with
        # assignment/"=":
        self.expecting_equals = 0

        # Extracting assignment value (we are extracting the 'x' from
        # a found occurrence of "assign_name = x"):
        self.extracting_assign_val = 0

        # Extracted assignment value:
        self.extracted_val = "not found"

        # Are we modifying an AST? Otherwise we're extracting
        # information from an AST:
        self.modifying_AST = modifying_AST

    def traverse(self, AST_sublist, assign_name, assign_val_subtree):

        # If we have a single element (terminating leaf node):
        if type(AST_sublist) != list:
            return AST_sublist

        # If we have a sub tree of the form [x, [....]]:
        elif len(AST_sublist) == 2:

            # If we are somewhere in the 'name_sequence' defined
            # earlier: [292, [293, [294, [295, [297, [298, [299, [300,
            # [301, [302, [303, [304, [305, ...

            if self.name_seq_index > 0:
                # If we are at the end of the 'name_sequence':
                if self.name_seq_index == len(name_sequence) - 1 and AST_sublist[0] == name_sequence[self.name_seq_index]:
                    if len(AST_sublist[1]) == 3:
                        if self.extracting_assign_val == 1:
                            extracted_val = AST_sublist[1][1]
                            self.extracted_val = extracted_val
                            self.extracting_assign_val = 0
                        else:
                            # Enter new mode: AST visitor will check
                            # the name associated with the
                            # 'name_sequence' to see if it will match
                            # 'assign_name':
                            self.checking_assign_name = 1
                    self.name_seq_index = 0

                else:
                    expected_val = name_sequence[self.name_seq_index]
                    if AST_sublist[0] == expected_val:
                        # Update position in 'name_sequence':
                        self.name_seq_index = self.name_seq_index + 1
                    else:
                        self.name_seq_index = 0
                return AST_sublist[0:1] + [self.traverse(AST_sublist[1], assign_name, assign_val_subtree)]

            # Else we are in some arbitrary sequence:
            # [a, [b, [c, [d, [e, [...
            else:
                # If we are at the start of the 'name_sequence':
                if AST_sublist[0] == 292:
                    if self.setting_assign_val == 1:
                        AST_sublist[1] = assign_val_subtree
                        self.setting_assign_val = 0
                    else:
                        # Enter new mode: AST visitor will check to
                        # see if we are progressing through the
                        # 'name_sequence' defined earlier:
                        self.name_seq_index = 1
                    return AST_sublist[0:1] + [self.traverse(AST_sublist[1], assign_name, assign_val_subtree)]
                else:
                    return AST_sublist[0:1] + [self.traverse(AST_sublist[1], assign_name, assign_val_subtree)]

        # If we have a sub tree with 3 parent nodes:
        elif len(AST_sublist) == 3:

            # If the second parent node is a single element
            # (terminating leaf node):
            if type(AST_sublist[1]) != list:
                # If the current AST visitor mode is set to checking
                # for equality with "assign_name" (ie. "x = ..." where
                # we are checking if 'x' == 'assign_name')::
                if self.checking_assign_name == 1:
                    # If 'x' == 'assign_name' (see above):
                    if AST_sublist[1] == assign_name:
                        # Enter new mode: AST visitor will check to
                        # see if the current sub tree is associated
                        # with assignment/"=":
                        self.expecting_equals = 1
                    self.checking_assign_name = 0

                # If the current AST visitor mode is set to check if
                # the current sub tree is associated with
                # assignment/"=":
                elif self.expecting_equals == 1:
                    # If the current AST sub tree is associated with
                    # assignment/"=":
                    if AST_sublist[1] == '=':
                        if self.modifying_AST == 1:
                            # Enter new mode: AST visitor will change
                            # the assignment value to
                            # "assign_val_subtree":
                            self.setting_assign_val = 1
                        elif self.modifying_AST == 0:
                            # Enter new mode: AST visitor will extract
                            # the assignment value of "assign_name":
                            self.extracting_assign_val = 1
                    self.expecting_equals = 0

                return AST_sublist[0:2]

        # If we are somewhere within the 'name_sequence':
        if self.name_seq_index > 0 or self.name_seq_index < len(name_sequence) - 1:
            # If the AST visitor is extracting the value of "assign_name":
            if self.extracting_assign_val == 1:
                self.extracted_val = "compound"
                self.extracting_assign_val = 0


        # For all other types of sub trees, AST visitor will traverse
        # in a depth first search pattern:
        sub_list = []
        for x in AST_sublist:
            sub_list = sub_list + [self.traverse(x, assign_name, assign_val_subtree)]
        return sub_list

def modify_AST(myAST, assign_name, assign_val):
    myAST_Visitor = AST_Visitor(1)
    old_AST_list = myAST.tolist(1)
    assign_val_type = 0
    if isinstance(assign_val, int):
        assign_val_type = 2
    elif isinstance(assign_val, float):
        assign_val_type = 1
    elif type(assign_val) == str:
        assign_val_type = 3
    new_AST_list = myAST_Visitor.traverse(old_AST_list, assign_name, gen_assign_val_subtree(assign_val, assign_val_type))
    myNewAST = parser.sequence2ast(new_AST_list)
    return myNewAST

# Extract the assigned value of a variable from an AST. Retains the type.
def extract_from_AST(myAST, assign_name):
    myAST_Visitor = AST_Visitor(0)
    old_AST_list = myAST.tolist(1)
    new_AST_list = myAST_Visitor.traverse(old_AST_list, assign_name, 0)
    return myAST_Visitor.extracted_val

