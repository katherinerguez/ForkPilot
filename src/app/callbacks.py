from dash.dependencies import Input, Output
from dash import html

def register_callbacks(app, rag): 
    @app.callback(
        [Output("response-container", "children"),
         Output("links-container", "children")],
        [Input("search-button", "n_clicks")],
        [Input("user-query", "value")]
    )
    def generate_response(n_clicks, query):
        if not n_clicks or not query:
            return "", ""

        docs = rag.retrieve(query)
        response = rag.generate(query)

        response_display = html.Div(response, className="response-text")

        unique_docs = {}
        for doc in docs:
            uid = doc.metadata.get("id")
            if uid and uid not in unique_docs:
                unique_docs[uid] = doc

        links_display = [
            html.Div([
                html.Strong(unique_docs[uid].metadata["title"]),
                html.Br(),
                html.A("Acceder a la receta", href=unique_docs[uid].metadata["url"], target="_blank", className="link-item")
            ], className="document-item")
            for uid in unique_docs
        ]

        return response_display, links_display