import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, register_page, callback
import os # Certifique-se de que esta linha está no topo do arquivo com os outros imports

# ============================================================
# Carregar e Tratar Dados
# ============================================================
try:
    # Constrói o caminho absoluto para o arquivo de dados
    # Sobe um nível de diretório (da pasta 'pages' para a pasta raiz)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Junta o caminho da pasta raiz com o nome do arquivo
    DATA_PATH = os.path.join(BASE_DIR, "USP_Completa.xlsx")
    
    # Tenta carregar o DataFrame usando o caminho completo
    df = pd.read_excel(DATA_PATH)
    print(f"SUCESSO (page3.py): Arquivo de dados carregado de '{DATA_PATH}'")

    # Continua com o tratamento de dados APENAS se o arquivo foi carregado
    df["Primeira matrícula"] = pd.to_datetime(df["Primeira matrícula"], errors="coerce")
    df.dropna(subset=["Primeira matrícula"], inplace=True)
    df["Curso"] = df["Curso"].replace("Doutorado Direto", "Doutorado")
    df['Mes_Ano_Matricula'] = df['Primeira matrícula'].dt.to_period('M').astype(str)

except FileNotFoundError:
    print(f"ERRO CRÍTICO (page3.py): O arquivo 'USP_Completa.xlsx' não foi encontrado no caminho esperado: '{DATA_PATH}'.")
    # Cria um DataFrame vazio com as colunas esperadas para evitar que o resto do app quebre
    df = pd.DataFrame(columns=["Programa", "Curso", "Primeira matrícula", "Mes_Ano_Matricula"])

except Exception as e:
    print(f"ERRO INESPERADO (page3.py) ao carregar ou tratar os dados: {e}")
    df = pd.DataFrame(columns=["Programa", "Curso", "Primeira matrícula", "Mes_Ano_Matricula"])

# FIM DO NOVO CÓDIGO


programas_opcoes = sorted(df["Programa"].unique())
cursos_opcoes = sorted(df["Curso"].unique())
min_date = df["Primeira matrícula"].min()
max_date = df["Primeira matrícula"].max()

TEMPLATE = "plotly_dark"

# ==============================================================
# Layout da Página
# ==============================================================
layout = dbc.Container([
    # Linha do título
    dbc.Row(
        dbc.Col(html.H1("Informações Acadêmicas",
                        className="text-center text-primary my-4"), width=12)
    ),
    dbc.Row(
        dbc.Col(html.H1("Filtros Analíticos",
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
                            dcc.DatePickerRange(
                                id='filtro-periodo',
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date(),
                                initial_visible_month=max_date.date(),
                                start_date=min_date.date(),
                                end_date=max_date.date(),
                                display_format='DD/MM/YYYY',
                                #locale='pt-br',
                                style={"backgroundColor": "#2c2c2c", "color": "white"}
                            ), 
                            md=4
                        )
                    ])
                ])
            ], className="bg-dark"),
            width=12,
            className="mb-4"
        )
    ]),

    # KPI
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Total de Alunos Selecionados", className="card-title text-center"),
                html.P(id='kpi-total-alunos', className="display-4 text-center mt-3")
            ])
        ]), md=4),
    ]),

    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-evolucao-matriculas'), md=8, className="mt-4"),
        dbc.Col(dcc.Graph(id='grafico-distribuicao-curso'), md=4, className="mt-4"),
    ], className="g-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-distribuicao-programa'), md=12, className="mt-4"),
    ])
], fluid=True)


# ==============================================================
# Callbacks da Página
# ==============================================================
@callback(
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
    fig_evolucao = px.area(
        evolucao, x='Mes_Ano_Matricula', y='Quantidade', color='Curso',
        title="Evolução de Novas Matrículas por Mês", template=TEMPLATE
    )
    fig_evolucao.update_layout(
        yaxis_title="Nº de Alunos", xaxis_title="Período",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )

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
        title="Nº de Alunos por Programas", template=TEMPLATE
    )
    fig_dist_programa.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Nº de Alunos", yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )

    return total_alunos, fig_evolucao, fig_dist_curso, fig_dist_programa
