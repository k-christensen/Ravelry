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

# input: list of pattern id's and attribute list, which is a list of dictionaries
# if using pattern attr function, it would be the dictionary keys and values
def pattern_attr_to_count_df(pattern_list, attr_list):
#     in case pattern list is list of strings, make it into list of integers
    p_l = [int(item) for item in pattern_list]
#     turn list of dictionaries into a dataframe, turn all the NaN values into zero so the dataframe is ones and zeroes
    df_attr = pd.DataFrame(attr_list).fillna(0)
    df_attr['pattern_id'] = p_l
    df_attr = df_attr.set_index('pattern_id')
    return df_attr


# below function combines many of above functions such that all you put in is someone's username and it spits out dataframe of favs and projects
def get_user_favs_and_projects(username):
    fav_list = get_favs_list(username)
    proj_list = get_project_list(username)
    favs = pattern_attr(fav_list)
    projs = pattern_attr(proj_list)
    pf_df = pattern_attr_to_count_df(projs, favs)
    return pf_df