# Historia zmian

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/).
Projekt stosuje [Semantic Versioning](https://semver.org/lang/pl/).

## [1.0.0] — 2026-06-18

Pierwszy stabilny release po testach terenowych na zawodach strzeleckich.

### Dodano

- Pełny workflow operatora: zawody, konkurencje, zawodnicy, serie, wyniki, ranking.
- Ekran wyników na drugim monitorze (TV/HDMI) z cyklicznym odświeżaniem.
- Edycja i usuwanie zawodów, zawodników oraz serii (menu kontekstowe).
- Lokalna baza SQLite z relacjami i kaskadowym usuwaniem (`ON DELETE CASCADE`).
- Licencja własnościowa ([`LICENSE`](LICENSE)) oraz noty komponentów zewnętrznych ([`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)).
- Przebudowana dokumentacja projektu ([`README.md`](README.md)).

### Usunięto

- Nieużywane szablony tabel UI (martwy kod).

### Znane ograniczenia

- Brak formalnego zamknięcia zawodów w aplikacji.
- Brak druku i eksportu wyników.
- Brak wyszukiwania zawodów po nazwie i dacie.

### Uwagi

- Pakiet Windows (PyInstaller) nie jest podpisany certyfikatem wydawcy. Przy pierwszym
  uruchomieniu Windows Defender lub SmartScreen może wydłużyć start albo wyświetlić
  ostrzeżenie — patrz sekcja „Antywirus i pierwsze uruchomienie” w [`README.md`](README.md).

[1.0.0]: https://github.com/Verter18328/SOKs_LOK/releases/tag/v1.0.0
