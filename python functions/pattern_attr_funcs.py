import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys

# multiple pattern request-
# input: list of patterns, output: json file with patterns
def multiple_pattern_request(pattern_list):
    patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(pattern_list))
    patterns = requests.get(patterns_url, 
                            auth = (personal_keys.username(),personal_keys.password()))
    if patterns.status_code is 200:
        return patterns.json()
    else:
        return 404

# input: pattern json from the multiple pattern request function
def create_attr_list(pattern_list):
    attr_list = []
    patterns = multiple_pattern_request(pattern_list)
    if patterns != 404:
        for key in patterns['patterns'].keys():
            attr_list.append({attr['permalink']:1 for attr in 
            patterns['patterns'][key]['pattern_attributes']})
    return attr_list

# input: list of pattern id's, 
# output: dictionary where keys are pattern id's and values are a dict of attributes
def pattern_attr(pattern_list):
    pattern_list = [str(item) for item in pattern_list]
    if len(pattern_list) < 50:
        attr_list = create_attr_list(pattern_list)
    else:
#         create nested list that contains lists of either 50 patterns or the remainder of length of list/50
        l_of_l_patterns = [pattern_list[i:i + 50] for i in range(0, len(pattern_list), 50)]
        batch_num = 0
        attr_list = []
        while batch_num < len(l_of_l_patterns):
            batch_attr_list = create_attr_list(l_of_l_patterns[batch_num])
            attr_list.extend(batch_attr_list)
            batch_num += 1
    return dict(zip(pattern_list, attr_list))