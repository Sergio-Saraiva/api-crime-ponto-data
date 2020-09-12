import json 
from unicodedata import normalize
import numpy as np

estados = '{"AC": "acre","AL": "alagoas","AP": "amapa","AM": "amazonas","BA": "bahia","CE": "ceara","DF": "distrito_federal","ES": "espirito_santo","GO": "goias","MA": "maranhao","MT": "mato_grosso","MS": "mato_grosso_do_sul","MG": "minas_gerais","PA": "para","PB": "paraiba","PR": "parana","PE": "pernambuco","PI": "piaui","RJ": "rio_de_janeiro","RN": "rio_grande_do_norte","RS": "rio_grande_do_sul","RO": "rondonia","RR": "roraima","SC": "santa_catarina","SP": "sao_paulo","SE": "sergipe","TO": "tocantins"}'
estados_json = json.loads(estados)
siglas = '{"acre":"AC" ,"alagoas":"AL","amapa":"AP","amazonas":"AM", "bahia":"BA", "ceara":"CE", "distrito_federal":"DF", "espirito_santo":"ES", "goias":"GO", "maranhao":"MA", "mato_grosso":"MT", "mato_grosso_do_sul":"MS", "minas_gerais":"MG", "para":"PA", "paraiba":"PB", "parana":"PR", "pernambuco":"PE", "piaui":"PI", "rio_de_janeiro":"RJ", "rio_grande_do_norte":"RN", "rio_grande_do_sul":"RS", "rondonia":"RO", "roraima":"RR", "santa_catarina":"SC", "sao_paulo":"SP", "sergipe":"SE", "tocantins":"TO"}'
siglas_json = json.loads(siglas)

# Funcao para converter uma UF no nome do respectivo estado 
def converter_sigla2nome (sigla):
    
    sigla = sigla.upper()

    try:
        resultado = estados_json [sigla]
    except:
        resultado = normalize('NFKD', sigla.lower()).encode('ASCII', 'ignore').decode('ASCII')
        resultado = resultado.replace(" ","_")
        resultado = resultado.replace("-","_")
    finally:
        return resultado


# Funcao para converter o nome do estado em sua respectiva UF
def converter_nome2sigla (nome):
        resultado = siglas_json [nome]
        return resultado


# Funcao para tratar os valores fornecidos para o campo crime
def converter_crime(nomecrime):
        resultado = normalize('NFKD', nomecrime.lower()).encode('ASCII', 'ignore').decode('ASCII')
        resultado = resultado.replace(" ","_")
        resultado = resultado.replace("-","_")
        return resultado

#Função que retorna o numero de meses
def contar_meses(inicio,fim):

    anos = max(inicio,fim) - min(inicio,fim)
    meses = anos*12
    return meses