import asyncio as asy
import AsyncLib as al
import time
import sys
import sqlite3 as sql
import GetDadosCamara as gdc

global congressmen, votings, votes


def create_db_file():
    fname = "DadosCamara-{}.db".format(time.time())
    with sql.connect(fname) as conn:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS congressman(
                congressman_id varchar primary key,
                name varchar null,
                party varchar null,
                uf varchar null);

            CREATE TABLE IF NOT EXISTS voting(
                voting_id varchar not null,
                bill_type varchar null,
                bill_number varchar null,
                bill_year varchar null,
                voting_date varchar not null,
                primary key(voting_id, voting_date));

            CREATE TABLE IF NOT EXISTS vote(
                congressman_id varchar not null,
                voting_id varchar not null,
                vote_type integer not null,
                primary key(congressman_id, voting_id),
                foreign key (congressman_id) references congressman(congressman_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
                foreign key (voting_id) references voting(voting_id));
                
            CREATE TABLE IF NOT EXISTS speeches(
                congressman_id varchar not null,
                tipo_discurso varchar null,
                discurso varchar null,
                data varchar not null,
                hora varchar not null,
                primary key(data, hora),
                foreign key (congressman_id) references congressman(congressman_id)
                ON DELETE CASCADE ON UPDATE CASCADE);''')

        conn.commit()
        return fname


if __name__ == "__main__":

    db_fname = create_db_file()

    try:
        initial_year = int(sys.argv[1])
        final_year = int(sys.argv[2])

    except IndexError:
        initial_year = 2019
        final_year = time.localtime()[0]

    print(db_fname)
    print(f'Dump from {initial_year} to {final_year}')

    loop = asy.get_event_loop()
    res = loop.run_until_complete(al.get_congressmen_id(initial_year, final_year))
    loop.run_until_complete(al.get_speeches(res, db_fname))
    loop.close()
    gdc.get_documents(db_fname)

    print('Dump Complete')