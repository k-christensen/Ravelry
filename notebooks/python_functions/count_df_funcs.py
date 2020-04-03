import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys
from fav_funcs import *
from proj_funcs import *
from pattern_attr_funcs import *


# input: dictionary created in all_attr_dict
# creates dataframe, index is pattern code, 
# cols are attrs, categories, and yarn weights
def pattern_attr_to_count_df(pattern_dict):
    df_attr = pd.DataFrame(list(pattern_dict.values()), 
            index=list(pattern_dict.keys())).fillna(0)
    return df_attr

# combo of previous func and all_attr_dict
def pattern_list_to_count_df(pattern_list):
    pattern_dict = all_attr_dict(pattern_list)
    df_attr = pattern_attr_to_count_df(pattern_dict)
    return df_attr

# below function combines many of above functions such that all you put in is someone's username and it spits out dataframe of favs and projects
def create_fav_df(username):
    fav_list = get_favs_list(username)
    fav_df = pattern_list_to_count_df(fav_list)
    return fav_df

def create_proj_df(username):
    proj_list = get_project_list(username)
    proj_df = pattern_attr_to_count_df(proj_list)
    return proj_df

