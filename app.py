import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)

# Configurações de Upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limite de 100MB para vídeos

# Conexão Banco de Dados (Neon)
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    db_url = "postgresql://neondb_owner:npg_rVAM7Sve5Flm@ep-gentle-glade-a4v86gk6-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Banco
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)
    arquivo_url = db.Column(db.String(300), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/tarefas/delete', methods=['POST'])
def deletar_tarefas():
    data = request.get_json()
    ids = data.get('ids', [])

    for tarefa_id in ids:
        tarefa = Tarefa.query.get(tarefa_id)
        if tarefa:
            if tarefa.arquivo_url:
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], tarefa.arquivo_url)
                if os.path.exists(caminho):
                    os.remove(caminho)

            db.session.delete(tarefa)

    db.session.commit()
    return jsonify({"status": "ok"})


@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/tarefas', methods=['GET', 'POST'])
def gerenciar_tarefas():
    if request.method == 'POST':
        texto = request.form.get('texto')
        arquivo = request.files.get('arquivo') # Nome deve bater com o JS
        
        nome_arquivo = None
        if arquivo and arquivo.filename != '':
            nome_arquivo = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))
            
        nova_tarefa = Tarefa(texto=texto, arquivo_url=nome_arquivo)
        db.session.add(nova_tarefa)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 201

    tarefas = Tarefa.query.all()
    return jsonify([{
        "id": t.id, 
        "texto": t.texto, 
        "midia": f"/static/uploads/{t.arquivo_url}" if t.arquivo_url else None
    } for t in tarefas])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
