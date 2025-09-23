import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, Dash

#===========================================================================|
#|                NÃO inicializamos o app aqui.                            |
#|                Este ficheiro é apenas um módulo de conteúdo.             |
#===========================================================================|

#===========================================================================|
#|                           Carregar e Tratar Dados                       |
#===========================================================================|
try:
    df = pd.read_excel("USP_Completa.xlsx")
except FileNotFoundError:
    print("AVISO (page1.py): Ficheiro 'USP_Completa.xlsx' não encontrado. A usar dados de exemplo.")
    df = pd.DataFrame({
        "Raça/Cor": ["Branca", "Parda", "Preta", "Parda", "Branca"],
        "Pessoa com Deficiência": ["Não", "Não", pd.NA, "Sim", "Não"],
        "Sexo": ["Masculino", "Feminino", "Feminino", "Masculino", "Feminino"],
        "Tempo para titulação (meses)": [24, 30, 28, 35, 26],
        "Financiamento": ["CAPES", "Sem informação", "CNPq", "CAPES", "Outro"]
    })

#===========================================================================|
#|                           Configuração Gráficos                         |
#===========================================================================|
TEMPLATE = "plotly_dark"

def create_empty_fig(column_name):
    fig = go.Figure()
    fig.update_layout(
        title=f"Dados para '{column_name}' não encontrados",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#CCCCCC"),
        xaxis_visible=False, yaxis_visible=False,
        annotations=[dict(text="Verifique se a coluna existe no Excel", showarrow=False, font=dict(size=14, color="#CCCCCC"))]
    )
    return fig

#===========================================================================|
#|                       Layout do Conteúdo da Página 1                    |
#===========================================================================|
layout = dbc.Container([
    # Título
    dbc.Row(
        dbc.Col(html.H2("Informações Pessoais e Acadêmicas", className="text-center text-primary my-4"), width=12)
    ),

    # Linha de Filtros
dbc.Row([
    # Primeira linha de filtros
    dbc.Col(
        dcc.Dropdown(
            id='filtro-financiamento',
            options=[{'label': i, 'value': i} for i in df["Financiamento"].dropna().unique()],
            multi=True,
            placeholder="Selecione Financiamento",
            style={"backgroundColor": "#2c2c2c", "color": "black"}
        ), md=3
    ),
    dbc.Col(
        dcc.Dropdown(
            id='filtro-titulacao',
            options=[{'label': str(i), 'value': i} for i in sorted(df["Tempo para titulação (meses)"].dropna().unique())],
            multi=True,
            placeholder="Selecione Titulação (meses)",
            style={"backgroundColor": "#2c2c2c", "color": "black"}
        ), md=3
    ),
    dbc.Col(
        dcc.Dropdown(
            id='filtro-raca',
            options=[{'label': i, 'value': i} for i in df["Raça/Cor"].dropna().unique()],
            multi=True,
            placeholder="Selecione Raça/Cor",
            style={"backgroundColor": "#2c2c2c", "color": "black"}
        ), md=3
    ),
    dbc.Col(
        dcc.Dropdown(
            id='filtro-sexo',
            options=[{'label': i, 'value': i} for i in df["Sexo"].dropna().unique()],
            multi=True,
            placeholder="Selecione Sexo",
            style={"backgroundColor": "#2c2c2c", "color": "black"}
        ), md=3
    ),
], className="mb-3"),

dbc.Row([
    # Segunda linha de filtros
    dbc.Col(
        dcc.Dropdown(
            id='filtro-pcd',
            options=[{'label': i, 'value': i} for i in df["Pessoa com Deficiência"].dropna().unique()],
            multi=True,
            placeholder="PCD",
            style={"backgroundColor": "#2c2c2c", "color": "black"}
        ), md=3
    ),
    dbc.Col(
        dcc.DatePickerRange(
            id='filtro-periodo',
            min_date_allowed=df["Primeira matrícula"].min().date() if "Primeira matrícula" in df.columns else None,
            max_date_allowed=df["Primeira matrícula"].max().date() if "Primeira matrícula" in df.columns else None,
            start_date=df["Primeira matrícula"].min().date() if "Primeira matrícula" in df.columns else None,
            end_date=df["Primeira matrícula"].max().date() if "Primeira matrícula" in df.columns else None,
            display_format='DD/MM/YYYY',
            style={"backgroundColor": "#2c2c2c", "color": "white", "height": "38px"}
        ), md=3
    ),
], className="mb-4"),

    # Primeira Linha de Gráficos
    dbc.Row([
        html.H4("Perfil Demográfico", className="text-secondary mb-3"),
        dbc.Col(dcc.Graph(id='raca-graph'), md=6, className="mb-4"),
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id='pcd-graph'), md=6),
                dbc.Col(dcc.Graph(id='sexo-graph'), md=6),
            ])
        ], md=6, className="mb-4"),
    ], className="g-4"),

    # Segunda Linha de Gráficos
    dbc.Row([
        html.H4("Perfil Acadêmico e Financeiro", className="text-secondary my-3"),
        dbc.Col(dcc.Graph(id='titulacao-graph'), md=5, className="mb-4"),
        dbc.Col(dcc.Graph(id='financiamento-graph'), md=7, className="mb-4"),
    ], className="g-4"),
], fluid=True)

#|===========================================================================|
#|                  Callbacks Para Aplicação de Filtro                       |
#|===========================================================================|
def register_callbacks(app):
    @app.callback(
        [
            Output('raca-graph', 'figure'),
            Output('pcd-graph', 'figure'),
            Output('sexo-graph', 'figure'),
            Output('titulacao-graph', 'figure'),
            Output('financiamento-graph', 'figure'),
        ],
        [
            Input('filtro-financiamento', 'value'),
            Input('filtro-titulacao', 'value'),
            Input('filtro-pcd', 'value'),
            Input('filtro-sexo', 'value'),
            Input('filtro-raca', 'value'),
            Input('filtro-periodo', 'start_date'),
            Input('filtro-periodo', 'end_date'),
        ]
    )
    def atualizar_graficos(financiamento, titulacao, pcd, sexo, raca, start_date, end_date):
        dff = df.copy()

        # -------------------------
        # Normalizações
        dff["Raça/Cor"] = dff["Raça/Cor"].fillna("Não informado").replace(
            ["", " ", "Prefiro não informar"], "Não informado"
        )
        dff["Pessoa com Deficiência"] = dff["Pessoa com Deficiência"].fillna("Não informado").replace(
            ["", " "], "Não informado"
        )

        # -------------------------
        # Aplicar filtros
        if financiamento:
            dff = dff[dff["Financiamento"].isin(financiamento)]
        if titulacao:
            dff = dff[dff["Tempo para titulação (meses)"].isin(titulacao)]
        if pcd:
            dff = dff[dff["Pessoa com Deficiência"].isin(pcd)]
        if sexo:
            dff = dff[dff["Sexo"].isin(sexo)]
        if raca:
            dff = dff[dff["Raça/Cor"].isin(raca)]
        if start_date and end_date and "Primeira matrícula" in dff.columns:
            dff["Primeira matrícula"] = pd.to_datetime(dff["Primeira matrícula"], errors="coerce")
            dff = dff[
                (dff["Primeira matrícula"] >= pd.to_datetime(start_date)) &
                (dff["Primeira matrícula"] <= pd.to_datetime(end_date))
            ]

        # -------------------------
        # Raça/Cor
        if "Raça/Cor" in dff.columns:
            df_raca = dff["Raça/Cor"].value_counts().reset_index()
            df_raca.columns = ["Raça/Cor", "Total"]
            fig_raca = px.bar(
                df_raca, x="Raça/Cor", y="Total",
                title="Distribuição por Raça/Cor",
                template=TEMPLATE, text_auto=True
            )
            fig_raca.update_traces(textposition="outside")
        else:
            fig_raca = create_empty_fig("Raça/Cor")

        # -------------------------
        # PCD
        if "Pessoa com Deficiência" in dff.columns:
            df_pcd = dff["Pessoa com Deficiência"].value_counts().reset_index()
            df_pcd.columns = ["Categoria", "Total"]
            fig_pcd = px.pie(
                df_pcd, names="Categoria", values="Total",
                title="Pessoas com Deficiência (PCD)",
                hole=0.4, template=TEMPLATE
            )
            fig_pcd.update_traces(textinfo="percent+label")
        else:
            fig_pcd = create_empty_fig("Pessoa com Deficiência")

        # -------------------------
        # Sexo
        if "Sexo" in dff.columns:
            df_sexo = dff["Sexo"].value_counts().reset_index()
            df_sexo.columns = ["Sexo", "Total"]
            fig_sexo = px.pie(
                df_sexo, names="Sexo", values="Total",
                title="Distribuição por Sexo",
                hole=0.4, template=TEMPLATE
            )
            fig_sexo.update_traces(textinfo="percent+label")
        else:
            fig_sexo = create_empty_fig("Sexo")

        # -------------------------
        # Titulação (apenas titulados, se existir "Última ocorrência")
        if "Tempo para titulação (meses)" in dff.columns:
            if "Última ocorrência" in dff.columns:
                dff_titulados = dff[dff["Última ocorrência"] == "Titulado"]
            else:
                dff_titulados = dff.copy()

            if not dff_titulados.empty:
                fig_titulacao = px.histogram(
                    dff_titulados.dropna(subset=["Tempo para titulação (meses)"]),
                    x="Tempo para titulação (meses)",
                    nbins=40,
                    title="Distribuição do Tempo para Titulação",
                    labels={"Tempo para titulação (meses)": "Meses"},
                    template=TEMPLATE
                )
                fig_titulacao.update_yaxes(title_text="Quantidade")
                fig_titulacao.update_layout(
                    bargap=0.2,
                    bargroupgap=0.1,
                    xaxis_title="Meses para Titulação"
                )
            else:
                fig_titulacao = create_empty_fig("Tempo para titulação (meses)")
        else:
            fig_titulacao = create_empty_fig("Tempo para titulação (meses)")

        # -------------------------
        # Financiamento
        if "Financiamento" in dff.columns:
            df_fin = dff["Financiamento"].value_counts().reset_index()
            df_fin.columns = ["Financiamento", "Total"]
            fig_fin = px.bar(
                df_fin, x="Financiamento", y="Total",
                title="Fontes de Financiamento",
                template=TEMPLATE, text_auto=True
            )
            fig_fin.update_traces(textposition="outside")
        else:
            fig_fin = create_empty_fig("Financiamento")
        # -------------------------
        # Fundo transparente em todos
        for f in [fig_raca, fig_pcd, fig_sexo, fig_titulacao, fig_fin]:
            f.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

        return fig_raca, fig_pcd, fig_sexo, fig_titulacao, fig_fin

        # -------------------------
        # Retorno final (sempre 5 figuras, na ordem dos Outputs)
        return fig_raca, fig_pcd, fig_sexo, fig_titulacao, fig_fin
        
