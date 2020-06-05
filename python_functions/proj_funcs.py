import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys as personal_keys
from fav_funcs import *

# returns json file with all the info about user patterns
def proj_json(username):
    projects_url = 'https://api.ravelry.com/projects/{}/list.json'.format(username)
    projects = requests.get(projects_url, 
                        auth = (personal_keys.username(),personal_keys.password()))
    return projects.json()

# output: list of pattern ids for user's projects
def project_list(p_json):
    proj_list = []
    proj_list.extend([p_json['projects'][item]['pattern_id'] 
                    for item in range(0,len(p_json['projects']))])
    return [item for item in proj_list if item is not None]

# puts together first two functions
def get_project_list_from_username(username):
    p_json = proj_json(username)
    return project_list(p_json)

# returns dictionary of project codes and user ratings, 
# default rating is 3 if none is given, 
# otherwise it's on a scale from 1-5 (hence the +1)

def project_rating(username):

    code_list = get_project_list_from_username(username)

    initial_list = [proj_json(username)['projects'][i]['rating'] 
    for i in range(0,len(proj_json(username)['projects'])) if 
    proj_json(username)['projects'][i]['pattern_id'] != None]

    rating_list = [3 if x == None else x for x in initial_list]
    return dict(zip(code_list, rating_list))


len(get_project_list_from_username('kerfufflesensue'))
# creates dictionary where the keys are 
# all user's favorites and projects
# all favorites get a 1 assigned
# projects get either their rating or 3 assigned
# the final dict is turned into a string so it 
# can combine with the existing user profile df
def user_data(username):
    user_data = fav_dict(username)
    user_data.update(project_rating(username))
    str_user_data_dict = {str(k):v for k,v in user_data.items()}
    return str_user_data_dict
