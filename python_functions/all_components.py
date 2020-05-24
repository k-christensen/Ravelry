import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys
import math
from fav_funcs import *
from proj_funcs import *
from pattern_attr_funcs import *
from search_functions import *
from yarn_weights import create_yarn_list
from count_df_funcs import *
import pickle

username = 'katec125'
search = 'default_search'

def search_minus_knowns(username, search):
    known_patterns = known_pattern_list(username)
    search_list = pattern_pool_list(search)
    search_minus_knowns =   [item for item in search_list 
                            if item not in known_patterns]
    return search_minus_knowns

def user_profile_edits(user_profile, pattern_pool):
    for item in list(pattern_pool.columns):
        if item not in user_profile.keys():
            user_profile[item] = 0

    for key in list(user_profile):
        if key not in list(pattern_pool.columns):
            user_profile.pop(key)
    return user_profile

search_minus_knowns = search_minus_knowns(username, search)

pattern_pool = pattern_list_to_df(search_minus_knowns)

user_profile = user_profile_edits(user_profile(username), pattern_pool)

pool_idf = [math.log(len(pattern_pool)/np.count_nonzero(pattern_pool[col])) for col in pattern_pool.columns]

idf_and_profile = np.array(pool_idf)*np.array(list(user_profile.values()))

predicted_user_prefs = {i:np.dot(idf_and_profile,pattern_pool.loc[i]) for i in pattern_pool.index}

pref_sort = dict((sorted(predicted_user_prefs.items(),key= lambda x: x[1], reverse=True)))

final_json = multiple_pattern_request(list(pref_sort)[:20])

for key in list(pref_sort)[:20]:
    final_json['patterns'][key]['user_preference_score'] = predicted_user_prefs[key]

pref_sort_20 = dict([(k,v) for k,v in pref_sort.items()][:20])

rank_list = ['rank_{}'.format(num) for num in list(range(1,len(list(pref_sort_20))+1))]

rank_dict = dict(zip(rank_list, list(pref_sort_20)))

for k,v in rank_dict.items():
    if v in final_json['patterns'].keys():
        final_json['patterns'][k] = final_json['patterns'][v]

final_json['patterns'] = dict([(k,v) for k,v in final_json['patterns'].items()][20:])

[final_json['patterns'][key]['permalink'] for key in final_json['patterns'].keys()]

# exporting things for testing in other files
with open("sample.json", "w") as outfile: 
    json.dump(final_json, outfile)

pickle.dump( pref_sort_20, open( "pref_sort_20.p", "wb" ) )