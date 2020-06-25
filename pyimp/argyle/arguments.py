

from .common import *


class ArgumentTypes(object):
  
  _atlut    = None
  
  def __init__(self, *initializer):
    self._atlut = {}
    for cls in initializer:
      self.add(cls)
  
  def add(self, cls):
    if not isinstance(cls, Argument):
      raise ValueError("Invalid type, expected a subclass of Argument" \
          " but found: {:s}".format(name))
    name = cls.__name__
    if name in self._atlut:
      if self._atlut[name] is not cls:
        raise ValueError("Duplicate Argument type {:s}".format(name))
      continue
    self._atlut[cls.__name__] = cls


class Argument(object):
  
  @classmethod
  def from_token(cls, whole, prefix=None, sep=None, suffix=None):
    return cls(whole)
  
  _value    = None
  _type     = None
  
  @property
  def value(self):
    return self._type(self._value) if self._type else self._value
  
  def __init__(self, value, astype=None):
    if astype is None:
      astype = type(value)
    self._value = str(value)
    self._type = astype
  
  def __str__(self):
    return self._value


class KeyWordArgument(Argument):
  
  @classmethod
  def from_token(cls, whole, prefix, sep, suffix):
    if sep not in ":=":
      raise ValueError('invalid {:s} token: {:s}'.format(cls.__name__, whole))
    return cls(prefix, suffix)
  
  _keyword  = None
  
  def key(self):
    return self._keyword
  
  def __init__(self, key, value):
    if not key or not type(key) is str:
      raise ValueError('key must be a string but found {:s}'.fomrat(key))
    self._key = key
    super().__init__(value or None)


class OptionArgument(KeyWordArgument):
  
  @classmethod
  def from_token(cls, whole, prefix, sep, suffix):
    if sep not in ":=":
      raise ValueError('invalid {:s} token: {:s}'.format(cls.__name__, whole))
    return cls(prefix, sep, suffix)
  
  _operator  = None
  
  def __init__(self, key, operator, value):
    if operator and not type(key) is str:
      raise ValueError('operator must be a string but found {:s}' \
          .fomrat(operator))
    self._operator = operator or None
    super().__init__(value)
  


class CommandArgument(OptionArgument):
  
  pass



