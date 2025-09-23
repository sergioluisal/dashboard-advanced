# Todas as suas importações aqui
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from pages import home, page1, page2, page3

# --- Bloco de Inicialização (CRÍTICO) ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# --- Layout Principal da Aplicação ---
app.layout = html.Div(...)

# --- Callback para a Navegação ---
@app.callback(...)
def display_page(pathname):
    # ... sua lógica de navegação ...

#===========================================================================|
#|                             Executar o App                              |
#|===========================================================================|
#if __name__ == '__main__':
    #app.run(debug=True)

import os
from dash import Dash, html

app = Dash(__name__)
server = app.server  # importante para o Render reconhecer

app.layout = html.Div("Hello Render!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # pega a porta do Render
    app.run(host="0.0.0.0", port=port, debug=False)
