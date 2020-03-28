import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import python_functions.personal_keys as personal_keys

# output: list of pattern ids for user's projects
def get_project_list(username):
    proj_list = []
    projects_url = 'https://api.ravelry.com/projects/{}/list.json'.format(username)
    projects = requests.get(projects_url, 
                        auth = (personal_keys.username(),personal_keys.password()))
    proj_list.extend([projects.json()['projects'][item]['pattern_id'] 
                    for item in range(0,len(projects.json()['projects']))])
    return proj_list
