#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import Self, Any
from functools import singledispatch
from pathlib import Path
import struct
from itertools import chain
from header import POLYGONS, PolygonType


class Field:
    def __init__(self, offset):
        self.offset = offset

    def fetch(self, instance):
        raise NotImplementedError

    def drop(self, instance, value):
        raise NotImplementedError

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.fetch(instance)

    def __set__(self, instance, value):
        self.drop(instance, value)


class FieldStr(Field):
    def __init__(self, offset, fmt):
        super().__init__(offset)
        self.fmt = fmt

    @property
    def _rng(self):
        return slice(self.offset, self.offset + struct.calcsize(self.fmt))

    def fetch(self, instance, owner=None):
        t = struct.unpack_from(self.fmt, instance.view[self._rng])
        return t[0] if len(t) == 1 else t

    def drop(self, instance, value):
        instance.view[self._rng] = struct.pack(self.fmt, value)


class FieldType(Field):
    def __init__(self, offset, typ):
        super().__init__(offset)
        self.typ = typ

    @property
    def _rng(self):
        return slice(self.offset, self.offset + self.typ._size)

    def fetch(self, instance):
        return self.typ(instance.view[self._rng])

    def drop(self, instance, value):
        instance.view[self._rng] = value.view if isinstance(value, View) else value


class FieldMeta(type):

    def __new__(mcls, name, bases, ns):
        off = 0
        fields = []

        for key, val in ns.items():

            @singledispatch
            def add_field(val, off):
                return None, None

            @add_field.register
            def _(val: str, off: int) -> tuple[FieldStr, int]:
                return FieldStr(off, val), struct.calcsize(val)

            @add_field.register
            def _(val: FieldMeta, off: int) -> tuple[FieldType, int]:
                return FieldType(off, val), val._size

            @add_field.register
            def _(val: Any, off: int) -> tuple[None, None]:
                raise TypeError

            if key[:2] == "__" and key[-2:] == "__":
                continue
            try:
                x = add_field(val, off)
                ns[key], off = x[0], (off + x[1])
                fields.append(key)
            except TypeError:
                pass
        ns["_size"] = off
        ns["_fields"] = fields
        return super().__new__(mcls, name, bases, ns)


class View(metaclass=FieldMeta):
    def __init__(self, bytesdata: bytes | memoryview):
        self.view = memoryview(bytesdata)

    def __repr__(self):
        args = ", ".join(f"{getattr(self, name)!r}" for name in self._fields)
        return f"{type(self).__name__}({args})"

    def write(self, path: str):
        with open(path, "wb") as f:
            f.write(self.view)

    @classmethod
    def from_file(cls, path: str) -> Self:
        with open(path, "rb") as f:
            return cls(f.read(cls._size))


class Point(View):
    x = "<d"
    y = "<d"

    @classmethod
    def from_bytes(cls, x: float, y: float) -> Self:
        p = cls(bytearray(cls._size))
        p.x, p.y = x, y
        return p


class Bbox(View):
    xy1 = Point
    xy2 = Point

    @classmethod
    def from_bytes(cls, xy1: Point, xy2: Point) -> Self:
        bbox = cls(bytearray(cls._size))
        bbox.xy1, bbox.xy2 = xy1, xy2
        return bbox


def get_bbox(polygons: list[PolygonType] = POLYGONS) -> Bbox:
    x1 = min(x for x, _ in chain(*polygons))
    y1 = min(y for _, y in chain(*polygons))
    x2 = max(x for x, _ in chain(*polygons))
    y2 = max(y for _, y in chain(*polygons))
    return Bbox.from_bytes(Point.from_bytes(x1, y1), Point.from_bytes(x2, y2))


class Header(View):
    magic = "<i"
    bbox = Bbox
    num_polygons = "<i"

    @classmethod
    def expected(cls) -> Self:
        h = cls(bytearray(cls._size))
        h.magic = 0x1234
        h.bbox = get_bbox(POLYGONS)
        h.num_polygons = len(POLYGONS)
        return h


HEADER_DAT = ".header.dat"

if __name__ == "__main__":
    if Path(HEADER_DAT).exists():
        h = Header.from_file(HEADER_DAT)
        print(h)
    else:
        h = Header.expected()
        h.write(HEADER_DAT)
        print(f"{HEADER_DAT} has written")
