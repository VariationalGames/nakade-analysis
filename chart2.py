"""Render nakade shapes as a chart, for either lattice.

Black stones are the enclosing wall, bare points are the eyespace. Every pair of
adjacent points among the wall and the eyespace is joined by a lattice edge, so
each shape reads as a fragment of the board. A red circle marks each vital
point: where the attacker must play to stop the defender making two eyes."""
import math, sys, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

SQ3 = math.sqrt(3)
BG, WALL, WALL_ED = "#f4f3ee", "#15171c", "#000000"
LINE, POINT, VITAL = "#2f3d9c", "#1c2670", "#d0342c"
TEXT, DIM = "#23282f", "#6d7480"

HEX_NBRS = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]
SQ_NBRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def cfg(kind):
    if kind == "hex":
        return HEX_NBRS, (lambda c: (SQ3 * (c[0] + c[2] / 2.0), -1.5 * c[2])), 0.7
    return SQ_NBRS, (lambda c: (1.5 * c[0], -1.5 * c[1])), 0.6


def ring_of(cells, nbrs):
    members = set(cells)
    ring = set()
    for c in cells:
        for d in nbrs:
            nb = tuple(a + b for a, b in zip(c, d))
            if nb not in members:
                ring.add(nb)
    return ring


def edges(points, nbrs):
    for c in points:
        for d in nbrs:
            nb = tuple(a + b for a, b in zip(c, d))
            if nb in points and c < nb:
                yield c, nb


def extent(cells, kind, nbrs, pix, r):
    pts = [pix(c) for c in list(set(cells)) + list(ring_of(cells, nbrs))]
    return (max(p[0] for p in pts) - min(p[0] for p in pts) + 2 * r + 0.5,
            max(p[1] for p in pts) - min(p[1] for p in pts) + 2 * r + 0.5)


def draw(ax, shape, kind, nbrs, pix, r, ox, oy):
    cells, vital = shape
    members, ring = set(cells), ring_of(cells, nbrs)
    pts = [pix(c) for c in list(members) + list(ring)]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    at = lambda c: (ox + pix(c)[0] - cx, oy + pix(c)[1] - cy)
    for a, b in edges(members | ring, nbrs):
        (x0, y0), (x1, y1) = at(a), at(b)
        ax.plot([x0, x1], [y0, y1], color=LINE, linewidth=1.5, solid_capstyle="round", zorder=1)
    for c in members:
        ax.add_patch(Circle(at(c), radius=r * 0.17, facecolor=POINT, edgecolor="none", zorder=2))
    for c in ring:
        ax.add_patch(Circle(at(c), radius=r, facecolor=WALL, edgecolor=WALL_ED, linewidth=0.8, zorder=3))
    for c in vital:
        ax.add_patch(Circle(at(c), radius=r * 0.6, facecolor="none", edgecolor=VITAL,
                            linewidth=4.0, zorder=4))


def render(by_size, kind, path, title, subtitle):
    nbrs, pix, r = cfg(kind)
    gap = 1.5
    rows = []
    for size in sorted(by_size):
        shapes = by_size[size]
        if not shapes:
            continue
        ext = [extent(cells, kind, nbrs, pix, r) for cells, _ in shapes]
        rows.append((size, shapes, [w for w, _ in ext], max(h for _, h in ext)))

    total_h = sum(h for _, _, _, h in rows) + gap * (len(rows) + 1) + 3.4
    total_w = max(max(sum(w) + gap * (len(w) + 1) for _, _, w, _ in rows) + 2.0, 14)

    fig, ax = plt.subplots(figsize=(total_w * 0.48, total_h * 0.48))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    y = total_h - 1.0
    ax.text(total_w / 2, y, title, ha="center", va="top", fontsize=21, color=TEXT, weight="bold")
    y -= 1.25
    ax.text(total_w / 2, y, subtitle, ha="center", va="top", fontsize=10.5, color=DIM)
    y -= 1.5

    for size, shapes, widths, rowh in rows:
        y -= rowh / 2
        ax.text(0.7, y, f"{size}", ha="left", va="center", fontsize=16, color=DIM, weight="bold")
        x = (total_w - (sum(widths) + gap * (len(widths) - 1))) / 2
        for s, w in zip(shapes, widths):
            draw(ax, s, kind, nbrs, pix, r, x + w / 2, y)
            x += w + gap
        y -= rowh / 2 + gap

    ax.set_xlim(0, total_w)
    ax.set_ylim(y, total_h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, dpi=200, facecolor=BG, bbox_inches="tight", pad_inches=0.28)
    print(f"wrote {path}")


if __name__ == "__main__":
    data, kind, out, title, sub = sys.argv[1:6]
    by = {int(k): [(tuple(tuple(c) for c in s["cells"]), tuple(tuple(c) for c in s["vital"]))
                   for s in v]
          for k, v in json.load(open(data)).items()}
    render(by, kind, out, title, sub)
