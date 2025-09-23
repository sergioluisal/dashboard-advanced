import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

#===========================================================================|
#|                           Inicialização do App                          |
#|===========================================================================|
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

#===========================================================================|
#|                           Carregar e Tratar Dados                       |
#|===========================================================================|
try:
    df = pd.read_excel("USP_Completa.xlsx")
except FileNotFoundError:
    print("AVISO: Arquivo 'USP_Completa.xlsx' não encontrado. Usando dados de exemplo para rodar o app.")
    df = pd.DataFrame({
        "Raça/Cor": ["Branca", "Parda", "Preta", "Parda", "Branca"],
        "Pessoa com Deficiência": ["Não", "Não", pd.NA, "Sim", "Não"],
        "Sexo": ["Masculino", "Feminino", "Feminino", "Masculino", "Feminino"],
        "Tempo para titulação (meses)": [24, 30, 28, 35, 26],
        "Financiamento": ["CAPES", "Sem informação", "CNPq", "CAPES", "Outro"]
    })

#===========================================================================|
#|                           Criação dos Gráficos                          |
#|===========================================================================|

# A MUDANÇA CRÍTICA ESTÁ AQUI:
# Usamos um tema interno do Plotly que corresponde ao visual escuro.
TEMPLATE = "plotly_dark"

figs = {} # Dicionário para armazenar as figuras

# --- Função para criar um gráfico vazio em caso de erro ---
def create_empty_fig(column_name):
    fig = go.Figure()
    fig.update_layout(
        title=f"Dados para '{column_name}' não encontrados",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#CCCCCC"),
        xaxis_visible=False,
        yaxis_visible=False,
        annotations=[dict(
            text="Verifique se a coluna existe no arquivo Excel",
            showarrow=False,
            font=dict(size=14, color="#CCCCCC")
        )]
    )
    return fig

# --- Gráfico de Raça/Cor ---
try:
    df_classificacao = df["Raça/Cor"].value_counts().sort_index().reset_index()
    df_classificacao.columns = ["Raça/Cor", "Total"]
    figs['raca'] = px.bar(
        df_classificacao, x="Raça/Cor", y="Total",
        title="Distribuição por Raça/Cor",
        template=TEMPLATE, text_auto=True
    )
except KeyError:
    figs['raca'] = create_empty_fig("Raça/Cor")

# --- Gráfico de Pessoa com Deficiência (PCD) ---
try:
    df["Pessoa com Deficiência"] = df["Pessoa com Deficiência"].fillna("Sem informação").replace("", "Sem informação")
    df_pcd = df["Pessoa com Deficiência"].value_counts().sort_index().reset_index()
    df_pcd.columns = ["Categoria", "Total"]
    figs['pcd'] = px.pie(
        df_pcd, names="Categoria", values="Total",
        title="Pessoas com Deficiência (PCD)",
        hole=0.4, template=TEMPLATE
    )
except KeyError:
    figs['pcd'] = create_empty_fig("Pessoa com Deficiência")

# --- Gráfico de Sexo ---
try:
    df_sexo = df["Sexo"].value_counts().sort_index().reset_index()
    df_sexo.columns = ["Sexo", "Total"]
    figs['sexo'] = px.pie(
        df_sexo, names="Sexo", values="Total",
        title="Distribuição por Sexo",
        hole=0.4, template=TEMPLATE
    )
except KeyError:
    figs['sexo'] = create_empty_fig("Sexo")

# --- Gráfico de Tempo de Titulação ---
try:
    df["Tempo para titulação (meses)"] = pd.to_numeric(df["Tempo para titulação (meses)"], errors="coerce")
    figs['titulacao'] = px.histogram(
        df.dropna(subset=["Tempo para titulação (meses)"]),
        x="Tempo para titulação (meses)", nbins=40,
        title="Distribuição do Tempo para Titulação",
        labels={"Tempo para titulação (meses)": "Meses"},
        template=TEMPLATE
    )
except KeyError:
    figs['titulacao'] = create_empty_fig("Tempo para titulação (meses)")

# --- Gráfico de Financiamento ---
try:
    df["Financiamento"] = df["Financiamento"].fillna("Sem informação").replace("", "Sem informação")
    df_fin_cat = df["Financiamento"].value_counts().sort_index().reset_index()
    df_fin_cat.columns = ["Financiamento", "Total"]
    figs['financiamento'] = px.bar(
        df_fin_cat, x="Total", y="Financiamento",
        title="Fontes de Financiamento",
        orientation='h', # Gráfico de barras horizontais
        template=TEMPLATE, text_auto=True
    )
    figs['financiamento'].update_yaxes(categoryorder="total ascending") # Ordena do menor para o maior
except KeyError:
    figs['financiamento'] = create_empty_fig("Financiamento")

# --- Atualizar layout de todos os gráficos criados ---
for fig in figs.values():
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        title_x=0.5
    )

#===========================================================================|
#|                              Layout do App                              |
#|===========================================================================|
app.layout = dbc.Container([
    # Linha do Título
    dbc.Row(
        dbc.Col(html.H1("Dashboard - Informações Pessoais e Acadêmicas", className="text-center text-primary my-4"), width=12)
    ),

    # --- Primeira Linha de Gráficos (Informações Demográficas) ---
    dbc.Row([
        html.H3("Perfil Demográfico", className="text-secondary mb-3"),
        # Coluna para o gráfico de Raça/Cor, ocupando metade da tela
        dbc.Col(dcc.Graph(figure=figs.get('raca')), md=6, className="mb-4"),
        
        # Coluna para os dois gráficos menores (PCD e Sexo)
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=figs.get('pcd')), md=6),
                dbc.Col(dcc.Graph(figure=figs.get('sexo')), md=6),
            ])
        ], md=6, className="mb-4"),

    ], className="g-4"),

    # --- Segunda Linha de Gráficos (Informações Acadêmicas) ---
    dbc.Row([
        html.H3("Perfil Acadêmico e Financeiro", className="text-secondary my-3"),
        # Coluna para o Tempo de Titulação
        dbc.Col(dcc.Graph(figure=figs.get('titulacao')), md=6, className="mb-4"),

        # Coluna para o Financiamento
        dbc.Col(dcc.Graph(figure=figs.get('financiamento')), md=6, className="mb-4"),
    ], className="g-4"),

], fluid=True)


if __name__ == '__main__':
    app.run(debug=True)
