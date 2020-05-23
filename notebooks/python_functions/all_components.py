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
from numpy.linalg import multi_dot


username = 'katec125'
search = 'default_search'

known_pattern_list = known_pattern_list(username)

search_list = pattern_pool_list(search)

search_minus_knowns =   [item for item in search_list 
                        if item not in known_pattern_list]

pattern_pool = pattern_list_to_df(search_minus_knowns)

user_profile = user_profile(username)

for item in list(pattern_pool.columns):
    if item not in user_profile.keys():
        user_profile[item] = 0

for key in list(user_profile):
    if key not in list(pattern_pool.columns):
        user_profile.pop(key)

pool_idf = [len(pattern_pool)/np.count_nonzero(pattern_pool[col]) for col in pattern_pool.columns]

idf_and_profile = np.array(pool_idf)*np.array(list(user_profile.values()))

predicted_user_prefs = {i:np.dot(idf_and_profile,pattern_pool.loc[i]) for i in pattern_pool.index}

pref_sort = dict((sorted(predicted_user_prefs.items(),key= lambda x: x[1], reverse=True)))

final_json = multiple_pattern_request(list(pref_sort)[:20])

for key in list(pref_sort):
    final_json['patterns'][key]['user_preference_score'] = predicted_user_prefs[key]

final_json['patterns'].keys()
# updata pattern pool to include predicted user prefs, 
# maybe order the entries by the predicted user prefs?

final_json['patterns'].keys()