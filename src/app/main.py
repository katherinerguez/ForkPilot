import dash
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import os
from layout import layout
from callbacks import register_callbacks
from rag import RAG

rag = RAG()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout

register_callbacks(app, rag)

if __name__ == "__main__":
    app.run(debug=True)