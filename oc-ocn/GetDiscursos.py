from utility import get_text_alt
import sqlite3 as sql


def extract_congressmen_id(corrotinas_id):
    ids_to_extract = []
    for ids in corrotinas_id:
        for id_ in ids.find_all("deputado_"):
            congressman_id = get_text_alt(id_, 'id', 'empty')
            id_legislatura = get_text_alt(id_, 'idlegislatura', 'empty')
            info = (congressman_id, id_legislatura)
            ids_to_extract.append(info)
    return ids_to_extract


def insert_speeches(speeches_to_extract, db_fname):
    with sql.connect(db_fname) as conn:
        cursor = conn.cursor()
        sql_speech = '''INSERT INTO speeches VALUES (?,?,?,?,?);'''

        speech = extract_speeches(speeches_to_extract)

        valid_insert(cursor, sql_speech, set(speech))
        conn.commit()

        print('''Save!''')


def extract_speeches(speeches_list):
    speeches_l = []
    for speeches in speeches_list:
        for speech in speeches[0].find_all("discurso"):
            data, hora = speech.find('datahorainicio').text.split('T')
            tipo_discurso = get_text_alt(speech, 'tipodiscurso', 'empty')
            discurso = get_text_alt(speech, 'transcricao', 'empty')
            congressman_id = speeches[1]
            info = (congressman_id, tipo_discurso, discurso, data, hora)
            speeches_l.append(info)
    return speeches_l


def valid_insert(cursor, sql_command, insert_list):
    for row in insert_list:
        try:
            cursor.execute(sql_command, row)

        except sql.IntegrityError as e:
            # import pdb; pdb.set_trace()
            print(e, row)
            # print(f'Invalid row: {row}', e)
            continue