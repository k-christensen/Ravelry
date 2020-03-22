import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys

# fav_request: makes request to API, returns json file of user
def fav_request(username, page_size, page):
    favs_url = 'https://api.ravelry.com/people/{}/favorites/list.json'.format(username)
    favs = requests.get(favs_url, auth = (personal_keys.username(),personal_keys.password()),
                        params={'page_size':page_size, 'page':page})
    return favs.json()

# create_fav_list: 
# input fav json, output list of fav pattern codes 
def create_fav_list(fav_request):
    fav_list = []
    favorites = fav_request['favorites']
    for item in range(0,len(favorites)):
        if favorites[item]['favorited'] is not None:
            if 'pattern_id' in favorites[item]['favorited'].keys():
                fav_list.append(favorites[item]['favorited']['pattern_id'])
            elif 'id' in favorites[item]['favorited'].keys():
                fav_list.append(favorites[item]['favorited']['id'])
    return [code for code in fav_list if code is not None]

def fav_req_to_list(username, page_size, page):
    fav_request = fav_request(username, page_size, page)
    return create_fav_list(fav_request)