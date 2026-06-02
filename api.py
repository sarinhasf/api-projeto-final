# Usando o flask para criação das rotas/endpoints em python
# Cors (Compartilhamento de recursos entre diferentes origens)
# Para exibir os dados, a api precisa estar rodando
# By Sara S. Ferreira

from flask import Flask, jsonify
import requests
from collections import Counter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://yixbooneuxsmtcssclap.supabase.co"
SUPABASE_KEY = "sb_publishable_zindsevd6sVCqMlZgfSgJg_4blVg0B5"
TABLE_NAME = "Filmes"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_filmes():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*"
    response = requests.get(url, headers=HEADERS)
    return response.json()

@app.route("/filmes")
def filmes():
    return jsonify(get_filmes())

@app.route("/dashboard")
def dashboard():
    filmes = get_filmes()

    total = len(filmes)

    brasileiros = sum(
        1 for f in filmes if str(f.get("brasileiro")).lower() == "true"
    )

    mais_99 = sum(
        1 for f in filmes if int(f["aprovacao"].replace("%","")) >= 99
    )

    antes_2000 = sum(
        1 for f in filmes if f["ano"] < 2000
    )

    diretores = [f["diretor"] for f in filmes]
    mais_comum = Counter(diretores).most_common(1)

    diretor_top = mais_comum[0][0] if mais_comum else "N/A"
    qtd_diretor = mais_comum[0][1] if mais_comum else 0

    return jsonify({
        "total_filmes": total,
        "filmes_brasileiros": brasileiros, 
        "mais_99_aprovacao": mais_99,
        "antes_2000": antes_2000,
        "diretor_top": diretor_top,
        "qtd_diretor": qtd_diretor
    })
    

if __name__ == "__main__":
    app.run(debug=True)