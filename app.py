import os
import jwt
import pandas as pd
from flask import Flask, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
FlaskJSON(app)
db = SQLAlchemy(app)

#apicrimepontodata

arquivo = 'indicadoressegurancapublicaufabr20.xlsx'
dicionario = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', ' ': '_'}
#dicionario para remoção de acentos
dadosOcorrencias = pd.read_excel(arquivo, sheet_name='Ocorrências')
# le tabela de ocorrencias
dadosVitimas = pd.read_excel(arquivo, sheet_name='Vítimas')
# le tabela de vitimas 
dadosVitimasDF = pd.DataFrame(dadosVitimas)
# cria dataframde de vitimas
dadosOcorrenciasDF = pd.DataFrame(dadosOcorrencias)
# cria dataframe de ocorencias 
dadosOcorrenciasDF.replace(dicionario, regex=True, inplace=True)
# aplica o dicionario de remoção de acentos
dadosOcorrenciasDF['uf'] = dadosOcorrenciasDF['uf'].str.lower()
# transforma os valores para letra minuscula
dadosOcorrenciasDF['tipocrime'] = dadosOcorrenciasDF['tipocrime'].str.lower()
dadosVitimasDF.replace(dicionario, regex=True, inplace=True)
dadosVitimasDF['uf'] = dadosVitimasDF['uf'].str.lower()
dadosVitimasDF['tipocrime'] = dadosVitimasDF['tipocrime'].str.lower()

def authorization(token):
    try:
        payload = jwt.decode(token, 'f17c92d8ac77d7785a681180dd759259')
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

# Rota de Cadastro
@app.route('/cadastro', methods=['POST'])
def cadastrar():

    from models import User


    body = request.get_json(force=True)
    email = body['email']
    password = body['password']
    try:
        user = User(
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id, 'email': user.email, 'password': user.password})
    except Exception as e:
        return jsonify(e)

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    from models import User

    body = request.get_json(force=True)
    email = body['email']
    password = body['password']

    user = User.query.filter_by(email=email).first()

    if not(user.check_password(password)):
        return 'Senha errada'

    token = user.encode_auth_token(user.id).decode()

    return jsonify({'id': user.id, 'email': user.email, 'password': user.password, 'token': token })

# Rota de quantidade de crimes por ano (Sérgio)
@app.route('/quantidade/crimes/<ano>', methods=['GET'])
def qtd_crime_ano(ano):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    if int(ano) < 2015:
        return jsonify({'msg': 'Favor inserir ano entre 2015 e 2020'})

    if int(ano) > 2020:
        return jsonify({'msg': 'Favor inserir ano entre 2015 e 2020'})

    resultVitimas = dadosVitimasDF.query('ano == valor'.replace('valor', ano)).vitimas
    resultOcorencas = dadosOcorrenciasDF.query('ano == valor'.replace('valor', ano)).ocorrencias

    return jsonify({'Ano':ano, 'Vítimas':sum(resultVitimas), 'Ocorrências': sum(resultOcorencas)})

# Rota de quantidade de determinada ocorrencia por estado (Sérgio)
@app.route('/quantidade/ocorrencias/<nome>/<sigla>', methods=['GET'])
def qtd_ocorrencias_nome_sigla(nome, sigla):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    if nome == 'todos' and(sigla == 'bra' or sigla == 'brasil'):
        result = dadosOcorrenciasDF.drop(['ano'], axis=1).groupby(['tipocrime']).sum().ocorrencias
        return result.to_json()
    
    if sigla == 'bra' or sigla == 'brasil':
        result = dadosOcorrenciasDF.query('tipocrime == "valor2"'.replace('valor2', nome)).ocorrencias
        return jsonify({'quantidade': sum(result)})
    
    if nome == 'todos':
        result = dadosOcorrenciasDF.query('uf == "valor1"'.replace('valor1', sigla)).drop(['ano'], axis=1).groupby(['tipocrime']).sum().ocorrencias
        return result.to_json()

    

    result = dadosOcorrenciasDF.query('uf == "valor1" & tipocrime == "valor2"'.replace('valor1', sigla).replace('valor2', nome)).ocorrencias

    print(sum(result))
    print(nome, sigla)

    return jsonify({'quantidade': sum(result)})

# Rota de quantidade de determinadas vititmas por estado (Raíssa)
@app.route('/quantidade/vitimas/<nomedocrime>/<sigla>', methods=['GET'])
def qtd_vitimas_nome_sigla(nomedocrime, sigla):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla})

# Média mensal de ocorrenias por estado dentro de um período (Raíssa)
@app.route('/media/ocorrencias/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_ocorrencias_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla, inicio, fim)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla, 'inicio': inicio, 'fim': fim})

# Media mensal de vítimas por estado dentro de um período (Geronimo)
@app.route('/media/vitimas/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_vitimas_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla, inicio, fim)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla, 'inicio': inicio, 'fim': fim})

# Ranking estadual por crime (Geronimo)
@app.route('/ranking/<quantidade>/estadual/<nomedocrime>')
def ranking_estadual_por_crime(quantidade, nomedocrime):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(quantidade, nomedocrime)

    return jsonify({'nomedocrime':nomedocrime, 'quantidade': quantidade})

# Ranking criminal por estado por estado (Lucas)
@app.route('/ranking/<quantidade>/criminal/<sigla>')
def ranking_criminal_por_estado(quantidade, sigla):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(quantidade, sigla)

    return jsonify({'sigla':sigla, 'quantidade': quantidade})

if __name__ == '__main__':
    app.run()