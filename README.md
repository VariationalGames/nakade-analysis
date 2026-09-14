# nakade-analysis

Enumerates the single-eye (nakade) eyespace shapes on the hex and square lattices, and renders them
as charts. This is the code and raw data behind the single-eye shapes of
[Badux](https://www.baduxgo.com/), Go on a hex board. Research tooling, not engine code.

| File                            | What it is                                                                 |
| ------------------------------- | -------------------------------------------------------------------------- |
| `nakade.py`                     | The solver and shape enumerator. Lattice-parameterised: `hex` or `square`.  |
| `vital.py`                      | Annotates a shape JSON file with each shape's vital points.                 |
| `chart2.py`                     | Renders a shape JSON file as a chart. Handles both lattices.                |
| `prune2.py`                     | Checks the growth rule against known results.                               |
| `monotone.py`                   | Tests whether monotonicity holds on a lattice. It does not, on either.      |
| `polyhex.py`                    | Counts free polyhexes and polyominoes by size.                              |
| `single-eye-shapes-badux.json`  | The 21 hex shapes with their vital points. Chart input.                     |
| `single-eye-shapes-go.json`     | The 9 square shapes with their vital points. Chart input.                   |
| `hex-results.txt`               | Hex, exhaustive to size 8, with every shape listed.                         |
| `square-results.txt`            | Square, exhaustive to size 9.                                               |
| `hex-size9-verification.txt`    | Hex size 9 exhaustive: all 6,572 shapes, none single-eye.                   |

## Setup

Only the chart needs a dependency. Matplotlib is not installed system-wide, so use a venv:

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Running it

```
python3 nakade.py square 7 -v     # reproduces the textbook five, and the empty size 7
python3 nakade.py hex 8 -v        # the 21 Badux shapes
```

**Always re-run the square case after touching the solver.** It is the only check that the rules
are implemented correctly: the square lattice has a published answer — the square four and pyramid
four at size 4, the bulky five and crossed five at size 5, the rabbity six at size 6, nothing at
size 7 — and the solver reproducing it is the entire basis for believing the hex numbers.

## The shape files and the charts

`single-eye-shapes-{badux,go}.json` are size-keyed maps of `{"cells", "vital"}` records, one shape
per line. `vital.py` fills in the vital points from the solver — the attacker's winning first moves,
or none when the defender cannot live even by moving first (the square four). Re-run it after
touching the solver, then re-render the charts:

```
python3 vital.py hex single-eye-shapes-badux.json
python3 vital.py square single-eye-shapes-go.json
venv/bin/python chart2.py single-eye-shapes-badux.json hex single-eye-shapes-badux.png \
    "The single-eye shapes of Badux" \
    "21 eyespaces that cannot be made to yield two eyes when the opponent moves first — the enclosed group dies. Rows are eyespace size."
venv/bin/python chart2.py single-eye-shapes-go.json square single-eye-shapes-go.png \
    "The single-eye shapes of Go" \
    "9 eyespaces that cannot be made to yield two eyes when the opponent moves first — the enclosed group dies. Rows are eyespace size."
```

The rendered PNGs are not checked in.

## Results

| Lattice | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | total |
| ------- | -:| -:| -:| -:| -:| -:| -:| -:| -:| -----:|
| Hex     | 1 | 1 | 3 | 3 | 4 | 5 | 3 | 1 | 0 |    21 |
| Square  | 1 | 1 | 2 | 2 | 2 | 1 | 0 | 0 | 0 |     9 |

Both rows are exhaustive to size 9. Sizes 8 and 9 take a while — size 9 hex is 6,572 shapes and ran
for roughly an hour.

## License

[Apache License 2.0](LICENSE).
