#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import BinaryIO, Self
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


class Header:
    def __init__(self, magic, x1, y1, x2, y2, num_polygons):
        self.magic = magic
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.num_polygons = num_polygons

    def __eq__(self, other) -> bool:
        return (
            self.__dict__ == other.__dict__
            if isinstance(other, type(self))
            else NotImplemented
        )

    def pack(self) -> bytes:
        return struct.pack(
            "<iddddi", self.magic, self.x1, self.y1, self.x2, self.y2, self.num_polygons
        )

    @classmethod
    def from_file(cls, f: BinaryIO) -> Self:
        return cls(*struct.unpack("<iddddi", f.read(40)))

    def __repr__(self):
        args = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Header({args})"


def write_header(f: BinaryIO) -> None:
    (x1, y1), (x2, y2) = get_bbox()
    h = Header(0x1234, x1, y1, x2, y2, len(POLYGONS))
    f.write(h.pack())


if __name__ == "__main__":
    (x1, y1), (x2, y2) = get_bbox()
    h = Header(0x1234, x1, y1, x2, y2, len(POLYGONS))
    with open("header.dat", "wb") as f:
        f.write(h.pack())
    with open("header.dat", "rb") as f:
        h2 = Header.from_file(f)
    assert h == h2
