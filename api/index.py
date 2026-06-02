from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configurar na Vercel
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


def init_db():
    """Cria a tabela caso ela não exista."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id BIGSERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            brasileiro BOOLEAN DEFAULT FALSE,
            ano BIGINT,
            diretor TEXT,
            aprovacao TEXT,
            imagem TEXT,
            descricao TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ==========================
# LISTAR E INSERIR FILMES
# ==========================
@app.route('/api/filmes', methods=['GET', 'POST'])
def gerenciar_filmes():

    init_db()

    # INSERIR
    if request.method == 'POST':

        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({
                "error": "Payload inválido."
            }), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO filmes
                (nome, brasileiro, ano, diretor, aprovacao, imagem, descricao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                dados.get("nome"),
                dados.get("brasileiro", False),
                dados.get("ano"),
                dados.get("diretor"),
                dados.get("aprovacao"),
                dados.get("imagem"),
                dados.get("descricao")
            ))

            conn.commit()

            cur.close()
            conn.close()

            return jsonify({
                "success": True,
                "message": "Filme cadastrado com sucesso!"
            }), 201

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500

    # LISTAR
    try:
        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""
            SELECT *
            FROM filmes
            ORDER BY id DESC
        """)

        filmes = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(filmes), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# BUSCAR FILME POR ID
# ==========================
@app.route('/api/filmes/<int:id>', methods=['GET'])
def buscar_filme(id):

    try:
        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""
            SELECT *
            FROM filmes
            WHERE id = %s
        """, (id,))

        filme = cur.fetchone()

        cur.close()
        conn.close()

        if not filme:
            return jsonify({
                "error": "Filme não encontrado."
            }), 404

        return jsonify(filme), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# ATUALIZAR FILME
# ==========================
@app.route('/api/filmes/<int:id>', methods=['PUT'])
def atualizar_filme(id):

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "error": "Payload inválido."
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE filmes
            SET
                nome = %s,
                brasileiro = %s,
                ano = %s,
                diretor = %s,
                aprovacao = %s,
                imagem = %s,
                descricao = %s
            WHERE id = %s
        """, (
            dados.get("nome"),
            dados.get("brasileiro"),
            dados.get("ano"),
            dados.get("diretor"),
            dados.get("aprovacao"),
            dados.get("imagem"),
            dados.get("descricao"),
            id
        ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Filme atualizado com sucesso!"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# DELETAR FILME
# ==========================
@app.route('/api/filmes/<int:id>', methods=['DELETE'])
def deletar_filme(id):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM filmes
            WHERE id = %s
        """, (id,))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Filme removido com sucesso!"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# DASHBOARD
# ==========================
@app.route('/api/dashboard', methods=['GET'])
def dashboard():

    try:
        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""
            SELECT *
            FROM filmes
        """)

        filmes = cur.fetchall()

        cur.close()
        conn.close()

        total = len(filmes)

        brasileiros = sum(
            1 for f in filmes
            if f["brasileiro"]
        )

        mais_99 = sum(
            1 for f in filmes
            if int(
                str(f.get("aprovacao", "0"))
                .replace("%", "")
            ) >= 99
        )

        antes_2000 = sum(
            1 for f in filmes
            if int(f.get("ano", 0)) < 2000
        )

        diretores = {}

        for filme in filmes:
            diretor = filme.get("diretor")

            if diretor:
                diretores[diretor] = (
                    diretores.get(diretor, 0) + 1
                )

        diretor_top = "N/A"
        qtd_diretor = 0

        if diretores:
            diretor_top = max(
                diretores,
                key=diretores.get
            )

            qtd_diretor = diretores[diretor_top]

        return jsonify({
            "total_filmes": total,
            "filmes_brasileiros": brasileiros,
            "mais_99_aprovacao": mais_99,
            "antes_2000": antes_2000,
            "diretor_top": diretor_top,
            "qtd_diretor": qtd_diretor
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)