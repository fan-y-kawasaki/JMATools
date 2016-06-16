#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import struct
import datetime
import time
import tarfile
  
class GRIB2():
  def __init__(self, fn):
    self._fn = fn

  def parse(self):
    with open(self._fn, 'rb') as f:
      self.session0(f.read(16))
      self.session1(f.read(21))
      self.session2(f.read(0))
      self.session3(f.read(72))
      self.session4(f.read(82))
      self.session5(f.read(519))
      self.session6(f.read(6))
      self.session7(f.read(self._grib_length - (16+21+0+72+82+519+6+4)))
      self.session8(f.read(4))
      
  def session0(self, buf):
    if buf[0:4].decode('ASCII') != 'GRIB':
      raise('Err')
    self._grib_length = struct.unpack('>Q', buf[8:16])[0]
    
    return
  
  def session1(self, buf):
    self._ref_time = datetime.datetime(year=struct.unpack('>H', buf[12:14])[0], month=buf[14], day=buf[15], hour=buf[16], minute=buf[17], second=buf[18])
    self._status = buf[19]
    self._product_kind = buf[20]
    print(self._ref_time)
    return
  
  def session2(self, buf):
    return

  def session3(self, buf):
    self._num_matrix = struct.unpack('>L', buf[6:10])[0]
    return

  def session4(self, buf):
    self._end_time = datetime.datetime(year=struct.unpack('>H', buf[34:36])[0], month=buf[36], day=buf[37], hour=buf[38], minute=buf[39], second=buf[40])
    ope = struct.unpack('>Q', buf[58:66])[0]
    self._rdr_ope = {
      'Sapporo': (ope &     0x0000000000000003),
      'Kushiro': (ope &     0x000000000000000C) >> 2,
      'Hakodate': (ope &    0x0000000000000030) >> 4,
      'Sendai': (ope &      0x00000000000000C0) >> 6,
      'Akita': (ope &       0x0000000000000300) >> 8,
      'Niigata': (ope &     0x0000000000000c00) >> 10,
      'Tokyo': (ope &       0x0000000000003000) >> 12,
      'Nagano': (ope &      0x000000000000c000) >> 14,
      'Shizuoka': (ope &    0x0000000000030000) >> 16,
      'Fukui': (ope &       0x00000000000c0000) >> 18,
      'Nagoya': (ope &      0x0000000000300000) >> 20,
      'Osaka' : (ope &      0x0000000000c00000) >> 22,
      'Matsue' : (ope &     0x0000000003000000) >> 24,
      'Hiroshima': (ope &   0x000000000c000000) >> 26,
      'Muroto': (ope &      0x0000000030000000) >> 28,
      'Fukuoka': (ope &     0x00000000c0000000) >> 30,
      'Tanegashima': (ope & 0x0000000300000000) >> 32,
      'Naze': (ope &        0x0000000c00000000) >> 34,
      'Okinawa': (ope &     0x0000003000000000) >> 36,
      'Ishigaki': (ope &    0x000000c000000000) >> 38,
      'NazeSP' : (ope &     0x0000030000000000) >> 40,
      'OkinawaSP': (ope &   0x00000c0000000000) >> 42,
    }
    print(self._rdr_ope)
    return

  def session5(self, buf):
    self._max_level = struct.unpack('>H', buf[12:14])[0]
    self._level_value = [-1.,]
    for i in range(251):
      v = struct.unpack('>H', buf[18 + (2 * i) - 1: 19 + (2 * i)])[0] / 100.
      self._level_value.append(v)

  def session6(self, buf):
    return

  def session7(self, buf):
    l = struct.unpack('>L', buf[0:4])[0]
    c = buf[4]
    vals = []
    lngu = 2 ** 8 - 1 - self._max_level
    j = 0
    for i in range(l - 5):
      v = buf[5 + i]
      if v <= self._max_level:
        j = 0
        vv = self._level_value[v]
        vals.append(vv)
        pv = vv
      else:
        k = (lngu ** j) * (v - (self._max_level + 1))
        for x in range(k):
          vals.append(pv)
        j += 1
    b = struct.pack('8601600f', *vals)
    with open(sys.argv[-1], 'wb') as f:
      f.write(b)
    return

  def session8(self, buf):
    if buf[0:4].decode('ASCII') != '7777':
      raise('Err')
    
  
if __name__ == '__main__':

  g = GRIB2(sys.argv[-2])
  g.parse()
