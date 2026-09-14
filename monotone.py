"""Does 'a bigger eyespace is never worse for the defender' hold on this lattice?
Equivalently: is every connected subshape of a nakade shape also nakade?"""
import re, sys
from nakade import lattice, canon

kind = sys.argv[2]
nbrs, refl, rot, folds, origin = lattice(kind)

by, size = {}, None
for line in open(sys.argv[1]):
    m = re.match(r"\s+size (\d+):", line)
    if m:
        size = int(m.group(1)); by[size] = set(); continue
    s = line.strip()
    if s.startswith("((") and size is not None:
        by[size].add(canon(list(eval(s)), refl, rot, folds))


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


viol = 0
for size in sorted(by):
    if size - 1 not in by:
        continue
    for sh in by[size]:
        for c in sh:
            rest = [x for x in sh if x != c]
            if rest and connected(rest) and canon(rest, refl, rot, folds) not in by[size - 1]:
                viol += 1
                print(f"  {kind} size {size}: removing a cell from {sh} yields a LIVE shape")
print(f"\n{kind}: {viol} violations — "
      f"{'monotonicity HOLDS' if viol == 0 else 'monotonicity FAILS'}")
