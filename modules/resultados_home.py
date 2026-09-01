import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import ui, render, module, reactive
from shinywidgets import output_widget, render_widget

from utils.team_logos import TEAM_LOGO_MAP, LOGO_DIR, build_team_styles
from utils.team_colors import TEAM_COLOR_MAP
from utils.cumulative_data import build_cumulative_construtores
from utils.head_to_head import build_h2h
from utils.country_flags import build_flag_path
from utils.driver_headshots import headshot_src
from utils.circuit_layouts import layout_src, proxima_corrida, TOTAL_CORRIDAS


#todo: remover a função de clareamento de cor (usar alternativa nativa ao plotly se possível)
def _clarear_cor(cor: str, fator: float = 0.45) -> str:
    """Clareia uma cor hex misturando com branco."""
    cor = cor.lstrip('#')
    if len(cor) != 6:
        return '#ffffff'
    r, g, b = (int(cor[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * fator)
    g = int(g + (255 - g) * fator)
    b = int(b + (255 - b) * fator)
    return f'#{r:02x}{g:02x}{b:02x}'


def obter_classificacao_pilotos(df_tabela: pd.DataFrame) -> pd.DataFrame:
    ultimo_snapshot = df_tabela[df_tabela['Ordem'] == df_tabela['Ordem'].max()]
    classificacao = ultimo_snapshot[ultimo_snapshot['Tipo'] == 'Piloto'][['Posição', 'Piloto', 'Equipe', 'Pontos']].copy()
    return classificacao.sort_values('Posição').reset_index(drop=True)


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
            ui.output_ui("vb_pilotos"),
            ui.output_ui("vb_equipes"),
            ui.output_ui("vb_proxima_corrida"),
            col_widths=[4, 4, 4],
            class_="valueboxes-layout",
        ),
        ui.layout_columns(
            ui.div(
                ui.div(
                    ui.h4("Classificação de Pilotos", class_="classificacao-titulo"),
                    ui.div(
                        ui.output_data_frame("tabela_classificacao"),
                        class_="tabela-classificacao tabela-classificacao-pilotos",
                    ),
                    class_="classificacao-card",
                ),
                ui.div(
                    output_widget("grafico_pilotos"),
                    class_="grafico-container",
                ),
            ),
            ui.div(
                ui.div(
                    ui.h4("Classificação de Construtores", class_="classificacao-titulo"),
                    ui.div(
                        ui.output_data_frame("tabela_construtores"),
                        class_="tabela-classificacao tabela-classificacao-construtores",
                    ),
                    class_="classificacao-card",
                ),
                ui.div(
                    output_widget("grafico_construtores"),
                    class_="grafico-container",
                ),
            ),
            col_widths=[6, 6],
        ),
        ui.div(
            ui.h4("Head-to-Head"),
            ui.div(
                ui.navset_tab(
                    ui.nav_panel("Corridas", value="corridas"),
                    ui.nav_panel("Sprint", value="sprint"),
                    ui.nav_panel("Qualy", value="qualy"),
                    ui.nav_panel("Sprint Qualy", value="sprint_qualy"),
                    id="h2h_sessao",
                ),
                ui.layout_columns(
                    ui.div(
                        output_widget("grafico_h2h"),
                        class_="grafico-container",
                    ),
                    ui.div(
                        ui.output_ui("h2h_detalhes"),
                        class_="h2h-detalhes",
                    ),
                    col_widths=[7, 5],
                    class_="h2h-layout",
                ),
                class_="h2h-card",
                style="margin-top: 30px;",
            ),
        ),
        style="padding: 20px;"
    )


@module.server
def resultados_home_server(input, output, session, df, df_tabela_classificacao,
                           df_race, df_sprint, df_qualy, df_sprint_qualy):
    df_pilotos = obter_classificacao_pilotos(df_tabela_classificacao)
    df_construtores = calcular_classificacao_construtores(df)

    pilotos_styles = build_team_styles(df_pilotos, team_col_idx=2)
    construtores_styles = build_team_styles(df_construtores, team_col_idx=1)

    # Ordem das equipes preservada antes de zerar a coluna 'Equipe'
    # (a coluna é ocultada na tabela para exibir apenas o logo).
    ordem_equipes_construtores = df_construtores['Equipe'].tolist()

    df_pilotos['Equipe'] = ""
    df_construtores['Equipe'] = ""

    lider_pilotos = df_pilotos.iloc[0]
    lider_equipe_nome = ordem_equipes_construtores[0]
    lider_equipe_pontos = df_construtores.iloc[0]['Pontos']

    @render.ui
    def vb_pilotos():
        nome = lider_pilotos['Piloto']
        pontos = lider_pilotos['Pontos']
        return ui.value_box(
            "Líder de Pilotos",
            nome,
            f"{float(pontos):g} pts",
            showcase=ui.img(
                src=headshot_src(nome),
                class_="vb-headshot",
            ),
            theme=ui.value_box_theme(fg="#ffffff", bg="#1a1a26"),
            class_="valuebox-f1",
        )

    @render.ui
    def vb_equipes():
        return ui.value_box(
            "Líder de Equipes",
            lider_equipe_nome,
            f"{float(lider_equipe_pontos):g} pts",
            showcase=ui.img(
                src=f'{LOGO_DIR}/{TEAM_LOGO_MAP[lider_equipe_nome]}',
                class_="vb-logo",
            ),
            theme=ui.value_box_theme(fg="#ffffff", bg="#1a1a26"),
            class_="valuebox-f1",
        )

    @render.ui
    def vb_proxima_corrida():
        proxima = proxima_corrida(df['Track'].unique())
        if not proxima:
            return ui.value_box(
                "Próxima Corrida",
                "Temporada encerrada",
                theme=ui.value_box_theme(fg="#ffffff", bg="#1a1a26"),
                class_="valuebox-f1",
            )
        track, rodada = proxima
        return ui.value_box(
            "Próxima Corrida",
            track,
            f"Rodada {rodada} de {TOTAL_CORRIDAS}",
            showcase=ui.img(
                src=layout_src(track),
                class_="vb-layout",
            ),
            theme=ui.value_box_theme(fg="#ffffff", bg="#1a1a26"),
            class_="valuebox-f1",
        )

    @render.data_frame
    def tabela_classificacao():
        return render.DataGrid(
            df_pilotos,
            styles=pilotos_styles,
            summary=False,
            width='100%', 
        )

    @render.data_frame
    def tabela_construtores():
        return render.DataGrid(
            df_construtores,
            styles=construtores_styles,
            summary=False,
            width='100%', 
        )

    @render_widget
    def grafico_pilotos():
        df_cumul = df_tabela_classificacao[
            df_tabela_classificacao['Tipo'] == 'Piloto'
        ].copy()
        df_cumul['Pontos'] = pd.to_numeric(df_cumul['Pontos'])
        df_cumul['Posição'] = pd.to_numeric(df_cumul['Posição'])
        df_cumul['Logo'] = df_cumul['Equipe'].map(
            lambda equipe: (
                f'{LOGO_DIR}/{TEAM_LOGO_MAP[equipe]}'
                if equipe in TEAM_LOGO_MAP
                else ''
            )
        )
        df_cumul['Bandeira'] = df_cumul['Corrida'].map(build_flag_path)

        ordem = (
            df_cumul.sort_values('Ordem')['Corrida']
            .drop_duplicates()
            .tolist()
        )

        # Mantém a ordem final dos pilotos nas categorias do gráfico.
        ordem_pilotos = (
            df_cumul[df_cumul['Ordem'] == df_cumul['Ordem'].max()]
            .sort_values('Posição')['Piloto']
            .tolist()
        )
        df_cumul['Piloto'] = pd.Categorical(df_cumul['Piloto'], categories=ordem_pilotos, ordered=True)
        df_cumul = df_cumul.sort_values(['Piloto', 'Ordem'])

        fig = px.line(
            df_cumul,
            x='Corrida',
            y='Pontos',
            color='Equipe',
            line_group='Piloto',
            color_discrete_map=TEAM_COLOR_MAP,
            category_orders={"Corrida": ordem, "Piloto": ordem_pilotos},
            markers=True,
        )

        # Os traces visuais nao devem controlar a ordem do hover unificado.
        # O hovertemplate do Plotly Express precisa ser removido porque ele
        # tem precedencia sobre o hoverinfo='skip'.
        fig.update_traces(
            hovertemplate=None,
            hoverinfo='skip',
        )

        # Usa a posicao oficial como valor de ordenacao do hover.
        for piloto in ordem_pilotos:
            df_piloto = df_cumul[
                df_cumul['Piloto'] == piloto
            ].sort_values('Ordem')

            fig.add_trace(
                go.Scatter(
                    x=df_piloto['Corrida'],
                    y=df_piloto['Posição'],
                    yaxis='y2',
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='rgba(0, 0, 0, 0)',
                    ),
                    hovertext=df_piloto['Piloto'],
                    customdata=df_piloto[
                        ['Pontos', 'Equipe', 'Logo', 'Bandeira']
                    ].to_numpy(),
                    hovertemplate=(
                        '%{hovertext}  %{customdata[0]:.0f}'
                        '<extra></extra>'
                    ),
                    meta='pilotos-hover',
                    showlegend=False,
                    name=piloto,
                )
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
                unifiedhovertitle=dict(text='<b>%{x}</b><br>'),
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
            yaxis2=dict(
                overlaying='y',
                visible=False,
                range=[0, df_cumul['Posição'].max() + 1],
            ),
            dragmode='pan',
            modebar=dict(
                orientation='v',
                bgcolor='rgba(21, 21, 30, 0.85)',
                color='#ffffff',
                activecolor='#E10600',
                remove=['select2d', 'lasso2d', 'zoom2d', 'resetScale2d']
            ),
            showlegend=False,
            hovermode='x unified',
            hoversort='value ascending',
        )

        return go.FigureWidget(fig)

    SESSOES = {
        'corridas': df_race,
        'sprint': df_sprint,
        'qualy': df_qualy,
        'sprint_qualy': df_sprint_qualy,
    }

    equipe_selecionada = reactive.value(None)

    @reactive.calc
    def dados_h2h():
        sessao = input.h2h_sessao()
        df_sessao = SESSOES.get(sessao, df_race)
        return build_h2h(df_sessao, sessao)

    @reactive.effect
    def selecionar_primeira_equipe():
        placar, _detalhes = dados_h2h()
        equipes_disponiveis = set(placar['Equipe'])

        primeira_equipe = next(
            (
                equipe
                for equipe in ordem_equipes_construtores
                if equipe in equipes_disponiveis
            ),
            None,
        )

        equipe_selecionada.set(primeira_equipe)

    @render_widget
    def grafico_h2h():
        placar, _detalhes = dados_h2h()

        ordem_equipes = ordem_equipes_construtores
        placar = placar[placar['Equipe'].isin(ordem_equipes)].copy()
        placar['Equipe'] = pd.Categorical(
            placar['Equipe'], categories=ordem_equipes, ordered=True
        )
        placar = placar.sort_values('Equipe')

        equipes = placar['Equipe'].tolist()
        pilotos_a = placar['Piloto A'].tolist()
        pilotos_b = placar['Piloto B'].tolist()
        vitorias_a = placar['Vit A'].astype(int).tolist()
        vitorias_b = placar['Vit B'].astype(int).tolist()

        cores_a = [TEAM_COLOR_MAP.get(equipe, '#888888') for equipe in equipes]
        cores_b = [_clarear_cor(cor) for cor in cores_a]

        max_wins = max(max(vitorias_a or [0]), max(vitorias_b or [0]), 1)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=equipes,
            x=[-v for v in vitorias_a],
            orientation='h',
            text=vitorias_a,
            textposition='auto',
            marker=dict(
                color=cores_a,
                cornerradius=8,
                line=dict(width=1, color='#15151e'),
            ),
            customdata=[
                [equipe, piloto, vitorias]
                for equipe, piloto, vitorias in zip(equipes, pilotos_a, vitorias_a)
            ],
            hovertemplate=(
                '<b>%{customdata[1]}</b> (%{customdata[0]})<br>'
                'Vitórias no duelo: %{customdata[2]}<extra></extra>'
            ),
            showlegend=False,
        ))

        fig.add_trace(go.Bar(
            y=equipes,
            x=vitorias_b,
            orientation='h',
            text=vitorias_b,
            textposition='auto',
            marker=dict(
                color=cores_b,
                cornerradius=8,
                line=dict(width=1, color='#15151e'),
            ),
            customdata=[
                [equipe, piloto, vitorias]
                for equipe, piloto, vitorias in zip(equipes, pilotos_b, vitorias_b)
            ],
            hovertemplate=(
                '<b>%{customdata[1]}</b> (%{customdata[0]})<br>'
                'Vitórias no duelo: %{customdata[2]}<extra></extra>'
            ),
            showlegend=False,
        ))

        # Coluna fixa com o logo de cada equipe à esquerda, seguida pelo
        # nome do piloto na extremidade da sua metade (esquerda/direita).
        margem_logo = 2.5
        margem_nome = max(max_wins * 0.35, 6.0)

        images = []
        annotations = []
        for equipe, piloto_a, piloto_b in zip(equipes, pilotos_a, pilotos_b):
            filename = TEAM_LOGO_MAP.get(equipe)
            if filename:
                images.append(dict(
                    source=f'{LOGO_DIR}/{filename}',
                    xref='x',
                    yref='y',
                    x=-(max_wins + margem_nome + margem_logo / 2),
                    y=equipe,
                    xanchor='center',
                    yanchor='middle',
                    sizex=margem_logo * 0.85,
                    sizey=0.55,
                    layer='below',
                ))
            annotations.append(dict(
                x=-(max_wins + margem_nome / 2),
                y=equipe,
                text=piloto_a,
                xanchor='center',
                yanchor='middle',
                showarrow=False,
                captureevents=False,
                font=dict(color='#ffffff', size=11),
            ))
            annotations.append(dict(
                x=max_wins + margem_nome / 2,
                y=equipe,
                text=piloto_b,
                xanchor='center',
                yanchor='middle',
                showarrow=False,
                captureevents=False,
                font=dict(color='#ffffff', size=11),
            ))

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            images=images,
            annotations=annotations,
            hoverlabel=dict(
                bgcolor='#1f1f2b',
                bordercolor='#444',
                font=dict(color='#ffffff', size=12),
                align='left',
            ),
            xaxis=dict(
                range=[
                    -(max_wins + margem_logo + margem_nome),
                    max_wins + margem_logo + margem_nome,
                ],
                showgrid=True,
                gridcolor='rgba(255,255,255,0.08)',
                zeroline=True,
                zerolinecolor='rgba(255,255,255,0.55)',
                zerolinewidth=2,
                tickmode='array',
                tickvals=list(range(-max_wins, max_wins + 1)),
                ticktext=[str(abs(v)) for v in range(-max_wins, max_wins + 1)],
                tickfont=dict(color='#ffffff', size=10),
                title=None,
                showspikes=False,
            ),
            yaxis=dict(
                categoryorder='array',
                categoryarray=list(reversed(ordem_equipes)),
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                tickfont=dict(color='#ffffff', size=11),
                title=None,
                showspikes=False,
            ),
            # O gráfico permanece clicável nas barras, mas sem pan, zoom ou seleção.
            dragmode=False,
            hovermode='closest',
            clickmode='event',
            modebar=dict(
                orientation='v',
                bgcolor='rgba(21, 21, 30, 0.85)',
                color='#ffffff',
                activecolor='#E10600',
                remove=[
                    'select2d',
                    'lasso2d',
                    'zoom2d',
                    'pan2d',
                    'zoomIn2d',
                    'zoomOut2d',
                    'autoScale2d',
                    'resetScale2d',
                    'toImage',
                ],
            ),
            showlegend=False,
            barmode='relative',
        )

        widget = go.FigureWidget(fig)

        def ao_clicar(trace, points, _state):
            if points.point_inds:
                equipe = trace.y[points.point_inds[0]]
                equipe_selecionada.set(str(equipe))

        widget.data[0].on_click(ao_clicar)
        widget.data[1].on_click(ao_clicar)

        widget._config.update({
            'doubleClick': False,
            'scrollZoom': False,
            'displayModeBar': False,
        })
        return widget

    @render.ui
    def h2h_detalhes():
        equipe = equipe_selecionada()
        if not equipe:
            return ui.div(
                ui.p(
                    "Não há dados disponíveis para esta sessão.",
                    class_="text-muted",
                ),
                class_="h2h-detalhes-vazio",
            )

        _placar, detalhes = dados_h2h()
        info = detalhes.get(equipe)
        if not info:
            return ui.div(
                ui.p("Equipe não encontrada.", class_="text-muted"),
                class_="h2h-detalhes-vazio",
            )

        piloto_a, piloto_b = info['pilotos']
        metricas = info['metricas']

        def _formatar(valor, chave):
            if valor is None:
                return '—'
            if chave == 'pct_vitorias':
                return f'{valor}%'
            if isinstance(valor, float):
                return f'{valor:g}'
            return str(valor)

        linhas = [
            ui.div(
                ui.div('', class_='h2h-cel h2h-cel-metrica'),
                ui.div(piloto_a['nome'], class_='h2h-cel h2h-cel-header'),
                ui.div(piloto_b['nome'], class_='h2h-cel h2h-cel-header'),
                class_='h2h-linha',
            ),
        ]
        for metrica in metricas:
            chave = metrica['key']
            va = piloto_a.get(chave)
            vb = piloto_b.get(chave)
            classe_a = classe_b = 'h2h-cel'
            if va is not None and vb is not None and metrica['invert'] is not None:
                if metrica['invert']:
                    melhor = 'a' if va < vb else ('b' if vb < va else None)
                else:
                    melhor = 'a' if va > vb else ('b' if vb > va else None)
                if melhor == 'a':
                    classe_a += ' h2h-cel-melhor'
                elif melhor == 'b':
                    classe_b += ' h2h-cel-melhor'
            linhas.append(ui.div(
                ui.div(metrica['label'], class_='h2h-cel h2h-cel-metrica'),
                ui.div(_formatar(va, chave), class_=classe_a),
                ui.div(_formatar(vb, chave), class_=classe_b),
                class_='h2h-linha',
            ))

        return ui.div(
            ui.h5(equipe, class_='h2h-detalhes-titulo'),
            ui.div(*linhas, class_='h2h-tabela-duelo'),
            class_='h2h-detalhes-painel',
        )

    @render_widget
    def grafico_construtores():
        df_cumul = build_cumulative_construtores(df)
        df_cumul['Logo'] = df_cumul['Equipe'].map(
            lambda equipe: (
                f'{LOGO_DIR}/{TEAM_LOGO_MAP[equipe]}'
                if equipe in TEAM_LOGO_MAP
                else ''
            )
        )
        df_cumul['Bandeira'] = df_cumul['Corrida'].map(build_flag_path)
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
            custom_data=['Pontos', 'Equipe', 'Logo', 'Bandeira'],
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
                unifiedhovertitle=dict(text='<b>%{x}</b><br>'),
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
            showlegend=False,
            hovermode='x unified',
        )
        fig.update_traces(
            meta='construtores-hover',
            hovertemplate='%{hovertext}  %{y:.0f}<extra></extra>'
        )
        return go.FigureWidget(fig)
