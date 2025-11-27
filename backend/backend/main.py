from flask import Flask, jsonify
from flask_cors import CORS
from rotas.analise_rotas import analise_bp


app = Flask(__name__)
CORS(app, origins="*")

@app.route("/", methods=["GET"])
def home():
    return jsonify("It's alive!"), 200

# Registra o Blueprint
app.register_blueprint(analise_bp)

if __name__ == "__main__":
    app.run("0.0.0.0", port=8000, debug=True)
    
