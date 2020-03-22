import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys

# search term goes in, search json comes out
def search(term):
    search_url = 'https://api.ravelry.com/patterns/search.json?query={}'.format(term)
    search = requests.get(search_url, auth = (personal_keys.username(),personal_keys.password()))
    s_json = search.json()
    return s_json

# json file of patterns goes in, list of pattern ids comes out
def search_pattern_list(s_json):
    p_list = s_json['patterns']
    return [p_list[ind]['id'] for ind in list(range(0,len(p_list)))]

def search_to_list(term):
    s_json = search(term)
    return search_pattern_list(s_json)