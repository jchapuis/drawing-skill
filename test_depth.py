#!/usr/bin/env python3
"""The depth gate, checked in both directions.

A gate nobody has seen fail is not a gate. Three of the checks here have at
some point reported clean over a drawing that was wrong, so this one is held
against a document known to be correct and one known to be broken, and has to
tell them apart.

    python3 test_depth.py
"""
import sys

from check import depth

INVENTORY = {
    "a/b": {"in_front": "b"},   # b is in front, so a's ink must precede b's fill
    "c/d": {"in_front": "d"},
}


def mark(stage, tag):
    return {"op": "stroke", "stage": stage, "tag": tag, "points": []}


def main():
    right = [mark("fill", "a"), mark("ink", "a"), mark("fill", "b"), mark("ink", "b"),
             mark("fill", "c"), mark("ink", "c"), mark("fill", "d"), mark("ink", "d")]
    hits, unresolved, rows = depth(right, INVENTORY)
    assert rows == 2 and not hits and not unresolved, (hits, unresolved, rows)

    # stage-major: every fill, then every ink. a's outline lands on b's colour.
    wrong = [mark("fill", "a"), mark("fill", "b"), mark("ink", "a"), mark("ink", "b"),
             mark("fill", "c"), mark("ink", "c"), mark("fill", "d"), mark("ink", "d")]
    hits, unresolved, _ = depth(wrong, INVENTORY)
    assert [hit[0] for hit in hits] == ["a/b"] and not unresolved, (hits, unresolved)

    # a pair the tags never name goes UNRESOLVED, never silently clean
    hits, unresolved, _ = depth(right[:4], INVENTORY)
    assert not hits and [row[0] for row in unresolved] == ["c/d"], (hits, unresolved)

    # a '+'-joined tag and a dotted child both still belong to their object
    shared = [mark("fill", "a"), mark("ink", "a.rim+ground"),
              mark("fill", "b"), mark("ink", "b"),
              mark("fill", "c"), mark("ink", "c"), mark("fill", "d"), mark("ink", "d")]
    hits, unresolved, _ = depth(shared, INVENTORY)
    assert not hits and not unresolved, (hits, unresolved)

    # an ink-only near form (a cable) covers with its first ink
    cable = {"frame/cable": {"in_front": "cable"}}
    hits, unresolved, _ = depth([mark("fill", "frame"), mark("ink", "frame"), mark("ink", "cable")], cable)
    assert not hits and not unresolved, (hits, unresolved)
    hits, _, _ = depth([mark("ink", "cable"), mark("fill", "frame"), mark("ink", "frame")], cable)
    assert [hit[0] for hit in hits] == ["frame/cable"], hits

    # before any ink (S2) the flats are ordered: the far flat after the near one fails
    hits, unresolved, _ = depth([mark("fill", "b"), mark("fill", "a")], {"a/b": {"in_front": "b"}})
    assert [hit[0] for hit in hits] == ["a/b"] and not unresolved, (hits, unresolved)

    # a sub-form with a row of its own opts out of its parent's rows: a hub nut
    # written after the bike's fork is decided by its own row, not the wheel's
    nut = {"wheel/bike.fork": {"in_front": "bike.fork"},
           "wheel/bike.tube": {"in_front": "bike.tube"},
           "bike.fork/wheel.nut": {"in_front": "wheel.nut"}}
    ops = [mark("fill", "wheel"), mark("ink", "wheel"), mark("fill", "bike.fork"), mark("ink", "bike.fork"),
           mark("fill", "bike.tube"), mark("ink", "bike.tube"), mark("fill", "wheel.nut"), mark("ink", "wheel.nut")]
    hits, unresolved, _ = depth(ops, nut)
    assert not hits and not unresolved, (hits, unresolved)

    print("depth: right order passes, stage-major order fails, "
          "an unnamed pair is UNRESOLVED, tags resolve through '+' and '.', "
          "ink-only near forms and S2 flats are ordered, a sub-form's own row wins")


if __name__ == "__main__":
    sys.exit(main())
