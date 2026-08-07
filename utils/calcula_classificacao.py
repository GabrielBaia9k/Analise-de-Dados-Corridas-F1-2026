"""Gera classificacoes historicas de pilotos e equipes.

As classificacoes sao calculadas ao final de cada Grande Premio. Os pontos
incluem a corrida e a Sprint do mesmo evento, quando existir. O desempate usa
as posicoes das corridas e, se necessario, as posicoes de qualifying.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


TEAM_ALIASES = {
    "Racing Bulls": "Racing Bulls Red Bull Ford",
    "Alpine Renault": "Alpine Mercedes",
    "Astom Martin Honda": "Aston Martin Honda",
}

TRACK_ALIASES = {
    "Asutria": "Austria",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def _normalise_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    normalised = []
    for row in rows:
        item = dict(row)
        item["Track"] = TRACK_ALIASES.get(item.get("Track", "").strip(), item.get("Track", "").strip())
        item["Team"] = TEAM_ALIASES.get(item.get("Team", "").strip(), item.get("Team", "").strip())
        item["Driver"] = item.get("Driver", "").strip()
        normalised.append(item)
    return normalised


def _integer(value: str | None) -> int | None:
    try:
        number = int(str(value or "").strip())
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _points(value: str | None) -> Decimal:
    try:
        return Decimal(str(value or "0").strip())
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _format_decimal(value: Decimal) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _track_order(rows: Iterable[dict[str, str]]) -> list[str]:
    order = []
    for row in rows:
        track = row["Track"]
        if track not in order:
            order.append(track)
    return order


def _position_counts(rows: Iterable[dict[str, str]], key: str) -> tuple[defaultdict[str, Counter], int]:
    counts: defaultdict[str, Counter] = defaultdict(Counter)
    max_position = 0
    for row in rows:
        entity = row.get(key, "")
        position = _integer(row.get("Position"))
        if not entity or position is None:
            continue
        counts[entity][position] += 1
        max_position = max(max_position, position)
    return counts, max_position


def _sort_entities(
    entities: Iterable[str],
    points: dict[str, Decimal],
    race_counts: defaultdict[str, Counter],
    qualifying_counts: defaultdict[str, Counter],
    max_race_position: int,
    max_qualifying_position: int,
    source_order: dict[str, int],
) -> list[str]:
    def sort_key(entity: str) -> tuple:
        return (
            points.get(entity, Decimal("0")),
            *(race_counts[entity][position] for position in range(1, max_race_position + 1)),
            *(qualifying_counts[entity][position] for position in range(1, max_qualifying_position + 1)),
            -source_order[entity],
        )

    return sorted(entities, key=sort_key, reverse=True)


def _classification_row(
    tipo: str,
    ordem: int,
    corrida: str,
    posicao: int,
    competidor: str,
    piloto: str,
    equipe: str,
    points: Decimal,
    race_counts: Counter,
    qualifying_counts: Counter,
    max_race_position: int,
    max_qualifying_position: int,
) -> dict[str, str | int]:
    row: dict[str, str | int] = {
        "Tipo": tipo,
        "Ordem": ordem,
        "Corrida": corrida,
        "Posição": posicao,
        "Competidor": competidor,
        "Piloto": piloto,
        "Equipe": equipe,
        "Pontos": _format_decimal(points),
    }
    row.update({
        f"Corrida_P{position}": race_counts[position]
        for position in range(1, max_race_position + 1)
    })
    row.update({
        f"Qualy_P{position}": qualifying_counts[position]
        for position in range(1, max_qualifying_position + 1)
    })
    return row


def gerar_tabela_classificacao(
    race_path: str | Path,
    sprint_path: str | Path,
    qualifying_path: str | Path,
) -> tuple[list[dict[str, str | int]], list[str]]:
    """Gera uma tabela longa com a classificacao de cada corrida.

    A tabela contem uma linha por piloto e por equipe em cada corrida. Os
    campos ``Corrida_Pn`` e ``Qualy_Pn`` preservam os criterios usados no
    desempate e tornam a tabela auditavel para usos futuros.
    """
    race_rows = _normalise_rows(_read_csv(Path(race_path)))
    sprint_rows = _normalise_rows(_read_csv(Path(sprint_path)))
    qualifying_rows = _normalise_rows(_read_csv(Path(qualifying_path)))

    tracks = _track_order(race_rows)
    for track in _track_order(sprint_rows):
        if track not in tracks:
            tracks.append(track)

    race_by_track: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    sprint_by_track: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    qualifying_by_track: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in race_rows:
        race_by_track[row["Track"]].append(row)
    for row in sprint_rows:
        sprint_by_track[row["Track"]].append(row)
    for row in qualifying_rows:
        qualifying_by_track[row["Track"]].append(row)

    driver_order: dict[str, int] = {}
    team_order: dict[str, int] = {}
    for row in race_rows + sprint_rows:
        driver_order.setdefault(row["Driver"], len(driver_order))
        team_order.setdefault(row["Team"], len(team_order))

    race_driver_counts, max_race_position = _position_counts(race_rows, "Driver")
    race_team_counts, _ = _position_counts(race_rows, "Team")
    qualifying_driver_counts, max_qualifying_position = _position_counts(qualifying_rows, "Driver")
    qualifying_team_counts, _ = _position_counts(qualifying_rows, "Team")

    driver_points: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    team_points: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    cumulative_race_driver: defaultdict[str, Counter] = defaultdict(Counter)
    cumulative_race_team: defaultdict[str, Counter] = defaultdict(Counter)
    cumulative_qualifying_driver: defaultdict[str, Counter] = defaultdict(Counter)
    cumulative_qualifying_team: defaultdict[str, Counter] = defaultdict(Counter)
    current_team: dict[str, str] = {}
    seen_drivers: list[str] = []
    seen_teams: list[str] = []
    output: list[dict[str, str | int]] = []

    for ordem, corrida in enumerate(tracks, start=1):
        event_rows = race_by_track[corrida] + sprint_by_track[corrida]
        for row in event_rows:
            driver = row["Driver"]
            team = row["Team"]
            current_team[driver] = team
            if driver not in seen_drivers:
                seen_drivers.append(driver)
            if team not in seen_teams:
                seen_teams.append(team)
            points = _points(row.get("Points"))
            driver_points[driver] += points
            team_points[team] += points

        for row in race_by_track[corrida]:
            driver = row["Driver"]
            team = row["Team"]
            position = _integer(row.get("Position"))
            if position is not None:
                cumulative_race_driver[driver][position] += 1
                cumulative_race_team[team][position] += 1

        for row in qualifying_by_track[corrida]:
            driver = row["Driver"]
            team = row["Team"]
            position = _integer(row.get("Position"))
            if position is not None:
                cumulative_qualifying_driver[driver][position] += 1
                cumulative_qualifying_team[team][position] += 1

        ordered_drivers = _sort_entities(
            seen_drivers,
            driver_points,
            cumulative_race_driver,
            cumulative_qualifying_driver,
            max_race_position,
            max_qualifying_position,
            driver_order,
        )
        ordered_teams = _sort_entities(
            seen_teams,
            team_points,
            cumulative_race_team,
            cumulative_qualifying_team,
            max_race_position,
            max_qualifying_position,
            team_order,
        )

        for posicao, driver in enumerate(ordered_drivers, start=1):
            output.append(_classification_row(
                "Piloto",
                ordem,
                corrida,
                posicao,
                driver,
                driver,
                current_team.get(driver, ""),
                driver_points[driver],
                cumulative_race_driver[driver],
                cumulative_qualifying_driver[driver],
                max_race_position,
                max_qualifying_position,
            ))

        for posicao, team in enumerate(ordered_teams, start=1):
            output.append(_classification_row(
                "Equipe",
                ordem,
                corrida,
                posicao,
                team,
                "",
                team,
                team_points[team],
                cumulative_race_team[team],
                cumulative_qualifying_team[team],
                max_race_position,
                max_qualifying_position,
            ))

    fieldnames = [
        "Tipo",
        "Ordem",
        "Corrida",
        "Posição",
        "Competidor",
        "Piloto",
        "Equipe",
        "Pontos",
        *(f"Corrida_P{position}" for position in range(1, max_race_position + 1)),
        *(f"Qualy_P{position}" for position in range(1, max_qualifying_position + 1)),
    ]
    return output, fieldnames


def salvar_tabela_classificacao(
    output_path: str | Path,
    race_path: str | Path,
    sprint_path: str | Path,
    qualifying_path: str | Path,
) -> Path:
    """Gera e salva a tabela de classificacao em CSV."""
    rows, fieldnames = gerar_tabela_classificacao(
        race_path,
        sprint_path,
        qualifying_path,
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return destination


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    output_path = project_root / "Dados Gerados" / "tabela_de_classificacao.csv"
    destination = salvar_tabela_classificacao(
        output_path,
        data_dir / "Formula1_2026Season_RaceResults.csv",
        data_dir / "Formula1_2026Season_SprintResults.csv",
        data_dir / "Formula1_2026Season_QualifyingResults.csv",
    )
    print(f"Tabela gerada: {destination}")


if __name__ == "__main__":
    main()
