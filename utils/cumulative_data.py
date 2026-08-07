"""
Constrói DataFrames com pontuação acumulada ao longo das corridas.
"""
import pandas as pd


def build_cumulative_pilotos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna DataFrame com colunas: Corrida, Piloto, Equipe, Pontos, Ordem
    Pontos = soma acumulada corrida a corrida por piloto.
    """
    df_sum = df.groupby(['Track', 'Driver', 'Team'])['Points'].sum().reset_index()

    # Ordem cronológica das corridas
    tracks_order = list(dict.fromkeys(df['Track']))
    track_to_order = {t: i for i, t in enumerate(tracks_order)}
    df_sum['Ordem'] = df_sum['Track'].map(track_to_order)

    df_sum = df_sum.sort_values(['Driver', 'Ordem'])
    df_sum['Pontos'] = df_sum.groupby('Driver')['Points'].cumsum()

    return df_sum.rename(columns={
        'Track': 'Corrida', 'Driver': 'Piloto', 'Team': 'Equipe'
    })


def build_cumulative_construtores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna DataFrame com colunas: Corrida, Equipe, Pontos, Ordem
    Pontos = soma acumulada corrida a corrida por equipe.
    """
    df_sum = df.groupby(['Track', 'Team'])['Points'].sum().reset_index()

    tracks_order = list(dict.fromkeys(df['Track']))
    track_to_order = {t: i for i, t in enumerate(tracks_order)}
    df_sum['Ordem'] = df_sum['Track'].map(track_to_order)

    df_sum = df_sum.sort_values(['Team', 'Ordem'])
    df_sum['Pontos'] = df_sum.groupby('Team')['Points'].cumsum()

    return df_sum.rename(columns={'Track': 'Corrida', 'Team': 'Equipe'})