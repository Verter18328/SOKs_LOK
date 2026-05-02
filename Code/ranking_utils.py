"""Logika sortowania wierszy tabeli wyników (serie / klasyfikacja).

Kolumny wiersza: ``[nr_serii, strzał_1, …, strzał_N, razem]``.

Przy sortowaniu klasyfikacji (``by_ranking=True``) używany jest klucz:
``(suma, strzał_1, strzał_2, …)`` w kolejności malejącej — po posortowaniu
strzałów malejąco w wierszu jest to równoważne regule „więcej dziesiątek,
potem dziewiątek…”.

Pełny remis (identyczny klucz): kolejność względna nie jest gwarantowana;
jawne ``ex aequo`` w UI zaplanowane są na wersję 1.0.
"""


def _nr_serii_key(texts: list[str]) -> int:
    s = texts[0].strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def _suma_key(texts: list[str], total_col: int) -> int:
    s = texts[total_col].strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def _strzaly_tuple(texts: list[str], total_col: int) -> tuple[int, ...]:
    out: list[int] = []
    for c in range(1, total_col):
        s = texts[c].strip()
        out.append(int(s) if s.isdigit() else -1)
    return tuple(out)


def _ranking_key(texts: list[str], total_col: int) -> tuple[int, ...]:
    return (_suma_key(texts, total_col),) + _strzaly_tuple(texts, total_col)


def sort_wyniki_grid(grid: list[list[str]], *, by_ranking: bool) -> list[list[str]]:
    """Zwraca nową listę wierszy posortowaną wg trybu.

    - ``by_ranking=False``: rosnąco po numerze serii (kolumna 0).
    - ``by_ranking=True``: malejąco po sumie i strzałach (tie-break).
    """
    if len(grid) < 2:
        return [row[:] for row in grid]
    cols = len(grid[0])
    if cols < 2:
        return [row[:] for row in grid]

    total_col = cols - 1
    out = [row[:] for row in grid]

    if by_ranking:
        out.sort(key=lambda t: _ranking_key(t, total_col), reverse=True)
    else:
        out.sort(key=_nr_serii_key)

    return out
