import os
import pandas as pd
from shiny import App, ui, render

# Ignora o proxy para conexões locais (Dashboard)
os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

# Carrega os dados do CSV (Ajuste o caminho se necessário)
# O caminho abaixo pressupõe que a pasta 'data' está no mesmo diretório que o main.py
caminho_csv = os.path.join(os.path.dirname(__file__), "data", "Formula1_2026Season_RaceResults.csv")
df_resultados = pd.read_csv(caminho_csv)

# 1. Interface de Usuário (UI)
app_ui = ui.page_fluid(
    ui.h2("Corridas F1 - Temporada 2026 🏎️"),
    ui.p("Tabela com os resultados das corridas da temporada."),
    
    # Adicionando um container para a tabela
    ui.card(
        ui.output_data_frame("tabela_resultados")
    ),
    ui.hr(),
    ui.hr(),
    ui.p(
        {"style": "font-size: 0.8rem; color: gray;"}, # Adiciona estilo CSS inline para ficar "small"
        "Dataset original por toUpperCase78 sob licença GPLv3. ",
        ui.a("Acesse o repositório orginal", href="https://github.com/toUpperCase78/formula1-datasets/tree/master")
    )
)

# 2. Lógica do Servidor (Server)
def server(input, output, session):
    
    # Renderiza o dataframe na UI
    @output
    @render.data_frame
    def tabela_resultados():
        return df_resultados

# 3. Construção do Aplicativo
app = App(app_ui, server)