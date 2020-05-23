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

# get favs list: input is username, output is list of pattern ids in a person's favorites
# if the user has over 500 favorites, then only returns the first 500
# this is done so other functions don't take forever
def get_favs_list(username):
    favs = fav_request(username, 100, 1)
    fav_list = create_fav_list(favs)
    if favs['paginator']['page_count']>1:
        page_number = 2
        if favs['paginator']['last_page'] > 5:
            last_page = 5
        else:
            last_page = favs['paginator']['last_page']
        while page_number <= last_page:
            new_request_favs = fav_request(username,100, page_number)
            fav_list.extend(create_fav_list(new_request_favs))
            page_number += 1
    return fav_list

# returns a dict that is just pattern code and 1 for every value
# done so we can then do the proj rating func to create user data col

def fav_dict (username):
    fav_list = get_favs_list(username)
    return {code:1 for code in fav_list}
