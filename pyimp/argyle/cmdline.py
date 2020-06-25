

import sys, os, io, asyncio


def split(line, start=0, stop=None, inquote='', cont=False, curr=None
    , blocking=True):
  end = len(line)
  if curr is None:
    curr = []
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
  pos = start
  while pos < stop:
    c = line[pos]
    if c == "\n":
      if cont:
        cont = False
        pos += 1
        continue
      if inquote:
        curr.append( c )
        pos += 1
        continue
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
    #print(blocking, curr)
    if blocking and len(curr):
      tokens.append(''.join(curr))
      curr.clear()
  return tokens, pos, inquote, cont, curr


class CommandLineSplitter(object):
  
  @staticmethod
  def from_string(text, ontoken=None, encoding="utf8"):
    return CommandLineSplitter.from_bytes(bytes(text, encoding=encoding
        , ontoken=ontoken))
  
  @staticmethod
  def from_bytes(text, ontoken=None):
    cin = io.BytesIO(text)
    return CommandLineSplitter(cin, 0, None, blocking=True
        , ontoken=ontoken, encoding="utf8")
  
  cin       = None
  encoding  = None
  buff      = None
  pos       = None
  tokens    = None
  inquote   = None
  cont      = None
  curr      = None
  blocking  = None
  ontoken   = None
  
  def __init__(self, istream
      , inquote="", cont=False, curr=None, blocking=None, ontoken=None
      , encoding="utf8"):
    cin = io.FileIO(istream) if isinstance(istream, str) else istream
    if callable(ontoken):
      # create asyncio.StreamReader from a io.IOBase or add the listerner to
      # an existing one.
      pass
    if not (isinstance(cin, (io.IOBase, asyncio.StreamReader)) \
        and hasattr(cin, "read")):
      raise ValueError("bad cin, expected a str or readable stream or asyncio" \
          " stream reader but found: {:s}".format(repr(istream)))
    if inquote and type(inquote) is not str:
      raise ValueError("bad inquote, expected None or str but found: {:s}" \
          .format(repr(inquote)))
    if curr and type(curr) is not list:
      raise ValueError("bad curr, expected None or list but found: {:s}" \
          .format(repr(curr)))
    if blocking is None:
      try:
        blocking = os.get_blocking(cin.fileno)
      except:
        blocking = False
    if ontoken and not callable(ontoken):
      raise ValueError("bad ontoken, expected None or callable but found: {:s}" \
          .format(repr(ontoken)))
    self.cin = cin
    self.encoding = encoding
    self.buff = bytearray("", encoding=encoding)
    self.pos = 0
    self.tokens = []
    self.inquote = inquote or ""
    self.cont = bool(cont)
    self.curr = curr or []
    self.blocking = bool(blocking)
    self.ontoken = ontoken or None
    if ontoken:
      ontoken(self.tokens.pop(0))
  
  def read(self, blocking=None):
    while True:
      if len(self.tokens):
        return self.tokens.pop(0)
      if len(self.buff) or len(self.curr):
        tokens, self.pos, self.inquote, self.cont, self.curr \
            = split(self.buff.decode(self.encoding), self.pos, None \
            , inquote=self.inquote, cont=self.cont, curr=self.curr \
            , blocking=self.blocking)
        self.buff = self.buff[self.pos:]
        self.pos = 0
        self.tokens.extend(tokens)
        continue
      if blocking is None:
        blocking = self.blocking
      more = self.cin.read()
      if more:
        if type(more) is str:
          more = bytes(more, encoding=self.encoding)
        self.buff.extend(more)
      if len(self.tokens) or len(self.buff):
        continue
      break
  
