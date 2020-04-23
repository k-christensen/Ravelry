import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys

# search term goes in, search json comes out
def search(term):
    search_url = 'https://api.ravelry.com/patterns/search.json?query={}'.format(term)
    search = requests.get(search_url, auth = (personal_keys.username(),personal_keys.password()))
    s_json = search.json()
    return s_json

# json file of patterns goes in, list of pattern ids comes out
def search_pattern_list(s_json):
    p_list = s_json['patterns']
    return [p_list[ind]['id'] for ind in list(range(0,len(p_list)))]

def search_to_list(term):
    s_json = search(term)
    return search_pattern_list(s_json)

# turns list into string separated by '%7C', which is 'or' in the rav search url
def or_string(attr_list):
    return '%7C'.join(attr_list)

# creates the unique part of the search url
def unique_search_url_section(attr_dict):
    yarn_str = or_string(create_yarn_list(attr_dict['yarn_weight']))
    attr_str = or_string(attr_dict['pattern_attributes'])
    cat_str = or_string(attr_dict['pattern_categories'][1:])
    return 'weight={}&pa={}&pc={}'.format(yarn_str,attr_str,cat_str)

# creates full search url
def full_search_url(url_sect):
    return 'https://api.ravelry.com/patterns/search.json?{}&sort=recently-popular&view=captioned_thumbs'.format(url_sect)

# combo of previous two functions
def create_search_url(attr_dict):
    url_sect = unique_search_url_section(attr_dict)
    return full_search_url(url_sect)




# testing work~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
search_url = create_search_url(attr_dict)
search = requests.get(search_url, auth = (personal_keys.username(),personal_keys.password()))
s_json = search.json()
search

# note: some of the attributes actually go into 'fit' when you create the url, 
# I'm so fucking tired and I need to make a physical list because the world is a nightmare
# why couldn't this actually make sense
# why did I have to create my own yarn ids and now this
# why do I care so much
# I'm so tired

create_search_url(attr_dict)

search_example = search("#pc=pullover&sort=recently-popular&view=captioned_thumbs")
search_example['patterns'][0]['name']

from fav_funcs import *
from proj_funcs import *
from pattern_attr_funcs import *
from yarn_weights import *

attr_dict = single_request_to_attrs('36436')

attr_dict

'%7C'.join(create_yarn_list(attr_dict['yarn_weight']))
'%7C'.join(attr_dict['pattern_attributes'])

attr_dict['pattern_categories'][1:]


yarn_str = or_string(create_yarn_list(attr_dict['yarn_weight']))
attr_str = or_string(attr_dict['pattern_attributes'])
cat_str = or_string(attr_dict['pattern_categories'][1:])
'weight={}&pc={}&pa={}'.format(yarn_str,attr_str,cat_str)


# would want to do some kind of loop like "%7C" with the different attributes, 
# weight=[weight-1{}weight{}weight+1]&pc=[pattern_cat]&pa = [pattern_attr{}pattern_attr]

# example of url with weight, pattern category, and pattern attrs
# weight=dk%7Cworsted%7Caran&pc=pullover&pa=stripes-colorwork%7CIntarsia
#  url would be something like 
# 'https://api.ravelry.com/patterns/search.json?weight={}&pc={}&pa={}&sort=recently-popular&view=captioned_thumbs'.format(weight_list, pattern_cat_list, pattern_attr_list)