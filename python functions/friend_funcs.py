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

# input: username, output: list of user's friends
def friend_username_list(username):
    user_url = 'https://api.ravelry.com/people/{}/friends/list.json'.format(username)
    user = requests.get(user_url, 
                        auth = (personal_keys.username(),personal_keys.password()))
    return [user.json()['friendships'][item]['friend_username'] 
            for item in range(0,len(user.json()['friendships']))]

# input: username, output: user's friends' favs 
def get_friend_favs(username):    
    friend_list = friend_username_list(username)
    all_friend_projs = []
    for user in friend_list:
        all_friend_projs.append(get_favs_list(user))   
    flat_list = [item for sublist in all_friend_projs for item in sublist]
    edited_flat_list = [item for item in flat_list if item is not None]
    return edited_flat_list

# output: list of user's friends' projects 
def get_friend_projs(username):    
    friend_list = friend_username_list(username)
    all_friend_projs = []
    for user in friend_list:
        all_friend_projs.extend(get_project_list(user))        
    edited_proj_list = [item for item in all_friend_projs if item is not None]
    return edited_proj_list