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


username = 'katec125'
search = 'default_search'

user_profile = user_profile(username)

known_pattern_list = known_pattern_list(username)

pattern_pool_json(search)

create_pattern_id_list()
