import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import ui, render, module
from shinywidgets import output_widget, render_widget

from utils.team_logos import build_team_styles
from utils.team_colors import TEAM_COLOR_MAP
from utils.cumulative_data import build_cumulative_pilotos, build_cumulative_construtores


def calcular_classificacao_pilotos(df: pd.DataFrame) -> pd.DataFrame:
    classificacao = df.groupby(['Driver', 'Team'])['Points'].sum().reset_index()
    classificacao = classificacao.sort_values('Points', ascending=False).reset_index(drop=True)
    classificacao.insert(0, 'Posição', range(1, len(classificacao) + 1))
    classificacao = classificacao.rename(columns={'Driver': 'Piloto', 'Team': 'Equipe', 'Points': 'Pontos'})
    return classificacao


def calcular_classificacao_construtores(df: pd.DataFrame) -> pd.DataFrame:
    classificacao = df.groupby('Team')['Points'].sum().reset_index()
    classificacao = classificacao.sort_values('Points', ascending=False).reset_index(drop=True)
    classificacao.insert(0, 'Posição', range(1, len(classificacao) + 1))
    classificacao = classificacao.rename(columns={'Team': 'Equipe', 'Points': 'Pontos'})
    return classificacao


@module.ui
def resultados_home_ui():
    return ui.div(
        ui.layout_columns(
            ui.div(
                ui.h4("Classificação de Pilotos"),
                ui.div(
                    ui.output_data_frame("tabela_classificacao"),
                    class_="tabela-classificacao",
                    style="margin-bottom: 20px;"
                ),
                ui.div(
                    output_widget("grafico_pilotos"),
                    class_="grafico-container",
                ),
            ),
            ui.div(
                ui.h4("Classificação de Construtores"),
                ui.div(
                    ui.output_data_frame("tabela_construtores"),
                    class_="tabela-classificacao",
                    style="margin-bottom: 20px;"
                ),
                ui.div(
                    output_widget("grafico_construtores"),
                    class_="grafico-container",
                ),
            ),
            col_widths=[6, 6],
        ),
        style="padding: 20px;"
    )


@module.server
def resultados_home_server(input, output, session, df):
    df_pilotos = calcular_classificacao_pilotos(df)
    df_construtores = calcular_classificacao_construtores(df)

    pilotos_styles = build_team_styles(df_pilotos, team_col_idx=2)
    construtores_styles = build_team_styles(df_construtores, team_col_idx=1)

    df_pilotos['Equipe'] = ""
    df_construtores['Equipe'] = ""

    @render.data_frame
    def tabela_classificacao():
        return render.DataGrid(
            df_pilotos,
            styles=pilotos_styles,
            summary=False,
        )

    @render.data_frame
    def tabela_construtores():
        return render.DataGrid(
            df_construtores,
            styles=construtores_styles,
            summary=False,
        )

    @render_widget
    def grafico_pilotos():
        df_cumul = build_cumulative_pilotos(df)
        ordem = df_cumul['Corrida'].unique().tolist()

        #ordena pilotos no eixo Y para o mouseover do eixo X
        ordem_pilotos = df_cumul.groupby('Piloto')['Pontos'].max().sort_values(ascending=False)
        df_cumul['Piloto'] = pd.Categorical(df_cumul['Piloto'], categories=ordem_pilotos.index, ordered=True)
        df_cumul = df_cumul.sort_values(['Piloto', 'Ordem'])

        fig = px.line(
            df_cumul,
            x='Corrida',
            y='Pontos',
            color='Equipe',
            line_group='Piloto',
            hover_name='Piloto',
            #hover_data={'Pontos': ':.0f'},
            color_discrete_map=TEAM_COLOR_MAP,
            category_orders={"Corrida": ordem, "Piloto": ordem_pilotos.index.tolist()},
            markers=True,
        )

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            margin=dict(l=10, r=50, t=80, b=10),
            hoverlabel=dict(
                bgcolor='#1f1f2b',
                bordercolor='#444',
                font=dict(color='#ffffff', size=12),
                align='left',
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color='#ffffff', size=11),
                title=None,
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(color='#ffffff', size=11),
                title=None,
                unifiedhovertitle=dict(text='<b>%{x}</b>'),
                showspikes=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.08)',
                zeroline=False,
                tickfont=dict(color='#ffffff', size=11),
                title=None,
                showspikes=False,
            ),
            dragmode='pan',
            modebar=dict(
                orientation='v',
                bgcolor='rgba(21, 21, 30, 0.85)',
                color='#ffffff',
                activecolor='#E10600',
                remove=['select2d', 'lasso2d', 'zoom2d', 'resetScale2d']
            ),
            hovermode='x unified'
        )
        fig.update_traces(
            hovertemplate='%{hovertext}  %{y:.0f}<extra></extra>'
        )

        return go.FigureWidget(fig)

    @render_widget
    def grafico_construtores():
        df_cumul = build_cumulative_construtores(df)
        ordem = df_cumul['Corrida'].unique().tolist()
        ordem_equipes = (
            df_cumul.groupby('Equipe')['Pontos']
            .max()
            .sort_values(ascending=False)
            .index
            .tolist()
        )
        df_cumul['Equipe'] = pd.Categorical(
            df_cumul['Equipe'],
            categories=ordem_equipes,
            ordered=True,
        )
        df_cumul = df_cumul.sort_values(['Equipe', 'Ordem'])

        fig = px.line(
            df_cumul,
            x='Corrida',
            y='Pontos',
            color='Equipe',
            hover_name='Equipe',
            color_discrete_map=TEAM_COLOR_MAP,
            category_orders={"Corrida": ordem, "Equipe": ordem_equipes},
            markers=True,
        )

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            margin=dict(l=10, r=50, t=70, b=10),
            hoverlabel=dict(
                bgcolor='#1f1f2b',
                bordercolor='#444',
                font=dict(color='#ffffff', size=12),
                align='left',
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color='#ffffff', size=11),
                title=None,
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(color='#ffffff', size=11),
                title=None,
                unifiedhovertitle=dict(text='<b>%{x}</b>'),
                showspikes=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.08)',
                zeroline=False,
                tickfont=dict(color='#ffffff', size=11),
                title=None,
                showspikes=False,
            ),
            dragmode='pan',
            modebar=dict(
                orientation='v',
                bgcolor='rgba(21, 21, 30, 0.85)',
                color='#ffffff',
                activecolor='#E10600',
                remove=['select2d', 'lasso2d', 'zoom2d', 'resetScale2d'],
            ),
            hovermode='x unified',
        )
        fig.update_traces(
            hovertemplate='%{hovertext}  %{y:.0f}<extra></extra>'
        )
        return go.FigureWidget(fig)
