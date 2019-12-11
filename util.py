def format_mem(mem):
    if mem > 1000000000:
        return '{0:.2f}'.format(mem/1000000000) + 'GB'
    elif mem > 1000000:
        return '{0:.0f}'.format(mem/1000000) + 'MB'
    elif mem > 1000:
        return '{0:.0f}'.format(mem/1000) + 'KB'
    else:
        return '{0:.0f}'.format(mem) + 'B'

def decode(s):
  import numpy
  from .qpython.qtype import QException
  if type(s) is bytes or type(s) is numpy.bytes_:
      return s.decode('utf-8')
  elif type(s) is QException:
      return str(s)[2:-1] #extract error from b'xxx'
  else:
      return str(s)