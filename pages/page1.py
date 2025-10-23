import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
from dash import html, dcc, Input, Output

# ============================================================
# Carregar os dados
# ============================================================
try:
    # Caminho absoluto do arquivo Excel (funciona local e no Render)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df_path = os.path.join(BASE_DIR, "../USP_Completa.xlsx")

    print(f"📂 Lendo dados a partir de: {df_path}")
    df = pd.read_excel(df_path)

except FileNotFoundError:
    print("⚠️ AVISO (page1.py): Arquivo 'USP_Completa.xlsx' não encontrado. Usando dados de exemplo.")
    df = pd.DataFrame({
        "Data da ocorrência": pd.to_datetime(['2023-05-10', '2024-01-15', '2022-11-20', '2023-08-01']),
        "Primeira matrícula": pd.to_datetime(['2021-02-10', '2021-08-15', '2021-02-10', '2022-02-01']),
        "Última ocorrência": ["Matriculado", "Titulado", "Desligado", "Trancado"],
        "Data da defesa": [pd.NaT, '2024-01-15', pd.NaT, pd.NaT],
        "Nacionalidade": ["Brasileira", "Brasileira", "Argentina", "Brasileira"],
        "Programa": ["Engenharia", "Direito", "Medicina", "Engenharia"],
        "Curso": ["Mestrado", "Doutorado Direto", "Mestrado", "Doutorado"]
    })

# ============================================================
# Normalização dos cursos e status
# ============================================================
# Normalizar nomes de curso — unificar "Doutorado Direto" → "Doutorado"
if "Curso" in df.columns:
    df["Curso"] = df["Curso"].replace({
        "Doutorado Direto": "Doutorado",
        "Doutora": "Doutorado"
    })

# Criar coluna de Status (caso não exista no Excel)
if "Status" not in df.columns and "Última ocorrência" in df.columns:
    status_map = {
        "Matricula de Acompanhamento": "Ativos",
        "Matriculado": "Ativos",
        "Mudança de Nível": "Ativos",
        "Prorrogação": "Ativos",
        "Trancado": "Ativos",
        "Transferido de Área": "Ativos",
        "Titulado": "Titulados",
        "Desligado": "Desligados"
    }
    df["Status"] = df["Última ocorrência"].map(status_map).fillna("Outros")

# Criar listas de opções para os filtros
programas_opcoes = sorted(df["Programa"].dropna().unique()) if "Programa" in df.columns else []
cursos_opcoes = sorted(df["Curso"].dropna().unique()) if "Curso" in df.columns else []
ativos_opcoes = sorted(df["Status"].dropna().unique()) if "Status" in df.columns else []

# ============================================================
# Configuração de tema e figura vazia
# ============================================================
TEMPLATE = "plotly_dark"

def create_empty_fig(title: str):
    fig = go.Figure()
    fig.update_layout(
        title=f"{title} - Sem dados",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CCCCCC"),
        xaxis_visible=False,
        yaxis_visible=False,
        annotations=[dict(text="Sem dados para exibir", showarrow=False, font=dict(size=14, color="#CCCCCC"))],
    )
    return fig

# ============================================================
# Layout da Página 1
# ============================================================
layout = dbc.Container([

    dbc.Row(
        dbc.Col(
            html.H2("Informações Pessoais e Acadêmicas", className="text-center text-primary my-4"),
            width=12
        )
    ),
    dbc.Row(
        dbc.Col(html.H1("Filtros Analítico", className="text-center my-4"), width=12)
    ),

    # ===================== Linha de Filtros =====================
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

    # ===================== Linha de Gráficos =====================
    dbc.Row([
        html.H4("Perfil Demográfico", className="text-secondary mb-3"),
        dbc.Col(dcc.Graph(id='raca-graph', style={"height": "400px"}), md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='titulacao-graph', style={"height": "400px"}), md=6, className="mb-4"),
    ], className="g-4"),

    dbc.Row([
        html.H4("Perfil Acadêmico e Financeiro", className="text-secondary my-3"),
        dbc.Col(dcc.Graph(id='financiamento-graph', style={"height": "400px"}), md=12, className="mb-4"),
    ], className="g-4"),

], fluid=True)

# ============================================================
# Callbacks
# ============================================================
def register_callbacks(app):
    @app.callback(
        [
            Output('raca-graph', 'figure'),
            Output('titulacao-graph', 'figure'),
            Output('financiamento-graph', 'figure'),
        ],
        [
            Input('filtro-programa', 'value'),
            Input('filtro-curso', 'value'),
            Input('filtro-ativos', 'value'),
            Input('filtro-periodo2', 'start_date'),
            Input('filtro-periodo2', 'end_date'),
        ]
    )
    def atualizar_graficos(programa, curso, status, start_date, end_date):
        dff = df.copy()

        # Aplicar filtros
        if programa:
            dff = dff[dff["Programa"].isin(programa)]
        if curso:
            dff = dff[dff["Curso"].isin(curso)]
        if status:
            dff = dff[dff["Status"].isin(status)]
        if start_date and end_date and "Primeira matrícula" in dff.columns:
            dff["Primeira matrícula"] = pd.to_datetime(dff["Primeira matrícula"], errors="coerce")
            dff = dff[
                (dff["Primeira matrícula"] >= pd.to_datetime(start_date)) &
                (dff["Primeira matrícula"] <= pd.to_datetime(end_date))
            ]

        # ===================== Gráfico Raça/Cor =====================
        if "Raça/Cor" in dff.columns:
            dff["Raça/Cor"] = dff["Raça/Cor"].fillna("Sem informação")
            dff["Raça/Cor"] = dff["Raça/Cor"].replace("", "Sem informação")

            df_raca = dff["Raça/Cor"].value_counts().reset_index()
            df_raca.columns = ["Raça/Cor", "Total"]

            fig_raca = px.bar(
                df_raca, x="Raça/Cor", y="Total",
                title="Distribuição por Raça/Cor",
                template=TEMPLATE, text_auto=True
            )
            fig_raca.update_traces(textposition="outside")
            max_value = df_raca["Total"].max()
            fig_raca.update_yaxes(range=[0, max_value * 1.2])
            fig_raca.update_layout(margin=dict(t=80, b=40, l=40, r=40), xaxis_tickangle=-45)
        else:
            fig_raca = create_empty_fig("Raça/Cor")

        # ===================== Gráfico Titulação =====================
        if "Tempo para titulação (meses)" in dff.columns:
            fig_titulacao = px.histogram(
                dff.dropna(subset=["Tempo para titulação (meses)"]),
                x="Tempo para titulação (meses)",
                nbins=40,
                title="Distribuição do Tempo para Titulação",
                labels={"Tempo para titulação (meses)": "Meses"},
                template=TEMPLATE
            )
            fig_titulacao.update_yaxes(title_text="Quantidade")
            fig_titulacao.update_layout(bargap=0.2, bargroupgap=0.1, xaxis_title="Meses para Titulação")
        else:
            fig_titulacao = create_empty_fig("Tempo para Titulação")

        # ===================== Gráfico Financiamento =====================
        if "Financiamento" in dff.columns:
            df_fin = dff["Financiamento"].value_counts().reset_index()
            df_fin.columns = ["Financiamento", "Total"]
            fig_fin = px.bar(df_fin, x="Financiamento", y="Total",
                             title="Fontes de Financiamento",
                             template=TEMPLATE, text_auto=True)
            fig_fin.update_traces(textposition="outside")
            max_value = df_fin["Total"].max()
            fig_fin.update_yaxes(range=[0, max_value * 1.2])
            fig_fin.update_layout(margin=dict(t=80, b=40, l=40, r=40), xaxis_tickangle=-45)
        else:
            fig_fin = create_empty_fig("Financiamento")

        # Fundo transparente
        for f in [fig_raca, fig_titulacao, fig_fin]:
            f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

        return fig_raca, fig_titulacao, fig_fin

