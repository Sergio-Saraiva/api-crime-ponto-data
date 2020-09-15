import os
import jwt
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter
from funcoes_aux import converter_sigla2nome , converter_crime , converter_nome2sigla, contar_meses



app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
FlaskJSON(app)
db = SQLAlchemy(app)

#apicrimepontodata

arquivo = 'indicadoressegurancapublicaufabr20.xlsx'
dicionario = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u','ã': 'a', 'õ': 'o', 'ê': 'e', ' ': '_', 'ç': 'c', 'ô': 'o'}
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
dicionario2 = {'janeiro': '1', 'fevereiro': '2', 'marco': '3', 'abril': '4', 'maio': '5', 'junho': '6', 'julho' : '7', 'agosto' : '8', 'setembro' : '9', 'outubro' : '10', 'novembro' : '11', 'dezembro' : '12'}
dadosVitimasDF.mes.replace(dicionario2, regex=True, inplace=True)


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

    print(nome)

    sigla = converter_sigla2nome(sigla)
    nome = converter_crime(nome)

    print(nome)

    print(dadosOcorrenciasDF.head())

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

    return jsonify({'quantidade': sum(result)})

# Rota de quantidade de determinadas vititmas por estado (Raíssa)
@app.route('/quantidade/vitimas/<nomedocrime>/<sigla>', methods=['GET'])
def qtd_vitimas_nome_sigla(nomedocrime, sigla):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    print(nomedocrime)
    
    # Tratamento dos dados de entrada

    sigla = converter_sigla2nome(sigla)
    nomedocrime = converter_crime(nomedocrime)

    print(nomedocrime)

    print(dadosVitimasDF[2900:3220])

    if nomedocrime == 'todos' and(sigla == 'bra' or sigla == 'brasil'):
        result = dadosVitimasDF.drop(['ano'], axis=1).groupby(['tipocrime']).sum().vitimas
        return result.to_json()

    if sigla == 'bra' or sigla == 'brasil':
        result = dadosVitimasDF.query('tipocrime == "valor2"'.replace('valor2', nomedocrime)).vitimas
        return jsonify({"UF" : "BR",'quantidade': sum(result)})

    if nomedocrime == 'todos':
        result = dadosVitimasDF.query('uf == "valor1"'.replace('valor1', sigla)).drop(['ano'], axis=1).groupby(['tipocrime']).sum().vitimas
        return result.to_json()

    if sigla == 'estados':
            result = dadosVitimasDF.query('tipocrime == "valor2"'.replace('valor2', nomedocrime)).groupby(['uf']).sum().vitimas
            return result.to_json()

    result = dadosVitimasDF.query('uf == "valor1" & tipocrime == "valor2"'.replace('valor1', sigla).replace('valor2', nomedocrime)).vitimas

    uf_estado = converter_nome2sigla(sigla)

    return jsonify({'UF': uf_estado ,'quantidade': sum(result)})

# Média mensal de ocorrenias por estado dentro de um período (Raíssa)
@app.route('/media/ocorrencias/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_ocorrencias_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    #token = request.headers.get('Authorization').split(' ')[1]
    #if not(authorization(token)):
    #    return jsonify({'msg': 'Token inválido, faça login novamente'})
    
    # Tratamento dos dados de entrada
    sigla = converter_sigla2nome(sigla)
    nomedocrime = converter_crime(nomedocrime)

    mes_inicio, ano_inicio = inicio.split("-")
    mes_inicio = int(mes_inicio)
    ano_inicio = int(ano_inicio)
    mes_fim, ano_fim = fim.split("-")
    mes_fim = int(mes_fim)
    ano_fim = int(ano_fim)

    dicionario_mes = {'janeiro': '1', 'fevereiro': '2', 'março': '3', 'abril': '4', 'maio': '5', 'junho': '6', 'julho' : '7', 'agosto' : '8', 'setembro' : '9', 'outubro' : '10', 'novembro' : '11', 'dezembro' : '12'}
    dadosOcorrenciasDF.replace(dicionario_mes, regex=True, inplace=True)
    dadosOcorrenciasDF.mes = dadosOcorrenciasDF.mes.astype(int)

    dadosOcorrenciasDF0 = dadosOcorrenciasDF[dadosOcorrenciasDF.tipocrime == nomedocrime]
    dadosOcorrenciasDF0 = dadosOcorrenciasDF0[dadosOcorrenciasDF0.uf == sigla]

    if (ano_fim != ano_inicio):
        dadosOcorrenciasDF1 = dadosOcorrenciasDF0.loc[np.logical_and(dadosOcorrenciasDF0.ano == ano_inicio, dadosOcorrenciasDF0.mes >= mes_inicio)]
        dadosOcorrenciasDF2 = dadosOcorrenciasDF0.loc[np.logical_and(dadosOcorrenciasDF0.ano > ano_inicio, dadosOcorrenciasDF0.ano < ano_fim)]
        dadosOcorrenciasDF3 = dadosOcorrenciasDF0.loc[np.logical_and(dadosOcorrenciasDF0.ano == ano_fim, dadosOcorrenciasDF0.mes >= mes_fim)]
        frames = [dadosOcorrenciasDF1, dadosOcorrenciasDF2, dadosOcorrenciasDF3]
        ocorrenciasNoPeriodo = pd.concat(frames)
    else:
        ocorrenciasNoPeriodo = dadosOcorrenciasDF0.loc[np.logical_and(dadosOcorrenciasDF0.mes >= mes_inicio, dadosOcorrenciasDF0.mes <= mes_fim)]

    ocorrenciasNoPeriodo = ocorrenciasNoPeriodo.iloc[:,[0,4]]
    ocorrenciasNoPeriodoMedio = ocorrenciasNoPeriodo.mean(axis=0)

    return  ocorrenciasNoPeriodoMedio.to_json ()

# Media mensal de vítimas por estado dentro de um período (Geronimo)
@app.route('/media/vitimas/<nomedocrime>/<sigla>/<inicio>/<fim>', methods=['GET'])
def media_vitimas_nome_sigla_periodo(nomedocrime, sigla, inicio, fim):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    sigla = converter_sigla2nome(sigla)
    nomedocrime = converter_crime(nomedocrime)

    mes_inicio, ano_inicio = inicio.split("-")
    mes_inicio = int(mes_inicio)
    ano_inicio = int(ano_inicio)
    mes_fim, ano_fim = fim.split("-")
    mes_fim = int(mes_fim)
    ano_fim = int(ano_fim)
        
    dadosVitimasDF.mes = dadosVitimasDF.mes.astype(int)

    dadosVitimasDF0 = dadosVitimasDF[dadosVitimasDF.tipocrime == nomedocrime]
    dadosVitimasDF0 = dadosVitimasDF0[dadosVitimasDF0.uf == sigla]

    if (ano_fim != ano_inicio):
        dadosVitimasDF1 = dadosVitimasDF0.loc[np.logical_and(dadosVitimasDF0.ano == ano_inicio, dadosVitimasDF0.mes >= mes_inicio)]
        dadosVitimasDF2 = dadosVitimasDF0.loc[np.logical_and(dadosVitimasDF0.ano > ano_inicio, dadosVitimasDF0.ano < ano_fim)]
        dadosVitimasDF3 = dadosVitimasDF0.loc[np.logical_and(dadosVitimasDF0.ano == ano_fim, dadosVitimasDF0.mes >= mes_fim)]
        frames = [dadosVitimasDF1, dadosVitimasDF2, dadosVitimasDF3]
        vitimasNoPeriodo = pd.concat(frames)
    else:
        vitimasNoPeriodo = dadosVitimasDF0.loc[np.logical_and(dadosVitimasDF0.mes >= mes_inicio, dadosVitimasDF0.mes <= mes_fim)]

    vitimasNoPeriodo = vitimasNoPeriodo.iloc[:,[0,4]]
    vitimasNoPeriodoMedio = vitimasNoPeriodo.mean(axis=0)

    return vitimasNoPeriodoMedio.to_json()

# Ranking estadual por crime (Geronimo)
@app.route('/ranking/<quantidade>/estadual/<nomedocrime>')
def ranking_estadual_por_crime(quantidade, nomedocrime):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    nomedocrime = converter_crime(nomedocrime)

    aux =  pd.DataFrame(dadosVitimas)
    aux.columns=['uf', 'tipocrime', 'ano', 'mes', 'ocorrencias']

    crimesDF = pd.concat([dadosOcorrenciasDF, aux])

    ocorrenciaEstado = crimesDF[crimesDF.tipocrime == nomedocrime]
    ocorrenciaEstado = ocorrenciaEstado.iloc[:,[0,4]]
    ranking = ocorrenciaEstado.groupby(['uf']).sum().sort_values(by=['ocorrencias'], ascending=False)

    return ranking.iloc[0:int(quantidade),:].ocorrencias.to_json()

# Ranking criminal por estado por estado (Lucas)
@app.route('/ranking/<quantidade>/criminal/<sigla>')
def ranking_criminal_por_estado(quantidade, sigla):
    # token = request.headers.get('Authorization').split(' ')[1]
    # if not(authorization(token)):
    #     return jsonify({'msg': 'Token inválido, faça login novamente'})

    sigla = converter_sigla2nome(sigla)

    aux = {}

    if sigla == 'bra' or sigla == 'brasil':
        for i in range(0, dadosOcorrenciasDF.index.stop):
            aux.update({dadosOcorrenciasDF.loc[i, 'tipocrime']: int(0 if aux.get(dadosOcorrenciasDF.loc[i, 'tipocrime']) is None else aux.get(dadosOcorrenciasDF.loc[i, 'tipocrime'])) + int(dadosOcorrenciasDF.loc[i, 'ocorrencias'])})
    else:
        for i in range(0, dadosOcorrenciasDF.index.stop):
            if dadosOcorrenciasDF.loc[i, 'uf'] == sigla:
                aux.update({dadosOcorrenciasDF.loc[i, 'tipocrime']: int(0 if aux.get(dadosOcorrenciasDF.loc[i, 'tipocrime']) is None else aux.get(dadosOcorrenciasDF.loc[i, 'tipocrime'])) + int(dadosOcorrenciasDF.loc[i, 'ocorrencias'])})

    aux = dict(sorted(aux.items(), key=itemgetter(1), reverse=True))
    result = list(aux)[:int(quantidade)]
    lista = [None]*len(result)
    for i in range(len(result)):
        lista[i] = aux[result[i]]
    
    auxDF = pd.DataFrame({'crime': result, 'ocorrencias': lista})
    auxDF.reset_index(drop=True)
    
    return auxDF.reset_index().to_json(orient='records')

if __name__ == '__main__':
    app.run()
