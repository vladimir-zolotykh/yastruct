#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import Self
from pathlib import Path
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

    def write(self, path: str):
        with open(path, "wb") as f:
            f.write(self.view)

    @classmethod
    def from_file(cls, path: str) -> Self:
        with open(path, "rb") as f:
            return cls(f.read(cls.VIEW_SIZE))


class Header(View):
    OFF = 0
    _I = struct.Struct("<i")
    _D = struct.Struct("<d")
    __schema__ = ["magic", "x1", "y1", "x2", "y2", "num_polygons"]
    magic = Field("<i", OFF)
    OFF += _I.size
    x1 = Field("<d", OFF)
    OFF += _D.size
    y1 = Field("<d", OFF)
    OFF += _D.size
    x2 = Field("<d", OFF)
    OFF += _D.size
    y2 = Field("<d", OFF)
    OFF += _D.size
    num_polygons = Field("<i", OFF)
    OFF += _I.size
    VIEW_SIZE = OFF

    @classmethod
    def expected(cls) -> Self:
        h = cls(bytearray(cls.VIEW_SIZE))
        h.magic = 0x1234
        (h.x1, h.y1), (h.x2, h.y2) = get_bbox(POLYGONS)
        h.num_polygons = len(POLYGONS)
        return h


SPECS_DAT = ".specs.dat"

if __name__ == "__main__":
    if Path(SPECS_DAT).exists():
        h = Header.from_file(SPECS_DAT)
        print(h)
    else:
        h = Header.expected()
        h.write(SPECS_DAT)
        print(f"{SPECS_DAT} has written")
