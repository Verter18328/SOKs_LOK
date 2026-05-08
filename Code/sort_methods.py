"""Logika sortowania wierszy tabeli wyników (serie / klasyfikacja)."""


class WynikiSorter:
    """Sortowanie tabeli wyników w trybie serii lub klasyfikacji."""

    def _nr_serii_key(self, texts: list[str]) -> int:
        s = texts[0].strip()
        if not s:
            return 0
        try:
            return int(s)
        except ValueError:
            return 0

    def _suma_key(self, texts: list[str], total_col: int) -> int:
        s = texts[total_col].strip()
        if not s:
            return 0
        try:
            return int(s)
        except ValueError:
            return 0

    def _strzaly_tuple(self, texts: list[str], total_col: int) -> tuple[int, ...]:
        out: list[int] = []
        for c in range(1, total_col):
            s = texts[c].strip()
            out.append(int(s) if s.isdigit() else -1)
        return tuple(out)

    def _ranking_key(self, texts: list[str], total_col: int) -> tuple[int, ...]:
        return (self._suma_key(texts, total_col),) + self._strzaly_tuple(texts, total_col)

    def sort_wyniki_grid(self, grid: list[list[str]], *, by_ranking: bool) -> list[list[str]]:
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
            out.sort(key=lambda t: self._ranking_key(t, total_col), reverse=True)
        else:
            out.sort(key=self._nr_serii_key)

        return out
