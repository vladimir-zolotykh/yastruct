#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import BinaryIO, Self
import os
from itertools import chain
import struct

PointType = tuple[float, float]
PolygonType = list[PointType]
POLYGONS: list[PolygonType] = [
    [(1.0, 2.5), (3.5, 4.0), (2.5, 1.5)],
    [(7.0, 1.2), (5.1, 3.0), (0.5, 7.5), (0.8, 9.0)],
    [(3.4, 6.3), (1.2, 0.5), (4.6, 9.2)],
]

BboxType = tuple[PointType, PointType]


def get_bbox(polygons: list[PolygonType] = POLYGONS) -> BboxType:
    x1 = min(x for x, _ in chain(*polygons))
    y1 = min(y for _, y in chain(*polygons))
    x2 = max(x for x, _ in chain(*polygons))
    y2 = max(y for _, y in chain(*polygons))
    return ((x1, y1), (x2, y2))


def get_schema_specs(schema) -> tuple[str, list[str]]:
    format: str = ""
    names: list[str] = []
    for name, fmt in schema:
        format += fmt
        names.append(name)
    return format, names


class SchemaMeta(type):
    def __new__(mcls, name, bases, ns):
        format, schema_names = get_schema_specs(ns.get("__schema__", []))

        args = ", ".join(schema_names)
        src = f"def __init__(self, {args}):\n"
        for sname in schema_names:
            src += f"    self.{sname} = {sname}\n"
        tmp = {}
        exec(src, {}, tmp)
        ns["__init__"] = tmp["__init__"]

        def pack(self) -> bytes:
            values = (getattr(self, a) for a in schema_names)
            return struct.pack(format, *values)

        @classmethod
        def from_file(cls, f: BinaryIO) -> Self:
            return cls(*struct.unpack(format, f.read(struct.calcsize(format))))

        ns["pack"] = pack
        ns["from_file"] = from_file
        return super().__new__(mcls, name, bases, ns)


class Header(metaclass=SchemaMeta):
    __schema__ = (
        ("magic", "<i"),
        ("x1", "d"),
        ("y1", "d"),
        ("x2", "d"),
        ("y2", "d"),
        ("num_polygons", "i"),
    )

    def __eq__(self, other) -> bool:
        return (
            self.__dict__ == other.__dict__
            if isinstance(other, type(self))
            else NotImplemented
        )

    def __repr__(self):
        args = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Header({args})"


def write_header(f: BinaryIO) -> None:
    (x1, y1), (x2, y2) = get_bbox()
    h = Header(0x1234, x1, y1, x2, y2, len(POLYGONS))
    f.write(h.pack())


def write_polygons(f: BinaryIO, polygons: list[PolygonType] = POLYGONS) -> None:
    for polygon in polygons:
        _I = struct.Struct("<i")
        _DD = struct.Struct("<dd")
        sz = _I.size + len(polygon) * _DD.size
        f.write(struct.pack(_I.format, sz))
        for p in polygon:
            f.write(_DD.pack(*p))


class Polygon:
    def __init__(self, bytesdata: bytes | memoryview):
        self.view = memoryview(bytesdata)

    @classmethod
    def from_file(cls, f: BinaryIO) -> Self:
        (sz,) = struct.unpack("<i", f.read(struct.calcsize("<i")))
        return cls(f.read(sz - struct.calcsize("<i")))

    def __iter__(self):
        _DD = struct.Struct("<dd")
        for off in range(0, len(self.view), _DD.size):
            sl = slice(off, off + _DD.size)
            yield _DD.unpack_from(self.view[sl])


def test_header():
    (x1, y1), (x2, y2) = get_bbox()
    h = Header(0x1234, x1, y1, x2, y2, len(POLYGONS))
    with open("header.dat", "wb") as f:
        f.write(h.pack())
    with open("header.dat", "rb") as f:
        h2 = Header.from_file(f)
    assert h == h2


def test_polygons():
    if not os.path.exists("header.dat"):
        (x1, y1), (x2, y2) = get_bbox()
        h = Header(0x1234, x1, y1, x2, y2, len(POLYGONS))
        with open("header.dat", "wb") as f:
            f.write(h.pack())
    if not os.path.exists("polygons.dat"):
        with open("polygons.dat", "wb") as f:
            write_polygons(f)
    with open("polygons.dat", "wb") as f:
        for _ in range(h.num_polygons):
            polygon = Polygon.from_file(f)
            for p in polygon:
                print(p)


if __name__ == "__main__":
    test_header()
    test_polygons()
