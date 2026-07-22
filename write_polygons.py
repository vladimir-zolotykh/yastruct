#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import struct
import itertools

polygons = [
    [(1.0, 2.5), (3.5, 4.0), (2.5, 1.5)],
    [(7.0, 1.2), (5.1, 3.0), (0.5, 7.5), (0.8, 9.0)],
    [(3.4, 6.3), (1.2, 0.5), (4.6, 9.2)],
]


def write_polygons(filename, polygons):
    # Determine bounding box
    flattened = list(itertools.chain(*polygons))
    min_x = min(x for x, y in flattened)
    max_x = max(x for x, y in flattened)
    min_y = min(y for x, y in flattened)
    max_y = max(y for x, y in flattened)

    with open(filename, "wb") as f:
        f.write(
            struct.pack("<iddddi", 0x1234, min_x, min_y, max_x, max_y, len(polygons))
        )

        for poly in polygons:
            size = len(poly) * struct.calcsize("<dd")
            f.write(struct.pack("<i", size + 4))
            for pt in poly:
                f.write(struct.pack("<dd", *pt))


# Call it with our polygon data
write_polygons("polygons.bin", polygons)


def read_polygons(filename):
    with open(filename, "rb") as f:
        # Read the header
        header = f.read(40)
        file_code, min_x, min_y, max_x, max_y, num_polygons = struct.unpack(
            "<iddddi", header
        )
        polygons = []
        for n in range(num_polygons):
            (pbytes,) = struct.unpack("<i", f.read(4))
            poly = []
            for m in range(pbytes // 16):
                pt = struct.unpack("<dd", f.read(16))
                poly.append(pt)
                polygons.append(poly)
    return polygons
