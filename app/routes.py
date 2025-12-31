def create_hello_view(app):
    @app.route('/')
    def index():
        return {"msg": "Hallo Papa!", "andere msg": "wow!"}
