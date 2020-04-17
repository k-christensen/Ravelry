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
    fav_list = get_favs_list(username)
    proj_list = get_project_list_from_username(username)
    full_list = list(set(fav_list+proj_list))
    df = pattern_list_to_df(full_list)
    user_data_dict = user_data(username)
    df['user_data'] = pd.Series(user_data_dict)
    return df 

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

user_profile = user_profile_df("katec125")
list(user_profile.columns)

user_profile.iloc[0]

example_dict = dict(zip(list(user_profile.columns), user_profile.loc['36436']))

[key for key in example_dict if example_dict[key] != 0]

user_profile.loc['36436']

single_pattern_request('36436')['yarn_weight']['name']


' ' in 'asdfas dfas'

'-'.join(string.split(' '))