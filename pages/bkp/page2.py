import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
from dash import html, dcc

#===========================================================================|
#|                           Carregar e Tratar Dados                       |
#===========================================================================|
try:
    df = pd.read_excel("USP_Completa.xlsx")
except FileNotFoundError:
    print("AVISO (page2.py): Ficheiro 'USP_Completa.xlsx' não encontrado. A usar dados de exemplo.")
    df = pd.DataFrame({
        "Data da ocorrência": pd.to_datetime(['2023-05-10', '2024-01-15', '2022-11-20', '2023-08-01']),
        "Primeira matrícula": pd.to_datetime(['2021-02-10', '2021-08-15', '2021-02-10', '2022-02-01']),
        "Última ocorrência": ["Matriculado", "Titulado", "Desligado", "Trancado"],
        "Data da defesa": [pd.NaT, '2024-01-15', pd.NaT, pd.NaT],
        "Nacionalidade": ["Brasileira", "Brasileira", "Argentina", "Brasileira"],
        "Programa": ["Engenharia", "Direito", "Medicina", "Engenharia"],
        "Curso": ["Mestrado", "Doutorado", "Mestrado", "Mestrado"]
    })

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
        return "Ativo"
    elif row["Última ocorrência"] in nao_ativos:
        return "Desligados"
    elif row["Última ocorrência"] == "Titulado":
        return "Titulado" if pd.notna(row["Data da defesa"]) else "Titulado (sem defesa)"
    else:
        return "Outro"

df["Status_aluno"] = df.apply(classificar_aluno, axis=1)

#===========================================================================|
#|                  Opções de Filtros Dinâmicos                            |
#===========================================================================|
programas_opcoes = sorted(df["Programa"].dropna().unique()) if "Programa" in df.columns else []
cursos_opcoes = sorted(df["Curso"].dropna().unique()) if "Curso" in df.columns else []
ativos_opcoes = sorted(df["Status_aluno"].dropna().unique())

#===========================================================================|
#|                       Layout do Conteúdo da Página 2                    |
#===========================================================================|
layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Dashboard Acadêmico - Análise de Alunos",
                            className="text-center text-primary my-4"), width=12)),

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
                                style={"backgroundColor": "#2c2c2c", "color": "black"}
                            ), md=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='filtro-curso',
                                options=[{'label': i, 'value': i} for i in cursos_opcoes],
                                multi=True,
                                placeholder="Selecione o(s) Curso(s)",
                                style={"backgroundColor": "#2c2c2c", "color": "black"}
                            ), md=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='filtro-ativos',
                                options=[{'label': i, 'value': i} for i in ativos_opcoes],
                                multi=True,
                                placeholder="Selecione Status (Ativos/Titulados/Desligados)",
                                style={"backgroundColor": "#2c2c2c", "color": "black"}
                            ), md=4
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
        dbc.Col(dcc.Graph(id="fig1"), md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="fig2"), md=6, className="mb-4"),
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
