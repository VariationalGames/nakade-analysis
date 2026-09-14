"""The strong rule (all subshapes nakade) is false. Test the weaker one:
does every nakade shape contain at least one nakade subshape one cell smaller?
If so, size-n candidates can be grown from the size-(n-1) nakade set."""
import re, sys
from nakade import lattice, canon

nbrs, refl, rot, folds, origin = lattice("hex")


def load(path):
    by, size = {}, None
    for line in open(path):
        m = re.match(r"\s+size (\d+):", line)
        if m:
            size = int(m.group(1)); by[size] = set(); continue
        s = line.strip()
        if s.startswith("((") and size is not None:
            by[size].add(canon(list(eval(s)), refl, rot, folds))
    return by


def connected(cells):
    cells = set(cells); start = next(iter(cells))
    seen, stack = {start}, [start]
    while stack:
        c = stack.pop()
        for d in nbrs:
            nb = tuple(a + b for a, b in zip(c, d))
            if nb in cells and nb not in seen:
                seen.add(nb); stack.append(nb)
    return len(seen) == len(cells)


def subshapes(shape):
    for c in shape:
        rest = [x for x in shape if x != c]
        if rest and connected(rest):
            yield canon(rest, refl, rot, folds)


def grow(shape):
    members = set(shape)
    for c in shape:
        for d in nbrs:
            nb = tuple(a + b for a, b in zip(c, d))
            if nb not in members:
                yield canon(list(shape) + [nb], refl, rot, folds)


known = load(sys.argv[1])
print("rule: every nakade shape contains >= 1 nakade subshape one cell smaller\n")
ok = True
for size in sorted(known):
    if size - 1 not in known or not known[size]:
        continue
    for sh in known[size]:
        if not any(s in known[size - 1] for s in subshapes(sh)):
            ok = False
            print(f"  VIOLATION at size {size}: {sh}")
print("  holds on every solved size" if ok else "  FALSE")

if ok:
    print("\nreachable candidate sets by growing the previous nakade set:")
    for size in sorted(known):
        if size - 1 not in known or not known[size - 1]:
            continue
        cands = set()
        for sh in known[size - 1]:
            cands.update(grow(sh))
        missed = [s for s in known[size] if s not in cands]
        print(f"  size {size}: {len(cands):>4} candidates vs {len(known[size]):>3} actual"
              f"{'  (MISSES ' + str(len(missed)) + ')' if missed else '  — all found'}")
