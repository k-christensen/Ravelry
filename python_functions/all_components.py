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

def pattern_pool_df(username, search):
    known_patterns = known_pattern_list(username)
    search_list = pattern_pool_list(search)
    search_minus_knowns =   [item for item in search_list 
                            if item not in known_patterns]
    return pattern_list_to_df(search_minus_knowns)

def user_profile_edits(profile, pattern_pool):
    for item in list(pattern_pool.columns):
        if item not in profile.keys():
            profile[item] = 0

    for key in list(profile):
        if key not in list(pattern_pool.columns):
            profile.pop(key)
    return profile

def pref_scores(username, search = 'default_search', user_prof = None, save_user_profile = 'no'):
    pattern_pool = pattern_pool_df(username, search)
    
    if save_user_profile == 'yes':
        u_p = user_profile(username)
        with open("user_profile.json", "w") as outfile: 
            json.dump(u_p, outfile) 
    elif user_prof == 'None':
        u_p = user_profile(username)
    else:
        u_p = user_prof
    
    # edits pattern pool so that it deletes user profile attrs not in pattern pool 
    # and adds attrs that are in the pattern pool
    user_profile_edited = user_profile_edits(u_p, pattern_pool)

    pool_idf = [math.log(len(pattern_pool)/np.count_nonzero(pattern_pool[col])) for col in pattern_pool.columns]
    
    # combines idf and profile into one so they can be combined with the pattern pool
    # essentially, since you can't do a dot product of three matricies all at once
    # this part is done first, 
    # then the predicted user prefs are done in the next step 
    idf_and_profile = np.array(pool_idf)*np.array(list(user_profile_edited.values()))

    # dictionary object: key = pattern id, value is percent match 
    predicted_user_prefs = {i:np.dot(idf_and_profile,pattern_pool.loc[i]) for i in pattern_pool.index}

    return predicted_user_prefs


def final_json(predicted_user_prefs, trim_number = 20):
    # orders the dictionary so the best matches are the highest
    pref_sort = dict((sorted(predicted_user_prefs.items(),key= lambda x: x[1], reverse=True)))
    
    # trims down pref_sort to the top matches (number determined by the trim number)
    pref_sort_trim = dict([(k,v) for k,v in pref_sort.items()][:trim_number])

    # new pattern request is made with the top matches
    final_json = multiple_pattern_request(list(pref_sort_trim))

    # adds a feature for every pattern entry in the json: percent match
    for key in list(pref_sort_trim):
        final_json['patterns'][key]['percent_match'] = predicted_user_prefs[key]

    # this list is just a list of strings with rank_(insert number ranking here)
    rank_list = ['rank_{}'.format(num) for num in list(range(1,len(list(pref_sort_trim))+1))]

    # dict key is the pattern's rank by percent match and the value is pattern id
    rank_dict = dict(zip(rank_list, list(pref_sort_trim)))

    # creates new set of key value pairs 
    # where the key is the rank number (as seen in the rank dict keys) 
    # and the value is the pattern info 
    for k,v in rank_dict.items():
        if v in final_json['patterns'].keys():
            final_json['patterns'][k] = final_json['patterns'][v]

    # this takes out the initial dictionary entries 
    # where the key was the pattern id
    # thus the key values after ['patterns'] are the ranks, 
    # thus they'll be in order
    final_json['patterns'] = dict([(k,v) for k,v in final_json['patterns'].items()][len(pref_sort_trim):])
    
    return final_json 

def search_to_json(username, search = 'default_search', user_prof = None, save_user_profile = 'no', trim_number = 20):
    predicted_user_prefs = pref_scores(username, search, user_prof)
    return final_json(predicted_user_prefs, trim_number)

output_json = search_to_json('katec125', user_prof=json.load(open('user_profile.json')))

{'https://www.ravelry.com/patterns/library/{}'.format(output_json['patterns'][rank]['permalink']):output_json['patterns'][rank]['percent_match'] for rank in output_json['patterns']}