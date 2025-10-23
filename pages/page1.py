import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from pages.page2 import programas_opcoes, cursos_opcoes, ativos_opcoes

# ============================================================
# Carregar os dados
# ============================================================
try:
    # Sobe um nível de diretório (da pasta 'pages' para a pasta raiz)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Junta o caminho da pasta raiz com o nome do arquivo
    DATA_PATH = os.path.join(BASE_DIR, "USP_Completa.xlsx")
    
except FileNotFoundError:
    print("AVISO (page1.py): Ficheiro 'USP_Completa.xlsx' não encontrado. A usar dados de exemplo.")
    df = pd.DataFrame({
        "Programa": ["Mestrado", "Doutorado", "Mestrado", "Mestrado", "Doutorado"],
        "Curso": ["Enfermagem", "Educação", "Administração", "História", "Matemática"],
        "Última ocorrência": ["Matriculado", "Titulado", "Prorrogação", "Desligado", "Matricula de Acompanhamento"],
        "Raça/Cor": ["Branca", "Parda", "Preta", "Parda", "Branca"],
        "Tempo para titulação (meses)": [24, 30, 28, 35, 26],
        "Financiamento": ["CAPES", "Sem informação", "CNPq", "CAPES", "Outro"],
        "Primeira matrícula": pd.date_range("2020-01-01", periods=5, freq="Y")
    })

programas_opcoes = sorted(df["Programa"].dropna().unique()) if "Programa" in df.columns else []
cursos_opcoes = sorted(df["Curso"].dropna().unique()) if "Curso" in df.columns else []
status_opcoes = sorted(df["Status_aluno"].dropna().unique()) if "Status_aluno" in df.columns else []

# ------------------------------
# Normalização dos nomes de curso
# ------------------------------
if "Curso" in df.columns:
    df["Curso"] = df["Curso"].replace({
        "Doutorado Direto": "Doutorado",
        "Doutora": "Doutorado"
    })

# ============================================================
# Criar coluna Status a partir de Última ocorrência
# ============================================================
status_map = {
    "Matricula de Acompanhamento": "Ativos",
    "Matriculado": "Ativos",
    "Mudança de Nível": "Ativos",
    "Prorrogação": "Ativos",
    "Transcado": "Ativos",
    "Transferido de Area": "Ativos",
    "Titulado": "Titulados",
    "Desligado": "Desligados"
}

df["Status"] = df["Última ocorrência"].map(status_map).fillna("Outros")

# ============================================================
# Configuração de tema
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
        annotations=[
            dict(text="Sem dados para exibir", showarrow=False, font=dict(size=14, color="#CCCCCC"))
        ],
    )
    return fig


# ============================================================
# Layout da Página 1
# ============================================================
layout = dbc.Container([

    # ===================== Título =====================
    dbc.Row(
        dbc.Col(
            html.H2("Informações Pessoais e Acadêmicas", className="text-center text-primary my-4"),
            width=12
        )
    ),
    dbc.Row(
        dbc.Col(html.H1("Filtros Analítico",
                        className="text-center my-4"), width=12)
    ),

    # ===================== Linha de Filtros 1 =====================
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
                                placeholder="Selecione Status (Ativos/Desligados)",
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
        # ===================== Gráfico de Status =====================
    

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
            #Output('status-graph', 'figure'),
        ],
        [
            Input('filtro-financiamento', 'value'),
            Input('filtro-titulacao', 'value'),
            Input('filtro-raca', 'value'),
            Input('filtro-programa1', 'value'),
            Input('filtro-curso1', 'value'),
            Input('filtro-status1', 'value'),
            Input('filtro-periodo', 'start_date'),
            Input('filtro-periodo', 'end_date'),
        ]
    )
    def atualizar_graficos(financiamento, titulacao, raca, programa, curso, status, start_date, end_date):
        dff = df.copy()

        # Aplicar filtros
        if financiamento:
            dff = dff[dff["Financiamento"].isin(financiamento)]
        if titulacao:
            dff = dff[dff["Tempo para titulação (meses)"].isin(titulacao)]
        if raca:
            dff = dff[dff["Raça/Cor"].isin(raca)]
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
        
        # Raça/Cor
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
        # Titulação
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

        # Financiamento
        df_fin = dff["Financiamento"].value_counts().reset_index()
        df_fin.columns = ["Financiamento", "Total"]
        fig_fin = px.bar(df_fin, x="Financiamento", y="Total",
                         title="Fontes de Financiamento",
                         template=TEMPLATE, text_auto=True)
        fig_fin.update_traces(textposition="outside")

        # Folga no eixo Y para não cortar os valores
        max_value = df_fin["Total"].max()
        fig_fin.update_yaxes(range=[0, max_value * 1.2])

        # Ajusta margens e rotação dos rótulos
        fig_fin.update_layout(margin=dict(t=80, b=40, l=40, r=40), xaxis_tickangle=-45)
        # Status (Ativos vs Titulados vs Desligados)
        
        # Fundo transparente
        for f in [fig_raca, fig_titulacao, fig_fin]:
            f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            
        return fig_raca, fig_titulacao, fig_fin
