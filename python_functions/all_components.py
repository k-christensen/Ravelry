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
    len_of_pool = profile['len_of_pool']
    for item in list(pattern_pool.columns):
        if item not in profile.keys():
            profile[item] = {'profile_num': 0, 'num_of_instances': 0}

    for key in list(profile)[:-1]:
        if key not in list(pattern_pool.columns):
            profile.pop(key)
    profile['len_of_pool'] = len_of_pool
    return profile

def user_json_and_profile(username, search = 'default_search', user_prof = 'None', save_user_profile = 'no'):
    pattern_pool = pattern_pool_df(username, search)
    
    if user_prof == 'None':
        u_json = user_profile(username, save_user_profile)
    else:
        u_json = user_prof
    # edits pattern pool so that it deletes user profile attrs not in pattern pool 
    # and adds attrs that are in the pattern pool
    user_profile_edited = user_profile_edits(u_json, pattern_pool)
    u_p = dict(zip(list(user_profile_edited),[item['profile_num'] 
    for item in list(user_profile_edited.values())[:-1]]))
    return [user_profile_edited,u_p]

def pref_scores(username, search = 'default_search', user_prof = 'None', save_user_profile = 'no'):
    user_list = user_json_and_profile(username, search, user_prof, save_user_profile)
    u_json = user_list[0]
    u_p = user_list[1]

    pattern_pool = pattern_pool_df(username, search)

    idf_numerator = u_json['len_of_pool']+len(pattern_pool)

    pattern_pool_instance_list = [np.count_nonzero(pattern_pool[col]) for col in pattern_pool.columns]
    user_instance_list = [item['num_of_instances'] for item in list(u_json.values())[:-1]]

    idf_denominator = [x+y for x,y in zip(pattern_pool_instance_list, user_instance_list)]
  
    pool_idf = [math.log(idf_numerator/denom) for denom in idf_denominator]
    
    # combines idf and profile into one so they can be combined with the pattern pool
    # essentially, since you can't do a dot product of three matricies all at once
    # this part is done first, 
    # then the predicted user prefs are done in the next step 
    idf_and_profile = np.array(pool_idf)*np.array(list(u_p.values()))

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

def search_to_json(username, search = 'default_search', user_prof = 'None', save_user_profile = 'no', trim_number = 20):
    predicted_user_prefs = pref_scores(username, search, user_prof, save_user_profile)
    return final_json(predicted_user_prefs, trim_number)

def link_and_score_json(username, output_json, save = 'no'):
    link_and_score_dict = {"https://www.ravelry.com/patterns/library/{}".format(
        output_json['patterns'][rank]['permalink']):
    output_json['patterns'][rank]['percent_match'] 
    for rank in output_json['patterns']}
    if save == 'yes':
        with open("{}_links_and_scores.json".format(username), "w") as outfile: 
            json.dump(link_and_score_dict, outfile)
    return link_and_score_dict

def search_to_link_and_score(username, search = 'default_search', 
                            user_prof = 'None', save_user_profile = 'no', 
                            trim_number = 20, save = 'no'):
    output_json = search_to_json(username, search, user_prof, save_user_profile, trim_number)
    return link_and_score_json(username, output_json, save)
 
# search_to_link_and_score(username = 'katec125', user_prof=json.load(open('katec125_user_profile.json')), save = 'yes')

# user_profile('katec125')


a = [1,2,3,4]
b = [2,3,4,5]

[x+y for x,y in zip(a,b)]