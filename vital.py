"""Annotate a shape JSON file with each shape's vital points.

Reads the chart input format — a size-keyed map of shapes, each either a bare
cell list or a {"cells", "vital"} record — and rewrites it in place with the
record form, computing the vital points fresh from the solver.

    python3 vital.py hex single-eye-shapes-badux.json
    python3 vital.py square single-eye-shapes-go.json
"""
import json
import sys

from nakade import Region, lattice


def cells_of(shape):
    raw = shape["cells"] if isinstance(shape, dict) else shape
    return [tuple(c) for c in raw]


def annotate(kind, path):
    nbrs = lattice(kind)[0]
    data = json.load(open(path))
    out = {}
    for size, shapes in data.items():
        records = []
        for shape in shapes:
            cells = cells_of(shape)
            vital = Region(cells, nbrs).vital_points()
            records.append({"cells": [list(c) for c in cells],
                            "vital": [list(cells[i]) for i in vital]})
        out[size] = records
    with open(path, "w") as f:
        f.write(compact(out))
    print(f"wrote {path}")


def compact(by_size):
    """one shape record per line, so the file diffs and reads by shape."""
    lines = ["{"]
    sizes = list(by_size)
    for i, size in enumerate(sizes):
        lines.append(f' "{size}": [')
        records = by_size[size]
        for j, record in enumerate(records):
            comma = "," if j < len(records) - 1 else ""
            lines.append("  " + json.dumps(record, separators=(",", ":")) + comma)
        lines.append(" ]" + ("," if i < len(sizes) - 1 else ""))
    lines.append("}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    annotate(sys.argv[1], sys.argv[2])
