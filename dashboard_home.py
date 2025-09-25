import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Importar os layouts das páginas
from pages import home, page1, page2, page3

#===========================================================================|
#|                           Inicialização do App                          |
#===========================================================================|
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.VAPOR, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Registrar callbacks da Page1
page1.register_callbacks(app)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#===========================================================================|
#|                  Layout Principal com Estrutura Fixa                    |
#===========================================================================|
app.layout = html.Div(className="home-dashboard-scope", children=[
    dcc.Location(id='url', refresh=False),

    dbc.Container([
        # Cabeçalho
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H1("Dashboard de Alunos", className="app-header-title"),
                    html.P("Análise geral da situação de alunos e programas.", className="app-header-subtitle")
                ]),
                width=12, className="mb-4 mt-4"
            )
        ),
        # Menu
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(html.H5("Navegação", className="card-title mb-0"), width="auto"),
                            dbc.Col([
                                dbc.Button([html.I(className="bi bi-house-door-fill me-2"), "Home"], color="dark", href="/", className="ms-md-2"),
                                dbc.Button([html.I(className="bi bi-kanban-fill me-2"), "Informações Acadêmicas"], color="primary", href="/page1", className="ms-md-2 mt-2 mt-md-0"),
                                dbc.Button([html.I(className="bi bi-bar-chart-line-fill me-2"), "Análise Acadêmica"], color="secondary", href="/page2", className="ms-md-2 mt-2 mt-md-0"),
                                dbc.Button([html.I(className="bi bi-file-earmark-arrow-down-fill me-2"), "Exploração Acadêmica"], color="info", href="/page3", className="ms-md-2 mt-2 mt-md-0"),
                            ], width="auto", className="text-end")
                        ], justify="between", align="center")
                    ])
                ),
                width=12
            )
        , className="mb-4 g-4"),

        # Conteúdo
        html.Div(id='page-content')
    ], fluid=True)
])

#===========================================================================|
#|                  Callback para Renderizar as Páginas                    |
#===========================================================================|
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page1':
        return page1.layout
    elif pathname == '/page2':
        return page2.layout
    elif pathname == '/page3':
        return page3.layout
    else:
        return home.layout

#===========================================================================|
#|                    Helpers para gráficos vazios                         |
#===========================================================================|
def _empty_fig(title):
    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        title=title,
        xaxis_visible=False, yaxis_visible=False,
        annotations=[dict(text="Sem dados para os filtros", x=0.5, y=0.5, showarrow=False)]
    )
    return fig

#===========================================================================|
#|              Callbacks para atualizar gráficos da Page2                 |
#===========================================================================|
@app.callback(
    [
        Output("fig2", "figure"),
        Output("fig3", "figure"),
        Output("fig5", "figure"),
        Output("fig6", "figure"),
        Output("fig7", "figure"),
        Output("variacao-label", "children"),
        Output("variacao-label", "className"),
    ],
    [
        Input("filtro-programa", "value"),
        Input("filtro-curso", "value"),
        Input("filtro-ativos", "value"),
        Input("filtro-periodo2", "start_date"),
        Input("filtro-periodo2", "end_date"),
    ]
)
def atualizar_page2(programa, curso, status, start_date, end_date):
    df = page2.df.copy()

    # Filtros
    if programa:
        df = df[df["Programa"].isin(programa)]
    if curso:
        df = df[df["Curso"].isin(curso)]
    if status:
        df = df[df["Status_aluno"].isin(status)]
    if start_date and end_date and "Primeira matrícula" in df.columns:
        df["Primeira matrícula"] = pd.to_datetime(df["Primeira matrícula"], errors="coerce")
        df = df[
            (df["Primeira matrícula"] >= pd.to_datetime(start_date)) &
            (df["Primeira matrícula"] <= pd.to_datetime(end_date))
        ]

    TEMPLATE = "plotly_dark"

    # fig1 - Histograma período
    fig1 = (_empty_fig("Tempo de Curso (Meses)") if df.empty else
            px.histogram(df, x="período_meses_inteiros", nbins=50,
                         title="Tempo de Curso (Meses)",
                         #labels={"período_meses_inteiros": "Meses desde a Matrícula"},
                         template=TEMPLATE))
    fig1.update_layout(
        yaxis_title="Nº de Alunos",
        xaxis_title="Meses desde a Matrícula",
        bargap=0.2,
        bargroupgap=0.1,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        title_x=0.5
    )
    # fig2 - Matrículas por ano
    df_matriculas = df.groupby("Ano_matricula").size().reset_index(name="Total").sort_values("Ano_matricula")
    if df_matriculas.empty:
        fig2 = _empty_fig("Número de Matrículas por Ano")
    else:
        df_matriculas["Ano"] = df_matriculas["Ano_matricula"].astype(str)
        fig2 = px.bar(df_matriculas, x="Ano", y="Total",
                      title="Número de Matrículas por Ano",
                      labels={"Ano": "Ano da Matrícula", "Total": "Nº de Alunos"},
                      template=TEMPLATE, barmode='group')
        fig2.update_traces(text=df_matriculas["Total"], textposition="outside")
        fig2.update_layout(yaxis=dict(range=[0, max(df_matriculas["Total"].max(), 5)]), # Metodo Antigo 
        xaxis_tickangle=-45,  # nomes na diagonal    
        bargap=0.2,
        bargroupgap=0.1,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        title_x=0.5
        )      
        
    # fig3 - Comparativo (ano atual vs anterior)
    ano_atual = pd.Timestamp.today().year
    ano_anterior = ano_atual - 1
    atual = df[df["Ano_matricula"] == ano_atual].shape[0]
    anterior = df[df["Ano_matricula"] == ano_anterior].shape[0]
    resumo = pd.DataFrame({"Ano": [str(ano_anterior), str(ano_atual)], "Matriculados": [anterior, atual]})
    if resumo["Matriculados"].sum() == 0:
        fig3 = _empty_fig(f"Comparativo de Matrículas ({ano_anterior} vs {ano_atual})")
    else:
        fig3 = px.bar(resumo, x="Ano", y="Matriculados",
                      title=f"Comparativo de Matrículas ({ano_anterior} vs {ano_atual})",
                      text_auto=True, template=TEMPLATE)        
        fig3.update_traces(textposition="outside", textfont=dict(size=14))
        #fig3.update_layout(yaxis=dict(range=[0, max(resumo["Matriculados"].max(), 5)])) # Metodo Antigo       
        fig3.update_layout(yaxis=dict(range=[0, resumo["Matriculados"].max() * 1.2]))  # 20% a mais
    fig3.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
    )  

    # fig5 - Status
    if df.empty:
        fig5 = _empty_fig("Distribuição de Status dos Alunos")
    else:
        df_status = df["Status_aluno"].value_counts().reset_index()
        df_status.columns = ["Status", "Total"]
        df_status = df_status[df_status["Total"] > 0]
        df_status = df_status[df_status["Total"] >= df_status["Total"].sum() * 0.005]  # remover fatias irrelevantes
        if df_status.empty:
            fig5 = _empty_fig("Distribuição de Status dos Alunos")
        else:
            fig5 = px.pie(df_status, values="Total", names="Status",
                          title="Distribuição de Status dos Alunos",
                          hole=0.5, template=TEMPLATE)
    fig5.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
    )

    # fig6 - Nacionalidade
    tot_br = df[df["Nacionalidade"].str.lower() == "brasileira"].shape[0]
    tot_est = df[~df["Nacionalidade"].str.lower().isin(["brasileira"])].shape[0]
    df_nac = pd.DataFrame({"Nacionalidade": ["Brasileiros", "Estrangeiros"], "Total": [tot_br, tot_est]})
    fig6 = (_empty_fig("Nacionalidade dos Alunos (Geral)") if df_nac["Total"].sum() == 0
            else px.pie(df_nac, values="Total", names="Nacionalidade",
                        title="Nacionalidade dos Alunos (Geral)", template=TEMPLATE))
    fig6.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
    )

    # fig7 - Estrangeiros
    estrangeiros_counts = (
        df[~df["Nacionalidade"].str.lower().isin(["brasileira"])]
        .value_counts(subset=["Nacionalidade"]).reset_index(name="Total")
        .rename(columns={"Nacionalidade": "País"})
    )
    fig7 = (_empty_fig("Distribuição de Alunos Estrangeiros") if estrangeiros_counts.empty
            else px.bar(estrangeiros_counts, x="País", y="Total",
                        title="Distribuição de Alunos Estrangeiros",
                        labels={"País": "País", "Total": "Nº de Alunos"},
                        template=TEMPLATE))
    fig7.update_layout(
    xaxis_tickangle=-45,  # nomes na diagonal
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
    )

    # Variação
    variacao = ((atual - anterior) / anterior) * 100 if anterior > 0 else 0
    variacao_texto = f"{variacao:.2f}%"
    variacao_classe = "card-text text-center display-4 text-success" if variacao >= 0 else "card-text text-center display-4 text-danger"

    return fig2, fig3, fig5, fig6, fig7, variacao_texto, variacao_classe

#===========================================================================|
#|                             Executar o App                              |
#===========================================================================|
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)





