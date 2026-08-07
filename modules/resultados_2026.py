import pandas as pd
from shiny import ui, render, module, reactive
from utils.team_logos import build_team_styles


@module.ui
def resultados_2026_ui(tracks=None):
    choices = tracks if tracks else ["Carregando..."]
    return ui.div(
        ui.h2("Resultados - Temporada 2026"),
        
        ui.input_select(
            "selecionar_corrida",
            label="Selecione a Corrida:",
            choices=choices,
            selected=choices[0] if choices else None,
            selectize=True 
        ),
        
        ui.div(
            ui.output_data_frame("tabela_resultados"),
            class_="tabela-classificacao",       # ← coluna Position estreita
        ),
        style="padding: 20px;"
    )


@module.server
def resultados_2026_server(input, output, session, df):
    
    @reactive.calc
    def df_filtrado():
        track_selecionado = input.selecionar_corrida()
        if track_selecionado and track_selecionado != "Carregando...":
            df_filt = df[df['Track'] == track_selecionado].copy()
            return df_filt.drop(columns=['Track']).rename(columns={
                'Position': 'Posição', 'No': 'Nº', 'Driver': 'Piloto',
                'Team': 'Equipe', 'Starting Grid': 'Grid', 'Laps': 'Voltas',
                'Time/Retired': 'Tempo', 'Points': 'Pontos',
                'Set Fastest Lap': 'Volta Mais Rápida', 'Fastest Lap Time': 'Tempo Volta',
            })
        return df.drop(columns=['Track']).rename(columns={
            'Position': 'Posição', 'No': 'Nº', 'Driver': 'Piloto',
            'Team': 'Equipe', 'Starting Grid': 'Grid', 'Laps': 'Voltas',
            'Time/Retired': 'Tempo', 'Points': 'Pontos',
            'Set Fastest Lap': 'Volta Mais Rápida', 'Fastest Lap Time': 'Tempo Volta',
        })
    
    @render.data_frame
    def tabela_resultados():
        df_atual = df_filtrado().copy()          # ← .copy() evita mutação do cache
        
        # Logos na coluna Equipe (índice 3 após renomear)
        team_styles = build_team_styles(df_atual, team_col_idx=3)
        
        # Coluna Position estreita (índice 0)
        narrow_pos = [{
            "cols": [0],
            "style": {
                "text-align": "center",
            },
        }]
        
        styles = narrow_pos + team_styles
        
        # Zera nome do time (logo entra via CSS background-image)
        df_atual['Equipe'] = ""
        
        return render.DataGrid(
            df_atual,
            styles=styles,
            summary=False,
        )