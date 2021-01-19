import asyncio as asy
import aiohttp as aio
from bs4 import BeautifulSoup
import GetDiscursos as gdc


default_connector_limit = 100
default_timeout = 90
default_headers = {'accept': 'text/xml'}


async def get_congressmen_id(initial_year, final_year, timeout=default_timeout,
                             connector_limit=default_connector_limit):
    connector = aio.TCPConnector(limit=connector_limit)
    timeout = aio.ClientTimeout(total=timeout)
    headers = default_headers
    async with aio.ClientSession(trust_env=True, timeout=timeout, connector=connector, headers=headers) as session:
        URL = 'https://dadosabertos.camara.leg.br/api/v2/deputados?dataInicio={0}-01-01&dataFim={0}-12-31'
        corrotinas_id = [get_id(URL, session, year) for year in range(int(initial_year), int(final_year) + 1)]
        return gdc.extract_congressmen_id(await asy.gather(*corrotinas_id))


async def get_speeches(congressmen_ids, db_fname, timeout=default_timeout, connector_limit=default_connector_limit):
    connector = aio.TCPConnector(limit=connector_limit)
    timeout = aio.ClientTimeout(total=timeout)
    headers = default_headers
    ids_c = [id_[0] for id_ in congressmen_ids]
    speeches_to_extract = []
    async with aio.ClientSession(trust_env=True, timeout=timeout, connector=connector, headers=headers) as session:
        URL = "https://dadosabertos.camara.leg.br/api/v2/deputados/{}/discursos?idLegislatura={}"
        ids_list = [get_speech(URL, session, ids) for ids in congressmen_ids]
        for speech, speech_id in zip(await asy.gather(*ids_list), ids_c):
            speeches_to_extract.append((speech, speech_id))
        gdc.insert_speeches(speeches_to_extract, db_fname)


async def get_id(url, session, *arg):
    print(url, arg)
    try:
        url = url.format(*arg)
        async with session.get(url) as info:
            info = BeautifulSoup(await info.text(), 'lxml')
            return info
    except:
        raise


async def get_speech(url, session, arg):
    print(url, arg)
    try:
        url = url.format(arg[0], arg[1])
        async with session.get(url) as info:
            info = BeautifulSoup(await info.text(), 'lxml')
            return info
    except:
        raise