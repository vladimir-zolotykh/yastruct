#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import struct
from header import get_bbox, POLYGONS


class Field:
    def __init__(self, fmt, offset):
        self.fmt = fmt
        self.offset = offset

    def __get__(self, instance, owner=None):
        rng = slice(self.offset, self.offset + struct.calcsize(self.fmt))
        t = struct.unpack_from(self.fmt, instance.view[rng])
        return t[0] if len(t) == 1 else t

    def __set__(self, instance, value):
        rng = slice(self.offset, self.offset + struct.calcsize(self.fmt))
        instance.view[rng] = struct.pack(self.fmt, value)


class View:
    def __init__(self, bytesdata: bytes | memoryview):
        self.view = memoryview(bytesdata)

    def __repr__(self):
        args = ", ".join(f"{getattr(self, name)!r}" for name in self.__schema__)
        return f"{type(self).__name__}({args})"


class Header(View):
    __schema__ = ["magic", "x1", "y1", "x2", "y2", "num_polygons"]
    magic = Field("<i", 0)
    x1 = Field("<d", 4)
    y1 = Field("<d", 4 + 8)
    x2 = Field("<d", 4 + 8 + 8)
    y2 = Field("<d", 4 + 8 + 8 + 8)
    num_polygons = Field("<i", 4 + 8 + 8 + 8 + 8)


if __name__ == "__main__":
    (x1, y1), (x2, y2) = get_bbox(POLYGONS)
    h = Header(bytearray(40))
    h.magic = 0x1234
    h.x1 = x1
    h.y1 = y1
    h.x2 = x2
    h.y2 = y2
    h.num_polygons = len(POLYGONS)
    print(h)
