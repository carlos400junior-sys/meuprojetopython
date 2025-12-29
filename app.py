import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Carrega o .env (importante para funcionar no seu PC)
load_dotenv()

app = Flask(__name__)

# AJUSTE 1: No Render, a variável é lida do sistema, não do arquivo .env
# Além disso, adicionamos uma correção para o prefixo 'postgres://' que o Render costuma usar
db_url = os.environ.get('DATABASE_URL')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    # Se não houver variável de ambiente, tenta usar a do Neon que você forneceu
    db_url = "postgresql://neondb_owner:npg_rVAM7Sve5Flm@ep-gentle-glade-a4v86gk6-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tarefas', methods=['GET', 'POST'])
def gerenciar_tarefas():
    if request.method == 'POST':
        # Boa prática: verificar se o JSON existe
        dados = request.get_json()
        if not dados or 'texto' not in dados:
            return jsonify({"erro": "Texto faltando"}), 400
            
        nova_tarefa = Tarefa(texto=dados['texto'])
        db.session.add(nova_tarefa)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 201

    tarefas = Tarefa.query.all()
    return jsonify([{"id": t.id, "texto": t.texto} for t in tarefas])

if __name__ == '__main__':
    # AJUSTE 2: O Render exige que o app escute na porta definida pela variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

