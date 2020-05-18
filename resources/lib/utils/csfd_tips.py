# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from resources.lib.const import GENERAL


def get_csfd_tips():
    """Get daily tips from CSFD site."""
    data_url = 'https://csfd.cz/televize'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    }
    # TODO: OBRAZKY A POPIS
    result = requests.get(data_url, headers=headers, timeout=GENERAL.API_TIMEOUT)
    soup = BeautifulSoup(result.content, 'html.parser')
    main = soup.find_all('ul', class_="content ui-image-list")
    tvtips = main[0].find_all('div', class_='right')

    final_list = []
    for elem in tvtips:
        cont = elem.get_text().encode('utf-8')
        cont_list = cont.split('\n')
        final_list.append(cont_list[1:3])

    return final_list
