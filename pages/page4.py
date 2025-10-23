import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ==========================================================
# CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================================
def carregar_dados(path="USP_Completa.xlsx"):
    try:
        df = pd.read_excel(path)
    except Exception:
        # Dados de exemplo (caso o arquivo não exista)
        df = pd.DataFrame({
            "Nascimento": pd.to_datetime(['1995-01-10', '1988-05-20', '1975-07-07', '1990-12-01']),
            "Início da contagem de prazo": pd.to_datetime(['2021-02-10', '2020-08-15', '2019-03-10', '2022-02-01']),
            "Curso": ["Mestrado", "Doutorado", "Mestrado", "Mestrado"],
            "Programa": ["Engenharia", "Direito", "Medicina", "Engenharia"],
            "Última ocorrência": ["Matriculado", "Titulado", "Desligado", "Matriculado"],
        })

    df["Início da contagem de prazo"] = pd.to_datetime(df["Início da contagem de prazo"], errors="coerce")
    df["Nascimento"] = pd.to_datetime(df["Nascimento"], errors="coerce")

    # ✅ INSIRA ESTE TRECHO AQUI
    # Unificar “Doutorado Direto” e variações com “Doutorado”
    df["Curso"] = df["Curso"].replace({
        "Doutorado Direto": "Doutorado",
        "Doutora": "Doutorado"
    })
    # ✅ FIM DO TRECHO

    df["Ano Início"] = df["Início da contagem de prazo"].dt.year
    df["Idade"] = ((df["Início da contagem de prazo"] - df["Nascimento"]).dt.days // 365).astype("float")

    bins = [0, 25, 30, 35, 40, 45, 50, 60, 200]
    labels = ['<25', '25-29', '30-34', '35-39', '40-44', '45-49', '50-59', '60+']
    df["Faixa Etária"] = pd.cut(df["Idade"], bins=bins, labels=labels, right=False)
    df["Faixa Etária"] = pd.Categorical(df["Faixa Etária"], categories=labels, ordered=True)

    ativos = ["Matriculado", "Matrícula de Acompanhamento", "Mudança de Nível", "Prorrogação", "Trancado", "Transferido de Área"]
    nao_ativos = ["Desligado"]
    def classificar(row):
        if row["Última ocorrência"] in ativos:
            return "Ativos"
        elif row["Última ocorrência"] in nao_ativos:
            return "Desligados"
        elif row["Última ocorrência"] == "Titulado":
            return "Titulados"
        else:
            return "Outros"
    df["Status"] = df.apply(classificar, axis=1)

    return df, labels

df, faixa_labels = carregar_dados()

# ==========================================================
# OPÇÕES DOS FILTROS
# ==========================================================
programas_opcoes = sorted(df["Programa"].dropna().unique())
cursos_opcoes = sorted(df["Curso"].dropna().unique())
status_opcoes = sorted(df["Status"].dropna().unique())

min_date = df["Início da contagem de prazo"].min().date()
max_date = df["Início da contagem de prazo"].max().date()

# ==========================================================
# LAYOUT DA PÁGINA 4
# ==========================================================
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Análise de Alunos por Curso",
                        className="text-center text-primary my-4"), width=12)
    ]),
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
                                id='filtro-status',
                                options=[{'label': i, 'value': i} for i in status_opcoes],
                                multi=True,
                                placeholder="Selecione Status (Ativos/Titulados/Desligados)",
                                style={"backgroundColor": "#2c2c2c", "color": "black", "height": "38px"}
                            ), md=3
                        ),
                        dbc.Col(
                            dcc.DatePickerRange(
                                id='filtro-periodo',
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                                display_format='DD/MM/YYYY'
                            ), md=3
                        ),
                    ])
                ])
            ], className="bg-dark text-light"),
            width=12,
            className="mb-4"
        )
    ]),

    # Gráfico 1
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico1", style={"height": "420px"}), md=12)
    ], className="mb-4"),

    # Gráfico 2
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico2", style={"height": "420px"}), md=12)
    ])
], fluid=True)

# ==========================================================
# CALLBACKS
# ==========================================================
@callback(
    Output("grafico1", "figure"),
    Output("grafico2", "figure"),
    Input("filtro-programa", "value"),
    Input("filtro-curso", "value"),
    Input("filtro-status", "value"),
    Input("filtro-periodo", "start_date"),
    Input("filtro-periodo", "end_date"),
)
def atualizar_graficos(programa, curso, status, data_inicio, data_fim):
    dff = df.copy()

    if programa:
        dff = dff[dff["Programa"].isin(programa)]
    if curso:
        dff = dff[dff["Curso"].isin(curso)]
    if status:
        dff = dff[dff["Status"].isin(status)]
    if data_inicio:
        dff = dff[dff["Início da contagem de prazo"] >= pd.to_datetime(data_inicio)]
    if data_fim:
        dff = dff[dff["Início da contagem de prazo"] <= pd.to_datetime(data_fim)]

    # --- Gráfico 1: Faixa Etária x Curso
    if dff.empty:
        fig1 = px.bar(title="Nenhum dado encontrado")
    else:
        fig1 = px.histogram(
            dff,
            x="Faixa Etária",
            color="Curso",
            category_orders={"Faixa Etária": faixa_labels},
            barmode="group",
            text_auto=True,
            title="Distribuição de Faixa Etária por Curso"
        )
        #fig1.update_layout(yaxis_title="Quantidade", xaxis_title="Faixa Etária")
        fig1.update_yaxes(title_text="Quantidade")
        fig1.update_layout(
        xaxis=dict(type='category', showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")) 

    # --- Gráfico 2: Faixa Etária x Ano de Início
    if dff.empty:
        fig2 = px.bar(title="Nenhum dado encontrado")
    else:
        dados_ano = dff.groupby(["Ano Início", "Faixa Etária"]).size().reset_index(name="Quantidade")
        fig2 = px.bar(
            dados_ano,
            x="Ano Início",
            y="Quantidade",
            color="Faixa Etária",
            category_orders={"Faixa Etária": faixa_labels},
            barmode="stack",
            title="Faixa Etária x Ano de Início"
        )
        fig2.update_layout(
        xaxis=dict(type='category', tickangle=-45, showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"))       

    # Tema escuro coerente com o layout
    for fig in [fig1, fig2]:
        fig.update_layout(
            plot_bgcolor="#1a1a2e",
            paper_bgcolor="#0f0b1a",
            font_color="#dbe9ff",
            title_font_size=18,
            title_x=0.5
        )
    # Fundo transparente
    for f in [fig1, fig2]:
        f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    return fig1, fig2


