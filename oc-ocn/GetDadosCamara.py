import pandas as pd
import time
import sys
import urllib.request
import os
import sqlite3 as sql

void_congressmen = pd.DataFrame()
void_votings = pd.DataFrame()
void_votes = pd.DataFrame()

try:
    initial_year = int(sys.argv[1])
    final_year = int(sys.argv[2])

except IndexError:
    initial_year = 2019
    final_year = time.localtime()[0] - 1


def get_documents(db_fname, congressmen=void_congressmen, votings=void_votings, votes=void_votes):
    for year in range(int(initial_year), int(final_year) + 1):
        if not (os.path.exists('votacoes-{}.csv'.format(year)) and os.path.exists('votos-{}.csv'.format(year))):
            urllib.request.urlretrieve(
                'http://dadosabertos.camara.leg.br/arquivos/votacoesVotos/csv/votacoesVotos-{}.csv'.format(year),
                'votos-{}.csv'.format(year))
            urllib.request.urlretrieve(
                'http://dadosabertos.camara.leg.br/arquivos/votacoesProposicoes/csv/votacoesProposicoes-{}.csv'.format(
                 year), 'votacoes-{}.csv'.format(year))

        df_votes = pd.read_csv('votos-{}.csv'.format(year), sep=';', engine="python")
        df_votings = pd.read_csv('votacoes-{}.csv'.format(year), sep=';', engine="python")

        congressmen = df_votes[['deputado_id', 'deputado_nome', 'deputado_siglaPartido', 'deputado_siglaUf']]
        votings = df_votings[['idVotacao', 'data', 'proposicao_siglaTipo', 'proposicao_numero', 'proposicao_ano']]
        votes = df_votes[['idVotacao', 'voto', 'deputado_id']]

    with sql.connect(db_fname) as conn:
        cursor = conn.cursor()

        congressmen = list(map(tuple, congressmen.to_numpy()))
        votings = list(map(tuple, votings.to_numpy()))
        votes = list(map(tuple, votes.to_numpy()))

        sql_congressman = '''INSERT INTO congressman VALUES (?,?,?,?);'''
        sql_vote = '''INSERT INTO vote VALUES (?,?,?);'''
        sql_voting = '''INSERT INTO voting VALUES (?,?,?,?,?);'''

        valid_insert(cursor, sql_congressman, set(congressmen))
        valid_insert(cursor, sql_vote, set(votes))
        valid_insert(cursor, sql_voting, set(votings))
        conn.commit()

        print('''Save!''')


def valid_insert(cursor, sql_command, insert_list):
    for row in insert_list:
        try:
            cursor.execute(sql_command, row)

        except sql.IntegrityError as e:
            print(e, row)
            continue