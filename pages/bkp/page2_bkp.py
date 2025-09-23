import dash_bootstrap_components as dbc
from dash import html

layout = dbc.Container([
    html.H1("Página de Análise Detalhada", className="app-header-title mt-4"),
    html.P("Aqui você pode adicionar gráficos e análises mais complexas.", className="app-header-subtitle"),
    html.Hr(), # Uma linha horizontal para separar
    
    # Botão para voltar para a página inicial
    dbc.Button(
        [html.I(className="bi bi-house-door-fill me-2"), "Voltar para a Home"],
        href="/", # O href "/" representa a página inicial
        color="primary"
    )
    # Adicione aqui os componentes da sua segunda página...
])

