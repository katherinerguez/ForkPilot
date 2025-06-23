from dash.dependencies import Input, Output, State
from dash import html

def register_callbacks(app, rag): 
    @app.callback(
        [Output("response-container", "children"),
         Output("links-container", "children")],
        [Input("search-button", "n_clicks")],
        [State("user-query", "value")]
    )
    def generate_response(n_clicks, query):
        """
        Responde a la consulta del usuario y le proporciona los enlaces de los documentos 
        que utilizo para la respuesta
            
            n_clicks (int): Clics en el botón de búsqueda.
            query (str): Consulta ingresada por el usuario.

        Devuelve:
            tuple:
                - html.Div: Contenedor con la respuesta generada.
                - list[html.Div]: Lista de enlaces a los documentos fuente únicos.
        """
        if not n_clicks or not query:
            return "", ""

        response, docs = rag.generate(query)
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
            for uid in unique_docs.values()
        ]

        return response_display, links_display