from dash.dependencies import Input, Output
from dash import html
from dash.dependencies import Input, Output

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
        
        context_docs_and_scores = rag.retrieve(query)
        context_docs = [doc for doc, _ in context_docs_and_scores]
        response = rag.generate(query, context_docs)

        response_display = html.Div(response, className="response-text")
        links_display = [
            html.Div([
                html.Strong(f"{doc.metadata['title']} - Relevancia: {score:.4f}"),
                html.Br(),
                html.A("Acceda al artículo aquí", href=doc.metadata['url'], target="_blank", className="link-item")
            ], className="document-item")
            for doc, score in context_docs_and_scores
        ]

        return response_display, links_display