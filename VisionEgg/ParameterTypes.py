# The Vision Egg: ParameterTypes
#
# Copyright (C) 2001-2003 Andrew Straw
# Copyright (C) 2005,2008 California Insitute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Type checking for the Vision Egg.

"""

import VisionEgg

import types, warnings
import numpy
import numpy.oldnumeric as numpyNumeric

array_types = [numpy.ndarray]
# Allow use of numarray and original Numeric Texture data without requiring either
try:
    import numarray
    array_types.append( numarray.numarraycore.NumArray )
except ImportError:
    pass
try:
    import Numeric as orig_Numeric
    array_types.append( orig_Numeric.ArrayType )
except ImportError:
    pass

class ParameterTypeDef(object):
    """Base class for all parameter type definitions"""
    def verify(value):
        # override this method with type-checking code
        raise RuntimeError('must override base class method verify')
    verify = staticmethod(verify)

def get_all_classes_list(klass):
    #assert(type(klass) == types.ClassType)
    result = [klass]
    for base_klass in klass.__bases__:
        result.extend(get_all_classes_list(base_klass))
    return result

def is_parameter_type_def(item_type):
    if type(item_type) == types.ClassType:
        if Sequence in get_all_classes_list(item_type):
            raise TypeError("Sequence definition must be an instance (with a contained type).")
        else:
            return ParameterTypeDef in get_all_classes_list(item_type)
    elif isinstance(item_type,ParameterTypeDef):
        return True
    elif issubclass(item_type,ParameterTypeDef): # for new style classes
        return True
    elif item_type == types.NoneType:
        warnings.warn("types.NoneType will stop being a supported type "+\
                      "argument.  Please call "+\
                      "VisionEgg.ParameterTypes.get_type(None) to get the "+\
                      "supported value",DeprecationWarning,stacklevel=2)
        return True
    else:
        return False

class AnyOf(ParameterTypeDef):
    def __init__(self,*item_types):
        for item_type in item_types:
            if not is_parameter_type_def(item_type):
                raise TypeError("%s is not a valid type definition")
        self.item_types = item_types
    def __str__(self):
        return 'AnyOf(%s)'%(' or '.join(map(str,self.item_types)))
    def verify(self,is_any_of):
        for item_type in self.item_types:
            if item_type.verify(is_any_of):
                return True
        return False
    def get_item_types(self):
        return self.item_types

class NoneMC(type):
    """metaclass for NoneType"""
    def __str__(self):
        return 'None'

class NoneType(ParameterTypeDef):
    __metaclass__ = NoneMC
    def verify(is_none):
        return is_none is None
    verify = staticmethod(verify)

class BooleanMC(type):
    """metaclass for Boolean"""
    def __str__(self):
        return 'Boolean'

class Boolean(ParameterTypeDef):
    __metaclass__ = BooleanMC
    def verify(is_boolean):
        if isinstance(is_boolean,(bool,int,numpy.integer)):
            return True
        else:
            return False
    verify = staticmethod(verify)

class CallableMC(type):
    """metaclass for Callable"""
    def __str__(self):
        return 'Callable'

class Callable(ParameterTypeDef):
    __metaclass__ = CallableMC
    def verify(is_callable):
        return callable(is_callable)
    verify = staticmethod(verify)

class AnyClassMC(type):
    """metaclass for AnyClass"""
    def __str__(self):
        return 'AnyClass'

class AnyClass(ParameterTypeDef):
    """parameter is a class"""
    __metaclass__ = AnyClassMC
    def verify(is_class):
        return type(is_class) == types.ClassType
    verify = staticmethod(verify)

class SubClass(ParameterTypeDef):
    """parameter is derived from base_class"""
    def __init__(self,base_class):
        if type(base_class) != types.ClassType:
            raise TypeError("base_class must be ClassType")
        self.base_class = base_class
    def verify(self,is_class):
        if type(self.base_class) != types.ClassType:
            return False
        return self.base_class in get_all_classes_list(is_class)
    def __str__(self):
        return 'SubClass of %s'%str(self.base_class)

class Instance(ParameterTypeDef):
    """parameter is an instance of class_type"""
    def __init__(self,class_type):
        if type(class_type) not in (types.ClassType, types.TypeType):
            raise TypeError("expected a class type")
        self.class_type = class_type
    def __str__(self):
        contained_string = str(self.class_type)
        return 'Instance of %s'%contained_string
    def verify(self,is_instance):
        return isinstance(is_instance,self.class_type)

class IntegerMC(type):
    """metaclass for Integer"""
    def __str__(self):
        return 'Integer'

class Integer(ParameterTypeDef):
    __metaclass__ = IntegerMC
    def verify(is_integer):
        return isinstance(is_integer,(int,numpy.integer))
    verify = staticmethod(verify)

class UnsignedIntegerMC(IntegerMC):
    """metaclass for UnsignedInteger"""
    def __str__(self):
        return 'UnsignedInteger'

class UnsignedInteger(Integer):
    __metaclass__ = UnsignedIntegerMC
    def verify(is_unsigned_integer):
        if not Integer.verify(is_unsigned_integer):
            return False
        return is_unsigned_integer >= 0
    verify = staticmethod(verify)

class RealMC(type):
    """metaclass for Real"""
    def __str__(self):
        return 'Real'

class Real(ParameterTypeDef):
    __metaclass__ = RealMC
    def verify(is_real):
        if isinstance(is_real, (int, float, numpy.floating, numpy.integer)):
            return True
        elif type(is_real) in array_types:
            # scalars can be Numeric arrays
            if len(is_real.shape)==0:
                try:
                    float(is_real)
                    return True
                except:
                    return False
        return False
    verify = staticmethod(verify)

class Sequence(ParameterTypeDef):
    """A tuple, list or Numeric array"""
    def __init__(self,item_type):
        if not is_parameter_type_def(item_type):
            raise TypeError("%s is not a valid type definition"%item_type)
        self.item_type = item_type
    def __str__(self):
        contained_string = str(self.item_type)
        return 'Sequence of %s'%contained_string
    def verify(self,is_sequence):
        try:
            len(is_sequence)
        except TypeError:
            return False
        for i in xrange(len(is_sequence)):
            if not self.item_type.verify(is_sequence[i]):
                return False
        return True

class Sequence2(Sequence):
    def __str__(self):
        contained_string = str(self.item_type)
        return 'Sequence2 of %s'%contained_string
    def verify(self,is_sequence2):
        if not Sequence.verify(self,is_sequence2):
            return False
        if not len(is_sequence2) == 2:
            return False
        return True

class Sequence3(Sequence):
    def __str__(self):
        contained_string = str(self.item_type)
        return 'Sequence3 of %s'%contained_string
    def verify(self,is_sequence3):
        if not Sequence.verify(self,is_sequence3):
            return False
        if not len(is_sequence3) == 3:
            return False
        return True

class Sequence4(Sequence):
    def __str__(self):
        contained_string = str(self.item_type)
        return 'Sequence4 of %s'%contained_string
    def verify(self,is_sequence4):
        if not Sequence.verify(self,is_sequence4):
            return False
        if not len(is_sequence4) == 4:
            return False
        return True

class Sequence4x4(Sequence4):
    def __str__(self):
        contained_string = str(self.item_type)
        return 'Sequence4x4 of %s'%contained_string
    def verify(self,is_sequence4x4):
        try:
            len(is_sequence4x4)
        except TypeError:
            return False
        if not len(is_sequence4x4) == 4:
            return False
        for i in range(4):
            if not Sequence4.verify(self,is_sequence4x4[i]):
                return False
        return True

class StringMC(type):
    """metaclass for String"""
    def __str__(self):
        return 'String'

class String(ParameterTypeDef):
    __metaclass__ = StringMC
    def verify(is_string):
        if isinstance(is_string,str):
            return True
        else:
            return False
    verify = staticmethod(verify)

class UnicodeMC(type):
    """metaclass for Unicode"""
    def __str__(self):
        return 'Unicode'

class Unicode(ParameterTypeDef):
    __metaclass__ = UnicodeMC
    def verify(is_unicode):
        if isinstance(is_unicode,unicode):
            return True
        else:
            return False
    verify = staticmethod(verify)

def get_type(value):
    """Take a value and return best guess of ParameterTypeDef it is."""
    py_type = type(value)

    if isinstance(value,bool):
        return Boolean
    elif value is None:
        return NoneType
    elif isinstance(value,(int,numpy.integer)):
        if py_type >= 0:
            return UnsignedInteger
        else:
            return Integer
    elif isinstance(value,(float,numpy.floating)):
        return Real
    elif py_type == types.InstanceType:
        # hmm, impossible to figure out appropriate class of all possible base classes
        return Instance(value.__class__)
    elif callable(value):
        return Callable
    else:
        try:
            len(value)
        except TypeError:
            is_sequence = False
        else:
            is_sequence = True
        if is_sequence:
            if len(value) == 4:
                # see if it's a 4x4 sequence
                is_sequence4x4 = True
                for i in range(4):
                    try:
                        len(value[i])
                    except TypeError:
                        is_sequence4x4 = False
                if is_sequence4x4:
                    sequence4x4_type = get_type(value[0][0]) # XXX assume all same types
                    return Sequence4x4(sequence4x4_type)
            if type(value) == str:
                return String
            lcd_type = get_type(value[0]) # lowest common denominator type
            for i in range(len(value)):
                this_type = get_type(value[i])
                if lcd_type != this_type:
                    # find lowest common denominator type
                    if lcd_type.verify( this_type ):
                        continue # covered by lowest common denominator
                    elif this_type.verify( lcd_type ):
                        lcd_type = this_type # new lowest common denominator
                    else:
                        lcd_type = AnyOf( lcd_type, this_type ) # make new lowest common denominator
            sequence_type = lcd_type
            if len(value) == 2:
                return Sequence2(sequence_type)
            elif len(value) == 3:
                return Sequence3(sequence_type)
            elif len(value) == 4:
                return Sequence4(sequence_type)
            else:
                return Sequence(sequence_type)
    # finally, one last check:
    if isinstance(value, object):
        # new style class
        # hmm, impossible to figure out appropriate class of all possible base classes
        return Instance(value.__class__)
    else:
        raise TypeError("Unable to determine type for '%s'"%value)

def assert_type(check_type,require_type):
    if not is_parameter_type_def(check_type):
        raise ValueError("require a ParameterTypeDef as argument (not %s)"%check_type)
    if not is_parameter_type_def(require_type):
        raise ValueError("require a ParameterTypeDef as argument (not %s)"%require_type)
    if check_type == require_type:
        return

    if check_type in (Integer,UnsignedInteger) and require_type == Boolean:
        return # let integers pass as booleans
    # XXX doesn't check if Instance is actually instance of proper class
    if isinstance(check_type,ParameterTypeDef):
        check_class = check_type.__class__
    else:
        check_class = check_type

    if isinstance(require_type,ParameterTypeDef):
        if isinstance(require_type,AnyOf):
            passed = False
            for ok_type in require_type.get_item_types():
                try:
                    assert_type(check_type, ok_type )
                    return # it's ok
                except:
                    pass
        else:
            require_class = require_type.__class__
    else:
        require_class = require_type

    if require_class in get_all_classes_list(check_class):
        return

    if issubclass(require_class,Real):
        if issubclass(check_class,Boolean):
            return
        elif issubclass(check_class,Integer):
            return

    if issubclass(require_class,Integer):
        if issubclass(check_class,Boolean):
            return

    raise TypeError("%s not of type %s"%(check_type,require_type))
