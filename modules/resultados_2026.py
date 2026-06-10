import pandas as pd
from shiny import ui, render, module, reactive


@module.ui
def resultados_2026_ui(tracks=None):
    # Usa tracks reais se disponíveis, senão fallback
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
        
        ui.output_data_frame("tabela_resultados"),
        style="padding: 20px;"
    )


@module.server
def resultados_2026_server(input, output, session, df):
    
    @reactive.calc
    def df_filtrado():
        track_selecionado = input.selecionar_corrida()
        if track_selecionado and track_selecionado != "Carregando...":
            df_filt = df[df['Track'] == track_selecionado].copy()
            return df_filt.drop(columns=['Track'])
        return df.drop(columns=['Track'])
    
    @render.data_frame
    def tabela_resultados():
        return df_filtrado()