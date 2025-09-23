import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

#===========================================================================|
#|                           Inicialização do App                          |
#|===========================================================================|
# AQUI ESTÁ A MUDANÇA: Usando o tema VAPOR que estava no seu outro script
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server

#===========================================================================|
#|                           Carregar e Tratar Dados                       |
#|===========================================================================|
try:
    df = pd.read_excel("USP_Completa.xlsx")
    df["Primeira matrícula"] = pd.to_datetime(df["Primeira matrícula"], errors="coerce")
    df.dropna(subset=["Primeira matrícula"], inplace=True)
    df["Curso"] = df["Curso"].replace("Doutorado Direto", "Doutorado")
    df['Mes_Ano_Matricula'] = df['Primeira matrícula'].dt.to_period('M').astype(str)

except FileNotFoundError:
    print("AVISO: Arquivo 'USP_Completa.xlsx' não encontrado. Usando dados de exemplo para rodar o app.")
    df = pd.DataFrame({
        "Programa": ["Física", "Química", "Física", "Biologia", "Química"],
        "Curso": ["Mestrado", "Doutorado", "Doutorado", "Mestrado", "Mestrado"],
        "Primeira matrícula": pd.to_datetime(["2022-03-15", "2022-08-20", "2023-03-10", "2023-08-25", "2024-03-12"]),
    })
    df['Mes_Ano_Matricula'] = df['Primeira matrícula'].dt.to_period('M').astype(str)

programas_opcoes = sorted(df["Programa"].unique())
cursos_opcoes = sorted(df["Curso"].unique())
min_date = df["Primeira matrícula"].min()
max_date = df["Primeira matrícula"].max()


#===========================================================================|
#|                              Layout do App                              |
#|===========================================================================|
TEMPLATE = "plotly_dark"

app.layout = dbc.Container([
    # Linha do Título
    dbc.Row(
        dbc.Col(html.H1("Dashboard - Informações Pessoais e Acadêmicas", className="text-center text-primary my-4"), width=12)
    ),
        dbc.Row(
            dbc.Col(html.H1("Analítico com Filtros", className="text-center my-4"), width=12)
        ),
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
                                    placeholder="Selecione o(s) Programa(s)"
                                ), md=4
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='filtro-curso',
                                    options=[{'label': i, 'value': i} for i in cursos_opcoes],
                                    multi=True,
                                    placeholder="Selecione o(s) Curso(s)"
                                ), md=4
                            ),
                            dbc.Col(
                                dcc.DatePickerRange(
                                    id='filtro-periodo',
                                    min_date_allowed=min_date.date(),
                                    max_date_allowed=max_date.date(),
                                    initial_visible_month=max_date.date(),
                                    start_date=min_date.date(),
                                    end_date=max_date.date(),
                                    display_format='DD/MM/YYYY'
                                ), md=4
                            ),
                        ])
                    ])
                ], className="bg-dark"), # Adicionado bg-dark para o cartão
                width=12,
                className="mb-4"
            )
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Total de Alunos Selecionados", className="card-title text-center"),
                    html.P(id='kpi-total-alunos', className="display-4 text-center mt-3")
                ])
            ]), md=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='grafico-evolucao-matriculas'), md=8, className="mt-4"),
            dbc.Col(dcc.Graph(id='grafico-distribuicao-curso'), md=4, className="mt-4"),
        ], className="g-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id='grafico-distribuicao-programa'), md=12, className="mt-4"),
        ])
    ], fluid=True)


#===========================================================================|
#|                      Callback para Interatividade                       |
#|===========================================================================|
@app.callback(
    [
        Output('kpi-total-alunos', 'children'),
        Output('grafico-evolucao-matriculas', 'figure'),
        Output('grafico-distribuicao-curso', 'figure'),
        Output('grafico-distribuicao-programa', 'figure')
    ],
    [
        Input('filtro-programa', 'value'),
        Input('filtro-curso', 'value'),
        Input('filtro-periodo', 'start_date'),
        Input('filtro-periodo', 'end_date')
    ]
)
def update_dashboard(programas_selecionados, cursos_selecionados, start_date, end_date):
    dff = df.copy()
    if start_date and end_date:
        dff = dff[(dff['Primeira matrícula'] >= start_date) & (dff['Primeira matrícula'] <= end_date)]
    if programas_selecionados:
        dff = dff[dff['Programa'].isin(programas_selecionados)]
    if cursos_selecionados:
        dff = dff[dff['Curso'].isin(cursos_selecionados)]

    total_alunos = len(dff)

    evolucao = dff.groupby(['Mes_Ano_Matricula', 'Curso']).size().reset_index(name='Quantidade')
    fig_evolucao = px.line(
        evolucao, x='Mes_Ano_Matricula', y='Quantidade', color='Curso',
        title="Evolução de Novas Matrículas por Mês", template=TEMPLATE, markers=True
    )
    fig_evolucao.update_layout(yaxis_title="Nº de Alunos", xaxis_title="Período", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    dist_curso = dff['Curso'].value_counts().reset_index()
    dist_curso.columns = ['Curso', 'Total']
    fig_dist_curso = px.pie(
        dist_curso, names='Curso', values='Total',
        title="Distribuição por Curso", template=TEMPLATE, hole=0.4
    )
    fig_dist_curso.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    dist_programa = dff['Programa'].value_counts().nlargest(15).reset_index()
    dist_programa.columns = ['Programa', 'Total']
    fig_dist_programa = px.bar(
        dist_programa, y='Programa', x='Total', orientation='h',
        title="Top 15 Programas por Nº de Alunos", template=TEMPLATE
    )
    fig_dist_programa.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Nº de Alunos", yaxis_title=None, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    return total_alunos, fig_evolucao, fig_dist_curso, fig_dist_programa

if __name__ == '__main__':
    app.run(debug=True)