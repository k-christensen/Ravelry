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


# input: dictionary created in all_attr_dict
# creates dataframe, index is pattern code, 
# cols are attrs, categories, and yarn weights
def pattern_attr_to_df(pattern_dict):
    df_attr = pd.DataFrame(list(pattern_dict.values()), 
            index=list(pattern_dict.keys())).fillna(0)
    return df_attr

# combo of previous func and all_attr_dict
def pattern_list_to_df(pattern_list):
    pattern_dict = all_attr_dict(pattern_list)
    df_attr = pattern_attr_to_df(pattern_dict)
    return df_attr

def known_pattern_list(username):
    fav_list = get_favs_list(username)
    proj_list = get_project_list_from_username(username)
    full_list = list(set(fav_list+proj_list))
    return [item for item in full_list if item is not None]

# input is a username, 
# output is a df of all the user's 
# favs and projects in one dataframe
# dataframe columns include 
# pattern categories (prefaced with "pc_"), 
# pattern attributes (prefaced with "pa_"), 
# and yarn weight (prefaced with "yarn_id_")
# also includes a final column that is user data
# each code either gets a 1 if it's in favs
# a 3 or user's rating if it's in their projects
def user_profile_df(username):
    full_list = known_pattern_list(username)
    df = pattern_list_to_df(full_list)
    user_data_dict = user_data(username)
    df['user_data'] = pd.Series(user_data_dict)
    df = df.dropna()
    return df

# input: previous df, output dictionary with scores of how much a user likes a given attr
def user_profile_dict(user_data):
     return {col:np.dot(user_data[col],user_data.user_data) for col in list(user_data.columns)[:-1]}

# input: user profile df output, output is a json 
# with each columns' user score for each column 
# number of instances of that item 
# and at the end the len of the profile df
def user_profile_json(user_data):
    user_profile = {col:{"profile_num":
     np.dot(user_data[col],user_data.user_data)/len(user_data),
    "num_of_instances":
    np.count_nonzero(user_data[col])}
    for col in list(user_data.columns)[:-1]}
    user_profile["len_of_pool"] = len(user_data)
    return user_profile

# put together previous two funcs, input username, output dict of attrs and user scores
def user_profile(username, save_json = 'no'):
    user_data = user_profile_df(username)
    u_p = user_profile_json(user_data)
    if save_json != 'no':
        with open("{}_user_profile.json".format(username), "w") as outfile: 
            json.dump(u_p, outfile)
    return u_p

# below function combines many of above functions such that all you put in is someone's username and it spits out dataframe of favs and projects
def create_fav_df(username):
    fav_list = get_favs_list(username)
    fav_df = pattern_list_to_df(fav_list)
    return fav_df

def create_proj_df(username):
    proj_list = get_project_list_from_username(username)
    proj_df = pattern_attr_to_df(proj_list)
    return proj_df

# work~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

