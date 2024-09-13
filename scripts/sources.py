
class Sources:
    def __init__(self):
        self.sources = [
            {
                "source": "elespanol.com",
                "x_username": "@elespanolcom"
            },
            {
                "source": "elmundo.es",
                "x_username": "@elmundoes"
            },
            {
                "source": "lavanguardia.com",
                "x_username": "@LaVanguardia"
            },
            {
                "source": "elpais.com",
                "x_username": "@el_pais"
            },
            {
                "source": "mundodeportivo.com",
                "x_username": "@mundodeportivo"
            },
            {
                "source": "eldiario.es",
                "x_username": "@eldiarioes"
            },
            {
                "source": "as.com",
                "x_username": "@diarioas"
            }
        ]

    def get_username(self, source):
        """ Given a source name, returns the Twitter/X username. """
        for item in self.sources:
            if item["source"] == source:
                return item["x_username"]
        return None