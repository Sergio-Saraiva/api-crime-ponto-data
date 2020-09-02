import os
import jwt
from flask import Flask, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_sqlalchemy import SQLAlchemy
# from flask_request_params import bind_request_params

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.before_request(bind_request_params)
FlaskJSON(app)
db = SQLAlchemy(app)


def authorization(token):
    try:
        payload = jwt.decode(token, 'f17c92d8ac77d7785a681180dd759259')
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

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

@app.route('/quantidade/crimes/<ano>', methods=['GET'])
def qtd_crime_ano(ano, mes):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})
    
    print(ano)

    return jsonify({'ano':ano, 'mes': mes})

@app.route('/quantidade/ocorrencias/<nome>/<sigla>', methods=['GET'])
def qtd_ocorrencias_nome_sigla(nome, sigla):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nome, sigla)

    return jsonify({'nome':nome, 'sigla': sigla})

@app.route('/quantidade/vitimas/<nomedocrime>/<sigla>', methods=['GET'])
def qtd_vitimas_nome_sigla(nomedocrime, sigla):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla})

@app.route('/media/ocorrencias/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_ocorrencias_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla, inicio, fim)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla, 'inicio': inicio, 'fim': fim})

@app.route('/media/vitimas/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_vitimas_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime, sigla, inicio, fim)

    return jsonify({'nomedocrime':nomedocrime, 'sigla': sigla, 'inicio': inicio, 'fim': fim})

@app.route('/ranking/<quantidade>/estadual/<nomedocrime>')
def ranking_estadual_por_crime(quantidade, nomedocrime):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(quantidade, nomedocrime)

    return jsonify({'nomedocrime':nomedocrime, 'quantidade': quantidade})

@app.route('/ranking/<quantidade>/criminal/<sigla>')
def ranking_criminal_por_estado(quantidade, sigla):
    token = request.headers.get('Authorization').split(' ')[1]
    if not(authorization(token)):
        return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(quantidade, sigla)

    return jsonify({'sigla':sigla, 'quantidade': quantidade})

if __name__ == '__main__':
    app.run()