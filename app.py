import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Força o carregamento do arquivo .env
load_dotenv()

app = Flask(__name__)

# Pega a URL do .env. Se não achar, exibe um erro mais claro.
db_url = os.getenv('DATABASE_URL')

if not db_url:
    raise ValueError("ERRO: A variável DATABASE_URL não foi encontrada. Verifique seu arquivo .env!")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Definição da Tabela
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)

# Cria as tabelas no banco remoto se não existirem
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tarefas', methods=['GET', 'POST'])
def gerenciar_tarefas():
    if request.method == 'POST':
        nova_tarefa = Tarefa(texto=request.json.get('texto'))
        db.session.add(nova_tarefa)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 201

    tarefas = Tarefa.query.all()
    return jsonify([{"id": t.id, "texto": t.texto} for t in tarefas])

if __name__ == '__main__':
    app.run(debug=True)
