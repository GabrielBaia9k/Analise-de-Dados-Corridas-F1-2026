"""
Placares head-to-head entre os dois pilotos principais de cada equipe.
"""

import pandas as pd

NAO_FINALIZOU = {'DNF', 'DNS', 'DSQ', 'RET'}


def build_h2h(df: pd.DataFrame, sessao: str) -> tuple[pd.DataFrame, dict]:
    """
    Calcula o placar H2H entre os dois pilotos principais de cada equipe.

    Args:
        df: DataFrame da sessão com colunas Track, Driver, Team, Position
            (e Points, Starting Grid, Time/Retired, Set Fastest Lap quando
            a sessão possuir essas colunas).
        sessao: 'corridas' | 'sprint' | 'qualy' | 'sprint_qualy'.

    Returns:
        placar: DataFrame com colunas Equipe, Piloto A, Piloto B,
            Vit A, Vit B, Empates, Eventos.
        detalhes: dict equipe -> dict com estatísticas detalhadas por
            piloto e a lista de métricas para exibição lado a lado.
    """
    dados = df.copy()
    dados['Position'] = pd.to_numeric(dados['Position'], errors='coerce')
    tem_pontos = 'Points' in dados.columns
    if tem_pontos:
        dados['Points'] = pd.to_numeric(dados['Points'], errors='coerce').fillna(0)
    tem_grid = 'Starting Grid' in dados.columns
    if tem_grid:
        dados['Starting Grid'] = pd.to_numeric(dados['Starting Grid'], errors='coerce')
    tem_tempo = 'Time/Retired' in dados.columns
    tem_fl = 'Set Fastest Lap' in dados.columns

    sessao_corrida = sessao in ('corridas', 'sprint')

    if sessao_corrida:
        metricas = [
            {'key': 'vitorias', 'label': 'Vitórias no duelo', 'invert': False},
            {'key': 'pct_vitorias', 'label': '% do duelo', 'invert': False},
            {'key': 'pontos', 'label': 'Pontos', 'invert': False},
            {'key': 'podios', 'label': 'Pódios', 'invert': False},
            {'key': 'media_pos', 'label': 'Média de posição', 'invert': True},
            {'key': 'melhor_pos', 'label': 'Melhor posição', 'invert': True},
            {'key': 'vitorias_corridas', 'label': 'Vitórias', 'invert': False},
            {'key': 'media_grid', 'label': 'Média de grid', 'invert': True},
            {'key': 'dnf', 'label': 'Abandonos', 'invert': True},
        ]
        if tem_fl:
            metricas.append(
                {'key': 'voltas_rapidas', 'label': 'Voltas rápidas', 'invert': False}
            )
    else:
        metricas = [
            {'key': 'vitorias', 'label': 'Vitórias no duelo', 'invert': False},
            {'key': 'pct_vitorias', 'label': '% do duelo', 'invert': False},
            {'key': 'media_pos', 'label': 'Média de posição', 'invert': True},
            {'key': 'melhor_pos', 'label': 'Melhor posição', 'invert': True},
            {'key': 'poles', 'label': 'Poles', 'invert': False},
            {'key': 'primeira_fila', 'label': 'Largadas na 1ª fila', 'invert': False},
            {'key': 'q3', 'label': 'Presenças em Q3', 'invert': False},
        ]

    linhas_placar = []
    detalhes: dict[str, dict] = {}

    for equipe, grupo in dados.groupby('Team', sort=False):
        pilotos = (
            grupo.groupby('Driver')['Track']
            .nunique()
            .sort_values(ascending=False)
        )
        if len(pilotos) < 2:
            continue

        piloto_a, piloto_b = pilotos.index[:2]
        pos_a = grupo[grupo['Driver'] == piloto_a].set_index('Track')['Position']
        pos_b = grupo[grupo['Driver'] == piloto_b].set_index('Track')['Position']

        eventos = sorted(set(pos_a.dropna().index) & set(pos_b.dropna().index))
        vit_a = vit_b = empates = 0
        for evento in eventos:
            pa, pb = pos_a[evento], pos_b[evento]
            if pa < pb:
                vit_a += 1
            elif pb < pa:
                vit_b += 1
            else:
                empates += 1

        def _stats(nome: str, pos: pd.Series, vitorias: int, derrotas: int) -> dict:
            linha = grupo[grupo['Driver'] == nome]
            serie = pos.dropna()
            stats = {
                'nome': nome,
                'vitorias': vitorias,
                'derrotas': derrotas,
                'empates': empates,
                'pct_vitorias': round(vitorias / len(eventos) * 100) if eventos else None,
                'media_pos': round(float(serie.mean()), 2) if len(serie) else None,
                'melhor_pos': int(serie.min()) if len(serie) else None,
            }
            if sessao_corrida:
                stats['podios'] = int((serie <= 3).sum())
                stats['vitorias_corridas'] = int((serie == 1).sum())
                if tem_pontos:
                    stats['pontos'] = int(
                        linha.groupby('Track')['Points'].sum().sum()
                    )
                if tem_grid:
                    grid = linha.set_index('Track')['Starting Grid'].dropna()
                    stats['media_grid'] = (
                        round(float(grid.mean()), 2) if len(grid) else None
                    )
                if tem_tempo:
                    tempo = (
                        linha.set_index('Track')['Time/Retired']
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )
                    stats['dnf'] = int(tempo.isin(NAO_FINALIZOU).sum())
                if tem_fl:
                    fl = (
                        linha.set_index('Track')['Set Fastest Lap']
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )
                    stats['voltas_rapidas'] = int((fl == 'YES').sum())
            else:
                stats['poles'] = int((serie == 1).sum())
                stats['primeira_fila'] = int((serie <= 2).sum())
                stats['q3'] = int((serie <= 10).sum())
            return stats

        stats_a = _stats(piloto_a, pos_a, vit_a, vit_b)
        stats_b = _stats(piloto_b, pos_b, vit_b, vit_a)

        linhas_placar.append({
            'Equipe': equipe,
            'Piloto A': piloto_a,
            'Piloto B': piloto_b,
            'Vit A': vit_a,
            'Vit B': vit_b,
            'Empates': empates,
            'Eventos': len(eventos),
        })

        detalhes[equipe] = {
            'sessao': sessao,
            'pilotos': [stats_a, stats_b],
            'metricas': metricas,
        }

    return pd.DataFrame(linhas_placar), detalhes
