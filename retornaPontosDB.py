#!/usr/bin/python

import json
import requests
import psycopg2
import re

from Ponto import Ponto

conectado = False

try:
    conn = psycopg2.connect(user = "postgres",
                                  password = "senha_aqui",
                                  host = "localhost",
                                  port = "5423",
                                  database = "pontos")
    cur = conn.cursor()
    conectado = True

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
    exit()


#========== Grava o Ponto no formato AFD no BD =================
def gravaPontoAFD(ponto):

    diaInvertido = ponto.get_diaI()
    data = diaInvertido + " " + ponto.hora
    query_inserir = """ INSERT INTO pontos_afd ("NSR", "pis", "data_hora", "dia") VALUES (%s,%s,%s,%s)"""
    registro_inserir = (ponto.NSR, ponto.pis, data, diaInvertido)

    if conectado:
        try:
            if ponto.NSR and ponto.NSR[0] != 'A' and bool(re.match('^\d{4}(\-)(((0)[1-9])|((1)[0-2]))(\-)([1-2][0-9]|[0][1-9]|(3)[0-1])', diaInvertido)):
                cur.execute(query_inserir, registro_inserir)
                conn.commit()
                print("NSR: " + ponto.NSR)
        except Exception as e:
            print("Erro ao inserir registro" )
            print(e)

#========== Fim gravaPonto =====================

#=========Grava um novo registro=========
def inserirNovoPonto(pis, marcacao, posicao, dia):

    sMarcacao = {2:'ent1', 3:'sai1', 4:'ent2', 5:'sai2', 6:'ent3', 7:'sai3', 8:'ent4', 9:'sai4'}
    insert_novo_ponto = """INSERT INTO pontos(pis, {}, dia) VALUES (%s,%s,%s)""".format(sMarcacao[posicao])
    dados = (pis, marcacao, dia)
    cur.execute(insert_novo_ponto, dados)
    conn.commit()

#=======Fim grava um novo registro

#==========Atualizacao de um registro existente
def atualizaPontoExistente(pis, marcacao, posicao, dia):
        sMarcacao = {2:'ent1', 3:'sai1', 4:'ent2', 5:'sai2', 6:'ent3', 7:'sai3', 8:'ent4', 9:'sai4'}
        insert_novo_ponto = """UPDATE pontos SET {}=%s WHERE dia BETWEEN  date %s and  date %s and pis = %s""".format(sMarcacao[posicao])
        dados = ( marcacao, dia, dia, pis)
        cur.execute(insert_novo_ponto, dados)
        conn.commit()

#=======Fim atualiza um registro

#===== editarRegistro

#=====

#=========================Retorna Ultimo NSR_inicial===========
def ultimoNSR():
    query_ultimo_NSR = "SELECT * FROM public.ultimo_nsr"
    cur.execute(query_ultimo_NSR)
    table_pontos_afd = cur.fetchall()

    ultimo_NSR = 0

    for row in table_pontos_afd:
        ultimo_NSR = int(row[1]) ;

    return ultimo_NSR

#==============================================================

#======Verifica se existe ponto na tabela de pontos com a combinacao de pis com as entradas ou saidas
def checaMarcacaoDiaDataHora(data_hora, pis):
    sMarcacao = {2:'ent1', 3:'sai1', 4:'ent2', 5:'sai2', 6:'ent3', 7:'sai3', 8:'ent4', 9:'sai4'}
    posicao = 0

    query_pontos = "SELECT * FROM pontos WHERE dia BETWEEN  date %s and  date %s and pis = %s;"
    cur.execute(query_pontos, (data_hora, data_hora, pis))
    table_pontos = cur.fetchall()
    for row1 in table_pontos:
        for i in range(2, 9):
            if row1[i] == data_hora:
                posicao = 0
                break
            if row1[i] == None:
                posicao = i
                break


    return posicao

#====== Fim checaMarcacaoDiaDataHora ====================


#======== Funcao para recuperar dia a dia e salvar uma unica linha no BD
def gravaPonto():

    query_consultar_pontos_dia = "SELECT * FROM public.listagem_dias_com_ponto"
    cur.execute(query_consultar_pontos_dia)
    view_Listagem_dias_com_ponto = cur.fetchall()
    for row1 in view_Listagem_dias_com_ponto:
        dia = row1[1]
        cur.execute("SELECT * FROM public.funcionarios_pis")
        view_Funcionarios_Pis = cur.fetchall()
        for row2 in view_Funcionarios_Pis:
            pis = row2[1]
            query_pontos = "SELECT COUNT(pon_id) FROM pontos WHERE dia BETWEEN  date %s and  date %s and pis = %s;"
            cur.execute(query_pontos, (dia, dia, pis))
            table_pontos = cur.fetchall()

            #print(table_pontos[0])
            if table_pontos[0] >= (1,):
                query_pontos = "SELECT * FROM pontos_afd WHERE dia BETWEEN  date %s and  date %s and pis = %s;"
                cur.execute(query_pontos, (dia, dia, pis))
                view_Pontos_afd = cur.fetchall()
                for row3 in view_Pontos_afd:
                    posicao = checaMarcacaoDiaDataHora(row3[2], pis)
                    if posicao != 0:
                        atualizaPontoExistente(pis, row3[2], posicao ,dia)

                #print 'Ja tem gravado o PIS: ' + pis

            else:
                query_consultar_pontos_dia = """SELECT * FROM pontos_afd  WHERE dia BETWEEN  date %s and  date %s and pis = %s;"""
                cur.execute(query_consultar_pontos_dia, (dia,dia, pis))
                view_Pontos_afd = cur.fetchall()
                i = 2
                for row3 in view_Pontos_afd:
                    if i == 2:
                        inserirNovoPonto(pis, row3[2], i, dia)
                    else:
                        atualizaPontoExistente(pis, row3[2], i ,dia)
                    i = i +1

#======== Fim gravaPonto =====================

#====== Apagar a tabela pontos_afd ==========
def apagaDadosPontosAFD():
    cur.execute('DELETE FROM pontos_afd')
    conn.commit()
#====== Fim apagaDadosPontosAFD =============

#======Atualiza tabela ultimo_NSR ===========
def atualizaDadosUltimoNSR(ultimo_NSR):
    cur.execute('SELECT "NSR" FROM ultimo_nsr')
    view_ultimo_NSR = cur.fetchall()
    for row1 in view_ultimo_NSR:
        if int(row1[0]) == ultimo_NSR:
            print("NSR ja foi gravado - Sem novo registro")
            exit()

    cur.execute('UPDATE ultimo_nsr SET "NSR" = (SELECT "NSR" FROM ultimo_registro_nsr)')
    conn.commit()
#===== atualizaDadosUltimoNSR ========

#========Obtem a sessao com o equipamento===============
url = 'localhost/login.fcgi'
data = {'login' : 'admin', 'password': 'password'}
data = json.dumps(data)

#ignora mensagens de erro de certificado SSL
requests.packages.urllib3.disable_warnings()

response = requests.post(url, data=data,headers={"Content-Type": "application/json"}, verify=False)
payload = json.loads(response.text)
session = payload['session']
#=======Fim do procedimento de criacao da sessao========


#Retorna dos pontos a partir de uma nsr ===> numero sequencial de registro
ultimo_NSR = ultimoNSR()

data = {'initial_nsr' : ultimo_NSR }
data = json.dumps(data)
url = 'localhost/get_afd.fcgi?session='  + session
response = requests.post(url, data=data, headers={"Content-Type": "application/json"}, verify=False)

lines = response.iter_lines()
first_line = next(lines)
patternPIS = re.compile(r'(\d{3})(\d{5})(\d{2})(\d{1})')
replacePIS = r'\1.\2.\3-\4'     
#          NSR                data                  hora                  PIS
for line in lines:
    if line[36:38]:       
        print(line[23:34].decode("utf-8"))
        
        ponto=Ponto(line[0:9].decode("utf-8"), line[10:18].decode("utf-8"), line[18:22].decode("utf-8"), line[23:34].decode("utf-8"))
        print(ponto) 
        gravaPontoAFD(ponto)
        ultimo_NSR = ponto.getNSR

gravaPonto()
atualizaDadosUltimoNSR(ultimo_NSR)
apagaDadosPontosAFD()

if conectado:
    cur.close()
    conn.close()
