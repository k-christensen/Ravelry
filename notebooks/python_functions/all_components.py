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


username = 'katec125'
search = 'default_search'

user_profile = user_profile(username)

known_pattern_list = known_pattern_list(username)

search_list = pattern_pool_list(search)

search_minus_knowns =   [item for item in search_list 
                        if item not in known_pattern_list]

pattern_pool = multiple_pattern_request(search_minus_knowns)

pool_idf = #maybe just make this a list object

predicted_user_prefs = #dictionary with ids and predicted like scores

# updata pattern pool to include predicted user prefs, 
# maybe order the entries by the predicted user prefs?
