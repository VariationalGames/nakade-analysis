"""Enumerate free polyhexes (hex-lattice eye shapes) and free polyominoes up to size N.

A "free" shape is counted once per equivalence class under translation plus the
lattice point group: 12 elements for hex (6 rotations x reflection), 8 for square.
This is the hex analogue of the polyomino <-> eye-shape isomorphism Vila &
Cazenave rely on, so the counts are the size of an exhaustive badux shape library.
"""
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10

# --- hex: cube coords (x, y, z) with x+y+z == 0 -----------------------------
HEX_NBRS = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]

def rot60(c):
    x, y, z = c
    return (-z, -x, -y)

def refl(c):
    x, y, z = c
    return (x, z, y)

def hex_transforms(cells):
    out = []
    for mirror in (False, True):
        cur = [refl(c) for c in cells] if mirror else list(cells)
        for _ in range(6):
            out.append(tuple(cur))
            cur = [rot60(c) for c in cur]
    return out

def hex_canon(cells):
    best = None
    for t in hex_transforms(cells):
        s = sorted(t)
        ox, oy, oz = s[0]
        norm = tuple(sorted((x - ox, y - oy, z - oz) for x, y, z in s))
        if best is None or norm < best:
            best = norm
    return best

# --- square: (x, y) ---------------------------------------------------------
SQ_NBRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def sq_transforms(cells):
    out = []
    for mirror in (False, True):
        cur = [(-x, y) for (x, y) in cells] if mirror else list(cells)
        for _ in range(4):
            out.append(tuple(cur))
            cur = [(-y, x) for (x, y) in cur]
    return out

def sq_canon(cells):
    best = None
    for t in sq_transforms(cells):
        s = sorted(t)
        ox, oy = s[0]
        norm = tuple(sorted((x - ox, y - oy) for x, y in s))
        if best is None or norm < best:
            best = norm
    return best

def enumerate_free(nbrs, canon, origin, n):
    counts = []
    level = {canon([origin])}
    counts.append(len(level))
    for _ in range(2, n + 1):
        nxt = set()
        for shape in level:
            cellset = set(shape)
            for c in shape:
                for d in nbrs:
                    cand = tuple(a + b for a, b in zip(c, d))
                    if cand in cellset:
                        continue
                    nxt.add(canon(list(shape) + [cand]))
        level = nxt
        counts.append(len(level))
    return counts

hexc = enumerate_free(HEX_NBRS, hex_canon, (0, 0, 0), N)
sqc = enumerate_free(SQ_NBRS, sq_canon, (0, 0), N)

print(f"{'size':>4}  {'free polyhexes':>15}  {'free polyominoes':>17}  {'hex/square':>10}  {'hex growth':>10}")
for i, (h, s) in enumerate(zip(hexc, sqc), start=1):
    g = f"{h / hexc[i - 2]:.2f}x" if i >= 2 else "-"
    print(f"{i:>4}  {h:>15,}  {s:>17,}  {h / s:>9.2f}x  {g:>10}")
