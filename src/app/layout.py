from dash import html, dcc
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(className="app-header", children=[
                    html.Img(src="/assets/logo_cocina.png", className="logo"),
                    html.H1("🍽️ Asistente Gastronómico"),
                    html.P("Explora recetas, técnicas y secretos de cocina con inteligencia aumentada.")
                ])
            ])
        ], justify="center"),

        dbc.Row([
            dbc.Col([
                html.Div(className="search-section", children=[
                    dbc.Input(
                        id="user-query", 
                        type="text", 
                        placeholder="🔍 ¿Qué deseas cocinar hoy?", 
                        className="search-bar"
                    ),
                    dbc.Button("Buscar", id="search-button", className="btn-search"),
                    html.Div(id="response-container", className="response-container")
                ])
            ], md=8),

            dbc.Col([
                html.Div(className="recommendations-sidebar", children=[
                    html.H4("Puede que te interese"),
                    html.Ul(id="recommendations-list", className="recommendation-list")
                ])
            ], md=4)
        ], justify="center")
    ])
])
