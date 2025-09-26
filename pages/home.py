import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

#===========================================================================|
#|                Carregar, Tratar Dados e Criar Gráficos                  |
#|===========================================================================|
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

# Classificar Alunos
ativos_list = ["Matrícula de Acompanhamento", "Matriculado", "Mudança de Nível", "Prorrogação", "Trancado", "Transferido de Área"]
def classificar_aluno(row):
    if row["Última ocorrência"] in ativos_list: return "Ativo"
    elif row["Última ocorrência"] == "Titulado": return "Titulado"
    else: return "Outro"
df["Status"] = df.apply(classificar_aluno, axis=1)
df["Curso"] = df["Curso"].replace("Doutorado Direto", "Doutorado")
df_filtrado = df[df["Status"].isin(["Ativo", "Titulado"])]

# Calcular KPIs
total_ativos = len(df_filtrado[df_filtrado["Status"] == "Ativo"])
total_titulados = len(df_filtrado[df_filtrado["Status"] == "Titulado"])
total_geral = len(df_filtrado)

# Criar Gráficos
TEMPLATE = "plotly_dark"
CORES_GRAFICO = ["#00e5ff", "#f800ff"]
df_mestrado = df_filtrado[df_filtrado["Curso"] == "Mestrado"]["Status"].value_counts().reset_index()
df_mestrado.columns = ['Status', 'Total']
fig_mestrado = px.pie(df_mestrado, values='Total', names='Status', title="Mestrado", hole=.4, template=TEMPLATE, color_discrete_sequence=CORES_GRAFICO)

df_doutorado = df_filtrado[df_filtrado["Curso"] == "Doutorado"]["Status"].value_counts().reset_index()
df_doutorado.columns = ['Status', 'Total']
fig_doutorado = px.pie(df_doutorado, values='Total', names='Status', title="Doutorado", hole=.4, template=TEMPLATE, color_discrete_sequence=CORES_GRAFICO)

for fig in [fig_mestrado, fig_doutorado]:
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_x=0.5, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))

#===========================================================================|
#|                   Layout do Conteúdo da Página Home                     |
#| ESTA LINHA É ESSENCIAL. Ela define a variável que o ficheiro principal procura.|
#|===========================================================================|
layout = html.Div([
    # --- Linha de KPIs ---
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Alunos Ativos", className="card-title"), html.P(f"{total_ativos}", className="card-value")])), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Alunos Titulados", className="card-title"), html.P(f"{total_titulados}", className="card-value")])), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Total Geral", className="card-title"), html.P(f"{total_geral}", className="card-value")])), md=4),
    ], className="mb-4 g-4"),

    # --- Linha de Gráficos ---
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_mestrado, config={'displayModeBar': False}), md=6),
        dbc.Col(dcc.Graph(figure=fig_doutorado, config={'displayModeBar': False}), md=6),
    ], className="g-4")
])

