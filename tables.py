"""Render the two counts-by-size tables as images, in the chart's visual style.

    venv/bin/python tables.py single-eye.png all-shapes.png

The single-eye counts come from the shape JSON files; the all-shapes counts are
enumerated afresh (fast — enumeration is cheap, solving is what takes an hour)."""
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from nakade import lattice, shapes_by_size

BG, TEXT, DIM, RULE = "#f4f3ee", "#23282f", "#6d7480", "#b9b4a7"
MAX_SIZE = 9
WIDTH = 12.5   # inches; both tables come out the same width
BOARDS = (("Badux", "hex", "single-eye-shapes-badux.json"),
          ("Go", "square", "single-eye-shapes-go.json"))


def single_eye_counts(path):
    data = json.load(open(path))
    return [len(data.get(str(n), [])) for n in range(1, MAX_SIZE + 1)]


def all_shape_counts(kind):
    nbrs, refl, rot, folds, origin = lattice(kind)
    by = shapes_by_size(nbrs, refl, rot, folds, MAX_SIZE, origin)
    return [len(by[n]) for n in range(1, MAX_SIZE + 1)]


def render(path, title, header, rows):
    ncol = len(header)
    row_h, first_w, width = 0.7, 1.9, WIDTH
    col_w = (width - first_w - 0.6) / (ncol - 1)
    height = row_h * (len(rows) + 1) + 1.6
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    ax.text(width / 2, height - 0.45, title, ha="center", va="center", fontsize=15,
            color=TEXT, weight="bold")

    def x_of(col):
        return 0.3 + (first_w if col > 0 else 0) + col_w * max(col - 1, 0) + (col_w if col > 0 else 0)

    def draw_row(y, cells, color, weight="normal"):
        for col, cell in enumerate(cells):
            if col == 0:
                ax.text(0.3, y, cell, ha="left", va="center", fontsize=13, color=color, weight=weight)
            else:
                ax.text(x_of(col) - 0.15, y, cell, ha="right", va="center", fontsize=13, color=color,
                        weight=weight)

    y = height - 1.15
    draw_row(y, header, DIM, "bold")
    ax.plot([0.3, width - 0.3], [y - row_h / 2] * 2, color=RULE, linewidth=1.2)
    for cells in rows:
        y -= row_h
        draw_row(y, cells, TEXT)
    ax.plot([0.3, width - 0.3], [y - row_h / 2] * 2, color=RULE, linewidth=1.2)
    fig.savefig(path, dpi=200, facecolor=BG)
    print(f"wrote {path}")


if __name__ == "__main__":
    single_path, all_path = sys.argv[1:3]
    sizes = [str(n) for n in range(1, MAX_SIZE + 1)]

    rows = []
    for name, _, data in BOARDS:
        counts = single_eye_counts(data)
        rows.append([name] + [str(c) for c in counts] + [str(sum(counts))])
    render(single_path, "Single-eye shapes by eyespace size", ["Board"] + sizes + ["total"], rows)

    rows = []
    for name, kind, _ in BOARDS:
        rows.append([name] + [f"{c:,}" for c in all_shape_counts(kind)])
    render(all_path, "All shapes by eyespace size", ["Board"] + sizes, rows)
