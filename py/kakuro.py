# Kakuro puzzle solver modeled after sudoku.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
import itertools
import random

Cell = Tuple[int, int]

@dataclass(frozen=True)
class Run:
    cells: Tuple[Cell, ...]
    total: int


def _combos(length: int, total: int) -> List[Tuple[int, ...]]:
    """All permutations of digits 1..9, length `length`, no repeats, summing to `total`."""
    digits = range(1, 10)
    return [c for c in itertools.permutations(digits, length)
            if sum(c) == total and len(set(c)) == length]


def _propagate(values: Dict[Cell, Set[int]],
               run_candidates: Dict[Run, List[Tuple[int, ...]]]) -> Optional[Dict[Cell, Set[int]]]:
    """Propagate constraints between cells and runs."""
    changed = True
    while changed:
        changed = False
        for run in list(run_candidates):
            candidates = run_candidates[run]
            candidates = [cand for cand in candidates
                           if all(cand[i] in values[run.cells[i]] for i in range(len(run.cells)))]
            if not candidates:
                return None
            if len(candidates) != len(run_candidates[run]):
                run_candidates[run] = candidates
                changed = True
            for i, cell in enumerate(run.cells):
                allowed = {cand[i] for cand in candidates}
                new_vals = values[cell] & allowed
                if not new_vals:
                    return None
                if new_vals != values[cell]:
                    values[cell] = new_vals
                    changed = True
    return values


def _search(values: Dict[Cell, Set[int]],
            run_candidates: Dict[Run, List[Tuple[int, ...]]]) -> Optional[Dict[Cell, int]]:
    values = _propagate(values, run_candidates)
    if values is None:
        return None
    if all(len(v) == 1 for v in values.values()):
        return {c: next(iter(v)) for c, v in values.items()}
    cell = min((c for c in values if len(values[c]) > 1), key=lambda c: len(values[c]))
    for val in list(values[cell]):
        new_values = {c: set(v) for c, v in values.items()}
        new_run_cands = {r: list(c) for r, c in run_candidates.items()}
        new_values[cell] = {val}
        result = _search(new_values, new_run_cands)
        if result:
            return result
    return None


def solve_kakuro(runs: List[Run]) -> Optional[Dict[Cell, int]]:
    """Solve a Kakuro puzzle described by a list of runs."""
    cells = {c for run in runs for c in run.cells}
    values = {c: set(range(1, 10)) for c in cells}
    run_candidates = {run: _combos(len(run.cells), run.total) for run in runs}
    return _search(values, run_candidates)


# Simple example puzzle utilities -------------------------------------------

def generate_example_puzzle() -> Tuple[List[Run], Dict[Cell, int]]:
    """Generate a tiny 2x2 Kakuro puzzle and its solution."""
    solution = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
    runs = [
        Run(((1, 1), (1, 2)), 3),
        Run(((2, 1), (2, 2)), 7),
        Run(((1, 1), (2, 1)), 4),
        Run(((1, 2), (2, 2)), 6),
    ]
    return runs, solution


def random_solution(n: int = 2) -> Dict[Cell, int]:
    """Return a random n x n grid of digits 1..9."""
    return {(r, c): random.randint(1, 9) for r in range(1, n + 1) for c in range(1, n + 1)}


__all__ = ['Run', 'solve_kakuro', 'generate_example_puzzle', 'random_solution']
