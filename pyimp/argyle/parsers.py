

#from .common import *
import re

def cmdline_split(line, start=0, stop=None, inquote='', cont=False):
  end = len(line)
  if type(start) is not int:
    raise ValueError("start requires an int but found {:s}".format(repr(start)))
  if start < 0:
    start += end
  if stop is None:
    stop = end
  elif type(stop) is not int:
    raise ValueError("stop requires an int but found {:s}".format(repr(stop)))
  elif stop < 0:
    stop += end
  if start < 0 or start > end or stop < 0 or stop > end:
    raise IndexError("bad index range {:d} {:d}".format(start, stop))
  tokens = []
  pos, curr = start, []
  while pos < stop:
    c = line[pos]
    if c.isspace():
      if not inquote:
        if len(curr):
          tokens.append(''.join(curr))
          curr.clear()
      else:
        curr.append(c)
      pos += 1
      continue
    if c in "'\"":
      if not inquote and len(curr) == 0:
        inquote = c
        pos += 1
        continue
      if c == inquote and len(curr) and (pos+1 == end or line[pos+1].isspace()):
        tokens.append(''.join(curr))
        curr.clear()
        inquote = ''
        pos += 1
        continue
    elif c == "\\":
      if pos+1 < end:
        curr.append(line[pos+1])
        pos += 2
        continue
      else:
        cont = True
        pos += 1
        continue
    curr.append(c)
    pos +=1
  else:
    if len(curr):
      tokens.append(''.join(curr))
      curr.clear()
  return tokens, inquote, cont


PARSER_PATTERN = r"(?:[-]{,2}(((?:[^\\\s=]+|\\.)+)(?:([:=+!])(\S+)?)?)|\S+)|\s+"
PARSER_REGEXP  = re.compile(PARSER_PATTERN, re.M)


def token_parse(text, parser, pos=0, tokens=None, onerror=None):
  end = len(text)
  if tokens is None:
    tokens = parser.new_tokens()
  while pos < end:
    m = PARSER_REGEXP.match(text, pos, end)
    if m is None:
      raise ValueError("this shouldn't be possible." \
          "  Failed to match at {:d} near {:s}".format(pos, text[pos:pos+10]))
    pos = m.end(0)
    whole, prefix, sep, suffix = m.groups()
    if whole.strip() == '':
      continue
    token_type = parser.get_type(whole, prefix, sep, suffix)
    if token_type is None:
      if callable(onerror):
        if onerror(text, tokens, m, pos, end, whole, prefix, sep, suffix):
          continue
        raise ValueError("Bad token: {:s} at {:d}".format(whole, pos))
    tokens.add_token(token_type, whole, prefix, sep, suffix)
  return tokens

def args_parse(args, parser, pos=0, tokens=None, onerror=None):
  for arg in args:
    token_parse(arg, parser, pos=0, onerror=None)

def nultiline_parser(text, parser, pos=0, tokens=None, onerror=None):
  if tokens is None:
    tokens = parser.new_tokens()
  lineno = 0
  for line in text.split('\n'):
    lineno += 1
    try:
      args_parse(line, parser, pos, tokens, onerror)
    except Exception as exc:
      print("Error parsing at line {:d}".format(lineno))
      raise exc
  return tokens


class Parser(object):
  
  
  def parse(self, text):
    pass
