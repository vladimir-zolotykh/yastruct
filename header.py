#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import BinaryIO
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


def write_header(f: BinaryIO) -> None:
    pass


if __name__ == "__main__":
    with open("header.dat", "wb") as f:
        print(get_bbox())
        # write_header(f)
