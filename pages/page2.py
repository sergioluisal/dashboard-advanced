import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
from dash import html, dcc
import os # Certifique-se de que esta linha está no topo do arquivo com os outros imports

# ============================================================
# Carregar os dados
# ============================================================

# Constrói o caminho absoluto para o arquivo de dados
# Isso assume que o arquivo 'USP_Completa.xlsx' está na pasta raiz do projeto (junto com app.py)
try:
    # Sobe um nível de diretório (da pasta 'pages' para a pasta raiz)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Junta o caminho da pasta raiz com o nome do arquivo
    DATA_PATH = os.path.join(BASE_DIR, "USP_Completa.xlsx")
    
    # Tenta carregar o DataFrame usando o caminho completo
    df = pd.read_excel(DATA_PATH)
    print(f"SUCESSO (page1.py): Arquivo de dados carregado de '{DATA_PATH}'")

except FileNotFoundError:
    print(f"ERRO CRÍTICO (page1.py): O arquivo 'USP_Completa.xlsx' não foi encontrado no caminho esperado: '{DATA_PATH}'.")
    print("A aplicação não pode iniciar sem os dados. Verifique se o arquivo existe e está no local correto.")
    # Cria um DataFrame vazio para evitar que a aplicação quebre na inicialização,
    # mas os gráficos não terão dados.
    df = pd.DataFrame()

# ------------------------------
# Normalização dos nomes de curso
# ------------------------------
if "Curso" in df.columns:
    df["Curso"] = df["Curso"].replace({
        "Doutorado Direto": "Doutorado",
        "Doutora": "Doutorado"
    })

# --- Lógica de tratamento de dados específica desta página ---
df["Data da ocorrência"] = pd.to_datetime(df["Data da ocorrência"], errors="coerce")
df["Primeira matrícula"] = pd.to_datetime(df["Primeira matrícula"], errors="coerce")

def diff_meses(row):
    if pd.isna(row["Data da ocorrência"]) or pd.isna(row["Primeira matrícula"]):
        return None
    rd = relativedelta(row["Data da ocorrência"], row["Primeira matrícula"])
    return rd.years * 12 + rd.months

df["período_meses_inteiros"] = df.apply(diff_meses, axis=1)
df["Ano_matricula"] = df["Primeira matrícula"].dt.year

# Classificação de status
ativos = ["Matrícula de Acompanhamento", "Matriculado", "Mudança de Nível", "Prorrogação", "Trancado", "Transferido de Área"]
nao_ativos = ["Desligado"]

def classificar_aluno(row):
    if row["Última ocorrência"] in ativos:
        return "Ativos"
    elif row["Última ocorrência"] in nao_ativos:
        return "Desligados"
    elif row["Última ocorrência"] == "Titulados":
        return "Titulados" if pd.notna(row["Data da defesa"]) else "Outros"

df["Status_aluno"] = df.apply(classificar_aluno, axis=1)

#===========================================================================|
#|                  Opções de Filtros Dinâmicos                            |
#===========================================================================|
programas_opcoes = sorted(df["Programa"].dropna().unique()) if "Programa" in df.columns else []
cursos_opcoes = sorted(df["Curso"].dropna().unique()) if "Curso" in df.columns else []
ativos_opcoes = sorted(df["Status_aluno"].dropna().unique())

#|==========================================================================|
#|                       Layout do Conteúdo da Página 2                     |
#|==========================================================================|
layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Dashboard Acadêmico - Análise de Alunos",
                            className="text-center text-primary my-4"), width=12)),
    dbc.Row(
        dbc.Col(html.H1("Filtros Analítico",
                        className="text-center my-4"), width=12)
    ),
    # Linha de Filtros
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id='filtro-programa',
                                options=[{'label': i, 'value': i} for i in programas_opcoes],
                                multi=True,
                                placeholder="Selecione o(s) Programa(s)",
                                style={"backgroundColor": "#2c2c2c", "color": "black", "height": "38px"}
                            ), md=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='filtro-curso',
                                options=[{'label': i, 'value': i} for i in cursos_opcoes],
                                multi=True,
                                placeholder="Selecione o(s) Curso(s)",
                                style={"backgroundColor": "#2c2c2c", "color": "black", "height": "38px"}
                            ), md=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='filtro-ativos',
                                options=[{'label': i, 'value': i} for i in ativos_opcoes],
                                multi=True,
                                placeholder="Selecione Status (Ativos/Titulados/Desligados)",
                                style={"backgroundColor": "#2c2c2c", "color": "black", "height": "38px"}
                            ), md=3
                        ),
                        dbc.Col(
                            dcc.DatePickerRange(
                            id='filtro-periodo2',
                            min_date_allowed=df["Primeira matrícula"].min().date() if "Primeira matrícula" in df.columns else None,
                            max_date_allowed=df["Primeira matrícula"].max().date() if "Primeira matrícula" in df.columns else None,
                            start_date=df["Primeira matrícula"].min().date() if "Primeira matrícula" in df.columns else None,
                            end_date=df["Primeira matrícula"].max().date() if "Primeira matrícula" in df.columns else None,
                            display_format='DD/MM/YYYY',
                            style={"height": "38px", "width": "100%"}
                            ), md=3
                        ),
                    ])
                ])
            ], className="bg-dark"),
            width=12,
            className="mb-4"
        )
    ]),

    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id="fig2", style={"height": "400px"}), md=12, className="mb-4"),    
    ], className="g-4"),
    # Linha do KPI sozinho
    dbc.Row([
        dbc.Col(
            dbc.Card(dbc.CardBody([
            html.H4("Variação vs Ano Anterior", className="card-title text-center"),
            html.P(id="variacao-label",
                   className="card-text text-center display-4 text-success")
        ])), md=12, className="mb-4")
    ], className="g-4"),

    # Linha dos gráficos lado a lado
    dbc.Row([
        dbc.Col(dcc.Graph(id="fig3"), md=6, className="mb-4"),
            dbc.Col(dcc.Graph(id="fig5"), md=6, className="mb-4"),
    ], className="g-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="fig6"), md=4, className="mb-4"),
        dbc.Col(dcc.Graph(id="fig7"), md=8, className="mb-4"),
    ], className="g-4"),
], fluid=True)
