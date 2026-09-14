"""Enumerate the nakade (dead) eyespace shapes on a given lattice.

A shape is nakade when the attacker, moving first inside an otherwise empty
enclosed eyespace, can capture the enclosing wall under real Go rules — chains,
liberties, captures, no suicide. The wall's only liberties are inside the
region, so capturing it is exactly "the defender never got two eyes".

The wall is modelled as one virtual defender stone at index n, adjacent to every
region cell that touches the outside. That makes all chain logic uniform.

Validated against the square lattice, where the answer is known: square four,
pyramid four, bulky five, crossed five, rabbity six, and nothing at size seven.
"""
import sys

EMPTY, ATK, DEF = 0, 1, 2

SQ_NBRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
HEX_NBRS = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]


def lattice(kind):
    if kind == "square":
        return SQ_NBRS, (lambda c: (-c[0], c[1])), (lambda c: (-c[1], c[0])), 4, (0, 0)
    return (HEX_NBRS,
            (lambda c: (c[0], c[2], c[1])),
            (lambda c: (-c[2], -c[0], -c[1])),
            6, (0, 0, 0))


def canon(cells, refl, rot, folds):
    best = None
    for mirror in (False, True):
        cur = [refl(c) for c in cells] if mirror else list(cells)
        for _ in range(folds):
            s = sorted(cur)
            o = s[0]
            norm = tuple(sorted(tuple(a - b for a, b in zip(c, o)) for c in s))
            if best is None or norm < best:
                best = norm
            cur = [rot(c) for c in cur]
    return best


def shapes_by_size(nbrs, refl, rot, folds, maxn, origin):
    level = {canon([origin], refl, rot, folds)}
    out = {1: set(level)}
    for size in range(2, maxn + 1):
        nxt = set()
        for sh in level:
            members = set(sh)
            for c in sh:
                for d in nbrs:
                    cand = tuple(a + b for a, b in zip(c, d))
                    if cand not in members:
                        nxt.add(canon(list(sh) + [cand], refl, rot, folds))
        level = nxt
        out[size] = set(level)
    return out


class Region:
    def __init__(self, cells, nbrs):
        n = len(cells)
        self.n = n
        self.wall = n
        idx = {c: i for i, c in enumerate(cells)}
        members = set(cells)
        adj = [[] for _ in range(n + 1)]
        for c in cells:
            i = idx[c]
            for d in nbrs:
                nb = tuple(a + b for a, b in zip(c, d))
                if nb in members:
                    adj[i].append(idx[nb])
                elif self.wall not in adj[i]:
                    adj[i].append(self.wall)
                    adj[self.wall].append(i)
        self.adj = [tuple(a) for a in adj]
        self.start = tuple([EMPTY] * n + [DEF])

    def chain(self, st, start):
        colour = st[start]
        seen, stack, libs = {start}, [start], set()
        while stack:
            i = stack.pop()
            for j in self.adj[i]:
                if st[j] == colour:
                    if j not in seen:
                        seen.add(j)
                        stack.append(j)
                elif st[j] == EMPTY:
                    libs.add(j)
        return seen, libs

    def wall_dead(self, st):
        _, libs = self.chain(st, self.wall)
        return not libs

    def play(self, st, cell, colour):
        lst = list(st)
        lst[cell] = colour
        opp = ATK if colour == DEF else DEF
        captured = False
        for j in self.adj[cell]:
            if j != cell and lst[j] == opp:
                grp, libs = self.chain(tuple(lst), j)
                if not libs:
                    if self.wall in grp:
                        return tuple(lst)   # wall captured — attacker has won
                    for k in grp:
                        lst[k] = EMPTY
                    captured = True
        new = tuple(lst)
        grp, libs = self.chain(new, cell)
        if not libs and not captured:
            return None                      # suicide
        if self.wall in grp and not libs:
            return None                      # defender must not kill its own wall
        return new

    def solver(self):
        memo = {}

        def search(st, turn, passes):
            if self.wall_dead(st):
                return True
            if passes >= 2:
                return False
            key = (st, turn, passes)
            if key in memo:
                return memo[key]
            memo[key] = False                # repetition counts as defender survival
            results = []
            for cell in range(self.n):
                if st[cell] != EMPTY:
                    continue
                nxt = self.play(st, cell, turn)
                if nxt is not None:
                    results.append(search(nxt, DEF if turn == ATK else ATK, 0))
            results.append(search(st, DEF if turn == ATK else ATK, passes + 1))
            out = any(results) if turn == ATK else all(results)
            memo[key] = out
            return out

        return search

    def attacker_wins(self):
        return self.solver()(self.start, ATK, 0)

    def vital_points(self):
        """the cells the attacker must occupy: its winning first moves, or none
        when the defender cannot live even by moving first."""
        search = self.solver()
        opening = lambda cell, colour: self.play(self.start, cell, colour)
        defender_lives = any(
            (st := opening(cell, DEF)) is not None and not search(st, ATK, 0)
            for cell in range(self.n))
        if not defender_lives:
            return []
        return [cell for cell in range(self.n)
                if (st := opening(cell, ATK)) is not None and search(st, DEF, 0)]


def run(kind, maxn, verbose=False):
    nbrs, refl, rot, folds, origin = lattice(kind)
    by_size = shapes_by_size(nbrs, refl, rot, folds, maxn, origin)
    found = {}
    for size in sorted(by_size):
        nak = [sh for sh in sorted(by_size[size]) if Region(list(sh), nbrs).attacker_wins()]
        found[size] = nak
        print(f"  size {size}: {len(by_size[size]):>5} shapes, {len(nak):>3} nakade")
        if verbose:
            for sh in nak:
                print(f"      {sh}")
    return found


if __name__ == "__main__":
    kind, maxn = sys.argv[1], int(sys.argv[2])
    print(f"{kind} lattice:")
    run(kind, maxn, verbose="-v" in sys.argv)
